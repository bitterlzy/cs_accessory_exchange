# CS饰品交易平台 — API 测试用例（Postman 版）

> **版本**: v3.0 | **日期**: 2026-06-06
> **覆盖范围**: 30 个 API 端点 | **测试工具**: Postman
> **数据库**: `cs_trade_db` | **服务器**: `http://localhost:3000`

## 目录
1. Postman 环境配置
2. 测试用数据总表
3. 认证模块（Auth）
4. 用户模块（Users）
5. 实名认证模块（KYC）
6. 库存模块（Inventory）
7. 交换请求模块（Listings）
8. 交换提议模块（Offers）
9. 交换历史模块（Trades）
10. 通知模块（Notifications）
11. Steam 交易模块
12. 集成测试：完整交换流程
13. 安全边界测试

---

## 1. Postman 环境配置

### 1.1 新建 Environment

在 Postman → Environments 中创建一个名为 **CS Trade - Local** 的环境，添加以下变量：

| 变量名 | 初始值 | 说明 |
|---|---|---|
| `base_url` | `http://localhost:3000` | 服务器地址 |
| `token_alice` | （空） | Alice 的 JWT Token（运行时填充） |
| `token_bob` | （空） | Bob 的 JWT Token（运行时填充） |
| `refresh_token_alice` | （空） | Alice 的刷新令牌 |
| `refresh_token_bob` | （空） | Bob 的刷新令牌 |
| `item_id_alice` | （空） | Alice 的库存物品 ID |
| `item_id_alice2` | （空） | Alice 的第二件物品 ID |
| `item_id_bob` | （空） | Bob 的库存物品 ID |
| `listing_id` | （空） | Alice 发布的交换请求 ID |
| `offer_id` | （空） | 交换提议 ID |
| `notif_id` | （空） | 通知 ID |
| `user_id_alice` | （空） | Alice 的用户 ID |
| `user_id_bob` | （空） | Bob 的用户 ID |
| `steam_trade_url` | `https://steamcommunity.com/tradeoffer/new/?partner=123456789` | 模拟 Steam 链接 |

### 1.2 Postman 使用指引

- **认证方式**: 在每个需要认证的请求中，打开 Authorization 标签页 → Type 选 **Bearer Token** → Token 填入 `{{token_alice}}` 或 `{{token_bob}}`
- **运行顺序**: 按 TC 编号从小到大依次执行，某些步骤会依赖前面的变量
- **变量传递**: 每次请求返回后，手动将关键字段（`id`、`token` 等）复制到环境变量中
- **数据库重置**: 如果需要重新测试，删除 MySQL 的 `cs_trade_db` 再重建

---

## 2. 测试用数据总表

| 角色 | 邮箱 | 用户名 | 密码 | 手机号 |
|---|---|---|---|---|
| **Alice**（卖方） | `alice@test.com` | `alice_cs` | `pass123` | `13800138001` |
| **Bob**（买方） | `bob@test.com` | `bob_cs` | `pass456` | `13900139001` |

### 饰品定义（来自 seed.py 自动生成）

| 定义 ID | 名称 | 品类 | 稀有度 |
|---|---|---|---|
| 15 | AK-47 | Redline | weapon | classified |
| 16 | AK-47 | Vulcan | weapon | covert |
| 37 | AWP | Asiimov | weapon | covert |

---

## 3. 认证模块（Auth）

### TC-AUTH-001: Alice 注册

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/auth/register` |
| **Headers** | `Content-Type: application/json` |
| **Body (raw JSON)** | `{"email":"alice@test.com","username":"alice_cs","password":"pass123","phone":"13800138001"}` |
| **期望状态码** | `201 Created` |

**期望响应体**（关键字段）：
```json
{
  "user": { "id": 1, "email": "alice@test.com", "username": "alice_cs" },
  "token": "eyJhbGci...",
  "refresh_token": "eyJhbGci..."
}
```

**后置操作**：
- 复制 `token` → 设为环境变量 `token_alice`
- 复制 `refresh_token` → 设为环境变量 `refresh_token_alice`
- 复制 `user.id` → 设为环境变量 `user_id_alice`

---

### TC-AUTH-002: Bob 注册

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/auth/register` |
| **Body** | `{"email":"bob@test.com","username":"bob_cs","password":"pass456","phone":"13900139001"}` |
| **期望状态码** | `201 Created` |

**后置操作**：存 `token` → `token_bob`，`refresh_token` → `refresh_token_bob`，`user.id` → `user_id_bob`

---

### TC-AUTH-003: 重复注册（查重验证）

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/auth/register` |
| **Body** | `{"email":"alice@test.com","username":"alice_cs","password":"pass123","phone":"13800138001"}` |
| **期望状态码** | `400 Bad Request` |

**期望响应**：`{"error":"邮箱或用户名已被注册"}`

---

### TC-AUTH-004: Alice 正常登录

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/auth/login` |
| **Body** | `{"email":"alice@test.com","password":"pass123"}` |
| **期望状态码** | `200 OK` |

---

### TC-AUTH-005: 密码错误登录

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/auth/login` |
| **Body** | `{"email":"alice@test.com","password":"wrongpassword"}` |
| **期望状态码** | `401 Unauthorized` |
| **期望响应** | `{"error":"邮箱或密码错误"}` |

---

### TC-AUTH-006: 刷新 JWT 令牌

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/auth/refresh` |
| **Body** | `{"refresh_token":"{{refresh_token_alice}}"}` |
| **期望状态码** | `200 OK` |

**后置操作**：更新环境变量

---

### TC-AUTH-007: 无效 refresh_token

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/auth/refresh` |
| **Body** | `{"refresh_token":"invalid_token_here"}` |
| **期望状态码** | `401 Unauthorized` |
| **期望响应** | `{"error":"刷新令牌已过期或无效"}` |

---

## 4. 用户模块（Users）

### TC-USR-001: 获取当前用户信息

| 字段 | 值 |
|---|---|
| **方法** | `GET` |
| **URL** | `{{base_url}}/api/users/me` |
| **Auth** | Bearer Token: `{{token_alice}}` |
| **期望状态码** | `200 OK` |

**期望响应**：`{"id":1,"email":"alice@test.com","username":"alice_cs","reputation_score":0,"trade_count":0}`

---

### TC-USR-002: 查看他人公开资料

| 字段 | 值 |
|---|---|
| **方法** | `GET` |
| **URL** | `{{base_url}}/api/users/2` |
| **Auth** | 无 |
| **期望状态码** | `200 OK` |

**注意**：不应包含 `password_hash` 等敏感字段

---

## 5. 实名认证模块（KYC）

### TC-KYC-001: 查看实名认证状态

| 字段 | 值 |
|---|---|
| **方法** | `GET` |
| **URL** | `{{base_url}}/api/kyc/status` |
| **Auth** | Bearer Token: `{{token_alice}}` |
| **期望状态码** | `200 OK` |

**期望响应**：`{"user_id":1,"verification_level":"none","is_verified":false}`

---

### TC-KYC-002: Alice 提交实名认证

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/kyc/submit` |
| **Body** | `{"real_name":"张三","id_number":"110101199001011234","alipay_account":"alice@alipay.com"}` |
| **期望状态码** | `200 OK` |

---

### TC-KYC-003: 身份证号查重

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/kyc/submit` |
| **Auth** | Bearer Token: `{{token_bob}}` |
| **Body** | `{"real_name":"李四","id_number":"110101199001011234","alipay_account":"bob@alipay.com"}` |
| **期望状态码** | `400 Bad Request` |
| **期望响应** | `{"error":"该身份证号已被其他账号绑定..."}` |

---

### TC-KYC-004: Bob 用不同身份证号提交

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/kyc/submit` |
| **Auth** | Bearer Token: `{{token_bob}}` |
| **Body** | `{"real_name":"李四","id_number":"110101199001011235","alipay_account":"bob@alipay.com"}` |
| **期望状态码** | `200 OK` |

---

### TC-KYC-005: Alice 通过实名认证

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/kyc/verify` |
| **Auth** | Bearer Token: `{{token_alice}}` |
| **期望状态码** | `200 OK` |

**期望响应**：`{"message":"实名认证成功","verified":true}`

---

### TC-KYC-006: Bob 通过实名认证

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/kyc/verify` |
| **Auth** | Bearer Token: `{{token_bob}}` |
| **期望状态码** | `200 OK` |

---

## 6. 库存模块（Inventory）

### TC-INV-001: Alice 添加 AK-47 | Redline (FT)

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/inventory` |
| **Auth** | Bearer Token: `{{token_alice}}` |
| **Body** | `{"definition_id":15,"quality":"FT","float_value":0.25}` |
| **期望状态码** | `201 Created` |

**后置操作**：存 `id` → `item_id_alice`

---

### TC-INV-002: Alice 添加 AK-47 | Vulcan (MW)

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/inventory` |
| **Auth** | Bearer Token: `{{token_alice}}` |
| **Body** | `{"definition_id":16,"quality":"MW","float_value":0.12,"stat_trak":true}` |
| **期望状态码** | `201 Created` |

**后置操作**：存 `id` → `item_id_alice2`

---

### TC-INV-003: Bob 添加 AWP | Asiimov (WW)

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/inventory` |
| **Auth** | Bearer Token: `{{token_bob}}` |
| **Body** | `{"definition_id":37,"quality":"WW","float_value":0.38}` |
| **期望状态码** | `201 Created` |

**后置操作**：存 `id` → `item_id_bob`

---

### TC-INV-004: 查看库存 / 筛选 / 搜索

| # | 测试 | URL | 期望 |
|---|---|---|---|
| 4a | Alice 查看全部 | `GET /api/inventory`（token=alice） | 返回 2 件物品 |
| 4b | 按品类筛选 | `GET /api/inventory?category=weapon` | 只返回 weapon |
| 4c | 按关键词搜索 | `GET /api/inventory?search=Redline` | 只匹配的物品 |
| 4d | 不存在的 definition | `POST /api/inventory` body: `{"definition_id":9999,"quality":"FN"}` | 404 |

---

### TC-INV-005: 删除库存物品

| # | 测试 | URL | 期望 |
|---|---|---|---|
| 5a | 删除自己的物品 | `DELETE /api/inventory/{{item_id_alice}}`（token=alice） | 200 |
| 5b | 删除别人的物品 | `DELETE /api/inventory/{{item_id_bob}}`（token=alice） | 403 |

---

## 7. 交换请求模块（Listings）

### TC-LST-001: 发布交换请求

**前置**：确保 `item_id_alice` 有效（若被删除，重新 TC-INV-001）

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/listings` |
| **Auth** | Bearer Token: `{{token_alice}}` |
| **Body** | `{"offered_item_id":{{item_id_alice}},"want_description":"想换 AWP 饰品","want_category":"weapon","want_quality":"any"}` |
| **期望状态码** | `201 Created` |

**后置操作**：存 `id` → `listing_id`

---

### TC-LST-002: 上架已 locked 物品（应拒绝）

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/listings` |
| **Auth** | Bearer Token: `{{token_alice}}` |
| **Body** | `{"offered_item_id":{{item_id_alice}},"want_category":"weapon"}` |
| **期望状态码** | `400 Bad Request` |
| **期望响应** | `{"error":"饰品当前状态不允许上架"}` |

---

### TC-LST-003: 浏览活跃请求

| # | 测试 | URL | 期望 |
|---|---|---|---|
| 3a | 全部 | `GET /api/listings`（无 auth） | 200，含 listings+total+page+limit |
| 3b | 按品类 | `GET /api/listings?category=weapon` | 筛选后至少 1 条 |
| 3c | 按品质（无匹配） | `GET /api/listings?quality=FN` | total: 0 |

---

### TC-LST-004: 查看自己的请求

| 字段 | 值 |
|---|---|
| **方法** | `GET` |
| **URL** | `{{base_url}}/api/listings/my` |
| **Auth** | Bearer Token: `{{token_alice}}` |
| **期望状态码** | `200 OK` |

---

### TC-LST-005: 关闭请求 / 权限校验

| # | 测试 | URL | 期望 |
|---|---|---|---|
| 5a | 自己的关闭 | `PATCH /api/listings/{{listing_id}}/close`（token=alice） | 200，物品解锁 |
| 5b | 别人的关闭 | `PATCH /api/listings/{{listing_id}}/close`（token=bob） | 403 |

---

## 8. 交换提议模块（Offers）

### TC-OFF-001: Bob 发起提议

**前置**：Alice 有活跃 listing（重新 TC-LST-001），Bob 有 AWP Asiimov

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/offers` |
| **Auth** | Bearer Token: `{{token_bob}}` |
| **Body** | `{"listing_id":{{listing_id}},"proposer_item_ids":[{{item_id_bob}}],"note":"想用 AWP 换你的 AK"}` |
| **期望状态码** | `201 Created` |

**后置操作**：存 `id` → `offer_id`

---

### TC-OFF-002: 对自己的 listing 发起提议（应拒绝）

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/offers` |
| **Auth** | Bearer Token: `{{token_alice}}` |
| **Body** | `{"listing_id":{{listing_id}},"proposer_item_ids":[{{item_id_alice2}}]}` |
| **期望状态码** | `400 Bad Request` |
| **期望响应** | `{"error":"不能对自己的请求发起交换"}` |

---

### TC-OFF-003: Alice 接受提议

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/offers/{{offer_id}}/accept` |
| **Auth** | Bearer Token: `{{token_alice}}` |
| **期望状态码** | `200 OK` |
| **期望响应** | `{"message":"提议已接受，请双方确认交换"}` |

---

### TC-OFF-004: 非接收方不能接受

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/offers/{{offer_id}}/accept` |
| **Auth** | Bearer Token: `{{token_bob}}` |
| **期望状态码** | `403 Forbidden` |

---

### TC-OFF-005: 确认交换（核心功能）

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/offers/{{offer_id}}/confirm` |
| **Auth** | Bearer Token: `{{token_alice}}` |
| **期望状态码** | `200 OK` |

**验证所有权转移**：
- Alice 库存：有 AWP Asiimov（Bob 的），无 Redline
- Bob 库存：有 AK Redline（Alice 的），无 Asiimov
- 双方 trade_count 各 +1

---

### TC-OFF-005b: 拒绝提议

**前置**：重新创建 listing + 提议（获得新 offer_id）

| 字段 | 值 |
|---|---|
| **方法** | `POST` |
| **URL** | `{{base_url}}/api/offers/{{offer_id}}/reject` |
| **Auth** | Bearer Token: `{{token_alice}}` |
| **期望状态码** | `200 OK` |

**验证**：提议方物品解锁回 `available`

---

## 9. 交换历史（Trades）

### TC-TRD-001: 查看历史

| # | 测试 | URL | 期望 |
|---|---|---|---|
| 1a | Alice 的历史 | `GET /api/trades`（token=alice） | 200，仅 completed |
| 1b | 查看详情 | `GET /api/trades/{{offer_id}}`（token=alice） | 完整信息 |

---

## 10. 通知模块（Notifications）

### TC-NOT-001: 查看通知

| 字段 | 值 |
|---|---|
| **方法** | `GET` |
| **URL** | `{{base_url}}/api/notifications` |
| **Auth** | Bearer Token: `{{token_alice}}` |
| **期望状态码** | `200 OK` |

**期望响应**：含 total 和 unread_count

---

### TC-NOT-002: 通知操作

| # | 测试 | URL | 期望 |
|---|---|---|---|
| 2a | 只看未读 | `GET /api/notifications?unread_only=true` | 仅未读 |
| 2b | 标记单条已读 | `PATCH /api/notifications/{{notif_id}}/read` | 200 |
| 2c | 全部标记已读 | `POST /api/notifications/read-all` | 200 |

---

## 11. Steam 模块

### TC-STM-001 ~ 004

| # | 测试 | URL（token=当前用户） | Body | 期望 |
|---|---|---|---|---|
| 1 | Alice 绑定 | `POST /api/steam/link`（token=alice） | `{"trade_url":"{{steam_trade_url}}","steam_name":"AliceSteam"}` | 200 |
| 2 | 重复绑定 | `POST /api/steam/link`（token=alice） | 不同的 trade_url | 400 |
| 3a | 同 Steam 被他人绑 | `POST /api/steam/link`（token=bob） | 同 trade_url | 400 |
| 3b | Bob 绑定不同 Steam | `POST /api/steam/link`（token=bob） | `{"trade_url":"https://steamcommunity.com/tradeoffer/new/?partner=987654321","steam_name":"BobSteam"}` | 200 |
| 4 | 查看绑定 | `GET /api/steam/accounts`（token=alice） | — | 200 返回列表 |

---

## 12. 集成测试：完整交换流程

| 序号 | 步骤 | API | 操作 | 期望 |
|---|---|---|---|---|
| 1 | Alice 注册 | POST /api/auth/register | `{"email":"alice@test.com","username":"alice_cs","password":"pass123","phone":"13800138001"}` | 201 |
| 2 | Bob 注册 | POST /api/auth/register | `{"email":"bob@test.com","username":"bob_cs","password":"pass456","phone":"13900139001"}` | 201 |
| 3 | Alice 加 Redline | POST /api/inventory | `{"definition_id":15,"quality":"FT"}` | 201 |
| 4 | Alice 加 Vulcan | POST /api/inventory | `{"definition_id":16,"quality":"MW"}` | 201 |
| 5 | Bob 加 Asiimov | POST /api/inventory | `{"definition_id":37,"quality":"WW"}` | 201 |
| 6 | Alice 发布请求 | POST /api/listings | `{"offered_item_id":item_id_alice1,"want_category":"weapon"}` | 201 |
| 7 | Bob 发起提议 | POST /api/offers | `{"listing_id":listing_id,"proposer_item_ids":[item_id_bob]}` | 201 |
| 8 | Alice 看通知 | GET /api/notifications | — | 含 new_offer |
| 9 | Alice 接受提议 | POST /api/offers/{id}/accept | — | 200 |
| 10 | Alice 确认交换 | POST /api/offers/{id}/confirm | — | 200 |
| 11 | 验 Alice 库存 | GET /api/inventory | — | 有 AWP Asiimov |
| 12 | 验 Bob 库存 | GET /api/inventory | — | 有 AK Redline |
| 13 | 交换历史 | GET /api/trades | — | 含记录 |
| 14 | 交换详情 | GET /api/trades/{id} | — | 完整信息 |

---

## 13. 安全边界测试

| # | 测试 | 操作 | 期望 |
|---|---|---|---|
| 1 | 无 token 访问受保护接口 | `GET /api/users/me`（无 auth） | 403 |
| 2 | 伪造 token | `GET /api/users/me`（Bearer: fake.jwt.token） | 401 |
| 3 | 物品互斥锁 | 已上架物品再次上架 | 400 |
| 4 | 所有权校验 | 操作他人物品 | 403 |
| 5 | 健康检查 | `GET /api/health`（无 auth） | 200 {"status":"ok"} |

---

## 附录 A：快速启动

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS cs_trade_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

## 附录 B：数据库重置

```bash
mysql -u root -p -e "DROP DATABASE IF EXISTS cs_trade_db; CREATE DATABASE cs_trade_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
python seed.py
```

## 附录 C：cURL 快速测试

```bash
# Alice 注册
curl -s -X POST http://localhost:3000/api/auth/register -H "Content-Type: application/json" -d '{"email":"alice@test.com","username":"alice_cs","password":"pass123","phone":"13800138001"}'

# 登录拿到 token
ALICE_TOKEN=$(curl -s -X POST http://localhost:3000/api/auth/login -H "Content-Type: application/json" -d '{"email":"alice@test.com","password":"pass123"}' | python -c "import sys,json;print(json.load(sys.stdin)['token'])")

# 添加物品
curl -s -X POST http://localhost:3000/api/inventory -H "Content-Type: application/json" -H "Authorization: Bearer $ALICE_TOKEN" -d '{"definition_id":15,"quality":"FT"}'

# 浏览请求
curl -s http://localhost:3000/api/listings | python -m json.tool
```
