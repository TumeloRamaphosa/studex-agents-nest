# StudEx Meat — Integration Reference for Charlie OS

> How every external service connects. Read this before wiring any module that touches mail, WhatsApp, ads, social, or store.

Maintained by: Robusca Romanov
Last updated: 2026-06-16

---

## 1. AgentMail (outbound campaigns + replies)

**Status:** Domain `send.studexmeat.com` registered with AgentMail. NOT_STARTED until DNS verified.

**API base:** `https://api.agentmail.to/v0`

**Auth:** `Authorization: Bearer am_us_8dc671f56280db47a8b602e682cbe27dde95e63979be6660b1dd81b7bfaa3188`
> ⚠ Rotate this — it has appeared in chat history. Generate fresh from agentmail.to dashboard.

**Sending identity (target):** `agent@send.studexmeat.com`, display name `Robusca · StudEx Meat`

**Reply routing:** AgentMail receives → forwards to `agent@studexmeat.com` (Google Workspace) so Tumelo reads everything in one Gmail inbox.

**DNS records required on `send.studexmeat.com`:**
| Type | Name | Value | Priority |
|---|---|---|---|
| TXT | `agentmail._domainkey.send` | DKIM key (see AGENT_PERPLEXITY_ROBUSCA.md) | — |
| MX  | `send` | `inbound-smtp.us-east-1.amazonaws.com` | 10 |
| MX  | `mail.send` | `feedback-smtp.us-east-1.amazonses.com` | 10 |
| TXT | `mail.send` | `v=spf1 include:amazonses.com -all` | — |
| TXT | `_dmarc.send` | `v=DMARC1; p=reject; rua=mailto:dmarc@send.studexmeat.com` | — |

**Send curl pattern (once verified):**
```bash
curl -X POST https://api.agentmail.to/v0/inboxes/{inbox_id}/messages \
  -H "Authorization: Bearer $AGENTMAIL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["customer@example.com"],
    "from": "agent@send.studexmeat.com",
    "subject": "...",
    "html": "...",
    "text": "...",
    "labels": ["flash_auction", "vip_segment"]
  }'
```

---

## 2. Google Workspace (`agent@studexmeat.com`)

**Status:** Mailbox created 2026-06-15. Admin roles need TRIMMING (currently over-privileged).

**Purpose:** Daily reports to Tumelo, AgentMail reply receiver, audit trail.

**Action required (Tumelo):**
1. Reset password to a 16-char random (current `Openclaw1$` is compromised — appeared in screenshot)
2. **Unassign all admin roles**: User Management Admin, Help Desk Admin, Services Admin, Storage Admin, Mobile Admin. Keep only Groups Editor IF the agent will post to Groups.
3. The mailbox is a regular user. Domain-wide delegation for API access is done via GCP service account, not user roles.

**Sending limits:** 2,000 recipients/day on Workspace Business Standard.

---

## 3. WhatsApp — Meta Cloud API (PRIMARY) vs Twilio (BACKUP)

### What's actually wired right now

| Service | Status | Where keys live |
|---|---|---|
| **Meta Cloud API** | Skill loaded (`studex-meta-whatsapp`) but WABA ID + Phone Number ID + Access Token NOT yet captured in Robusca memory | Tumelo's Meta Business Manager |
| **Twilio** | Tumelo says he gave keys; no Twilio credentials currently in Robusca memory or sandbox env | Tumelo's Twilio console |

**Recommendation: USE META CLOUD API as primary. Keep Twilio in reserve.**

Why Meta Cloud over Twilio:
- Lower cost (free first 1,000 service convos/month vs Twilio's $0.005/msg + Meta fees on top)
- Direct access to template approvals, no intermediary
- Native Shopify integration via Meta Catalog → richer cart abandonment messages
- Built for the volume StudEx will hit (Youth Day + auction broadcasts)

When to use Twilio instead:
- If Meta Cloud verification gets blocked (rare but happens)
- If we need programmable voice/SMS alongside WhatsApp (auction outbid alerts via SMS fallback)

### Meta Cloud API setup (canonical)

**Prerequisites (Tumelo must do once):**
1. Meta Business Manager account claimed for StudEx Meat (likely done — connected to Facebook Pages connector)
2. WhatsApp Business Account (WABA) created inside Business Manager
3. Phone number added + verified for WhatsApp (the +27 number that customers see)
4. Business verification submitted (1-2 day Meta review)
5. System User created → permanent access token issued

**Three identifiers Robusca needs:**
- `WABA_ID` — WhatsApp Business Account ID
- `PHONE_NUMBER_ID` — the sending phone's Meta-internal ID (not the +27 number)
- `META_ACCESS_TOKEN` — permanent system user token (starts with `EAA...`)

**Connect to Facebook Pages:**
Inside Business Manager → Settings → Accounts → Pages → confirm StudEx Meat FB Page is owned by the same business. This auto-links WhatsApp to the FB Page so cross-platform analytics work and Shop tabs surface WhatsApp Click-to-Chat buttons.

**Connect to Shopify:**
1. Shopify Admin → Sales channels → Add channel → **Facebook & Instagram by Meta**
2. Select StudEx Meat Business Manager
3. Connect Catalog → Shopify auto-syncs products to Meta Catalog
4. In Meta Commerce Manager → Catalog → WhatsApp → enable WhatsApp commerce
5. Customers can now browse products inside WhatsApp threads

**Send curl pattern:**
```bash
curl -X POST https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages \
  -H "Authorization: Bearer ${META_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "{TUMELO_WHATSAPP_E164}",
    "type": "template",
    "template": {
      "name": "auction_outbid",
      "language": {"code": "en_ZA"},
      "components": [{"type": "body", "parameters": [{"type": "text", "text": "..."}]}]
    }
  }'
```

**Founder direct line:** Tumelo's personal mobile — stored in Robusca memory only, NEVER in this repo. Used for auction-bid replies and founder notes.

### Twilio (backup path — only if Meta blocks)

Twilio Console → Messaging → WhatsApp Senders → add number → request approval. Then use Twilio's Programmable Messaging API. Keys would be:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM` (the +14155xxx or registered SA number)

**Cost reality:** Twilio adds ~50% markup on top of Meta's per-conversation fee. Skip unless Meta verification fails.

---

## 4. Shopify

**Status:** ✅ Connector active in Perplexity.
**Store:** `studexmeat.com`
**Skills using it:**
- `studex-inventory-audit`
- `studex-shopify-fulfil`
- `studex-morning-brief`

**Critical:** R 127k unfulfilled pipeline currently. 87% checkout abandonment is the #1 revenue lever — enable Shopify cart-recovery email + WhatsApp recovery flow once Meta wired.

---

## 5. Facebook Pages + Instagram

**Status:** Connector loaded but page-read scope MISSING. Needs reconnect with full permissions.

**Action:** In Perplexity → Connectors → Facebook Pages → Reconnect → grant `pages_read_engagement`, `pages_manage_posts`, `instagram_basic`, `instagram_content_publish`, `business_management`.

**Same Business Manager** as WhatsApp (above) — all three (FB Page + IG + WhatsApp) live under one StudEx Meat business entity.

---

## 6. Google Ads + Search Console

**Google Ads:** ✅ Connected. ROAS 1.63× (R 11,756 spend). Jun 6 best day at 8.8×.
**Search Console:** ⛔ Access denied. Needs reconnect.

---

## 7. AgentMail audience strategy (Tumelo answered "emails")

**Plan:** Pull from Shopify customers (POPIA opt-in only) → import into AgentMail as a list called `studex_all_customers`. Segment within that into:
- `vip_top10pct` (by 12-month spend)
- `wagyu_buyers` (Wagyu Ribeye / Biltong Gold purchasers)
- `ankole_loyal` (Ankole buyers)
- `cart_abandoners` (started checkout, didn't complete)

**Import flow (run once DNS verified):**
1. Shopify Admin → Customers → Filter `accepts_marketing=true` → Export CSV
2. POST to AgentMail `/v0/lists` to create list
3. POST CSV to `/v0/lists/{id}/import`
4. Tag with segments via metadata field

---

## 8. Hosting decision — GoDaddy API vs Cloudflare vs Orgo VM

See `AGENT_PERPLEXITY_ROBUSCA.md` Session Log for the live comparison. Summary:

| Option | What it solves | Cost | Robusca recommendation |
|---|---|---|---|
| **GoDaddy DNS API** | DNS only. Robusca writes records directly. | Free (key from developer.godaddy.com) | Fastest unblock. Use today. |
| **Cloudflare migration** | DNS + DDoS + analytics + WAF + Workers (edge compute). Faster SA resolution. | Free | Strategic move. Do over the next week. |
| **Orgo dedicated VM** | Persistent Linux desktop Robusca controls 24/7. Solves: nightly content generation, FeedHive scheduling, AgentMail sender that survives Perplexity session reboots, browser automation that doesn't depend on Tumelo's MacBook being awake. | $29/mo Hacker tier ($351/yr) | YES — Robusca becomes always-on. Order this. |

Orgo gives Robusca a real cloud computer that boots in <500ms and runs continuously, separate from Perplexity sessions. The browser-automation failures we had with the GoDaddy panel happened because Comet bridge to Tumelo's MacBook is fragile. An Orgo VM is reachable directly via API/VNC, no bridge required.

---

## Where credentials live

All credentials are referenced by env var name in code. Never committed to repo.

| Var | Service | Status |
|---|---|---|
| `AGENTMAIL_KEY` | AgentMail | Live (rotate after DNS) |
| `META_ACCESS_TOKEN` | WhatsApp Cloud API | ⛔ NEEDED |
| `WABA_ID` | WhatsApp Cloud API | ⛔ NEEDED |
| `PHONE_NUMBER_ID` | WhatsApp Cloud API | ⛔ NEEDED |
| `TWILIO_ACCOUNT_SID` | Twilio (backup) | ⛔ NEEDED if backup path activated |
| `TWILIO_AUTH_TOKEN` | Twilio (backup) | ⛔ NEEDED if backup path activated |
| `SHOPIFY_ADMIN_TOKEN` | Shopify | Via Perplexity connector |
| `GOOGLE_ADS_REFRESH_TOKEN` | Google Ads | Via Perplexity connector |
| `FB_PAGE_ACCESS_TOKEN` | Facebook | ⛔ Needs reconnect with full scopes |
| `GODADDY_API_KEY` + `GODADDY_API_SECRET` | DNS | ⛔ NEEDED to unblock DNS |
| `ORGO_API_KEY` | Orgo VM | ⛔ NEEDED once Tumelo signs up |
