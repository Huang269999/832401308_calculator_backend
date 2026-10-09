# 前后端分离计算器 - 后端

## 项目简介

本仓库是软件工程实践第一次作业的后端项目。后端负责表达式校验、安全解析、计算、异常处理以及 SQLite 历史记录持久化，不使用 `eval` / `exec` 执行用户输入。

## 技术栈

- Python 3.10+
- FastAPI
- SQLite
- Uvicorn

## 目录

```text
app/
├── calculator_service.py  # 表达式解析与计算
├── database.py            # SQLite 数据访问
├── main.py                # API
└── schemas.py             # 请求模型
tests/
└── test_calculator_service.py
```

## 安装

```bash
python -m venv .venv
```

Windows：

```bash
.venv\Scripts\activate
```

macOS / Linux：

```bash
source .venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

## 启动

```bash
uvicorn app.main:app --reload
```

默认地址：`http://127.0.0.1:8000`

接口文档：`http://127.0.0.1:8000/docs`

## 数据库初始化

无需手工建表。首次启动时自动生成 `calculator.db`，并创建 `calculation_history` 表。

如需自定义数据库文件位置，可设置环境变量：

```text
CALCULATOR_DB_PATH=/path/to/calculator.db
```

## CORS 配置

默认允许：

- `http://127.0.0.1:5500`
- `http://localhost:5500`

部署时可通过环境变量设置：

```text
CORS_ORIGINS=https://your-frontend.example.com
```

多个域名使用英文逗号分隔。

## API

### POST `/api/calculate`

请求：

```json
{"expression":"(1+2)*3"}
```

成功：

```json
{"success":true,"id":1,"expression":"(1+2)*3","result":9}
```

### GET `/api/history`

查询数据库中的计算历史。

### DELETE `/api/history/{id}`

删除指定历史记录。

### DELETE `/api/history`

扩展功能：清空全部历史记录。

## 测试

```bash
pip install -r requirements-dev.txt
pytest -q
```

## 前后端连接

前端 `src/config.js` 中的 `API_BASE_URL` 应指向本后端地址。本地开发默认：

```js
window.APP_CONFIG = {
    API_BASE_URL: "http://127.0.0.1:8000",
};
```
