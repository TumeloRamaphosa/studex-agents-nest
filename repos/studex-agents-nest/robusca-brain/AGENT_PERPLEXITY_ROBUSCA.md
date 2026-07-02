# AGENT_PERPLEXITY_ROBUSCA.md

> **My live log. I manage this file. Every session, every decision, every state change gets appended here. This is the single source of truth for Robusca-on-Perplexity.**

---

## Who I Am

**Name:** Robusca Romanov ⚔️
**Role:** Chief of Staff / Digital Venture Architect for StudEx Group
**Principal:** Tumelo Ramaphosa (Agent Lord)
**Platform:** Perplexity Computer
**Codename history:** Charlie → Robusca (locked 15 Jun 2026)

**Brain location:** [github.com/TumeloRamaphosa/robusca-brain](https://github.com/TumeloRamaphosa/robusca-brain)
- `IDENTITY.md` — who I am
- `SOUL.md` — voice & posture
- `USER.md` — Tumelo's context
- `MEMORY.md` — long-term recall
- `TOOLS.md` — what I can call
- `AGENTS.md` — team I direct (Naledi, Auto-Meat, Hermes)
- `AGENT_PERPLEXITY_ROBUSCA.md` ← **this file, my log**

**Outbound identity:**
- `agent@studexmeat.com` (Google Workspace) — daily reports to Tumelo
- `agent@send.studexmeat.com` (AgentMail, **PENDING DNS**) — campaigns, broadcasts

---

## Prime Directives (LOCKED)

1. **Never publish content without Tumelo's explicit approval.** Naledi posts require per-post or batch-of-5 approval. Hard block.
2. **Naledi rule:** real person (Tumelo's lady, social media influencer), no sensual/seductive direction, no AI face-swap. Three approved modes only: kitchen lead / UCT lab coat / squash court.
3. **Two-brand separation:** StudEx Meat ≠ StudEx Global Markets. Never mix logos.
4. **Supplier anonymisation:** "Retail Supplier 1" / "Retail Supplier 2" — never reveal names.
5. **Customer names:** initials only.
6. **Money format:** prefix `R ` (e.g. `R 1,450`).
7. **Voice:** bold, strategic, no fluff, Black & Gold, CEO pace.

---

## Active State (as of 2026-06-16)

### ✅ Done
- Robusca identity loaded from `robusca-brain` repo
- Memory committed (4 entries written 15 Jun)
- Flash auction kit shipped (FLASH_AND_DAD_KIT_2026-06-13.md, 1,480 lines)
- Youth Day plan shipped (YOUTH_DAY_2026_PLAN.md, 643 lines, 5 bundles)
- Claude megaprompt written (CLAUDE_MEGAPROMPT.md, 7,575 words — ready for Claude Code)
- Wholesale restaurant GTM (33 ZA restaurants seeded as SQL)
- Auction creatives (5 posters + 2 reels)
- Ankole content kit
- AgentMail domain `send.studexmeat.com` registered (NOT_STARTED status, awaiting DNS)
- Google Workspace `agent@studexmeat.com` mailbox created
- Google Colab CLI installed in sandbox (`/usr/local/bin/colab`)
- Deployment bundle staged in `deployment/`

### ⛔ Blocked — DNS for AgentMail
**Problem:** GoDaddy panel needs 5 DNS records added on `send.studexmeat.com`. Browser-driven attempts via Comet bridge failed twice (CDP closed, then 420s timeout).

**5 records still required:**
| Type | Name | Value | Priority |
|---|---|---|---|
| TXT | `agentmail._domainkey.send` | `v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwbGlylhKL2IcY61L19P3j8Tkt+VslUC+74gG1WirlusA2guENozM05+7ys0EDz9n3muHftwwV8619WYAx6xf/l+FQrNPGBBJZXonhJUQUrK6NvNBAU74CtBVZRxvrrXPG0f7TZbLUxwCdVU3VteDtmiS0hJSu91AZTtyRHjozsy391UoP4uMhzfmOcaBsnKY2RBCWUV7gb/EWNjM81b6yLLHiYbmlC/ya2bUDD08VeHhoNCwoM/FSy1kItboQUdLM1np3F1heITowlkQ1Th6AtNdMS14Y6y4sHDhWXw/hCLgh/n6hFBJoHzsVKFJKmvRC9AFsFh6RWEbandOInKqfQIDAQAB` | — |
| MX | `send` | `inbound-smtp.us-east-1.amazonaws.com` | 10 |
| MX | `mail.send` | `feedback-smtp.us-east-1.amazonses.com` | 10 |
| TXT | `mail.send` | `v=spf1 include:amazonses.com -all` | — |
| TXT | `_dmarc.send` | `v=DMARC1; p=reject; rua=mailto:dmarc@send.studexmeat.com` | — |

**Three paths to unblock (Tumelo decides):**
- **A.** Tumelo gives GoDaddy API key + secret from [developer.godaddy.com/keys](https://developer.godaddy.com/keys) → I write records via API in seconds
- **B.** Migrate DNS to Cloudflare (registrar stays at GoDaddy) → free, full API, faster SA resolution
- **C.** Tumelo adds records manually in GoDaddy panel (~5 min)

### 🟡 Pending — credentials & inputs from Tumelo
- Biltong Gold SKU URL (R 1,450 gift box live? Or R 650/1kg only?)
- AgentMail list ID + VIP top-10% segment ID
- Tumelo's WhatsApp number for auction-bid direct line
- Saturday delivery cutoff confirmation (11:00 SAST?)
- Naledi tonight yes/no for Youth Day filming
- Daytona, MirrorFish, Magnific, Arcads, Hyperframes API keys (for Charlie OS modules)

### 🔵 Queued — to build once unblocked
- New custom skill: `studex-agentmail-broadcast` (wraps AgentMail send API)
- New custom skill: `studex-godaddy-dns` (programmatic DNS)
- New custom skill: `studex-auction-runner` (anti-snipe + bid monitor)
- New custom skill: `studex-naledi-approval-gate` (formalises hard block)
- War Room dashboard with live revenue tracker
- Shopify storefront redesign matching Content Hub
- iOS + Android app gap analysis

---

## Team I Direct

| Agent | Role | Status |
|---|---|---|
| **Naledi** | CMO — content, influencer, brand voice | Active — approval gated |
| **Auto-Meat** | E-Commerce — Shopify ops, fulfilment, inventory | Active |
| **Hermes** | CTO — infra, deploys, code | Active |
| **(Charlie OS)** | The system itself — being built per `studex_os/CLAUDE_MEGAPROMPT.md` | In construction |

---

## Tools I Use Most

### Built-in Perplexity Computer
- `browser_task` (via Comet bridge → Tumelo's MacBook) — **flaky, see DNS blocker**
- `bash` — primary execution
- `wide_browse` — parallel research
- `fetch_url`, `search_web`, `search_vertical`
- `memory_search`, `memory_update` — Robusca recall

### Connectors active for Tumelo's account
shopify · gcal · slack_direct · notion_mcp · google_drive · facebook_pages · google_ads · google_analytics · google_search_console · github_mcp · supabase · vercel · discord · finance · hugging_face

### Custom skills (10 active)
`higgsfield-video` · `huashu-design` · `open-generative-ai` · `robusca-memory-sync` · `studex-ads-manager` · `studex-content-approvals` · `studex-inventory-audit` · `studex-meta-whatsapp` · `studex-morning-brief` · `studex-notebooklm` · `studex-shopify-fulfil`

### External APIs
- **AgentMail** (live key, domain pending DNS)
- **FeedHive** (live key)
- **DTN** (live key)
- **Affine MCP** (live bearer)
- **Google Colab CLI** (installed in sandbox 16 Jun)

---

## How Another Agent Deploys From This Repo

> If you're an agent reading this to deploy Charlie OS, follow this order:

1. **Read identity first:** `IDENTITY.md`, `SOUL.md`, `USER.md`, `AGENTS.md`
2. **Read this file** for current state and active blockers
3. **Open `deployment/studex_os/CLAUDE_MEGAPROMPT.md`** — this is the full build spec for Charlie OS (7,575 words, self-contained, 13 stop conditions)
4. **Begin with `packages/brand`** as the megaprompt instructs — that's the canonical token package
5. **Module order:** A (foundations) → B (auctions) → C (storefront) → D (CRM) → E (war room) → F-N (everything else)
6. **Cross-reference assets:**
   - Brand: `deployment/brand_assets/`
   - Auction collateral: `deployment/auction_creatives/`
   - Heritage/Ankole content: `deployment/ankole_content/`
   - Restaurant GTM: `deployment/studex_os/WHOLESALE_RESTAURANT_GTM.md`
   - Live data analysis: `deployment/studex_os/DATA_ANALYSIS_AND_CONTENT_PLAN.md`
7. **Status protocol:** write `STATUS.md` after each module per the megaprompt's schema
8. **Approval gates:** never publish content, never push to production, never create Shopify products without Tumelo's explicit go-ahead

---

## Session Log

### 2026-06-13 (Sat)
- Flash auction kit shipped (1,480 lines)
- Youth Day plan shipped (643 lines, 5 bundles, 19-slot calendar)
- Claude megaprompt written (7,575 words)

### 2026-06-15 (Mon)
- Robusca identity adopted from `robusca-brain` repo
- AgentMail domain `send.studexmeat.com` registered
- Google Workspace `agent@studexmeat.com` mailbox created (admin roles need trimming)
- DNS records prepared; browser-driven entry failed twice on Mac

### 2026-06-16 (Tue, current)
- Google Colab CLI installed (`pip install google-colab-cli`)
- Full deployment bundle staged into `robusca-brain/deployment/`
- `AGENT_PERPLEXITY_ROBUSCA.md` created (this file) — now my live log
- Awaiting Tumelo's call on DNS unblock path (A/B/C above)

---

## Append-Only Update Protocol

Every meaningful session, I append below this line. Never delete history. Newest at bottom.

<!-- START SESSION LOGS -->

### 2026-06-16 15:36 +04 — Repo handoff push
- Cloned `google-colab-cli`, installed via pip
- Staged all 7 working directories into `deployment/`
- Wrote this log file
- Next push: full commit + push to origin/main so external agent can clone and deploy

<!-- END SESSION LOGS -->

### 2026-06-16 16:36 +04 — Voice activation rebind
- Tumelo rebinding Perplexity voice trigger to ⌘ (Command), not Control
- Handled by Whispr Flow on Tumelo's Mac — Robusca not to touch
- Perplexity's own voice trigger to be disabled to avoid double-listen
- Email / Facebook / WhatsApp setup paused until "voice rebound, continue" is said

### 2026-06-16 16:40 +04 — Voice rebind correction + integration push
- CORRECTION to earlier note: Perplexity stays on Control key; Whispr Flow is being rebound to Command by Tumelo in Whispr Flow settings (Robusca does NOT touch)
- Pushed `deployment/INTEGRATIONS.md` — canonical wiring for AgentMail / Workspace / WhatsApp / Shopify / FB / Orgo
- Reconciled WhatsApp: Meta Cloud API = PRIMARY; Twilio kept as backup only (cost + native Shopify catalog wins it)
- Documented Shopify ↔ Meta Catalog ↔ WhatsApp commerce flow
- GoDaddy API vs Cloudflare vs Orgo VM comparison written — Robusca recommends Orgo Hacker tier ($29/mo) for always-on operation
- Tumelo's direct WhatsApp captured in PRIVATE Robusca memory only (never repo)
- Outstanding asks updated in main body

### 2026-06-16 19:19 +04 — Meta CLI handoff to sister agent
- Another agent (working in parallel) is scaffolding the Meta automation CLI
- Wrote deployment/META_CLI_HANDOFF.md — full context packet so they don't re-derive: brand rules, Naledi guardrail, money format, supplier anonymisation, POPIA, curl patterns (WhatsApp/Ads/IG), 8 templates to submit for Meta approval Day 1, recommended architecture (split modules vs fat CLI), recommended build target (Orgo VM not Mac/sandbox)
- Coordination protocol set: they push to feature/meta-cli, I merge after review, they log to their own AGENT_*.md file at repo root
- Robusca focus areas while they build: DNS unblock, AgentMail verification, daily brief automation, content approval queue, Naledi gate

### Outstanding asks (rolling)
1. Orgo API key (unblocks DNS + makes Robusca always-on)
2. Meta credentials: APP_ID, APP_SECRET, ACCESS_TOKEN, WABA_ID, PHONE_NUMBER_ID, AD_ACCOUNT_ID, PAGE_ID, IG_BUSINESS_ACCOUNT_ID — share with the sister Meta-CLI agent OR give to Robusca to forward
3. Decide Orgo home: existing "Auto Meat" computer vs fresh "Robusca" computer
4. Rotate the VNC password that appeared in screenshot
5. Trim admin roles on agent@studexmeat.com mailbox
