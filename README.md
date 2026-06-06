# CS饰品交换平台

> 基于 Python + FastAPI + SQLAlchemy + Vue 3 的 CS2 饰品 P2P 交换全栈平台  
> 版本: 1.0.0 | 后端: Python 3.8+ | 前端: Vue 3 + Vite | 数据库: MySQL 8.0

---

## 目录

- [项目介绍](#项目介绍)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [数据库设计（10 张表）](#数据库设计10-张表)
- [核心业务流程](#核心业务流程)
- [API 概览](#api-概览)
- [前端概览](#前端概览)
- [快速启动（后端）](#快速启动后端)
- [快速启动（前端）](#快速启动前端)
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
| **全栈覆盖** | Python 后端 + Vue 3 前端，开发环境通过 Vite 代理无缝集成 |

---

## 技术栈

### 后端

| 层级 | 技术 | 说明 |
|---|---|---|
| 语言 | Python 3.8+ | 同步/异步混合 |
| Web 框架 | FastAPI | 自动 OpenAPI 文档 |
| ORM | SQLAlchemy 1.4 | 声明式模型 + 关系映射 |
| 数据库 | MySQL 8.0 | InnoDB 引擎，字符集 utf8mb4 |
| 认证 | JWT (python-jose) | access_token + refresh_token 双令牌 |
| 密码 | bcrypt | 直接使用 bcrypt 库哈希 |
| 实时通信 | python-socketio | ASGI 模式挂载在 FastAPI 上 |
| 数据校验 | Pydantic v1 | 请求/响应模型自动校验 |
| 迁移工具 | Alembic | 数据库版本管理（已初始化） |

### 前端

| 层级 | 技术 | 说明 |
|---|---|---|
| 框架 | Vue 3 (Composition/Options API) | SFC 单文件组件 |
| 构建工具 | Vite 5 | 快速 HMR 开发服务器 |
| 路由 | Vue Router 4 | Hash 模式，导航守卫鉴权 |
| HTTP | Axios | API 调用，自动 Token 管理 |
| 代理 | Vite Proxy | 开发环境自动代理 /api 到后端 |

---

## 项目结构

```
cs_accessory_exchange/
│
├── app/                          # 后端应用主目录
│   ├── __init__.py
│   ├── main.py                   # FastAPI 入口: 注册路由/CORS/中间件/Socket.IO
│   ├── config.py                 # Pydantic BaseSettings 配置 (环境变量)
│   ├── database.py               # SQLAlchemy 引擎/会话/依赖注入
│   ├── models.py                 # 10 张 ORM 数据模型
│   ├── schemas.py                # Pydantic 请求/响应 Schema
│   ├── deps.py                   # JWT 认证依赖注入
│   ├── errors.py                 # 业务异常类
│   ├── socketio_server.py        # Socket.IO 实时推送服务
│   └── api/                      # REST API 路由模块
│       ├── auth.py               # 注册 / 登录 / 令牌刷新
│       ├── users.py              # 用户信息查询
│       ├── kyc.py                # 实名认证
│       ├── inventory.py          # 库存管理 CRUD
│       ├── listings.py           # 交换请求发布/浏览/关闭
│       ├── offers.py             # 交换提议发起/接受/拒绝/确认
│       ├── trades.py             # 交换历史查询
│       ├── notifications.py      # 通知列表/标记已读
│       └── steam.py              # Steam 账号绑定
│
├── frontend/                     # 前端应用目录
│   ├── index.html                # 入口 HTML
│   ├── package.json              # 依赖配置
│   ├── vite.config.js            # Vite 配置 + API 代理
│   └── src/
│       ├── main.js               # 应用入口
│       ├── App.vue               # 主组件 + 导航栏
│       ├── api/index.js          # Axios API 层 (12 个模块)
│       ├── router/index.js       # Vue Router (Hash 模式)
│       └── views/                # 11 个页面组件
│           ├── Login.vue         # 登录
│           ├── Register.vue      # 注册
│           ├── Dashboard.vue     # 仪表盘
│           ├── Inventory.vue     # 库存管理
│           ├── Listings.vue      # 浏览请求
│           ├── MyListings.vue    # 我的请求
│           ├── Offers.vue        # 交换提议
│           ├── Trades.vue        # 交换历史
│           ├── Notifications.vue # 通知
│           ├── KYC.vue           # 实名认证
│           └── Steam.vue         # Steam 绑定
│
├── docs/                         # 文档
│   ├── 01-requirements-analysis.md
│   ├── 02-database-design.md
│   ├── 03-api-test-report.md
│   └── api_test_script.sh        # 自动化 API 测试脚本
│
├── middleware/                   # 中间件
│   └── security.py               # 安全中间件
│
├── services/                     # 外部服务
│   └── buff_scraper.py           # BUFF 价格同步
│
├── seed.py                       # 装备数据字典填充脚本 (75 条热门饰品)
├── requirements.txt              # Python 依赖
├── .env                          # 环境变量配置
├── .gitignore                    # Git 忽略规则
└── README.md                     # 本文档
```

## 数据库设计（10 张表）

### 核心实体关系

```
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
```

### 各表用途

| 表名 | 说明 | 关键字段 |
|---|---|---|
| users | 用户账号 | email, username, password_hash, steam_id, reputation_score |
| user_verifications | 实名认证 | real_name, id_number_hash, alipay_account, verification_level |
| steam_accounts | Steam 账号绑定 | steam_id, trade_url, is_primary, is_verified |
| item_definitions | 装备数据字典（全局唯一） | name, category, weapon_type, rarity, market_hash_name |
| inventory_items | 用户库存实例 | owner_id, definition_id, quality, float_value, stat_trak |
| listings | 交换请求 | seller_id, offered_item_id, want_description, want_category |
| listing_tracking | 上架跟踪（快速统计） | definition_id, user_id, listing_id, status |
| item_prices | 多源价格参考 | definition_id, quality, source, price_min/max/avg |
| trade_offers | 交换提议 | listing_id, proposer_id, receiver_id, status |
| offer_items | 提议物品明细 | trade_offer_id, inventory_item_id, side |
| event_logs | 审计日志 | trade_offer_id, actor_id, event_type, metadata |
| notifications | 通知记录 | user_id, type, title, body, is_read |
| platform_bots | 平台机器人 | bot_steam_id, status, inventory_snapshot |
| steam_trade_operations | Steam 交易操作 | operation_type, status, trade_offer_id |

---

## 核心业务流程

### 交换状态机

```
                   +---> Rejected
                   |
Pending -----------+---> Cancelled
    |              |
    |              +---> Accepted ---> Confirmed ---> Completed
    |
    +---> Countered ---> Pending (重新进入)
```

### 完整交换流程

```
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
```

### 关键约束

1. 库存互斥：一件饰品同时只能出现在一个活跃的 Listing 或 Offer 中
2. 所有权校验：仅饰品拥有者可操作，系统校验 user_id == item.owner_id
3. 防重入：状态机确保每个状态只可进入一次
4. 审计留痕：所有状态变更写入 event_logs，全链路可追溯

---

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

### 实名认证 /api/kyc

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| GET | /api/kyc/status | 认证状态 | 是 |
| POST | /api/kyc/submit | 提交认证信息 | 是 |
| POST | /api/kyc/verify | 模拟通过认证 | 是 |

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

### Steam /api/steam

| 方法 | 路径 | 说明 | 认证 |
|---|---|---|---|
| POST | /api/steam/link | 绑定 Steam 账号（终生制） | 是 |
| GET | /api/steam/accounts | 查看已绑定账号 | 是 |

### WebSocket

端点: /ws (Socket.IO)
认证: JWT token (auth.token)

客户端示例:
```javascript
import { io } from 'socket.io-client';
const socket = io('http://localhost:3000/ws', {
  auth: { token: your-jwt-token }
});
socket.on('offer_update', (data) => console.log(data));
socket.on('notification', (data) => console.log(data));
```

### API 文档（启动后）

- Swagger UI: http://localhost:3000/docs
- ReDoc: http://localhost:3000/redoc
- 健康检查: http://localhost:3000/api/health

---

## 前端概览

### 页面功能

| 页面 | 路由 | 功能 |
|---|---|---|
| 登录 | /login | 邮箱密码登录，Token 持久化 |
| 注册 | /register | 新用户注册 |
| 仪表盘 | /dashboard | 统计数据：库存数/请求数/提议数/已完成交换 |
| 库存管理 | /inventory | 查看/搜索/添加/删除饰品 |
| 浏览请求 | /listings | 浏览全部活跃请求，发起交换提议 |
| 我的请求 | /my-listings | 查看/发布/关闭自己的请求 |
| 交换提议 | /offers | 管理收到的/发出的提议，接受/拒绝/确认 |
| 交换历史 | /trades | 已完成交换记录 |
| 通知 | /notifications | 查看/标记已读/全部已读 |
| 实名认证 | /kyc | 提交认证信息/模拟通过 |
| Steam 绑定 | /steam | 绑定/查看 Steam 账号（终生制） |

### 前端架构特点

- **API 代理**: 开发环境 Vite 自动代理 /api 请求到后端 (localhost:5173 -> localhost:3000)
- **Token 管理**: Axios 拦截器自动携带 JWT，401 自动刷新令牌
- **路由守卫**: 未登录自动跳转登录页
- **Hash 路由**: 使用 Hash 模式，部署无需服务端路由配置

---

## 快速启动（后端）

### 前置要求

- Python 3.8+
- MySQL 8.0+
- pip

### 步骤

```bash
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
```

### 运行自动化测试

```bash
# 后端 API 测试脚本
bash docs/api_test_script.sh
```

---

## 快速启动（前端）

### 前置要求

- Node.js 18+
- npm

### 步骤

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器（需后端先启动）
npm run dev

# 4. 打开浏览器
# http://localhost:5173
```

**注意**: 前端通过 Vite 代理将 /api 请求转发到后端，请确保后端先启动（端口 3000）。

### 生产构建

```bash
cd frontend
npm run build
# 输出到 dist/ 目录，可部署到任意静态服务器
# 部署后需配置反向代理将 /api 转发到后端
```

---

## 部署指南

### 后端部署

```bash
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
#         proxy_set_header Upgrade $http_upgrade;
#         proxy_set_header Connection "upgrade";
#     }
# }
```

### 环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| DATABASE_URL | mysql+pymysql://root:@localhost:3306/cs_trade_db | MySQL 连接 |
| JWT_SECRET | cs-trade-jwt-secret-dev-2026 | JWT 签名密钥 |
| JWT_REFRESH_SECRET | cs-trade-refresh-secret-dev-2026 | 刷新令牌密钥 |
| CORS_ORIGINS | ["http://localhost:5173","http://localhost:3000"] | 允许的跨域源 |
| PORT | 3000 | 服务端口 |
| LOG_LEVEL | debug | 日志级别 |

---

## API 测试

完整测试报告: [docs/03-api-test-report.md](./docs/03-api-test-report.md)
测试用例文档: [docs/05-api-test-cases.md](./docs/05-api-test-cases.md)
自动化脚本: [docs/api_test_script.sh](./docs/api_test_script.sh)

### 测试结果摘要

| 模块 | 通过率 | 测试项 |
|---|---|---|
| 认证模块 | 5/5 | 注册、登录、重复注册、令牌刷新 |
| 用户模块 | 2/2 | 获取信息、公开资料 |
| 实名认证 | 6/6 | 提交、身份证查重、验证 |
| 库存管理 | 4/4 | 添加、筛选、删除、无效定义 |
| 交换请求 | 5/5 | 发布、锁定、浏览、关闭、权限 |
| 交换提议 | 5/5 | 发起、接受、拒绝、确认、权限 |
| 所有权转移 | 已验证 | 物品跨用户自动转移 |
| 交换历史 | 1/1 | 已完成记录查询 |
| 通知系统 | 2/2 | 列表、标记已读 |
| Steam 绑定 | 5/5 | 绑定、重复、唯一性 |
| 安全测试 | 2/2 | 无令牌、伪造令牌 |
| **合计** | **38/38** | **全部通过** |

### 手动测试示例

```bash
# 注册
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"test123","phone":"13800138000"}'

# 登录
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'
```

---

## 常见问题

### Q: 启动时报 cannot import name Decimal from sqlalchemy
A: 修改 app/models.py，将 Decimal 替换为 Numeric。

### Q: metadata is reserved 错误
A: EventLog 类的 metadata 属性是 SQLAlchemy 保留字，已改为 event_metadata。

### Q: bcrypt 报错 "module 'bcrypt' has no attribute '__about__'"
A: passlib 和 bcrypt 新版本不兼容。解决方案：修改 app/api/auth.py 使用 bcrypt.hashpw/checkpw 替代 passlib 的 CryptContext。

### Q: Python 3.8 报错 "TypeError: 'type' object is not subscriptable"
A: Python 3.8 不支持 list[Model] 语法。解决方案：将 list[X] 改为 List[X]（from typing import List）。

### Q: UnicodeEncodeError
A: Windows 终端默认 GBK 编码。设置: $env:PYTHONIOENCODING='utf-8'

### Q: 数据库连接失败
A: 确认 MySQL 服务运行中，检查 .env 中的 DATABASE_URL 是否正确。
   如在 WSL 中运行，需将 localhost 改为 Windows 主机 IP（如 172.25.0.1）。

### Q: 前端 API 请求失败
A: 确认后端已启动（端口 3000），前端 Vite 代理配置正确（vite.config.js 中 proxy 指向正确的后端地址）。

---

## License

MIT
