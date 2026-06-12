from __future__ import annotations

import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from finance.models import DEFAULT_CATEGORIES
except ImportError:
    from .models import DEFAULT_CATEGORIES  # type: ignore

DB_DIR = Path.home() / ".finance-cli"
DB_PATH = DB_DIR / "data.db"


def _ensure_dir() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)


def get_conn() -> sqlite3.Connection:
    _ensure_dir()
    conn = sqlite3.connect(str(DB_PATH), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    schema_categories = """
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );
    """
    schema_records = """
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        category_id INTEGER NOT NULL,
        record_date TEXT NOT NULL,
        note TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (category_id) REFERENCES categories(id)
    );
    """
    with get_conn() as conn:
        conn.execute(schema_categories)
        conn.execute(schema_records)
        conn.executemany(
            "INSERT OR IGNORE INTO categories (name) VALUES (?)",
            [(name,) for name in DEFAULT_CATEGORIES],
        )
        conn.commit()


def _normalize_date(value: Union[str, date, datetime]) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        try:
            return date.fromisoformat(value).isoformat()
        except ValueError as exc:
            raise ValueError("日期格式必须是 YYYY-MM-DD") from exc
    raise ValueError("日期类型无效")


def add_record(
    amount: float,
    category_name: str,
    record_date: Union[str, date, datetime],
    note: Optional[str] = None,
) -> int:
    if amount <= 0:
        raise ValueError("金额必须大于 0")
    record_date_text = _normalize_date(record_date)

    with get_conn() as conn:
        cur = conn.execute(
            "SELECT id FROM categories WHERE name = ?",
            (category_name,),
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"分类不存在：{category_name}")

        category_id = row["id"]
        cur = conn.execute(
            "INSERT INTO records (amount, category_id, record_date, note) VALUES (?, ?, ?, ?)",
            (float(amount), category_id, record_date_text, note),
        )
        conn.commit()
        return cur.lastrowid


def list_records(
    month: Optional[str] = None,
    category_name: Optional[str] = None,
) -> List[Dict[str, Any]]:
    sql = """
    SELECT r.id, r.amount, r.category_id, r.record_date, r.note, r.created_at,
           c.name AS category_name
    FROM records r
    JOIN categories c ON c.id = r.category_id
    """
    conditions: List[str] = []
    params: List[Any] = []

    if month:
        conditions.append("strftime('%Y-%m', r.record_date) = ?")
        params.append(month)
    if category_name:
        conditions.append("c.name = ?")
        params.append(category_name)
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY r.record_date DESC, r.id DESC"

    with get_conn() as conn:
        cur = conn.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]


def delete_record(record_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM records WHERE id = ?",
            (record_id,),
        )
        conn.commit()
        return cur.rowcount > 0


def get_stats(month: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = """
    SELECT c.name AS category_name,
           COALESCE(SUM(r.amount), 0.0) AS total_amount,
           COUNT(r.id) AS count
    FROM categories c
    LEFT JOIN records r
      ON c.id = r.category_id
      AND (? IS NULL OR strftime('%Y-%m', r.record_date) = ?)
    GROUP BY c.id, c.name
    ORDER BY total_amount DESC
    """
    with get_conn() as conn:
        cur = conn.execute(sql, (month, month))
        return [
            {
                "category_name": row["category_name"],
                "total_amount": float(row["total_amount"] or 0.0),
                "count": int(row["count"]),
            }
            for row in cur.fetchall()
        ]
