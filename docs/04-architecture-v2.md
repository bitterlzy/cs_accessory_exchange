# CS饰品交易平台 v2.0 — 完整架构设计

> 版本: 2.0 | 日期: 2026-06-06
> 参考对象: 悠悠有品、BUFF、IGXE 等主流饰品交易平台安全模型

---

## 1. 系统架构总览

### 1.1 整体架构

`	ext
+------------------------------------------------------------------+
|                        前端 (React/Vue)                            |
+------------------------------------------------------------------+
                               |
+------------------------------------------------------------------+
|                     API 网关 / 负载均衡                             |
+------------------------------------------------------------------+
        |               |               |               |
+---------------+ +---------------+ +---------------+ +---------------+
| 用户/认证模块  | | 饰品/库存模块 | | 交易核心模块  | | Steam 集成模块|
+---------------+ +---------------+ +---------------+ +---------------+
        |               |               |               |
+------------------------------------------------------------------+
|                    业务逻辑层 (FastAPI)                             |
+------------------------------------------------------------------+
                               |
+------------------------------------------------------------------+
|   MySQL 8.0 (主库)    |    Redis (缓存/队列/限流)   |  任务队列     |
+------------------------------------------------------------------+
|                    Steam Web API / BUFF API                        |
+------------------------------------------------------------------+
`

### 1.2 核心模块划分

| 模块 | 职责 | 关键文件 |
|---|---|---|
| 用户认证模块 | 注册、登录、JWT、KYC 实名 | api/auth.py, api/kyc.py |
| 饰品数据模块 | BUFF数据同步、价格追踪 | api/items.py, services/buff_scraper.py |
| 库存管理模块 | 用户平台库存 CRUD | api/inventory.py |
| 交换请求模块 | Listing 发布、浏览 | api/listings.py |
| 交易核心模块 | Offer、状态机、结算 | api/offers.py, services/trade_engine.py |
| Steam 集成模块 | 机器人管理、交易报价、状态轮询 | api/steam.py, services/steam_bot.py |
| 风控安全模块 | 限流、反欺诈、审计 | middleware/security.py, services/risk_control.py |
| 通知模块 | WebSocket推送、站内信 | api/notifications.py, socketio_server.py |

---

## 2. 数据库设计 (v2.0 新增与变更)

### 2.1 新增表

#### user_verifications — 用户实名认证

`sql
CREATE TABLE user_verifications (
  id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id         BIGINT UNSIGNED NOT NULL UNIQUE,
  real_name       VARCHAR(100) NOT NULL COMMENT '真实姓名',
  id_number       VARCHAR(18) NOT NULL COMMENT '身份证号',
  id_number_hash  VARCHAR(64) NOT NULL COMMENT '身份证号哈希(用于查重)',
  alipay_account  VARCHAR(100) NOT NULL COMMENT '支付宝账号',
  verification_level ENUM('none','pending','verified','failed') DEFAULT 'none',
  verified_at     TIMESTAMP NULL,
  fail_reason     VARCHAR(500),
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (user_id) REFERENCES users(id),
  UNIQUE INDEX idx_id_hash (id_number_hash),
  INDEX idx_alipay (alipay_account),
  INDEX idx_level (verification_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
`

#### steam_accounts — 用户Steam账号绑定

`sql
CREATE TABLE steam_accounts (
  id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id         BIGINT UNSIGNED NOT NULL,
  steam_id        VARCHAR(64) NOT NULL COMMENT 'Steam64 ID',
  steam_name      VARCHAR(255) COMMENT 'Steam用户名',
  avatar_url      VARCHAR(500) COMMENT 'Steam头像',
  trade_url       VARCHAR(500) NOT NULL COMMENT 'Steam交易链接',
  trade_offer_url VARCHAR(500) COMMENT '交易报价API URL',
  is_primary      BOOLEAN DEFAULT TRUE,
  is_verified     BOOLEAN DEFAULT FALSE COMMENT 'Steam所有权验证',
  last_sync_at    TIMESTAMP NULL COMMENT '最近库存同步时间',
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (user_id) REFERENCES users(id),
  UNIQUE INDEX idx_steam_id (steam_id),
  INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
`

#### platform_bots — 平台机器人账号

`sql
CREATE TABLE platform_bots (
  id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  steam_id        VARCHAR(64) NOT NULL UNIQUE,
  bot_name        VARCHAR(100) COMMENT '机器人名称',
  steam_username  VARCHAR(255) COMMENT 'Steam登录名',
  shared_secret   VARCHAR(255) COMMENT 'Steam Shared Secret (2FA)',
  identity_secret VARCHAR(255) COMMENT 'Steam Identity Secret (确认交易)',
  api_key         VARCHAR(255) COMMENT 'Steam Web API Key',
  inventory_url   VARCHAR(500) COMMENT '库存JSON API URL',
  status          ENUM('online','offline','busy','error') DEFAULT 'offline',
  max_concurrent  INT DEFAULT 5 COMMENT '最大同时交易数',
  current_load    INT DEFAULT 0 COMMENT '当前交易数',
  trade_count     INT DEFAULT 0 COMMENT '累计交易数',
  is_active       BOOLEAN DEFAULT TRUE,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
`

#### steam_trade_operations — Steam交易操作记录

`sql
CREATE TABLE steam_trade_operations (
  id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  operation_type  ENUM('deposit','withdraw','trade') NOT NULL COMMENT '操作类型',
  trade_offer_id  VARCHAR(64) COMMENT 'Steam交易报价ID',
  bot_id          BIGINT UNSIGNED COMMENT '执行机器人',
  from_user_id    BIGINT UNSIGNED COMMENT '发出方',
  to_user_id      BIGINT UNSIGNED COMMENT '接收方',
  related_offer_id BIGINT UNSIGNED COMMENT '关联的平台Offer ID',
  status          ENUM('pending','sent','accepted','cancelled','expired','declined','failed') DEFAULT 'pending',
  items           JSON COMMENT '交易物品快照',
  sent_at         TIMESTAMP NULL,
  accepted_at     TIMESTAMP NULL,
  cancelled_at    TIMESTAMP NULL,
  escrow_days     INT DEFAULT 0 COMMENT 'Steam托管天数',
  retry_count     INT DEFAULT 0,
  error_message   TEXT,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (bot_id) REFERENCES platform_bots(id),
  FOREIGN KEY (from_user_id) REFERENCES users(id),
  FOREIGN KEY (to_user_id) REFERENCES users(id),
  INDEX idx_steam_offer (trade_offer_id),
  INDEX idx_status (status),
  INDEX idx_related (related_offer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
`

### 2.2 变更表

#### users 表 — 新增字段

| 字段 | 类型 | 说明 |
|---|---|---|
| verification_level | ENUM('none','pending','verified','failed') | 实名认证级别 |
| phone | VARCHAR(20) | 手机号 |
| phone_verified | BOOLEAN | 手机是否验证 |
| is_frozen | BOOLEAN | 是否冻结 |
| freeze_reason | VARCHAR(500) | 冻结原因 |

#### inventory_items 表 — 变更

| 字段 | 类型 | 说明 |
|---|---|---|
| storage_type | ENUM('user','platform') | 物品存储位置(用户/平台机器人) |
| bot_id | BIGINT UNSIGNED | 存储的机器人ID |
| asset_id | VARCHAR(64) | Steam资产ID |
| inspect_link | TEXT | 检视链接 |

---

## 3. 核心业务流程

### 3.1 用户注册与实名认证流程

`	ext
用户注册 (邮箱+密码)
    |
    v
手机号验证 (SMS)
    |
    v
实名认证 (支付宝实名接口)
    |-- 提交: 姓名 + 身份证号 + 支付宝账号
    |-- 支付宝转账0.01元验证(或API查询)
    |-- 验证通过: 实名标志 = verified
    |-- 验证失败: 记录失败原因
    |
    v
绑定 Steam 账号
    |-- 输入 Steam 交易链接
    |-- 系统解析 steam_id
    |-- 验证 Steam 所有权 (发送测试交易报价)
    |-- 绑定完成
    |
    v
可以开始使用交易功能
`

### 3.2 实名认证防一人多号机制

`	ext
身份证号查重:
  - id_number_hash 字段存储身份证 SHA256 哈希
  - 唯一索引禁止重复
  - 同一身份证只能绑定一个账号

支付宝账号查重:
  - alipay_account 字段
  - 唯一索引禁止重复支付宝账号

手机号查重:
  - phone 字段
  - 唯一索引禁止重复手机号

风控检测:
  - 同一IP注册多个账号 -> 触发风控
  - 同一设备指纹 -> 触发风控
  - 相似用户名模式 -> 触发风控
`

### 3.3 饰品上架与交易流程 (仿悠悠有品)

#### 3.3.1 存入 (Deposit)

`	ext
用户点击存入 -> 选择物品 -> 确认
    |
    v
系统分配平台机器人
    |
    v
机器人向用户发送交易报价
    |-- 包含: 用户选择的物品
    |-- 不包含: 机器人任何物品
    |
    v
用户接受报价 (在Steam客户端)
    |
    v
系统轮询交易状态 (每30秒)
    |-- 状态: pending -> 继续轮询
    |-- 状态: accepted -> 确认物品入库
    |-- 状态: cancelled/expired -> 标记失败
    |-- 超时(30分钟) -> 取消报价
    |
    v
物品入库成功
    |-- inventory_items 新增记录
    |-- status = available
    |-- storage_type = platform
    |-- bot_id = 机器人ID
    v
用户平台库存 +1
`

#### 3.3.2 交换 (Trade)

`	ext
Alice 发布交换请求
    |-- 拿出物品 A (已在平台库存中)
    |-- 期望换取: 某类/某件饰品
    |
Bob 浏览到请求 -> 发起交换提议
    |-- 拿出物品 B (已在平台库存中)
    |
Alice 确认接受
    |
    v
系统锁定 A 和 B (双锁定)
    |
    v
系统创建两条 Steam 交易报价:
    |-- 机器人 -> Alice: 空 (回退用)
    |-- 机器人 -> Bob: 空 (回退用)
    |-- 暂不发送, 先准备
    |
    v
系统执行原子交换:
    |-- 机器人 -> Alice: 物品 B
    |-- 机器人 -> Bob: 物品 A
    |
    v
Alice 和 Bob 分别在 Steam 接受报价
    |
    v
系统轮询两个交易状态
    |-- 都 accepted -> 平台库存更新
    |-- 任一 cancelled/expired -> 回滚
    |
    v
交换完成
`

#### 3.3.3 取回 (Withdraw)

`	ext
用户点击取回 -> 选择物品 -> 确认
    |
    v
风控检查:
    |-- 物品是否在活跃挂单中? -> 禁止
    |-- 用户是否异常? -> 二次验证
    |-- 大额取回(>5000)? -> 审核 + 24小时延迟
    |
    v
系统分配平台机器人
    |
    v
机器人向用户发送交易报价
    |-- 包含: 用户选择的物品
    |
    v
用户接受报价 (在Steam客户端)
    |
    v
系统轮询交易状态
    |-- accepted -> 确认出库
    |-- 超时未接受 -> 取消报价
    |
    v
取回完成
    |-- inventory_items status = removed

---

## 修订记录: P2P 直接交易模式修正

### 核心修正
原设计中的"平台机器人中转"模式已修正为 P2P 直接交易模式:

- 平台只做撮合 + 验证，不做中转
- 双方用户在 Steam 上直接互发交易报价
- 平台通过 Steam Web API 验证报价内容
- 平台轮询报价状态(接受/取消/过期)

### 安全机制保持不变
- KYC 实名认证 + 身份证/支付宝/手机号查重
- Steam 账号绑定与所有权验证
- 交易报价 ID 提交 + 平台验证
- 报价内容持续比对(防撤回/篡改)
- 风控中间件: 限流 + 设备指纹 + IP 追踪
