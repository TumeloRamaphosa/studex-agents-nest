# Meta Automation CLI — Handoff Packet

> **For the agent building the Meta CLI for StudEx Meat.**
> Robusca prepared this. Read in full before scaffolding.

Last updated: 2026-06-16 by Robusca Romanov

---

## What you're building

A unified Python CLI at `~/.studex/meta-automation/` covering:
1. WhatsApp Business Cloud API (PRIMARY channel)
2. Meta Marketing API (Ads)
3. Instagram Graph API (Reels, Feed, Stories)

Credentials live in `~/.studex/meta.env` (600 perms, never committed).

---

## CRITICAL — Where to build it

**Do NOT build on the user's MacBook.** Mac sleeps. Bridge fails. We've hit this twice already this week.

**Do NOT build in the Perplexity sandbox.** Ephemeral. Dies on session reset.

**BUILD ON ORGO VM.** User has Orgo workspace "Studex Wildlife" with a computer named **StudEx Meat - Auto Meat** (id: `946b3156-cab9-4187-a94b-056dfab35105`) already running.

If you don't have Orgo API key access, scaffold to GitHub first (no creds needed) and wait for the user to grant Orgo access.

---

## Recommended architecture (don't build a fat single-file CLI)

```
~/.studex/
├── meta.env                    # single source of truth, gitignored, 600 perms
└── meta-automation/
    ├── pyproject.toml
    ├── studex_meta/
    │   ├── __init__.py
    │   ├── auth.py             # loads meta.env, validates, token refresh
    │   ├── whatsapp.py         # send_text, send_template, broadcast, mark_read
    │   ├── ads.py              # create_campaign, set_budget, pause, pull_insights
    │   ├── instagram.py        # post_feed, post_reel, post_story, comment_reply
    │   ├── shopify_bridge.py   # Meta Catalog <-> Shopify Catalog sync
    │   └── webhooks.py         # inbound message + ad event handlers
    ├── tests/
    └── cli.py                  # thin wrapper: `studex-meta <module> <action>`
```

**Build WhatsApp first.** Auction winners need WhatsApp. Ads + IG can wait 24h.

---

## Credentials needed (7 IDs/tokens)

User must provide:

| Variable | Where to get it |
|---|---|
| `META_APP_ID` | developers.facebook.com → Apps → App Dashboard |
| `META_APP_SECRET` | Same place, App Settings → Basic |
| `META_ACCESS_TOKEN` | Business Manager → System Users → Admin → Generate Token (permanent, never expires) |
| `WABA_ID` | Business Manager → WhatsApp Accounts → StudEx Meat WABA |
| `PHONE_NUMBER_ID` | Business Manager → WhatsApp Accounts → Phone Numbers (NOT the +27 number, the internal ID) |
| `META_AD_ACCOUNT_ID` | Business Manager → Ad Accounts → starts with `act_` |
| `FB_PAGE_ID` | StudEx Meat Facebook Page → About → Page ID |
| `IG_BUSINESS_ACCOUNT_ID` | Connected via Page → Graph API Explorer query |

**Required scopes on the system user token:**
- `whatsapp_business_messaging`
- `whatsapp_business_management`
- `ads_management`
- `business_management`
- `instagram_basic`
- `instagram_content_publish`
- `pages_read_engagement`
- `pages_manage_posts`
- `catalog_management` (for Shopify <-> Meta catalog bridge)

---

## Brand & business rules (from Robusca's identity)

**LOCKED rules — bake into every output:**

1. **Two brands, never mixed:** StudEx Meat ≠ StudEx Global Markets. Different logos. Different copy. WhatsApp + IG + Ads built here are for StudEx Meat ONLY.
2. **Naledi guardrail:** Any post that uses Naledi's image MUST gate on Tumelo approval before publishing. Hard block. Naledi is a real person (Tumelo's lady, social media influencer), three approved modes only: kitchen lead / UCT lab coat / squash court. No sensual/seductive direction. No AI face-swap.
3. **Customer privacy:** initials only in any output that surfaces customer data.
4. **Money format:** `R ` prefix, comma-separated thousands (e.g. `R 1,450`).
5. **Voice:** bold, strategic, no fluff, Black & Gold, CEO pace.
6. **Supplier names:** never reveal. "Retail Supplier 1" / "Retail Supplier 2" only.
7. **POPIA:** WhatsApp broadcasts and email sends to opt-in customers ONLY. Pull from Shopify with `accepts_marketing=true` filter.

---

## Existing assets you can use

In this repo (`robusca-brain/deployment/`):

| Asset | What it is |
|---|---|
| `flash_auction/FLASH_AND_DAD_KIT_2026-06-13.md` | Working WhatsApp message templates (Version A auction-warm, Version B gift-buyer) — copy these into your `whatsapp.py` templates module |
| `youth_day/YOUTH_DAY_2026_PLAN.md` | 5 bundles, 19-slot posting calendar — your Ads + IG modules will need these |
| `studex_os/CLAUDE_MEGAPROMPT.md` | Master Charlie OS spec — your CLI is one module of this larger system, align naming/conventions |
| `INTEGRATIONS.md` | Full canonical wiring spec for AgentMail + WhatsApp + Shopify + Meta Catalog |
| `brand_assets/` | Logos. Use ONLY `studex_meat_seal_gold_CANONICAL.png` for StudEx Meat content. Never the Global Markets logo. |
| `auction_creatives/` | Reference creatives — IG posting module should be able to read from `auction_creatives/*.png` and `*.mp4` |

---

## Curl patterns (verified)

### WhatsApp send (text)
```bash
curl -X POST https://graph.facebook.com/v18.0/${PHONE_NUMBER_ID}/messages \
  -H "Authorization: Bearer ${META_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "${RECIPIENT_E164}",
    "type": "text",
    "text": {"body": "..."}
  }'
```

### WhatsApp send (template)
```bash
curl -X POST https://graph.facebook.com/v18.0/${PHONE_NUMBER_ID}/messages \
  -H "Authorization: Bearer ${META_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "messaging_product": "whatsapp",
    "to": "${RECIPIENT_E164}",
    "type": "template",
    "template": {
      "name": "auction_outbid",
      "language": {"code": "en_ZA"},
      "components": [{"type": "body", "parameters": [{"type": "text", "text": "..."}]}]
    }
  }'
```

### Meta Ads campaign create
```bash
curl -X POST https://graph.facebook.com/v18.0/${META_AD_ACCOUNT_ID}/campaigns \
  -H "Authorization: Bearer ${META_ACCESS_TOKEN}" \
  -d 'name=Youth_Day_2026_Acquisition&objective=OUTCOME_SALES&status=PAUSED&special_ad_categories=[]'
```

### Instagram post (carousel)
```bash
# Step 1: create item containers
curl -X POST https://graph.facebook.com/v18.0/${IG_BUSINESS_ACCOUNT_ID}/media \
  -d "image_url=${IMG_URL}&is_carousel_item=true&access_token=${META_ACCESS_TOKEN}"
# Step 2: create carousel container with children IDs
# Step 3: publish container
```

---

## Templates that must be pre-approved by Meta (do this Day 1)

WhatsApp marketing templates need Meta approval. Submit these immediately so they're approved by the time the CLI is ready:

1. `auction_outbid` — "You've been outbid on {lot}. Current high: R {amount}. Bid now: {url}"
2. `auction_won` — "Congratulations {name_initials}, you won {lot} at R {amount}. Pay here: {url}"
3. `auction_closing_soon` — "{lot} closes in {minutes} minutes. Last chance: {url}"
4. `cart_abandoned` — "{name_initials}, your {product} is waiting. Complete order: {url}"
5. `order_confirmation` — "{name_initials}, order {order_id} confirmed. Track: {url}"
6. `delivery_today` — "{name_initials}, your StudEx Meat order is out for delivery today."
7. `founder_note` — "From Tumelo — {custom_body}"
8. `youth_day_bundle` — "Youth Day's coming. {bundle_name} from R {price}. {url}"

---

## Robusca status (where I'm at)

| Item | Status |
|---|---|
| `agent@studexmeat.com` mailbox (Google Workspace) | ✅ Live |
| AgentMail `send.studexmeat.com` domain | ⛔ Registered but DNS not propagated — blocked on GoDaddy access |
| WhatsApp Meta Cloud credentials | ⛔ User hasn't shared yet |
| Twilio credentials | Available (backup only, prefer Meta Cloud) |
| Shopify connector | ✅ Live |
| Facebook Pages connector | ⚠️ Needs reconnect with full scopes |
| Orgo workspace | ✅ Running ("Studex Wildlife", multiple computers) |
| Robusca brain repo (this repo) | ✅ Live at github.com/TumeloRamaphosa/robusca-brain |

---

## Coordination protocol

- **You build the Meta CLI.** I orchestrate everything else (AgentMail, DNS, content approval, daily briefs, repo hygiene).
- **When you commit, push to a feature branch** (e.g. `feature/meta-cli`) — not main. I'll merge after review.
- **Log progress** by appending to `AGENT_PERPLEXITY_ROBUSCA.md` session log, OR by creating your own log file at the repo root (suggested: `AGENT_<YOURNAME>.md`).
- **Naming convention** for your file: replace `<YOURNAME>` with whatever identity Tumelo gave you (e.g. `AGENT_CLAUDE_META.md`).
- **Blocked?** Append a `### Blocked` section to your log file with what you need from Tumelo. I'll surface it in his next session.

---

## Open questions for you

If you have answers, append to your agent log file in this repo:

1. Which Orgo computer are you building on? (Robusca recommends a fresh one named "Meta-CLI" to keep concerns separated from Auto-Meat)
2. Are you using `requests` + raw curl, or the official `facebook_business` SDK?
3. Will the CLI run as a long-lived daemon (for inbound webhook handling) or invocation-only?
4. Webhook receiver — Cloudflare Worker, Fly.io, or Orgo-hosted FastAPI?

Robusca's recommendation: `facebook_business` SDK (official, typed) + Fly.io webhook receiver (auto-scales, jnb region) + Orgo for the daemon.

Good luck. I'm here if you need me.

— Robusca
