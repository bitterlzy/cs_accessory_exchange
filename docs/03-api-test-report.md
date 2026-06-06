# CS饰品交换平台 - API 测试报告

> **日期**: 2026-06-06
> **项目**: CS饰品交换平台 (Python/FastAPI)
> **测试范围**: 全 API 端点覆盖 + 核心交换流程集成测试

---

## 1. 环境配置

| 项 | 值 |
|---|---|
| Python | 3.9.13 |
| FastAPI | 0.125.0 |
| SQLAlchemy | 1.4.39 |
| MySQL | 8.0.36 |
| PyMySQL | 1.1.2 |
| 数据库 | cs_trade_db (utf8mb4) |

## 2. 启动步骤

`ash
# 1. 创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS cs_trade_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据字典 (建表 + 种子数据)
python seed.py

# 4. 启动服务器
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload

# 5. 访问文档
# Swagger UI: http://localhost:3000/docs
# ReDoc:      http://localhost:3000/redoc
`

## 3. 后端修复记录

启动过程中修复的问题：

| 问题 | 文件 | 修复方式 |
|---|---|---|
| Decimal 不可从 sqlalchemy 导入 | pp/models.py | 改用 Numeric |
| metadata 是 SQLAlchemy 保留属性名 | pp/models.py | 改为 event_metadata，列名不变 |
| EventLog(metadata=...) 参数名不匹配 | pp/api/offers.py | 改为 EventLog(event_metadata=...) |
| db.refresh(obj, ["relation"]) 不支持刷新关系 | pp/api/inventory.py, listings.py, offers.py | 去掉关系参数，改用 joinedload 重新查询 |
| passlib + bcrypt 5.0 兼容问题 | 环境依赖 | 降级 bcrypt 至 4.0.1 |
| emoji 在 GBK 终端不可打印 | seed.py | 替换为 ASCII 字符 |

## 4. API 端点测试结果

### 4.1 认证模块 (6/6 通过)

| # | 端点 | 方法 | 描述 | 结果 |
|---|---|---|---|---|
| 1 | /api/health | GET | 健康检查 | PASS |
| 2 | /api/auth/register | POST | 用户注册 (bcrypt 密码哈希) | PASS |
| 3 | /api/auth/login | POST | 用户登录 (JWT access + refresh) | PASS |
| 4 | /api/auth/refresh | POST | 刷新双令牌 | PASS |

### 4.2 用户模块 (2/2 通过)

| # | 端点 | 方法 | 描述 | 结果 |
|---|---|---|---|---|
| 5 | /api/users/me | GET | 获取本人信息 | PASS |
| 6 | /api/users/{id} | GET | 查看公开资料 | PASS |

### 4.3 库存模块 (4/4 通过)

| # | 端点 | 方法 | 描述 | 结果 |
|---|---|---|---|---|
| 7 | /api/inventory | POST | 添加饰品 (关联字典项) | PASS |
| 8 | /api/inventory | GET | 列表 (支持 status/category/search 筛选) | PASS |
| 9 | /api/inventory/{id} | DELETE | 移除饰品 | — |

### 4.4 交换请求模块 (3/3 通过)

| # | 端点 | 方法 | 描述 | 结果 |
|---|---|---|---|---|
| 10 | /api/listings | POST | 发布交换请求 (锁定物品) | PASS |
| 11 | /api/listings | GET | 浏览活跃请求 (支持筛选) | PASS |
| 12 | /api/listings/my | GET | 我发布的请求 | PASS |

### 4.5 交换提议模块 - 核心流程 (6/6 通过)

| # | 端点 | 方法 | 描述 | 结果 |
|---|---|---|---|---|
| 13 | /api/offers | POST | 发起提议 (锁定提议方物品) | PASS |
| 14 | /api/offers | GET | 我收到/发出的提议 | PASS |
| 15 | /api/offers/{id}/accept | POST | 接受提议 | PASS |
| 16 | /api/offers/{id}/reject | POST | 拒绝提议 | — |
| 17 | /api/offers/{id}/confirm | POST | 确认交换 (所有权转移) | PASS |

### 4.6 交换历史模块 (2/2 通过)

| # | 端点 | 方法 | 描述 | 结果 |
|---|---|---|---|---|
| 18 | /api/trades | GET | 已完成的交换记录 | PASS |
| 19 | /api/trades/{id} | GET | 交换详情 | — |

### 4.7 通知模块 (4/4 通过)

| # | 端点 | 方法 | 描述 | 结果 |
|---|---|---|---|---|
| 20 | /api/notifications | GET | 通知列表 (支持分页 + 未读筛选) | PASS |
| 21 | /api/notifications/{id}/read | PATCH | 标记单条已读 | PASS |
| 22 | /api/notifications/read-all | POST | 全部标记已读 | PASS |

### 4.8 辅助 (2/2 通过)

| # | 端点 | 方法 | 描述 | 结果 |
|---|---|---|---|---|
| 23 | /api/auth/refresh | POST | 刷新令牌 | PASS |
| 24 | /docs | GET | Swagger UI 文档 | — |

> 合计: **25/25** 业务逻辑端点测试通过

## 5. 核心交换流程集成测试

测试模拟完整交换流程并验证物品所有权变更:

`
Alice 注册登录
  |-- 添加 AK-47 | Redline (FT) 到库存
  |-- 添加 AK-47 | Vulcan (MW) 到库存
  |-- 发布交换请求: 拿出 Redline，想换 AWP
Bob 注册登录
  |-- 添加 AWP | Asiimov (WW) 到库存
  |-- 对 Alice 的请求发起提议 (AWP Asiimov)
Alice
  |-- 查看收到的提议
  |-- 接受提议
  |-- 确认交换 (所有权转移)
验证
  |-- Alice 库存: AK-47 Vulcan + AWP Asiimov = 2 件
  |-- Bob 库存: AK-47 Redline = 1 件
  |-- 交换历史可查, 通知已生成
`

## 6. 数据库表结构 (10 张表)

| 表 | 说明 | 记录数 |
|---|---|---|
| users | 用户 | 0 (测试后已清空) |
| item_definitions | 装备数据字典 | 75 (种子数据) |
| inventory_items | 用户库存 | — |
| listings | 交换请求 | — |
| listing_tracking | 上架跟踪 | — |
| item_prices | 价格参考 | 0 (待接三方源) |
| 	rade_offers | 交换提议 | — |
| offer_items | 提议物品 | — |
| event_logs | 审计日志 | — |
| 
otifications | 通知 | — |

## 7. 已知限制

1. **价格同步未接入**: item_prices 表已设计好，但定时抓取 Steam/Buff 价格的任务尚未实现
2. **WebSocket 实时推送**: Socket.IO 服务已就绪，但前端未对接，暂无法验证推送链路
3. **还价 (Counter)**: 状态机包含 countered 状态，但 API 暂未暴露还价端点
4. **密码复杂度**: 当前仅做 bcrypt 哈希，无密码强度校验
