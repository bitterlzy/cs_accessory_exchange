# CS饰品交换平台 — 后端服务

用于《Counter-Strike 2》玩家之间的饰品 P2P 交换平台后端。

## 技术栈

- **运行时**: Node.js 20+ (TypeScript)
- **框架**: Express.js + Socket.IO
- **ORM**: Prisma
- **数据库**: MySQL 8.0
- **缓存**: Redis (可选, 用于 WS 跨进程广播)
- **认证**: JWT (access_token + refresh_token)

## 快速开始

### 1. 环境准备

```bash
# Node.js 20+ (推荐用 nvm)
nvm install 20
nvm use 20

# MySQL 8.0 (需提前安装)
# Redis (可选, 用于生产环境)
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env, 填入你的 MySQL 连接信息
```

### 3. 安装依赖 & 初始化数据库

```bash
npm install
npm run prisma:generate
npm run prisma:push    # 同步表结构到数据库
npm run prisma:seed    # 填充装备数据字典
```

### 4. 启动开发服务器

```bash
npm run dev
```

服务默认运行在 `http://localhost:3000`.

## 项目结构

```
src/
├── config/          # 配置
├── middleware/      # 中间件 (auth, validation, error)
├── routes/          # API 路由
│   ├── auth.ts          # 注册/登录/刷新令牌
│   ├── users.ts         # 用户管理
│   ├── inventory.ts     # 库存管理
│   ├── listings.ts      # 交换请求
│   ├── offers.ts        # 交换提议
│   ├── trades.ts        # 交换历史
│   └── notifications.ts # 通知
├── services/        # 业务服务 (Socket.IO)
└── index.ts         # 入口文件
prisma/
├── schema.prisma    # 数据库模型 (10 张表)
└── seed.ts          # 装备数据字典填充 (70+ 热门饰品)
docs/                # 需求分析 & 数据库设计文档
```

## WebSocket 事件

连接地址: `ws://localhost:3000?token=<JWT_TOKEN>`

| 事件 | 方向 | 说明 |
|------|------|------|
| `notification` | 服务→客户端 | 新通知推送 |
| `offer_update` | 服务→客户端 | 提议状态变更 |
| `user_online` | 双向 | 在线状态广播 |

## API 概览

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 注册 |
| POST | /api/auth/login | 登录 |
| POST | /api/auth/refresh | 刷新令牌 |
| GET | /api/inventory | 我的库存 |
| POST | /api/inventory | 添加饰品 |
| GET | /api/listings | 浏览交换请求 |
| POST | /api/listings | 发布交换请求 |
| GET | /api/offers | 我的交换提议 |
| POST | /api/offers | 发起提议 |
| POST | /api/offers/:id/accept | 接受提议 |
| POST | /api/offers/:id/reject | 拒绝提议 |
| POST | /api/offers/:id/confirm | 确认交换 |
| GET | /api/trades | 交换历史 |
| GET | /api/notifications | 通知列表 |
