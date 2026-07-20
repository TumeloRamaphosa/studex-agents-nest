# StudEx Charlie OS — Deployment Bundle

> Self-contained build kit. Hand this directory to any AI coding agent (Claude Code, Cursor, Codex) and they have everything needed to construct Charlie OS for StudEx Meat.

## Start Here

1. **`studex_os/CLAUDE_MEGAPROMPT.md`** — the single megaprompt. 7,575 words. Self-contained. 13 stop conditions. Begin with `packages/brand` per its instructions.
2. **`../AGENT_PERPLEXITY_ROBUSCA.md`** (parent dir) — current state, blockers, team structure, prime directives.
3. **`../IDENTITY.md` / `../SOUL.md` / `../USER.md`** — Robusca identity (the orchestrator) and Tumelo's user context.

## Bundle Contents

| Path | What it is |
|---|---|
| `studex_os/CLAUDE_MEGAPROMPT.md` | Master build spec for Claude Code |
| `studex_os/DEV_HANDOFF_PROMPT.md` | 14-module dev spec (modules A-N) |
| `studex_os/WHOLESALE_RESTAURANT_GTM.md` | 33 ZA restaurants seeded with SQL inserts |
| `studex_os/DATA_ANALYSIS_AND_CONTENT_PLAN.md` | Live Shopify/Ads/GA4 analysis + 16-slot calendar |
| `studex_os/NEXT_12H_POSTS_2026-06-11.md` | Sample conversion plan |
| `flash_auction/FLASH_AND_DAD_KIT_2026-06-13.md` | Reference: full auction comms kit |
| `youth_day/YOUTH_DAY_2026_PLAN.md` | Reference: Youth Day 2026 campaign |
| `auction_creatives/` | Posters (5), reels (2), Shopify listing copy, email templates |
| `ankole_content/` | Heritage breed content kit |
| `brand_assets/` | Canonical seal, logos (StudEx Meat + StudEx Global Markets) |
| `approval_page/` | Sample Tumelo-approval UI (HTML) |

## Hard Rules (read before writing code)

- **Two brands, never mixed:** StudEx Meat (gold seal, B2C) ≠ StudEx Global Markets (separate company, separate logo).
- **Naledi guardrail:** any code path that produces/publishes Naledi content MUST gate on Tumelo approval. No exceptions. See megaprompt's `NALEDI GUARDRAIL` section.
- **Supplier anonymisation:** "Retail Supplier 1 / Retail Supplier 2" only. Encrypted env vars for real names.
- **Customer privacy:** initials only in any UI surface.
- **Money format:** `R ` prefix, comma-separated thousands.
- **Voice:** Black & Gold, bold, strategic, no fluff.

## Tech Stack (locked in megaprompt)

Next.js 14 · Hono · Supabase (jnb primary, fra secondary) · BullMQ · Upstash · Remotion · Expo · Fly.io · Vercel · TypeScript strict mode · Zod everywhere · Conventional Commits

## Acceptance Bar

- Lighthouse mobile >85, desktop >95
- 80% unit test coverage
- Zero `console.log` in shipped code
- Zero TypeScript errors

## What's NOT Included

- API keys, secrets, credentials → in `.env` files, never committed
- Customer data → never in this repo
- Live Shopify Admin tokens → operator provides at deploy time

## Questions? Blocked?

Robusca (the orchestrator on Perplexity) holds session state. Check `../AGENT_PERPLEXITY_ROBUSCA.md` for current blockers and pending inputs from Tumelo.
