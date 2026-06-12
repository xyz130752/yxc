from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import List, Optional

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from finance.database import add_record, delete_record, get_stats, init_db, list_records
from finance.models import DEFAULT_CATEGORIES

st.set_page_config(page_title="个人记账助手", layout="wide")
init_db()


def get_recent_months(count: int = 24) -> List[str]:
    today = date.today()
    months: List[str] = []
    for offset in range(count):
        year = today.year
        month = today.month - offset
        while month <= 0:
            month += 12
            year -= 1
        months.append(f"{year:04d}-{month:02d}")
    return months


def format_currency(value: float) -> str:
    return f"{value:.2f} 元"


def render_add_record() -> None:
    st.header("记账本")
    with st.form("add_record_form"):
        amount = st.number_input("金额", min_value=0.01, step=0.01, format="%.2f")
        category = st.selectbox("分类", DEFAULT_CATEGORIES)
        record_date = st.date_input("日期", value=date.today())
        note = st.text_input("备注（可选）")
        submitted = st.form_submit_button("提交")

    if submitted:
        try:
            record_id = add_record(
                amount,
                category,
                record_date,
                note.strip() or None,
            )
            st.success(f"记录已添加，ID = {record_id}")
        except Exception as exc:
            st.error(f"添加失败：{exc}")


def render_record_list() -> None:
    st.header("账目列表")

    month_options = ["全部"] + get_recent_months(24)
    category_options = ["全部"] + DEFAULT_CATEGORIES

    selected_month = st.selectbox("筛选月份", month_options, index=0)
    selected_category = st.selectbox("筛选分类", category_options, index=0)

    month_filter = None if selected_month == "全部" else selected_month
    category_filter = None if selected_category == "全部" else selected_category

    records = list_records(month_filter, category_filter)

    if not records:
        st.info("当前没有符合条件的账目。")
    else:
        st.dataframe(records, use_container_width=True)

    total_amount = sum(record["amount"] for record in records)
    total_count = len(records)

    st.markdown(
        f"**合计金额：{format_currency(total_amount)}    记录数：{total_count}**"
    )

    st.markdown("---")
    st.subheader("按 ID 删除记录")
    delete_id = st.number_input("输入要删除的记录 ID", min_value=1, step=1, format="%d")
    if st.button("删除记录"):
        deleted = delete_record(int(delete_id))
        if deleted:
            st.success(f"记录 {delete_id} 已删除，请刷新页面查看最新结果。")
        else:
            st.warning(f"未找到 ID 为 {delete_id} 的记录。")


def render_stats() -> None:
    st.header("分类统计")

    month_options = ["全部"] + get_recent_months(24)
    selected_month = st.selectbox("统计月份", month_options, index=0)
    month_filter = None if selected_month == "全部" else selected_month

    stats = get_stats(month_filter)
    total_amount = sum(item["total_amount"] for item in stats)

    rows = []
    for item in stats:
        percentage = (item["total_amount"] / total_amount * 100) if total_amount else 0.0
        rows.append(
            {
                "分类": item["category_name"],
                "笔数": item["count"],
                "合计": format_currency(item["total_amount"]),
                "占比": f"{percentage:.1f}%",
            }
        )

    st.table(rows)

    chart_data = {item["category_name"]: item["total_amount"] for item in stats}
    if any(value > 0 for value in chart_data.values()):
        st.bar_chart(chart_data)
    else:
        st.info("当前没有可展示的分类支出数据。")


def main() -> None:
    st.sidebar.title("导航")
    page = st.sidebar.radio("页面", ["记账本", "账目列表", "分类统计"])

    if page == "记账本":
        render_add_record()
    elif page == "账目列表":
        render_record_list()
    else:
        render_stats()


if __name__ == "__main__":
    main()
