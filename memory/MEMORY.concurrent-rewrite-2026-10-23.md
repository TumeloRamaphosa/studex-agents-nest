# MEMORY.md — Katia's Long-Term Memory

## Primary Mission
- **Every day:** find ways to make money using underutilised resources and AI agents.
- All research, content, sales, and infrastructure work should serve this mission.
- Review progress and report daily.

## Identity & Operating Rules
- Name: **Katia** — not Robusca.
- Role: Chief Assistant Officer (CAO), Head of Customer Sales, Base Orchestrator.
- Handler for Tumelo StudEx (“The Agent Lord”; “Katja” in Base44 systems).
- Platform: OpenClaw / MaxClaw on MaxClaw-7jggs.
- **Never modify `openclaw.json` directly or run auto-fix commands** such as `openclaw doctor --fix` or `openclaw config fix`.
- Configuration changes must use the `gateway` tool: `config.get` followed by `config.patch` with `raw` and `baseHash`.
- If blocked by permissions, do not modify other config files as a workaround; inform Tumelo and ask how to proceed.
- Discord chat exec approvals are unavailable; `approval-timeout` means the command never ran. Use read-only tools where possible rather than repeatedly retrying exec.

## Active Projects

### Rwanda Mission — Delayed
- Original trip has not occurred; awaiting a new departure date from Tumelo.
- CIIE coffee landing page is live: `y0r9ilfj96mj.space.mcode.io`.

### Studex Global Markets
- Brand: Michelangelo-style creation of Adam + Gucci influence + circuit-board bull globe.
- Palette: Emerald `#0B4F3C`, Gold `#C9A84C`, Circuit Black.
- Products: biltong, Rwanda coffee, caviar, and Mouse Bot/AI agents.
- Live store: `studexmeat.com`.
- `amboras.com` is the store-builder platform’s own site, **not** a Studex store.

### Canonical Live Sales Surfaces
| URL | Purpose |
|---|---|
| `hrji88f70666.space.mcode.io` | Studex Biltong retail store v4; Shopify-synced prices; orders route to WhatsApp |
| `j439h3l2g94g.space.mcode.io` | Studex Meat wholesale, white-label, creator and investor offer |
| `z7p9urw22jwb.space.mcode.io` | Institutional/corporate sales sheet for GCC buyers; use with Saudi/Jordan enquiries |
| `klre58fvhmdc.space.mcode.io` | Canonical Wildlife Coffee B2B green-coffee export page |
| `psq9xaisb9kf.space.mcode.io` | South African hospitality specialty-coffee trade page |
| `ess0ocgcd9f0.space.mcode.io` | Canonical Studex Caviar trade/hospitality page |
| `x2tvaieb5qgz.space.mcode.io` | Rwanda Premium Coffee export-to-China/CIIE asset |
| `oi28dhtke3yk.space.mcode.io` | Corporate Gifting Christmas 2026 |
| `3zryumjeuemk.space.mcode.io` | Studex Computer / Always-On Agent Machine |

- Retail prices were corrected against live Shopify: Wagyu Biltong from R650, 1kg R1,450, 7kg case R12,500, Fire & Feast R999, StudBot Rise R4,599.
- Caviar listed prices: Oscietra R4,200/100g, Kaluga R2,800/100g, Sevtruga R1,600/100g.
- Coffee pricing: Rwanda A1 FOB USD 4,200–4,800/MT; A2 USD 3,600–4,000/MT; samples USD 28–45/kg.
- Christmas gifting tiers: Classic R1,299/MOQ5, Executive R2,499/MOQ3, Boardroom R4,999/MOQ2; code `STUDEXGIFT10`.
- Static HTML is required for WhatsApp/email previews; JavaScript-only SPA shells render blank in link previews.
- Superseded/retire: `suzfmm8at06c`, `ddnave0dco76`, `0osny82hcvj4`, `2eumijearf87`, `fprncut7na9x`, `jy13ixd8o4sl`, `f4345txsmlkw`, `gr1swkg77b8o`, `1poi6r0sw6a1`.
- Source for static institutional page: `/workspace/studex-meat-static/`.
- Vite fix: `studex-meat/vite.config.ts` uses `base: './'`; favicon is now a data URI.
- **Always verify live storefront pricing before publishing any number.**

### Caviar Pricing-Floor Tool
- Research identified live caviar trade prices below the internally modelled margin floor.
- Pricing source/sheet was corrected; a floor-enforcement tool was built in the previously empty `caviar-trade-desk/` scaffold.
- The model/engine reproduced all three SKUs correctly during verification.
- **Pending:** confirm the corrected sheet and trade desk are deployed and visible on the live caviar surface.

### Email Warmup
- Five-email sequence exists at `/workspace/biltong-email-sequence.md`.
- On 2026-10-23, the campaign reached **5/5 emails for the day and 10 total**; the 17:00 UTC cycle correctly skipped because the daily limit was already reached.
- Emails were sent from `robusca.romanov@studex-group.com`.
- Separate Biltong sequence still