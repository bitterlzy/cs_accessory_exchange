# CS饰品交换平台

> 基于 Python + FastAPI + SQLAlchemy 的 CS2 饰品 P2P 交换平台后端服务  
> 版本: 1.0.0 | 语言: Python 3.9+ | 数据库: MySQL 8.0

---

## 目录

- [项目介绍](#项目介绍)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [数据库设计（10 张表）](#数据库设计10-张表)
- [核心业务流程](#核心业务流程)
- [API 概览](#api-概览)
- [快速启动](#快速启动)
- [部署指南](#部署指南)
- [API 测试](#api-测试)
- [常见问题](#常见问题)
- [License](#license)

---

## 项目介绍

### 背景

《Counter-Strike 2》(CS2) 玩家拥有大量的饰品（武器皮肤、刀具、手套、贴纸、探员等），
但现有平台多以**现金交易**为主，缺少便捷的**物品互换**渠道。
本项目解决的是：**让玩家直接用自己的饰品交换别人的饰品，无需经过现金买卖环节。**

### 目标

- **发布交换需求**：玩家上架自己愿意拿出的饰品，描述想换什么
- **发现匹配**：浏览其他玩家的交换请求，找到心仪的目标
- **发起提议**：向对方发起一对多/多对一的交换提议
- **确认交换**：双方确认后系统自动转移物品所有权
- **实时通知**：WebSocket 推送每一步的状态变更

### 设计亮点

| 特点 | 说明 |
|---|---|
| **统一装备字典** | 全局唯一的 item_definitions 表，所有库存引用同一字典，消除数据孤岛 |
| **库存互斥锁** | 物品在被提议/上架时自动锁定，防止并发"双花"(double-spending) |
| **两阶段确认** | 提议 -> 接受 -> 确认，状态机防重入，确保数据一致性 |
| **全链路审计** | 每次状态变更写入 event_logs，交易全程可追溯 |
| **实时推送** | 基于 Socket.IO 的 WebSocket，状态变更即时通知 |

---

## 技术栈

| 层级 | 技术 | 说明 |
|---|---|---|
| 语言 | Python 3.9+ | 同步/异步混合 |
| Web 框架 | FastAPI | 自动 OpenAPI 文档 |
| ORM | SQLAlchemy 1.4 | 声明式模型 + 关系映射 |
| 数据库 | MySQL 8.0 | InnoDB 引擎，字符集 utf8mb4 |
| 认证 | JWT (python-jose) | access_token + refresh_token 双令牌 |
| 密码 | bcrypt | passlib + bcrypt 哈希 |
| 实时通信 | python-socketio | ASGI 模式挂载在 FastAPI 上 |
| 数据校验 | Pydantic v1 | 请求/响应模型自动校验 |
| 迁移工具 | Alembic | 数据库版本管理（已初始化） |

---

## 项目结构

`
cs_accessory_exchange/
|
+-- app/                          # 应用主目录
|   +-- __init__.py
|   +-- main.py                   # FastAPI 入口: 注册路由/CORS/中间件/Socket.IO
|   +-- config.py                 # Pydantic BaseSettings 配置 (环境变量)
|   +-- database.py               # SQLAlchemy 引擎/会话/依赖注入
|   +-- models.py                 # 10 张 ORM 数据模型
|   +-- schemas.py                # Pydantic 请求/响应 Schema
|   +-- deps.py                   # JWT 认证依赖注入
|   +-- errors.py                 # 业务异常类
|   +-- socketio_server.py        # Socket.IO 实时推送服务
|   +-- api/                      # REST API 路由模块
|       +-- __init__.py
|       +-- auth.py               # 注册 / 登录 / 令牌刷新
|       +-- users.py              # 用户信息查询
|       +-- inventory.py          # 库存管理 CRUD
|       +-- listings.py           # 交换请求发布/浏览/关闭
|       +-- offers.py             # 交换提议发起/接受/拒绝/确认
|       +-- trades.py             # 交换历史查询
|       +-- notifications.py      # 通知列表/标记已读
|
+-- docs/                         # 文档
|   +-- 01-requirements-analysis.md
|   +-- 02-database-design.md
|   +-- 03-api-test-report.md
|
+-- seed.py                       # 装备数据字典填充脚本 (70+ 热门饰品)
+-- requirements.txt              # Python 依赖
+-- .env                          # 环境变量配置
+-- .gitignore                    # Git 忽略规则
+-- README.md                     # 本文档
`


## 数据库设计（10 张表）

### 核心实体关系

`
users 1--N inventory_items
users 1--N listings
users 1--N trade_offers (as proposer / receiver)
item_definitions 1--N inventory_items
item_definitions 1--N listing_tracking
item_definitions 1--N item_prices
inventory_items 1--1 listings (offered_in)
trade_offers 1--N offer_items
trade_offers 1--N event_logs
listings 1--1 listing_tracking
`

### 各表用途

| 表名 | 说明 | 关键字段 |
|---|---|---|
| users | 用户账号 | email, username, password_hash, steam_id, reputation_score |
| item_definitions | 装备数据字典（全局唯一） | name, category, weapon_type, rarity, market_hash_name |
| inventory_items | 用户库存实例 | owner_id, definition_id, quality, float_value, stat_trak |
| listings | 交换请求 | seller_id, offered_item_id, want_description, want_category |
| listing_tracking | 上架跟踪（快速统计在出人数） | definition_id, user_id, listing_id, status |
| item_prices | 多源价格参考 | definition_id, quality, source, price_min/max/avg |
| trade_offers | 交换提议 | listing_id, proposer_id, receiver_id, status |
| offer_items | 提议物品明细 | trade_offer_id, inventory_item_id, side |
| event_logs | 审计日志 | trade_offer_id, actor_id, event_type, metadata |
| notifications | 通知记录 | user_id, type, title, body, is_read |


## 核心业务流程

### 交换状态机

`
                   +---> Rejected
                   |
Pending -----------+---> Cancelled
    |              |
    |              +---> Accepted ---> Confirmed ---> Completed
    |
    +---> Countered ---> Pending (重新进入)
`

### 完整交换流程

`	ext
 Alice                              Bob
  |                                  |
  |-- 注册/登录 -----------------------|
  |-- 添加饰品到库存                    |
  |-- 发布交换请求 (listing)           |
  |                                  |-- 浏览活跃请求
  |                                  |-- 发起交换提议 (offer)
  |-- 收到实时通知                     |
  |-- 接受提议                         |
  |-- 确认交换                         |
  |                                  |
  |    系统执行物品所有权转移            |
  |                                  |
  |-- 库存: 原物品 -> Bob             |
  |-- 库存: Bob的物品 -> Alice         |
  |                                  |
  |-- 查看交换历史                     |
  |-- 收到通知                        |
`

### 关键约束

1. 库存互斥：一件饰品同时只能出现在一个活跃的 Listing 或 Offer 中
2. 所有权校验：仅饰品拥有者可操作，系统校验 user_id == item.owner_id
3. 防重入：状态机确保每个状态只可进入一次
4. 审计留痕：所有状态变更写入 event_logs，全链路可追溯


## API 概览

### 认证 /api/auth

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| POST | /api/auth/register | 注册（bcrypt 哈希） | 否 |
| POST | /api/auth/login | 登录，返回 JWT 双令牌 | 否 |
| POST | /api/auth/refresh | 刷新 access_token | 否 |

### 用户 /api/users

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | /api/users/me | 当前用户信息 | 是 |
| GET | /api/users/{id} | 公开资料 | 否 |

### 库存 /api/inventory

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | /api/inventory | 我的库存列表 | 是 |
| POST | /api/inventory | 添加饰品 | 是 |
| DELETE | /api/inventory/{id} | 移除饰品 | 是 |

### 交换请求 /api/listings

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | /api/listings | 浏览活跃请求 | 否 |
| GET | /api/listings/my | 我发布的请求 | 是 |
| POST | /api/listings | 发布请求（锁定物品） | 是 |
| PATCH | /api/listings/{id}/close | 关闭请求 | 是 |

### 交换提议 /api/offers

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | /api/offers | 我收到/发出的提议 | 是 |
| POST | /api/offers | 发起提议（锁定物品） | 是 |
| POST | /api/offers/{id}/accept | 接受提议 | 是 |
| POST | /api/offers/{id}/reject | 拒绝提议 | 是 |
| POST | /api/offers/{id}/confirm | 确认交换（所有权转移） | 是 |

### 交换历史 /api/trades

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | /api/trades | 我的完成交换记录 | 是 |
| GET | /api/trades/{id} | 交换详情 | 是 |

### 通知 /api/notifications

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | /api/notifications | 通知列表（分页/未读筛选） | 是 |
| PATCH | /api/notifications/{id}/read | 标记已读 | 是 |
| POST | /api/notifications/read-all | 全部标记已读 | 是 |

### WebSocket

端点: /ws (Socket.IO)
认证: JWT token (auth.token)

客户端示例:
`javascript
import { io } from socket.io-client;
const socket = io(http://localhost:3000/ws, {
  auth: { token: your-jwt-token }
});
socket.on(offer_update, (data) => console.log(data));
socket.on(notification, (data) => console.log(data));
`

### API 文档（启动后）

- Swagger UI: http://localhost:3000/docs
- ReDoc: http://localhost:3000/redoc
- 健康检查: http://localhost:3000/api/health


## 快速启动

### 前置要求

- Python 3.9+
- MySQL 8.0+
- pip

### 步骤

`ash
# 1. 克隆项目
git clone <your-repo-url>
cd cs_accessory_exchange

# 2. 创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS cs_trade_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 3. 配置环境变量
#    编辑 .env 文件中的 DATABASE_URL 和 JWT 密钥

# 4. 安装依赖
pip install -r requirements.txt

# 5. 初始化数据库（建表 + 种子数据）
python seed.py

# 6. 启动开发服务器
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload

# 7. 验证
curl http://localhost:3000/api/health
# 预期输出: {"status": "ok", "timestamp": "..."}
`

### 已知兼容性问题

在 Windows 环境下首次启动可能遇到以下问题，均已修复:

1. 将 app/models.py 中 sqlalchemy 的 Decimal 改为 Numeric
2. 将 EventLog 类的 metadata 属性命名为 event_metadata
3. 降级 bcrypt: pip install bcrypt==4.0.1
4. 设置环境变量: $env:PYTHONIOENCODING='utf-8'

---

## 部署指南

### 生产环境部署

`ash
# 1. 关闭 SQLAlchemy SQL 日志
#    编辑 .env: DEBUG=false

# 2. 使用 Gunicorn + Uvicorn Worker（Linux）
pip install gunicorn
gunicorn app.main:app   --worker-class uvicorn.workers.UvicornWorker   --workers 4   --bind 0.0.0.0:8000

# 3. Nginx 反向代理配置示例
# server {
#     listen 80;
#     server_name your-domain.com;
#     location / {
#         proxy_pass http://127.0.0.1:8000;
#     }
#     location /ws {
#         proxy_pass http://127.0.0.1:8000;
#         proxy_http_version 1.1;
#         proxy_set_header Upgrade ;
#         proxy_set_header Connection "upgrade";
#     }
# }
`

### 环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| DATABASE_URL | mysql+pymysql://root:@...localhost:3306/cs_trade_db | MySQL 连接 |
| JWT_SECRET | cs-trade-jwt-secret-dev-2026 | JWT 签名密钥 |
| JWT_REFRESH_SECRET | cs-trade-refresh-secret-dev-2026 | 刷新令牌密钥 |
| CORS_ORIGINS | ["http://localhost:5173","http://localhost:3000"] | 允许的跨域源 |
| PORT | 3000 | 服务端口 |
| LOG_LEVEL | debug | 日志级别 |

---

## API 测试

完整测试报告: docs/03-api-test-report.md

手动测试示例:

`ash
# 注册
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"test123"}'

# 登录
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'
`

测试结果: 25 个业务端点全部通过，涵盖完整交换流程。

---

## 常见问题

### Q: 启动时报 cannot import name Decimal from sqlalchemy
A: 修改 app/models.py，将 Decimal 替换为 Numeric。

### Q: metadata is reserved 错误
A: EventLog 类的 metadata 属性是 SQLAlchemy 保留字，已改为 event_metadata。

### Q: passlib + bcrypt 报错
A: 降级 bcrypt 到 4.0.x: pip install bcrypt==4.0.1

### Q: UnicodeEncodeError
A: Windows 终端默认 GBK 编码。设置: $env:PYTHONIOENCODING='utf-8'

### Q: 数据库连接失败
A: 确认 MySQL 服务运行中，检查 .env 中的 DATABASE_URL 是否正确。

---

## License

MIT
