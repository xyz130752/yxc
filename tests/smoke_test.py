from finance.database import add_record, delete_record, get_stats, init_db, list_records


def main() -> None:
    init_db()
    print("数据库初始化完成。")

    record_id = add_record(18.80, "餐饮", "2026-06-12", "测试午餐")
    print(f"已添加测试记录，ID={record_id}")
    assert record_id > 0

    records = list_records("2026-06", None)
    print(f"查询到 {len(records)} 条记录。")
    assert any(record["id"] == record_id for record in records)

    stats = get_stats("2026-06")
    print("分类统计结果：")
    for item in stats:
        print(f"  {item['category_name']}: 笔数={item['count']}，合计={item['total_amount']:.2f}")
    assert isinstance(stats, list)

    deleted = delete_record(record_id)
    print(f"删除测试记录 ID={record_id}，结果={deleted}")
    assert deleted

    print("smoke test passed.")


if __name__ == "__main__":
    main()
