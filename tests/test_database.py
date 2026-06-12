import tempfile
from pathlib import Path

import pytest

import finance.database as db


def test_database_crud(tmp_path: Path) -> None:
    db.DB_DIR = tmp_path / ".finance-cli"
    db.DB_PATH = db.DB_DIR / "data.db"

    db.init_db()
    assert db.DB_PATH.exists()

    record_id = db.add_record(10.00, "餐饮", "2026-06-12", "测试")
    assert record_id > 0

    records = db.list_records("2026-06", None)
    assert any(record["id"] == record_id for record in records)
    assert all(record["category_name"] == "餐饮" for record in records)

    stats = db.get_stats("2026-06")
    assert isinstance(stats, list)
    assert any(item["count"] >= 1 for item in stats)

    deleted = db.delete_record(record_id)
    assert deleted


def test_add_record_unknown_category(tmp_path: Path) -> None:
    db.DB_DIR = tmp_path / ".finance-cli"
    db.DB_PATH = db.DB_DIR / "data.db"
    db.init_db()

    with pytest.raises(ValueError, match="分类不存在"):
        db.add_record(5.0, "未知分类", "2026-06-12", "测试")
