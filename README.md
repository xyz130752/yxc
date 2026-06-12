# finance-cli

一个简单的 Python Streamlit 记账工具，支持：

- 添加账目（金额、分类、日期、备注）
- 查看账目列表（按月份和分类筛选）
- 删除账目（按 ID 删除）
- 分类统计（统计表 + 柱状图）

## 快速开始

1. 创建并激活虚拟环境：

```bash
python -m venv .venv
.venv\\Scripts\\activate
```

2. 安装依赖：

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> 如果没有 `requirements.txt`，可以直接安装：

```bash
pip install streamlit
```

3. 运行应用：

```bash
streamlit run finance/web.py
```

## 项目结构

- `finance/` - 应用包
  - `models.py` - 数据模型（`DEFAULT_CATEGORIES`, `Category`, `Record`）
  - `database.py` - 使用 SQLite 的数据库操作
  - `web.py` - Streamlit 前端界面
- `tests/smoke_test.py` - 简单的烟雾测试脚本
- `README.md` - 本文档

## 数据库

应用会在用户主目录下创建数据库文件：

- Windows: `%USERPROFILE%\\.finance-cli\\data.db`
- macOS / Linux: `~/.finance-cli/data.db`

默认分类：餐饮、交通、购物、娱乐、居住、其他。

## 运行测试

本项目提供两个测试方式：

### 1. 烟雾测试

```bash
python tests/smoke_test.py
```

### 2. Pytest 单元测试

```bash
pytest
```

## 其他说明

- 本地数据库文件会自动创建在用户主目录：
  - Windows: `%USERPROFILE%\\.finance-cli\\data.db`
  - macOS / Linux: `~/.finance-cli/data.db`
- 默认分类：餐饮、交通、购物、娱乐、居住、其他。
- 如果你希望忽略本地 Python 虚拟环境，请确保 `.venv/` 已添加到 `.gitignore`。

## 许可

MIT
