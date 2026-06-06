#!/bin/bash
BASE='http://172.25.0.113:3000'
PASS=0; FAIL=0
check() { local d=$1 e=$2 a=$3; if echo "$a" | grep -Eq "$e"; then echo "  [PASS] $d"; PASS=$((PASS+1)); else echo "  [FAIL] $d - expected: $e"; echo "    got: $a"; FAIL=$((FAIL+1)); fi }

echo '========== CS饰品交换平台 全面API测试 =========='
echo ''

echo '=== 1. Health ==='
R=$(curl -s $BASE/api/health)
check Health ok "$R"

echo '=== 2. Auth ==='
R=$(curl -s -X POST $BASE/api/auth/register -H 'Content-Type: application/json' -d '{"email":"alice@test.com","username":"alice_cs","password":"pass123","phone":"13800138001"}')
check 'Alice register' 'alice_cs' "$R"
ALICE_TOKEN=$(echo "$R" | python3 -c 'import sys,json; print(json.load(sys.stdin)["token"])' 2>/dev/null)
ALICE_ID=$(echo "$R" | python3 -c 'import sys,json; print(json.load(sys.stdin)["user"]["id"])' 2>/dev/null)
echo "  Alice ID: $ALICE_ID"

R=$(curl -s -X POST $BASE/api/auth/register -H 'Content-Type: application/json' -d '{"email":"bob@test.com","username":"bob_cs","password":"pass456","phone":"13900139001"}')
check 'Bob register' 'bob_cs' "$R"
BOB_TOKEN=$(echo "$R" | python3 -c 'import sys,json; print(json.load(sys.stdin)["token"])' 2>/dev/null)
BOB_ID=$(echo "$R" | python3 -c 'import sys,json; print(json.load(sys.stdin)["user"]["id"])' 2>/dev/null)
echo "  Bob ID: $BOB_ID"

R=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BASE/api/auth/register -H 'Content-Type: application/json' -d '{"email":"alice@test.com","username":"alice_cs","password":"pass123","phone":"13800138001"}'); check 'Dup 400' 400 "$R"
R=$(curl -s -X POST $BASE/api/auth/login -H 'Content-Type: application/json' -d '{"email":"alice@test.com","password":"pass123"}'); check 'Login' token "$R"
R=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BASE/api/auth/login -H 'Content-Type: application/json' -d '{"email":"alice@test.com","password":"wrong"}'); check 'Wrong pwd 401' 401 "$R"

echo '=== 3. Users ==='
R=$(curl -s $BASE/api/users/me -H "Authorization: Bearer $ALICE_TOKEN"); check 'Get me' alice_cs "$R"
R=$(curl -s $BASE/api/users/$BOB_ID); check 'Get user 2' bob_cs "$R"

echo '=== 4. KYC ==='
R=$(curl -s $BASE/api/kyc/status -H "Authorization: Bearer $ALICE_TOKEN"); check 'KYC status' none "$R"
R=$(curl -s -X POST $BASE/api/kyc/submit -H 'Content-Type: application/json' -H "Authorization: Bearer $ALICE_TOKEN" -d '{"real_name":"张三","id_number":"110101199001011234","alipay_account":"alice@alipay.com"}'); check 'KYC submit' pending "$R"
R=$(curl -s -X POST $BASE/api/kyc/submit -H 'Content-Type: application/json' -H "Authorization: Bearer $BOB_TOKEN" -d '{"real_name":"李四","id_number":"110101199001011234","alipay_account":"bob@alipay.com"}'); check 'ID dup invalid' '已被' "$R"
R=$(curl -s -X POST $BASE/api/kyc/submit -H 'Content-Type: application/json' -H "Authorization: Bearer $BOB_TOKEN" -d '{"real_name":"李四","id_number":"110101199001011235","alipay_account":"bob@alipay.com"}'); check 'Bob KYC' pending "$R"
R=$(curl -s -X POST $BASE/api/kyc/verify -H "Authorization: Bearer $ALICE_TOKEN"); check 'Alice verify' verified "$R"
R=$(curl -s -X POST $BASE/api/kyc/verify -H "Authorization: Bearer $BOB_TOKEN"); check 'Bob verify' verified "$R"

echo '=== 5. Inventory ==='
R=$(curl -s -X POST $BASE/api/inventory -H 'Content-Type: application/json' -H "Authorization: Bearer $ALICE_TOKEN" -d '{"definition_id":15,"quality":"FT","float_value":0.25}'); check 'Alice Redline' Redline "$R"
ALICE_ITEM1=$(echo "$R" | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])' 2>/dev/null)
R=$(curl -s -X POST $BASE/api/inventory -H 'Content-Type: application/json' -H "Authorization: Bearer $ALICE_TOKEN" -d '{"definition_id":16,"quality":"MW","float_value":0.12,"stat_trak":true}'); check 'Alice Vulcan' Vulcan "$R"
ALICE_ITEM2=$(echo "$R" | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])' 2>/dev/null)
R=$(curl -s -X POST $BASE/api/inventory -H 'Content-Type: application/json' -H "Authorization: Bearer $BOB_TOKEN" -d '{"definition_id":37,"quality":"WW","float_value":0.38}'); check 'Bob add AWP' 'AWP |' "$R"
BOB_ITEM1=$(echo "$R" | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])' 2>/dev/null)
R=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BASE/api/inventory -H 'Content-Type: application/json' -H "Authorization: Bearer $ALICE_TOKEN" -d '{"definition_id":9999,"quality":"FN"}'); check 'Invalid def 404' 404 "$R"

echo '=== 6. Listings ==='
R=$(curl -s -X POST $BASE/api/listings -H 'Content-Type: application/json' -H "Authorization: Bearer $ALICE_TOKEN" -d '{"offered_item_id":'$ALICE_ITEM1',"want_description":"想换 AWP","want_category":"weapon","want_quality":"any"}'); check 'Create listing' active "$R"
LISTING_ID=$(echo "$R" | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])' 2>/dev/null)
R=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BASE/api/listings -H 'Content-Type: application/json' -H "Authorization: Bearer $ALICE_TOKEN" -d '{"offered_item_id":'$ALICE_ITEM1',"want_category":"weapon"}'); check 'Relist locked 400' 400 "$R"
R=$(curl -s $BASE/api/listings); check 'Browse' listings "$R"
R=$(curl -s -X PATCH $BASE/api/listings/$LISTING_ID/close -H "Authorization: Bearer $ALICE_TOKEN"); check 'Close' 已关闭 "$R"
R=$(curl -s -X POST $BASE/api/listings -H 'Content-Type: application/json' -H "Authorization: Bearer $ALICE_TOKEN" -d '{"offered_item_id":'$ALICE_ITEM2',"want_category":"weapon","want_quality":"any"}')
LISTING_ID=$(echo "$R" | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])' 2>/dev/null)
R=$(curl -s -o /dev/null -w '%{http_code}' -X PATCH $BASE/api/listings/$LISTING_ID/close -H "Authorization: Bearer $BOB_TOKEN"); check 'Close others 403' 403 "$R"
# Close Alice listing properly
R=$(curl -s -X PATCH $BASE/api/listings/$LISTING_ID/close -H "Authorization: Bearer $ALICE_TOKEN")
# Recreate listing for offers
R=$(curl -s -X POST $BASE/api/listings -H 'Content-Type: application/json' -H "Authorization: Bearer $ALICE_TOKEN" -d '{"offered_item_id":'$ALICE_ITEM1',"want_category":"weapon","want_quality":"any"}')
LISTING_ID=$(echo "$R" | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])' 2>/dev/null)

echo '=== 7. Offers ==='
R=$(curl -s -X POST $BASE/api/offers -H 'Content-Type: application/json' -H "Authorization: Bearer $BOB_TOKEN" -d '{"listing_id":'$LISTING_ID',"proposer_item_ids":['$BOB_ITEM1'],"note":"想用 AWP 换你的 AK"}'); check 'Create offer' pending "$R"
OFFER_ID=$(echo "$R" | python3 -c 'import sys,json; print(json.load(sys.stdin)["id"])' 2>/dev/null)
R=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BASE/api/offers -H 'Content-Type: application/json' -H "Authorization: Bearer $ALICE_TOKEN" -d '{"listing_id":'$LISTING_ID',"proposer_item_ids":['$ALICE_ITEM2']}'); check 'Self offer 400' 400 "$R"
R=$(curl -s -X POST $BASE/api/offers/$OFFER_ID/accept -H "Authorization: Bearer $ALICE_TOKEN"); check 'Accept offer' '已接受|accepted' "$R"
R=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BASE/api/offers/$OFFER_ID/accept -H "Authorization: Bearer $BOB_TOKEN"); check 'Bob accept 403' 403 "$R"
R=$(curl -s -X POST $BASE/api/offers/$OFFER_ID/confirm -H "Authorization: Bearer $ALICE_TOKEN"); check 'Confirm trade' 已完成 "$R"

echo '--- Ownership ---'
echo "  Alice:" && curl -s $BASE/api/inventory -H "Authorization: Bearer $ALICE_TOKEN" | python3 -c 'import sys,json; [print("   -",i["definition"]["name"]) for i in json.load(sys.stdin)]' 2>/dev/null
echo "  Bob:" && curl -s $BASE/api/inventory -H "Authorization: Bearer $BOB_TOKEN" | python3 -c 'import sys,json; [print("   -",i["definition"]["name"]) for i in json.load(sys.stdin)]' 2>/dev/null

echo '=== 8. Trades ==='
R=$(curl -s $BASE/api/trades -H "Authorization: Bearer $ALICE_TOKEN"); check 'Trades' completed "$R"

echo '=== 9. Notifications ==='
R=$(curl -s $BASE/api/notifications -H "Authorization: Bearer $ALICE_TOKEN"); check 'Notifications' notifications "$R"
R=$(curl -s -X POST $BASE/api/notifications/read-all -H "Authorization: Bearer $ALICE_TOKEN"); check 'Mark all read' 已读 "$R"

echo '=== 10. Steam ==='
R=$(curl -s -X POST $BASE/api/steam/link -H 'Content-Type: application/json' -H "Authorization: Bearer $ALICE_TOKEN" -d '{"trade_url":"https://steamcommunity.com/tradeoffer/new/?partner=123456789","steam_name":"partner="}'); check 'Alice link Steam' trade_url "$R"
R=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BASE/api/steam/link -H 'Content-Type: application/json' -H "Authorization: Bearer $ALICE_TOKEN" -d '{"trade_url":"https://steamcommunity.com/tradeoffer/new/?partner=987654321"}'); check 'Alice relink 400' 400 "$R"
R=$(curl -s -o /dev/null -w '%{http_code}' -X POST $BASE/api/steam/link -H 'Content-Type: application/json' -H "Authorization: Bearer $BOB_TOKEN" -d '{"trade_url":"https://steamcommunity.com/tradeoffer/new/?partner=123456789"}'); check 'Same Steam 400' 400 "$R"
R=$(curl -s -X POST $BASE/api/steam/link -H 'Content-Type: application/json' -H "Authorization: Bearer $BOB_TOKEN" -d '{"trade_url":"https://steamcommunity.com/tradeoffer/new/?partner=987654321","steam_name":"BobSteam"}'); check 'Bob link Steam' '987654321' "$R"
R=$(curl -s $BASE/api/steam/accounts -H "Authorization: Bearer $ALICE_TOKEN"); check 'List Steam accounts' partner= "$R"

echo '=== 11. Security ==='
R=$(curl -s -o /dev/null -w '%{http_code}' $BASE/api/users/me); check 'No token 401' 401 "$R"
R=$(curl -s -o /dev/null -w '%{http_code}' $BASE/api/users/me -H 'Authorization: Bearer fake.jwt.token'); check 'Fake token 401' 401 "$R"

echo ''
echo "========== Results: PASS=$PASS FAIL=$FAIL =========="
