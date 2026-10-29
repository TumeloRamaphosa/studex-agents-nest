# Build Hour Plan — Blotato DM Automation for Studex Meat
**Created:** 2026-08-26 | **Status:** Action required from Tumelo

---

## What We Found

Blotato API is LIVE and confirmed working. Connected accounts:
- ✅ Facebook (personal — Tumelo Ramaphosa)
- ✅ Instagram (personal — laisa_aesthetics)
- ❌ Facebook Page `studexmeat` — NOT connected
- ❌ Instagram `studex.meat` — NOT connected

**Before DM automations work for Studex, the business accounts need to be connected.**

---

## Step 1: Connect Studex Business Accounts to Blotato (5 mins)

1. Go to: https://app.blotato.com
2. Login → Settings → Connected Accounts
3. Click "Connect Facebook Page"
   - Auth with Meta → select `Studex Meat` page (ID: 108934711902801)
   - Grant: Pages, Instagram, Messaging permissions
4. Click "Connect Instagram"
   - Select the `studex.meat` business account

Once connected, the account IDs will show up in the API. Note them down.

---

## Step 2: Create DM Keyword Automation (via Blotato API)

After accounts are connected, run this. Replace `FACEBOOK_ACCOUNT_ID` and `INSTAGRAM_ACCOUNT_ID` with the IDs from Step 1.

```bash
# Create DM keyword automation — triggers on "price", "order", "delivery"
curl -X POST "https://backend.blotato.com/v2/automations/dm" \
  -H "blotato-api-key: [REDACTED:28 chars - rotate this key]YN2ZvCeGsVWWwdaf8Og=" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "STUDEX_FACEBOOK_PAGE_ID",
    "platform": "facebook",
    "trigger_keyword": "price",
    "reply_message": "Hi! 👋 Studex Meat delivers SA'\''s finest Halaal Wagyu + biltong nationwide. Shop: https://studexmeat.com | WhatsApp order: +27XX XXX XXXX"
  }'
```

Repeat for keywords: `order`, `delivery`, `cost`, `how much`

---

## Step 3: n8n Lead Capture (deploy to Orgo VM this week)

Flow:
```
Website form → n8n webhook → Create ClickUp task → Send AgentMail confirmation → Discord #war-room ping
```

Deploy command on Orgo VM:
```bash
cd /root/robusca/robusca-brain/
git pull
# n8n is pre-installed on the VM
pm2 restart n8n
```

---

## Files Produced Tonight

- `/workspace/research/2026-08-26.md` — Full research brief
- `/workspace/research/build-hour-plan.md` — This file

---

## Immediate Next Actions for Tumelo

1. ⏱️ **Tonight (5 min):** Connect Studex Meat FB page + IG to Blotato dashboard
2. 📋 **This week:** Note the new account IDs → I can then configure DM automations via API
3. 🖥️ **This week:** n8n lead capture flow — requires部署 on Orgo VM
4. 📅 **Next Research Hour:** Track conversion rate from DM auto-replies
