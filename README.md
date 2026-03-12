# AI CRM - 客户群分析模块 (MVP)

## 目标
- 从公司 API 拉取客户群与消息
- 通过 Dify 处理并落库
- 人工检阅、分类客户群体
- 审核后写入 QA 知识库，并同步到 Dify

## 运行
1. 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. 设置环境变量（示例）

```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/ai_crm"
export DIFY_MOCK="true"
```

3. 启动服务

```bash
uvicorn app.main:app --reload
```

访问 `http://localhost:8000`

## 公司 API (WeWork Robot)
在首页填写基础地址与 ApiKey，保存后将持久化到本地数据库（`app_settings` 表）。
基础地址默认：`http://192.168.230.160:19000/api`

## 环境变量
- `DATABASE_URL`: Postgres 连接串
- `COMPANY_API_BASE`: 公司 API 基础地址（留空使用 mock）
- `COMPANY_API_TOKEN`: 公司 API Token
- `DIFY_BASE_URL`: Dify 基础地址
- `DIFY_API_KEY`: Dify API Key
- `DIFY_MESSAGE_PROCESS_URL`: Dify 处理消息接口 URL（必须）
- `DIFY_KB_UPSERT_URL`: Dify 知识库 upsert 接口 URL
- `DIFY_MOCK`: `true` 使用 mock
