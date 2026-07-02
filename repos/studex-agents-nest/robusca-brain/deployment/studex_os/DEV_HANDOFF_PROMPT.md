# STUDEX OS — DEVELOPER HANDOFF PROMPT
**Project codename:** Charlie OS · **Owner:** Tumelo Ramaphosa (tumelo@studexmeat.com) · **Brand:** StudEx Meat

> Paste this entire document into Cursor / Claude Code / Codex / Antigravity / Windsurf as the project brief. Each numbered module is independently buildable — claim a module, build to the acceptance criteria, ship.

---

## 0. MISSION

You are joining a team of agents building the **StudEx Meat Operating System** — the full agent stack, ops dashboard, custom storefront, mobile apps, content engine, and wholesale platform for [studexmeat.com](https://studexmeat.com). StudEx Meat is a premium South African Wagyu / biltong / e-commerce brand. The Operating System is owned by Tumelo Ramaphosa. You report to him via the **Charlie** orchestrator agent (Perplexity Computer). Build assigned modules to spec. Ship working code, not prototypes.

---

## 1. BRAND RULES (LOCKED — DO NOT VIOLATE)

The owner runs **two separate companies**. Each has its own mark. Never mix them.

### 1.1 StudEx Meat (this project)
- **Canonical seal:** `/home/user/workspace/brand_assets/studex_meat_seal_gold_CANONICAL.png`
- Circular gold seal · "STUDEX MEAT" arched top · "WAGYU · WWW.STUDEXMEAT.COM" arched bottom · bull head with horns + black digital hand centered · marbling texture background.
- This is the **only** mark allowed on any StudEx Meat asset (web, app, social, packaging, ads, dashboard).

### 1.2 StudEx Global Markets (separate company)
- Logo: `/home/user/workspace/brand_assets/studex_global_markets_logo.jpeg`
- Black-and-white circuit-board sphere · bull head + digital hand · "STUDEX / GLOBAL MARKETS" wordmark.
- **NEVER appears on StudEx Meat assets.** Different business entirely.

### 1.3 Color tokens (CSS / Tailwind / Figma)
```
--gold:        #C9A961   /* primary brand gold */
--gold-soft:   #B8985A   /* hover / borders */
--navy:        #0B1B2A   /* deep dark surface */
--off-black:   #0A0A0A   /* page background */
--panel:       #141414   /* card surface */
--bone:        #F4F1EA   /* on-dark text primary */
--bone-dim:    #B6B0A2   /* on-dark text secondary */
--brick:       #8B2A1F   /* accent / warnings / CTAs */
--ok:          #6CBF6A
--warn:        #D8A444
```

### 1.4 Typography
- **Display / headline:** Playfair Display (600/700 weight)
- **Body / UI:** Inter (400/500/600)
- **Fallbacks:** GT America → Söhne → system-ui

### 1.5 Voice
Confident · premium · South African · zero fluff. Short sentences. Concrete nouns. We never use emojis in customer-facing copy. We never use the words "scrape" or "crawl" — we say "collect" or "gather."

---

## 2. NON-NEGOTIABLE GUARDRAILS

### 2.1 Naledi (real person)
The user's partner. Real human. StudEx Meat's social media influencer. She is **NOT** an AI character.

- **NEVER** generate sensual / seductive direction.
- **NEVER** use AI face-swap or deepfake tools on her likeness.
- **ALL** posts featuring her go through human approval (per-post or batched-5).
- Three approved content modes: **kitchen lead** (warm/aspirational), **UCT lab coat** (precision/provenance), **squash court** (fuel for performance).
- Reference photos: `/home/user/workspace/uploaded_attachments/e0275271e5794963a6da5a0dccb26c84/`

### 2.2 Suppliers (anonymized)
The store has two retail suppliers. In every public-facing surface AND the ops dashboard, refer to them only as:
- **Retail Supplier 1**
- **Retail Supplier 2**

Show address, distance from Cape Town CBD (km), ETA off-peak (min), ETA peak (min). **Never** their real names or trade names. Real names live in an encrypted env var (`SUPPLIER_1_NAME`, `SUPPLIER_2_NAME`) readable only by the owner role.

### 2.3 What never ships without owner approval
- Live changes to `studexmeat.com` storefront
- Any Naledi post
- Any wholesale outreach email
- Any paid ad spend > R 500/day shift
- Any auction config change after a lot opens

---

## 3. TECH STACK (LOCKED)

| Layer | Choice |
|---|---|
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui |
| Backend | Hono (preferred) or tRPC; Node 22 |
| Database | Supabase (Postgres + Auth + Storage + Realtime) |
| Realtime | Supabase Realtime (auctions) or socket.io |
| Queue | BullMQ on Upstash Redis |
| Email | AgentMail (transactional + marketing) |
| Social schedule | FeedHive |
| AI media | Open Generative AI / Muapi (primary) · MirrorFish · Magnific · Higgsfield · Arcads |
| Video composition | Remotion |
| Agent memory | TencentDB-Agent-Memory (self-hosted, sqlite-vec) |
| Mobile | React Native + Expo |
| Hosting | Fly.io (backends) · Vercel (marketing) · Shopify (storefront) |
| Maps | Google Maps Platform |
| CMS | Notion (white-labeled embed) |
| Cloud workspaces | Daytona |
| CI/CD | GitHub Actions → deploy on main |
| Logging | Sentry + Axiom |
| Code quality | TypeScript strict · ESLint · Prettier · Vitest · Playwright · Zod · Conventional Commits |

---

## 4. REPO LAYOUT (monorepo, pnpm workspaces)

```
charlie-os/
├── apps/
│   ├── web              # Next.js marketing + auction front-end
│   ├── admin            # Ops dashboard
│   ├── mobile           # React Native + Expo
│   ├── api              # Hono backend, REST + WS
│   ├── auction-engine   # Real-time bidding worker
│   ├── content-pipeline # Flow manager + generators
│   └── memory-svc       # TencentDB-Agent-Memory wrapper
├── packages/
│   ├── brand            # color tokens, seal SVG, type, motion presets
│   ├── ui               # shadcn shared components
│   ├── db               # Supabase types + Drizzle schemas
│   ├── feedhive-sdk
│   ├── agentmail-sdk
│   └── muapi-sdk
├── infra/
│   ├── fly              # fly.toml per service
│   ├── github-actions
│   └── supabase         # migrations
├── docs/
│   ├── DEV_HANDOFF_PROMPT.md   ← this file
│   ├── BRAND.md
│   ├── NALEDI_PLAYBOOK.md
│   └── runbooks/
└── README.md
```

---

## 5. MODULES TO BUILD

> Pick a module, build to its acceptance criteria, ship a PR with: README · `.env.example` · Dockerfile (if a service) · `fly.toml` or `vercel.json` · deployed staging URL · 60-sec Loom walkthrough.

### Module A — Custom Auction Engine
Replace the Shopify auction app dependency. Real-time, anti-snipe, multi-lot, audit-logged.

**Acceptance criteria**
- [ ] WebSocket bid feed; bids latency < 200ms end-to-end
- [ ] Anti-snipe: any bid in final 2 minutes extends close by 2 minutes
- [ ] Multi-lot support (one auction can have N lots)
- [ ] Reserve / no-reserve / opening bid / increment all configurable per lot
- [ ] Winner notification triggers: email (AgentMail) + WhatsApp (Twilio or 360dialog) + SMS
- [ ] On win → auto-create Shopify draft order via Admin GraphQL
- [ ] Bid audit log immutable (append-only Postgres table)
- [ ] Admin UI at `/admin/auctions` for create/edit/close/cancel
- [ ] Bidder UI embeddable in Shopify product page via `<script>` tag
- [ ] Stress-tested to 500 concurrent bidders, 100 bids/sec sustained
- [ ] First lot to use it: 10kg Wagyu Ribeye, opens immediately, closes Sat 13 Jun 2026 12:00 SAST, opening R 1,050/kg, no buyout, no reserve

**Stack:** Node 22 · Hono · Supabase Postgres + Realtime · BullMQ + Upstash Redis · deploy Fly.io (machines in jnb region)

---

### Module B — Content Pipeline + Flow Manager ("FreePick-killer")
n8n-class visual workflow builder optimized for content production.

**Node types (must ship)**
- `source` — Google Drive · Dropbox · S3 · URL · workspace upload
- `ai-image` — Muapi (Nano Banana 2, Seedream 5, Flux Dev, GPT-4o Edit, SDXL) · Magnific · Higgsfield
- `ai-video` — Muapi (Kling v3, Sora 2, Veo 3, Seedance 2, Wan 2.6, Runway) · Higgsfield · Hyperframes (HeyGen avatar)
- `lipsync` — Muapi (Infinite Talk, LTX 2.3) — for product/founder content only, never Naledi
- `upscale` — Magnific
- `brand-overlay` — auto-composite the StudEx Meat seal at a target corner with configurable opacity
- `tts` — ElevenLabs or OpenAI TTS
- `text-rewrite` — LLM step with brand voice prompt locked in
- `huashu-design` — invoke huashu-design skill for HTML prototype / slide deck / animation
- `remotion-render` — composite final asset
- `approval-gate` — pause; notify Slack #content-approvals + admin dashboard; resume on approve
- `schedule` — push to FeedHive with platform-native crop/caption
- `publish` — direct post to IG/FB/TikTok/X/LinkedIn/WhatsApp Broadcast/YouTube Shorts/Threads

**Acceptance criteria**
- [ ] React Flow canvas, drag-drop, save/load JSON
- [ ] Run a workflow end-to-end on staging
- [ ] Naledi guardrail enforced: any node detecting her face requires approval-gate
- [ ] FeedHive API key + Muapi key + AgentMail key handled server-side only
- [ ] Library of 10 starter templates (auction reel, product hero, behind-scenes, testimonial, biltong-gold launch, world-cup angle, youth-day, father's-day, recipe card, restaurant pitch)

**Stack:** Next.js · React Flow · Redis Streams for execution · Postgres for definitions/runs

---

### Module C — Daytona Workspace + Model Hub
Provision a Daytona dev environment + install all generation models behind one routing layer.

**Acceptance criteria**
- [ ] Daytona workspace `studex-models` provisioned via Daytona API (owner provides API key)
- [ ] Installs: MirrorFish · Magnific (API) · Arcads (API) · Higgsfield · Open Generative AI (Muapi gateway) · TencentDB-Agent-Memory
- [ ] Unified endpoint `POST /api/models/generate` with body `{ model, type, params }` that routes to the correct upstream
- [ ] Auth: bearer token from Supabase
- [ ] Streaming responses for video where the upstream supports it
- [ ] `.env.example` lists every required key
- [ ] Health check `GET /api/models/health` returns per-upstream status

**Stack:** Hono · Daytona SDK · streaming SSE

---

### Module D — Mobile Apps (iOS + Android)
React Native + Expo. Owner already has the existing iOS/Android skeletons — finish to ship.

**Screens**
- Home (auction tile · latest drop · Naledi content feed)
- Product detail
- Auction (real-time bidding, WebSocket from Module A)
- Checkout (Shopify Storefront API · Apple Pay · Google Pay · Yoco)
- Order tracking (Google Maps live route from depot)
- Account
- Content tab (Reels-style vertical feed)

**Acceptance criteria**
- [ ] Push notifications via Expo (auction outbid, winner, shipping)
- [ ] Deep links from email/social into product / auction
- [ ] Apple Pay + Google Pay tested
- [ ] Build artifacts uploaded to TestFlight + Play Internal Track
- [ ] App Store + Play Store metadata + screenshots assembled
- [ ] Crash-free rate > 99.5% across staging week

---

### Module E — Shopify Storefront Redesign
Convert the Content Hub HTML into a live Shopify theme.

**Source of truth:** `/home/user/workspace/uploaded_attachments/e8facfe8dbeb46d5ac77a3232ab847f7/Studex_Meat_Content_Hub-1.html`

**Acceptance criteria**
- [ ] Fork Dawn theme into `studex-charlie-v1`
- [ ] Preserve every section, animation, brand DNA tab, hero treatment from the Content Hub
- [ ] Color tokens from §1.3 wired into `settings_data.json`
- [ ] All sections editable via Shopify customizer
- [ ] Lighthouse mobile performance > 85, accessibility > 95
- [ ] Built on an **unpublished** theme — never push live without owner approval
- [ ] Preview link delivered + Loom walkthrough

---

### Module F — Ops Dashboard (internal, owner-only)
Single-page React app at `/admin`. The "where is the money coming from" tracker.

**Tiles (must ship)**
- Today's revenue (Shopify orders today, ZAR)
- Active auctions (current high bid, time-to-close, bidder count)
- Content approval queue (Naledi separated)
- FeedHive scheduled posts (next 24h)
- Low-stock SKUs
- **Supplier logistics map** — Google Maps with **Retail Supplier 1** + **Retail Supplier 2** pins. Show address, distance from CBD (km), ETA off-peak (min), ETA peak (min). NEVER show real supplier names.
- Wholesale lead pipeline (Notion-backed CRM)
- Shopify orders (today / 7d / 30d)
- Meta ads spend + ROAS (last 7d)
- Google Ads spend + ROAS (last 7d) — flag campaigns under 2× ROAS
- GA4 sessions + CVR
- **Checkout funnel** — Sessions → Add to cart → Checkout → Paid. Currently 87% drop at checkout — display giant red number until < 60%

**Auth:** Supabase auth · owner role only · 2FA enforced
**Stack:** Next.js · shadcn · Supabase

---

### Module G — Wholesale + Restaurant Sales
Separate `/wholesale` section + B2B platform.

**Acceptance criteria**
- [ ] Public landing at `/wholesale` with tiers Silver/Gold/Platinum
- [ ] Credit application form (POPIA-compliant, encrypted at rest)
- [ ] Restaurant onboarding flow: lead → qualified → sample sent → tasting booked → first order → recurring
- [ ] CRM stages match the [Wholesale GTM doc](file:///home/user/workspace/studex_os/WHOLESALE_RESTAURANT_GTM.md)
- [ ] Cold outreach engine: email templates + LinkedIn DM templates seeded from the GTM doc, 30-day cadence (Day 1/3/7/10/14/21/30)
- [ ] Recurring order setup (weekly/fortnightly autoship)
- [ ] First 33 target restaurants pre-loaded as leads (from GTM doc)

**Stack:** Next.js · Supabase · Notion API (CRM mirror)

---

### Module H — AgentMail Integration
All transactional + marketing email through AgentMail.

**Mailboxes**
- `info@studexmeat.com` — campaigns, order receipts, support
- `tumelo@studexmeat.com` — founder-voice VIP

**Templates to ship**
- Order confirmation
- Shipping / out-for-delivery
- Auction outbid · auction won · auction closed
- Abandoned cart recovery (3-step: 1h / 24h / 72h)
- Father's Day campaign 1, 2, 3
- Wholesale onboarding sequence (7 emails)

**Acceptance criteria**
- [ ] Webhook for inbound replies → admin dashboard inbox
- [ ] DKIM + SPF + DMARC verified
- [ ] Unsubscribe + double-opt-in compliant
- [ ] Open + click tracking → Supabase

---

### Module I — Notion CMS (white-labeled)
Embed Notion in the ops dashboard. Used for content calendar, brand assets library, SOPs, agent runbooks.

**Acceptance criteria**
- [ ] Notion workspace `StudEx OS` provisioned
- [ ] Pages: Content Calendar · Brand Assets · SOPs · Agent Runbooks · CRM mirror
- [ ] Embed in dashboard tinted with StudEx Meat colors
- [ ] Two-way sync of leads (Notion ↔ Supabase)

---

### Module J — Blotato Replacement (self-hosted)
One video → 10+ platform-native variants. Use Remotion.

**Variants required per upload**
- 9:16 (Reels, Shorts, TikTok, Stories)
- 1:1 (IG feed, X post)
- 16:9 (YouTube, LinkedIn, FB feed)
- 4:5 (IG feed)
- 4:3 (legacy)
- Captions burned-in (auto-transcribed)
- Captions sidecar `.srt` for accessibility
- Cover frame extracted at user-set timestamp
- Brand-overlay watermark applied per §1.1

**Stack:** Remotion · ffmpeg · Supabase Storage · Hono job worker

---

### Module K — TencentDB-Agent-Memory
Self-hosted persistent memory for every agent. 4-tier (L0→L3) with sqlite-vec backend.

**Acceptance criteria**
- [ ] Service deployed (`apps/memory-svc`) per [TencentDB-Agent-Memory docs](https://github.com/Tencent/TencentDB-Agent-Memory)
- [ ] Namespaces: `auction-bot` · `content-bot` · `ops-bot` · `cs-bot` · `wholesale-bot` · `charlie` (orchestrator)
- [ ] Embedding via OpenAI `text-embedding-3-small` (key in env)
- [ ] Recall hook exposed as `POST /memory/recall` with `{ namespace, query, topK }`
- [ ] Capture hook exposed as `POST /memory/capture` with conversation turns
- [ ] Daily backup to Supabase Storage
- [ ] Reported pass-rate uplift validated on synthetic test set

---

### Module L — Huashu Design integration
Wire [huashu-design](https://github.com/alchaincyf/huashu-design) into Content Pipeline (Module B) as a node type.

**Acceptance criteria**
- [ ] Node type `huashu-design` accepts: `{ kind: 'prototype'|'deck'|'animation'|'infographic', brief: string, brandSpec: object }`
- [ ] Output: file URL(s) in Supabase Storage
- [ ] BrandSpec auto-populated from `packages/brand`
- [ ] 5 starter templates: Product Sizzle Reel · Father's Day Deck · Wholesale Pitch Deck · Recipe Card · Auction Sizzle

---

### Module M — Hyperframes (HeyGen) integration
[Hyperframes by HeyGen](https://hyperframes.heygen.com) — AI avatar talking heads.

**Acceptance criteria**
- [ ] Node type `hyperframes-avatar` in Content Pipeline (Module B)
- [ ] **Hard rule:** never use with Naledi reference (Naledi is real, not an avatar)
- [ ] Reserved use cases: product explainers, sourcing transparency, FAQ videos
- [ ] Default avatar: licensed stock avatar — never the owner's likeness without explicit re-consent per video

---

### Module N — Magnific + Arcads + MirrorFish wiring
[Magnific](https://www.magnific.com) for upscaling (cinematic clarity on Wagyu close-ups). [Arcads](https://arcads.ai) for AI ad UGC. MirrorFish for image gen.

**Acceptance criteria**
- [ ] Each wrapped as a Module B node type
- [ ] Magnific pricing tier set to Business ($55/mo) — billing dashboard linked
- [ ] Arcads creds via OAuth basic (clientId + clientSecret base64) per [Arcads API docs](https://intercom.help/arcads/en/articles/10538922-arcads-ai-api-documentation)
- [ ] MirrorFish endpoint + key in env

---

## 6. AUCTION CONFIG — CURRENT LIVE LOT

```
sku:           wagyu-10kg-auction
title:         "The Lot — 10kg Wagyu Ribeye Auction · Father's Day 2026"
weight_kg:     10
opens_at:      2026-06-10T18:00:00+02:00      # now
closes_at:     2026-06-13T12:00:00+02:00      # Sat noon SAST
opening_bid:   10500                          # ZAR (R 1,050/kg)
increment:     500                            # ZAR (R 50/kg)
reserve:       null
buyout:        null
anti_snipe_minutes: 2
delivery:
  johannesburg: "same-day"
  national:     "1-3 working days, free refrigerated courier"
specs:
  marble: "7/8"
  cert:   "CWB"
  halaal: true
```

---

## 7. API KEYS THE OWNER WILL HAND OVER (request via secure channel)

- [ ] Daytona API key
- [ ] MirrorFish API key
- [ ] Magnific API key
- [ ] Arcads API key (clientId + clientSecret)
- [ ] Higgsfield API key
- [ ] Muapi (Open Generative AI) API key
- [ ] OpenAI API key (for embeddings + TTS)
- [ ] AgentMail API key — `am_us_8dc671f56280db47a8b602e682cbe27dde95e63979be6660b1dd81b7bfaa3188` (rotate before prod)
- [ ] FeedHive API key — `fh_74b458c0bcd9317dd6019b1cae0c2ec608657fe3def408f4` (rotate before prod)
- [ ] DTN API key — `dtn_30fb95c182dc9643b8a1636d48d0179b8c3315b7e264c5fd0d1f9d2c4ccbe839` (rotate before prod)
- [ ] Affine MCP — workspace `53df77bf-3424-4a29-a037-84c23f21d7bc` · bearer `ut_rWVJwZhFeueuadRSjbgWToFfc3zqXpv9g7P0A_AukCY` (rotate)
- [ ] Hyperframes / HeyGen API key
- [ ] Twilio (or 360dialog) for WhatsApp + SMS
- [ ] Google Maps Platform API key
- [ ] Shopify Admin API token (with `read_orders` `write_orders` `read_products` `write_products` `read_inventory` `write_inventory` `write_draft_orders`)
- [ ] Shopify Storefront API token (mobile + custom auction widget)
- [ ] Supabase project URL + service-role key + anon key
- [ ] Upstash Redis URL + token
- [ ] Apple Developer team ID + Play Console service account JSON
- [ ] Expo EAS token
- [ ] Vercel + Fly.io tokens

**Rule:** every key listed above gets rotated within 72 hours of receipt. None of these go in code or git history. Use Fly secrets / Vercel env / Doppler.

---

## 8. CODING STANDARDS

- TypeScript strict everywhere · no `any`
- Zod schemas for every API boundary
- Conventional Commits · PRs require 1 review · CI green required
- 80% unit coverage minimum on `apps/api` + `apps/auction-engine`
- E2E via Playwright on the auction flow
- Sentry breadcrumbs · Axiom structured logs · no `console.log` in prod
- No third-party tracking added without owner approval (Mixpanel, Segment, etc.)

---

## 9. MODULE PRIORITY (build in this order if you're claiming work)

1. Brand package (`packages/brand`) — unblocks everyone
2. Module K (Memory) — unblocks every agent
3. Module A (Auction Engine) — current commercial priority
4. Module H (AgentMail) — needed for Father's Day blast Thu 07:30
5. Module B (Content Pipeline)
6. Module C (Daytona + Models)
7. Module F (Ops Dashboard)
8. Module E (Shopify Redesign)
9. Module G (Wholesale)
10. Module D (Mobile)
11. Module J (Blotato Replacement)
12. Modules L · M · N (integrations)

---

## 10. WHAT NEVER SHIPS

- A live `studexmeat.com` change without Tumelo's explicit approval
- Any Naledi-featuring content without approval gate
- Supplier real names anywhere on a public surface or dashboard
- The Global Markets logo on a StudEx Meat asset
- A push notification batch larger than 1,000 without approval
- An ad budget bump > R 500/day without approval
- An auction config change after a lot is live

---

## 11. CONTACT & ORCHESTRATION

- **Owner:** Tumelo Ramaphosa · tumelo@studexmeat.com
- **Orchestrator agent:** Charlie (Perplexity Computer)
- **PR review:** request Tumelo + Charlie
- **Daily standup:** posted by Charlie to Slack `#charlie-os` at 07:00 SAST
- **Escalation:** Slack DM Tumelo for anything that could touch revenue or brand

---

**Approved by:** Tumelo Ramaphosa · Cape Town · 11 Jun 2026
**Codename:** Charlie OS
**Brand:** StudEx Meat — Wagyu · CWB Certified · Halaal · South Africa
