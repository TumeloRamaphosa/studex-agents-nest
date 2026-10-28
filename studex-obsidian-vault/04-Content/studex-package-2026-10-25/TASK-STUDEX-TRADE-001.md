# TASK-STUDEX-TRADE-001 — "StudEx Trade" B2B content package

**Task ID:** `TASK-STUDEX-TRADE-001`
**Created:** 2026-10-25 12:05 UTC
**Coordinator:** Katia (Chief Assistant Officer / base orchestrator — the brief names this role
"Robusca"; the roster lists Robusca as COO/Chief of Staff. Same seat, one agent.)
**Requested by:** Tumelo Ramaphosa
**Status:** IN PROGRESS — drafting only. **Nothing may be published, scheduled, or advertised.**

---

## 1. Brand (confirmed from the current approved brief)

**Approved brief:** `/workspace/skills/studex-daily-posting/SKILL.md` (source of truth for content
production) + the live post queue in `/workspace/memory/post-queue/`.

**Brand = StudEx Group / Global Markets content line**, carrying StudEx Meat products.
- Palette: Emerald `#0B4F3C` + Gold `#C9A84C` + Circuit Black `#0A0A0A`
- Tagline: "Technology. Capital. Opportunity."
- Pillars: Knowledge · Africa · Build · Business · Agents
- CTA inbox: `info@studexmeat.com`
- Voice: confident, visionary, culturally rooted, authentic — never discount-led, never generic
- Language: British/South African English, plain and concrete

⚠️ **Open decision for Tumelo (does not block drafting):** the live Facebook Page is
**"Studex Meat"** (`108934711902801`) while the content line is StudEx Group / StudBot. Which
page the copy is written *for* is a publishing decision, not a drafting decision. Drafting assumes
StudEx Group voice, StudEx Meat product facts.

---

## 2. Campaign topic (chosen to avoid duplicating queued work)

**Existing active work — PRESERVED, not duplicated:**
- `memory/post-queue/2026-10-28-wednesday-build.md` — Build pillar, Wed 28 Oct (queued)
- `memory/post-queue/2026-10-23-friday-agents.md` — Agents pillar (published 23 Oct)

**This package therefore targets a pillar and audience that is NOT in the queue:**
**Business pillar · B2B trade · "StudEx Trade"** — what it actually costs a hospitality buyer to
stock StudEx biltong, caviar and green coffee. This is the live revenue line (every canonical
trade page points here) and every number is owned by a single registry file.

---

## 3. Named owners + acceptance criteria

| # | Owner (existing agent persona) | Deliverable | Acceptance criteria | Writes to |
|---|---|---|---|---|
| 1 | **Research Synthesist** — `agency-agents/research/research-synthesist.md` | Sourced content brief + fact sheet | Every price/claim carries a source file + line; **no number that is not in `studex-meat/PRICE-SOURCE-REGISTRY.md`**; retired names ("Sevruga Premium", "Siberian Reserve", "per 250g") banned; a claims table listing every assertion → its source | `01-brief.md` |
| 2 | **Marketing Content Creator** — `agency-agents/marketing/marketing-content-creator.md` | Facebook caption + Instagram adaptation + 5-slide carousel script | One FB caption (≤1,200 chars, conversational, one CTA, no emoji spam); one IG adaptation (different hook + shorter, IG-native, 3–5 hashtags, no FB CTA link); carousel = exactly 5 slides, one idea per slide, slide 1 hook, slide 5 CTA; **no invented price, no invented award, no invented customer quote** | `02-facebook-instagram.md` |
| 3 | **Visual Storyteller** — `agency-agents/design/design-visual-storyteller.md` | 20–30s video script + visual brief | Script timed to 20–30s (≈75 words spoken), shot-by-shot with timecodes, VO lines, on-screen text, and a visual brief (setting, subject, lighting, palette, props, shot size) per shot; brand-consistent; no product shown that isn't in the fact sheet | `03-video-script.md` |
| 4 | **Brand Guardian** — `agency-agents/design/design-brand-guardian.md` (independent, runs last, does not write the copy) | Reviewer report | Checks every claim against the fact sheet, checks brand voice + palette + pillar, checks the CTA is a verified contact and a single clear ask, checks no banned retired content; outputs **PASS / FIX LIST** per asset with line-level findings | `04-review.md` |
| — | **Katia (coordinator)** | Task file, fact base, final assembly, links | All 5 files present, all acceptance criteria met or explicitly marked NOT MET with reason; no publish/schedule action taken | `README.md` (this package) |

**Verification rule (binding on all owners):** each owner must begin its reply with a
`TASK-ACK` line naming its task ID, its role and the file it wrote, and end with `TASK-REPLY`.
An owner that does not acknowledge in this format is **not connected** and will be re-run.

---

## 4. Hard constraints (bind every owner)

1. **Never publish, schedule, queue to Blotato, or run an ad.** Drafting only.
2. **No generation credits spent.** No Higgsfield image/video generation, no paid image API.
3. **Every price comes from** `studex-meat/PRICE-SOURCE-REGISTRY.md`. If a number is not in it, it
   does not appear in the copy.
4. **Only verified contacts:** `info@studexmeat.com` · `+27 84 421 6035` · WhatsApp/store
   `+27 94 988 8737`. **Never** `agent.studexmeat.com` (no DNS — enquiries are lost there).
5. **No client-private data, no buyer names, no RFQ pricing, no internal cost model** (landed cost,
   farm gate, margin floor, duty/VAT/FX assumptions) in any asset.
6. **No credentials or API keys** in any file written by this task.
7. British/South African English. No "you're going to love it". No generic AI phrasing.

---

## 5. Shared folder (approved)

`/workspace/studex-obsidian-vault/04-Content/studex-package-2026-10-25/`
(workspace files on this platform are externally accessible — no separate upload step required)

| File | Owner |
|---|---|
| `TASK-STUDEX-TRADE-001.md` | coordinator |
| `00-fact-base.md` | coordinator (source extract for all owners) |
| `01-brief.md` | Research Synthesist |
| `02-facebook-instagram.md` | Marketing Content Creator |
| `03-video-script.md` | Visual Storyteller |
| `04-review.md` | Brand Guardian |
| `README.md` | coordinator (final index + decisions needed) |
