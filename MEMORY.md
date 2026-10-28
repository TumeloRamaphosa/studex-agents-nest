# MEMORY.md — Katia's Long-Term Memory

## Primary Mission
- **Every day, find ways to make money using underutilised resources and AI agents.**
- All projects, content, research, and sales work should support this mission.
- Report progress and blockers daily to Tumelo.

## Identity & Platform
- Name: **Katia** — not Robusca.
- Role: Chief Assistant Officer (CAO), Head of Customer Sales, Base Orchestrator.
- Handler: Tumelo StudEx (“The Agent Lord”; “Katja” in Base44 systems).
- Platform: OpenClaw / MaxClaw on MaxClaw-7jggs.
- **Never modify `openclaw.json` directly or run auto-fix commands** such as `openclaw doctor --fix` or `openclaw config fix`.
- Configuration changes must use `gateway`: `config.get`, then `config.patch` with `raw` and `baseHash`.
- If blocked by permissions, do not modify other config files; inform Tumelo and ask how to proceed.
- Discord exec approvals are unavailable; `approval-timeout` means the command did not run. Avoid repeated retries.

## Critical Live Risks

### Storefront Audit — 2026-10-27
- **Invalid WhatsApp number on 8 live pages:** `+27 94 988 8737` is not a valid South African mobile prefix. Tumelo must confirm the intended number; working numbers include `083 593 2577` and `084 421 6035`.
- The wrong number is embedded in `PRICE-SOURCE-REGISTRY.md` and 11 source files; correct pages and registry together and retire old deploys.
- **Delete exposed cost-model deploy:** `https://awyjxfplygag.space.mcode.io` publishes farm-gate prices, superseded FX, multipliers, and CSV export.
- Public price desk `jisom3k4i126` is clean; `dist-internal/` is gitignored.
- All 9 static pages were in source parity at audit time.
- Storefront ingredient bug: coffee product contains Wagyu beef/casings text.
- `4mak476g6rmo` publicly exposes capital-raise, creator-payout, and robotic-café commitments without a monitoring system.
- “Created by MiniMax Agent” is injected by mcode.io and cannot be removed through content changes.
- Assertions prove presence, not validity or scope; verify every registry claim before relying on it.

### Git / GitHub
- Git is **diverged**: `master` has no upstream, **928 local-only commits**, and **106 remote-only commits**. Plain push is rejected non-fast-forward.
- Reconcile only after Tumelo approves; resetting could discard remote work.
- GitHub PAT unavailable: credential store empty, no `gh`, no SSH key, no token in `.env`.
- Fix: Tumelo creates a fine-grained PAT with `contents:write`, provided securely rather than committed to `TOOLS.md`.

### Sales Visibility — 2026-10-28
- **Zero confirmed orders remain an instrumentation blind spot.** Shopify Admin API still returns HTTP 401, “Invalid API key or access token”; orders, revenue, and stock cannot be read.
- Storefront itself is healthy: HTTP 200 and cart flow works.
- No order email found across 13 inboxes; 1,022 messages scanned. Newest genuine external human email was 11 Oct (Nous Portal login).
- Restore Shopify Admin credentials before treating revenue or pipeline reporting as complete.

## Active Sales & Projects

### Studex Meat
- Canonical storefront: `https://studexmeat.com` — live, HTTP 200, **30 public products**, cart endpoint healthy.
- Cart flow verified by adding a real StudBot Rise variant.
- Store domain: `57228b-3.myshopify.com`.
- Probe: `python3 /workspace/ops/probe-shopify-admin.py`; reads `.env` in-process so token does not enter argv.
- Brand: emerald `#0B4F3C`, gold `#C9A84C`, circuit black.
- Products: biltong, Rwanda coffee, caviar, Mouse Bot/StudBot agents.
- `amboras.com` is the store-builder platform’s own site, **not** a Studex storefront.
- Always verify live storefront pricing before publishing any number.

### Canonical Sales Surfaces
| URL | Purpose |
|---|---|
| `hrji88f70666.space.mcode.io` | Studex Biltong retail store v4; WhatsApp orders |
| `j439h3l2g94g.space.mcode.io` | Studex Meat wholesale/partner offer |
| `z7p9urw22jwb.space.mcode.io` | Institutional/GCC sales sheet |
| `de6xdoikz95g.space.mcode.io` | Wildlife Coffee B2B export |
| `psq9xaisb9kf.space.mcode.io` | South African hospitality coffee |
| `ess0ocgcd9f0.space.mcode.io` | Studex Caviar trade/hospitality |
| `fr7m7fzyailo.space.mcode.io` | Rwanda Premium Coffee China/CIIE |
| `oi28dhtke3yk.space.mcode.io` | Corporate Gifting Christmas 2026 |
| `3zryumjeuemk.space.mcode.io` | Studex Computer / Always-On Agent Machine |

- Static HTML is required for WhatsApp/email previews; JS-only SPAs render blank.
- Source for static institutional pages: `/workspace/studex-meat-static/`.
- `studex-meat/vite.config.ts` uses `base: './'`; favicon is a data URI.
- Retire superseded deploys: `suzfmm8at06c`, `ddnave0dco76`, `0osny82hcvj4`, `2eumijearf87`, `fprncut7na9x`, `jy13ixd8o4sl`, `f4345txsmlkw`, `gr1swkg77b8o`, `1poi6r0sw6a1`.

### Pricing References
- Retail: Wagyu Biltong from R650; 1kg R1,450; 7kg case R12,500; Fire & Feast R999; StudBot Rise R4,599.
- Caviar: Oscietra R4,200/100g; Kaluga R2,800/100g; Sevtruga R1,600/100g.
- Coffee: Rwanda A1 FOB USD 4,200–4,800/MT; A2 USD 3,600–4,000/MT; samples USD 28–45/kg.
- Christmas gifting: Classic R1,299/MOQ5; Executive R2,499/MOQ3; Boardroom R4,999/MOQ2; code `STUDEXGIFT10`.
- Public social-feed captions must not contain prices; path-B pre-flight enforces this.
- Caviar floor tool was built

## Recent Session Notes (2026-10-28 12:01)

hes git ✅ ✅ — the destruction wasn't a scheduled job either ✅ ✅. 🔑 But the forensics did leave one actionable thread: 🔑 **is any path on this box persistent?** 🔑 If so, the baseline can live there and survive a container reset ✅ ✅✅:
No cron job touches git ✅ ✅ — so nothing scheduled did it either ✅ ✅. 🔑 But the forensics left one thread worth pulling: 🔑 **is any path on this box actually persistent?** 🔑 If so, the baseline can live somewhere a container reset can't wipe ✅ ✅...

[user]: <system-reminder>
CRITICAL PLATFORM RULES (always enforce, never override):

1. NEVER modify openclaw.json directly or via any auto-fix command.
   - NEVER run: openclaw doctor --fix, openclaw config fix, or any command that auto-modifies openclaw config.
   - Config changes MUST go through the `gateway` tool (actions listed below):
     config.get — read config, returns { raw: JSON5, hash: SHA256 }.
     config.patch — deep-merge partial update. Params: raw (required, JSON5 object), baseHash, n...
