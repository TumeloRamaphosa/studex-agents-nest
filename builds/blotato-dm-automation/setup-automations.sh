#!/bin/bash
# Blotato DM Keyword Automations — Studex Build Hour 2026-08-26
# Creates auto-reply flows for Facebook and Instagram DMs

BLOTATO_KEY="[REDACTED:28 chars - rotate this key]********************"
BASE="https://backend.blotato.com/v2"
FB_ACCOUNT="38744"
IG_ACCOUNT="55765"
FB_PAGE_ID="108934711902801"

HEADERS="Content-Type: application/json"
AUTH="blotato-api-key: $BLOTATO_KEY"

echo "═══════════════════════════════════════════════"
echo "🐄 STUDEX BLOTATO DM AUTOMATION SETUP"
echo "   Build Hour — 2026-08-26"
echo "═══════════════════════════════════════════════"

# ── Helper: create automation ──────────────────────────────────────────
create_automation() {
  local name="$1"
  local platform="$2"
  local account_id="$3"
  local page_id="$4"
  local keywords_json="$5"
  local dm_message="$6"
  local btn1_title="$7"
  local btn1_url="$8"
  local btn2_title="$9"
  local btn2_url="${10}"

  echo "[Automation] Creating: $name"
  echo "  Platform: $platform | Account: $account_id"

  # Build JSON payload
  local payload="{"
  payload="$payload\"accountId\":\"$account_id\","
  payload="$payload\"platform\":\"$platform\","
  payload="$payload\"name\":\"$name\","
  payload="$payload\"trigger\":{\"type\":\"message-received\",\"keywords\":$keywords_json,\"isActive\":true},"
  payload="$payload\"dmMessage\":$(echo "$dm_message" | jq -Rs .),"
  payload="$payload\"isActive\":true"

  if [ "$platform" = "facebook" ] && [ -n "$page_id" ]; then
    payload="$payload,\"pageId\":\"$page_id\""
  fi

  if [ -n "$btn1_title" ]; then
    payload="$payload,\"buttons\":[{\"type\":\"url\",\"title\":\"$btn1_title\",\"url\":\"$btn1_url\"}"
    if [ -n "$btn2_title" ]; then
      payload="$payload,{\"type\":\"url\",\"title\":\"$btn2_title\",\"url\":\"$btn2_url\"}"
    fi
    payload="$payload]"
  fi

  payload="$payload}"

  echo "  Trigger keywords: $keywords_json"

  local response
  response=$(curl -s -X POST "$BASE/automations" \
    -H "Content-Type: application/json" \
    -H "blotato-api-key: $BLOTATO_KEY" \
    -H "Accept: application/json" \
    -d "$payload")

  local id=$(echo "$response" | jq -r '.id // .automation?.id // .error // "unknown"')
  if echo "$response" | jq -e '.id // .automation?.id' > /dev/null 2>&1; then
    echo "  ✅ Created! ID: $id"
  else
    echo "  ❌ Failed: $(echo "$response" | jq '.')"
  fi
  echo ""
}

# ── Price Reply ────────────────────────────────────────────────────────
PRICE_REPLY="🐄 *Hi from Studex Meat!* 🐄

Thanks for your interest! We deliver premium South African beef nationwide.

📦 *Our Bestsellers:*
• Wagyu Ribeye — R780/pack (450g)
• Karoo Lamb Chops — R420/pack
• Dry-aged Beef — from R380/pack
• Premium Biltong — from R280/300g

📍 *Delivery:* Johannesburg, Cape Town, Durban + nationwide
🚚 *Free delivery* on orders over R800

👉 *Order via WhatsApp:* https://wa.me/27690183427
🛒 *Shop online:* studexmeat.com

We'd love to hear from you! 🥩"

# ── Order Reply ────────────────────────────────────────────────────────
ORDER_REPLY="🥩 *Studex Meat — Ready to Serve!* 🥩

Absolutely, ordering is easy!

📱 *WhatsApp (fastest):* https://wa.me/27690183427
🛒 *Online shop:* studexmeat.com

We accept:
✅ EFT / SnapScan
✅ Visa / Mastercard
✅ Business invoicing (B2B)

🚚 Delivery nationwide — JHB, CPT, DBN + more
Free delivery on orders over R800

What would you like? We have Wagyu, Karoo Lamb, Biltong and more! 🐄"

# ── Delivery Reply ─────────────────────────────────────────────────────
DELIVERY_REPLY="📦 *Studex Delivery Info* 📦

We deliver premium meat nationwide!

🌍 *Areas:* Johannesburg, Cape Town, Durban, Port Elizabeth, Bloemfontein + all major SA centres

⏱️ *Turnaround:* 2–5 business days (fresh) / 3–7 days (frozen)

💰 *Delivery:*
• Orders over R800 = FREE delivery
• Orders under R800 = R95 flat rate

🏃 *Urgent?* WhatsApp us: https://wa.me/27690183427

🛒 Shop: studexmeat.com 🥩"

# Keywords as JSON arrays
PRICE_KW='["price","cost","how much","rates","quotation","quote","r多少","价钱"]'
ORDER_KW='["order","buy","purchase","get one","want to","need some","stock","ordering","how to order"]'
DELIVERY_KW='["deliver","delivery","shipping","ship","courier","collect","pickup","jhb","cpt","durban","port elizabeth"," Bloem"]'

# ── FACEBOOK AUTOMATIONS ────────────────────────────────────────────────
echo "[1] Creating Facebook automations..."
echo ""

create_automation \
  "Studex FB — Price Enquiry Auto-Reply" \
  "facebook" \
  "$FB_ACCOUNT" \
  "$FB_PAGE_ID" \
  "$PRICE_KW" \
  "$PRICE_REPLY" \
  "Shop Online" "https://studexmeat.com" \
  "WhatsApp Us" "https://wa.me/27690183427"

create_automation \
  "Studex FB — Order Request Auto-Reply" \
  "facebook" \
  "$FB_ACCOUNT" \
  "$FB_PAGE_ID" \
  "$ORDER_KW" \
  "$ORDER_REPLY" \
  "Shop Online" "https://studexmeat.com" \
  "WhatsApp Us" "https://wa.me/27690183427"

create_automation \
  "Studex FB — Delivery Info Auto-Reply" \
  "facebook" \
  "$FB_ACCOUNT" \
  "$FB_PAGE_ID" \
  "$DELIVERY_KW" \
  "$DELIVERY_REPLY" \
  "Shop Online" "https://studexmeat.com" \
  "WhatsApp Us" "https://wa.me/27690183427"

# ── INSTAGRAM AUTOMATIONS ──────────────────────────────────────────────
echo "[2] Creating Instagram automations..."
echo ""

create_automation \
  "Studex IG — Price Enquiry Auto-Reply" \
  "instagram" \
  "$IG_ACCOUNT" \
  "" \
  "$PRICE_KW" \
  "$PRICE_REPLY" \
  "Shop Online" "https://studexmeat.com" \
  "WhatsApp Us" "https://wa.me/27690183427"

create_automation \
  "Studex IG — Order Request Auto-Reply" \
  "instagram" \
  "$IG_ACCOUNT" \
  "" \
  "$ORDER_KW" \
  "$ORDER_REPLY" \
  "Shop Online" "https://studexmeat.com" \
  "WhatsApp Us" "https://wa.me/27690183427"

create_automation \
  "Studex IG — Delivery Info Auto-Reply" \
  "instagram" \
  "$IG_ACCOUNT" \
  "" \
  "$DELIVERY_KW" \
  "$DELIVERY_REPLY" \
  "Shop Online" "https://studexmeat.com" \
  "WhatsApp Us" "https://wa.me/27690183427"

echo "═══════════════════════════════════════════════"
echo "✅ All 6 automations deployed!"
echo ""
echo "📘 Facebook: 3 automations (Price/Order/Delivery)"
echo "📸 Instagram: 3 automations (Price/Order/Delivery)"
echo ""
echo "🌐 Manage at: https://app.blotato.com"
echo "═══════════════════════════════════════════════"
