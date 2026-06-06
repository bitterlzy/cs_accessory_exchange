# CS饰品交换平台 — 后端服务 (Python/FastAPI)

基于 Python + FastAPI + SQLAlchemy 构建的 CS2 饰品 P2P 交换平台后端。

## 技术栈

- **语言**: Python 3.9+
- **框架**: FastAPI (异步)
- **ORM**: SQLAlchemy 1.4 (同步)
- **数据库**: MySQL 8.0
- **认证**: JWT (python-jose)
- **实时通信**: python-socketio
- **数据验证**: Pydantic v1

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件（已配置好 MySQL 连接密码）。

### 3. 初始化数据库表 & 种子数据

```bash
# 建表 + 填充装备字典
python seed.py
```

### 4. 启动开发服务器

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 3000
```

## 项目结构

```
app/
├── main.py              # FastAPI 应用入口
├── config.py            # 配置 (BaseSettings)
├── database.py          # SQLAlchemy 引擎和会话
├── models.py            # 数据模型 (10 张表)
├── schemas.py           # Pydantic 请求/响应模型
├── deps.py              # 依赖注入 (JWT 认证)
├── errors.py            # 错误处理
├── api/
│   ├── auth.py          # 注册/登录/刷新
│   ├── users.py         # 用户管理
│   ├── inventory.py     # 库存管理
│   ├── listings.py      # 交换请求
│   ├── offers.py        # 交换提议 (含事务锁)
│   ├── trades.py        # 交换历史
│   └── notifications.py # 通知系统
└── socketio_server.py   # Socket.IO 实时服务
seed.py                  # 装备数据字典填充 (70+ 热门饰品)
```

## API 文档

启动后访问:
- Swagger UI: http://localhost:3000/docs
- ReDoc: http://localhost:3000/redoc
- 健康检查: http://localhost:3000/api/health

## WebSocket 连接

```js
// 客户端连接示例 (JavaScript)
import { io } from "socket.io-client";
const socket = io("http://localhost:3000/ws", {
  auth: { token: "your-jwt-token" }
});
socket.on("offer_update", (data) => console.log(data));
socket.on("notification", (data) => console.log(data));
```
