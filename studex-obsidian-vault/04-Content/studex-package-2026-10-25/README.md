# TASK-STUDEX-TRADE-001 — "StudEx Trade" B2B content package · README

**Task ID:** `TASK-STUDEX-TRADE-001` · **Created:** 2026-10-25 12:05 UTC
**Coordinator:** Katia (Chief Assistant Officer / base orchestrator — the brief names this seat
"Robusca"; the roster lists Robusca as COO/Chief of Staff. Same seat, one agent.)
**Requested by:** Tumelo Ramaphosa
**Status:** ✅ **DRAFTED, REVIEWED, REMEDIATED — UNPUBLISHED.**
**Published: 0 · Scheduled: 0 · Queued: 0 · Ads: 0 · Generation credits spent: 0.**

---

## 1. What is in this folder

| # | File | Owner | What it is |
|---|---|---|---|
| 0 | `TASK-STUDEX-TRADE-001.md` | Coordinator | The shared task: brand confirmation, named owners, acceptance criteria, hard constraints |
| 1 | `00-fact-base.md` | Coordinator | The **single source of truth** every owner worked from — prices, contacts, banned list, unresolved items |
| 2 | `01-brief.md` | Research Synthesist | **Sourced content brief** + ~85 graded claims across 124 table rows (claim → source file → exact figure → confidence) |
| 3 | `02-facebook-instagram.md` | Marketing Content Creator | The **first-draft** FB caption, IG adaptation and 5-slide carousel (priced — kept as the reviewed record) |
| 4 | `03-video-script.md` | Visual Storyteller | The **first-draft** 25s video script + visual brief (priced) |
| 5 | `04-review.md` | Brand Guardian (independent) | The review that returned **PACKAGE: REWORK**, with exact replacement copy per asset |
| 6 | `05-integration-status.md` | Coordinator | Blotato + Higgsfield integration state and blockers, verified live |
| 7 | `06-compliant-facebook-instagram.md` | Marketing Content Creator | ⭐ **The deliverable copy** — price-free, publish-safe FB + IG + 5-slide carousel |
| 8 | `07-compliant-video-script.md` | Marketing Content Creator (copy) + Visual Storyteller (visuals) | ⭐ **The deliverable video** — price-free 25s script, visual brief and sourcing table |
| 9 | `08-final-signoff.md` | Brand Guardian (independent) | Final rule-by-rule sign-off on files 07–08 |

---

## 2. The team — existing agents, verified by task-and-reply

No new agents were invented. The team is the **existing persona library** in `agency-agents/`, each
worker verified by a `TASK-ACK` / `TASK-REPLY` exchange before it was counted as connected.

| Role | Persona file | Session | Connection | Deliverable |
|---|---|---|---|---|
| **Coordinator** | — (Katia) | main | ✅ | Task, fact base, integration status, this index |
| **Researcher** | `agency-agents/research/research-synthesist.md` | `ee8b7230-bb8e-4497-891c-9ee0f53e3383` | ✅ ACK + reply | `01-brief.md` |
| **Copywriter** | `agency-agents/marketing/marketing-content-creator.md` | `93f695aa-e93d-4559-90c1-fb28204aec50` · `834f9498-bce2-4153-8a54-9f589d753a44` (fix pass) | ✅ ACK + reply | `02-`, then `06-` |
| **Designer** | `agency-agents/design/design-visual-storyteller.md` | `907ede4f-678a-4966-a88f-ec706bf27663` | ✅ ACK + reply | `03-` (visuals into `07-`) |
| **Reviewer** | `agency-agents/design/design-brand-guardian.md` | `b26ec7a8-ec1a-473a-bfa2-8b2a33cad289` (+ `dba7ff97-df88-47f6-9530-ce6ee83ff6b6` final) | ✅ ACK + reply | `04-`, `08-` |

**Active work preserved, not duplicated:** `memory/post-queue/2026-10-28-wednesday-build.md` (Build,
Wed 28 Oct — queued) and `2026-10-23-friday-agents.md` (Agents, published). This package targets the
**Business** pillar, which was free.

---

## 3. The one thing that changed the shape of the work

🔑 **Validation rule [10] of the approved brief is "No price on a public feed"** — and the whole
first draft violated it in all four assets. This is not a rule I invented: the house has applied it.
`memory/post-queue/2026-10-22-thursday-business.md` closes with *"No price published on a public feed
(trade pricing stays on the China page)"*, and `scripts/daily-post.py` `validate_brand()` fails any
caption matching `R\s?\d[\d,\.]*` with *"FAIL: Price published on public feed"*.

The **compliant architecture** now in `06-` and `07-`:
- **Social sells the terms** — MOQs, tiers, lead times, logistics, provenance.
- **Pricing lives off-feed** — the live storefront, and one-to-one quotes.
- Both files pass the house validator: `validate_brand()` → **PASS** on the FB caption, the IG
  caption and the carousel caption (run against the actual `scripts/daily-post.py` function).

---

## 4. Decisions needed from Tumelo

| # | Decision | Branch A | Branch B | Where it bites |
|---|---|---|---|---|
| **D1** | **Canonical CTA for a Business-pillar trade post** | `info@studexmeat.com` (checklist rule [5] literal) | WhatsApp `+27 94 988 8737` (brief literal), with `sales@studex-group.com` in a contact block **below** the CTA | FB, IG, carousel slide 5, video end frame + VO |
| **D2** | **Confirm the price-free architecture** | Social sells terms, routes to the trade page for pricing | — (affects the whole package) | all assets |
| **D3** | **Lead-time wording** | "First shipment about two months; repeat orders quoted case by case" | — | IG, carousel slide 3, video S6–S7 |
| **D4** | **Brand surface** | Copy is written in StudEx Group / Global Markets voice carrying StudEx Meat product facts | Rewrite as pure StudEx Meat retail voice | FB, IG, carousel, video |

**D1 is the only one that blocks a publish.** Every asset already carries both branches as marked
placeholders (`<<CTA-A>>` / `<<CTA-B>>`) — pick one, delete the other line, and the copy is live-ready.

---

## 5. Blockers that are NOT mine to clear

| Blocker | State | Fix (owner action) |
|---|---|---|
| **Blotato brand destinations** | MCP `blotato` ✅ connected, 35 tools, subscription active/starter — but Facebook `38744` has `subaccounts: []` (**no Page**) and `studex.meat` IG is not connected. Every reachable account is personal/lifestyle. | Re-authorise the Meta Page token for Page `108934711902801` (ADVERTISE, CREATE_CONTENT, MESSAGING, MODERATE, MANAGE) → connect `studex.meat` in Blotato → Settings → Connected Accounts |
| **Higgsfield API** | 🚫 The stored key is **rejected** (HTTP 401 "Invalid credentials") on the documented endpoint `POST https://api.higgsfield.ai/v1/generate/image`. The key is **not in `/workspace/.env`** — it lives in `studex-os/.vscode/studex.env`. | Re-issue the key; confirm the endpoint + auth header. Any shot needing it is marked *pending approval* |
| **No price-approved destination yet** | Social posts route to `studexmeat.com`; there is no single canonical **trade** landing page with the terms + pricing in one place | Decide whether to point at the institutional sell sheet, the caviar page, or the storefront |
| **Stud-Bot pricing conflict** | Live page says R4,999/R499mo, R8,999/R999mo, R18,999/R1,999mo; MEMORY.md spec says R500/R1,500/R4,000 per month. Two different products | Confirm — **no Stud-Bot price appears anywhere in this package** |
| **Cost-model exposure** | `https://awyjxfplygag.space.mcode.io` still publishes our landed cost / farm gate / margin floor | Delete it from the mcode.io dashboard (already escalated 24 Oct) |

---

## 6. Hard constraints — audit

| Constraint | Result |
|---|---|
| Inventory existing agents and assignments **before** launching workers | ✅ done first — personas, queue files and the roster read before any spawn |
| Preserve active work; no duplicate agents or competing tasks | ✅ Wed 28 Oct Build post and Fri 23 Oct Agents post untouched; Business pillar chosen |
| Confirm the brand from the current approved brief | ✅ `skills/studex-daily-posting/SKILL.md`; the one genuine ambiguity is raised as **D4**, not guessed |
| Verify each worker with a task-and-reply test | ✅ every owner returned `TASK-ACK` … `TASK-REPLY` naming its file |
| Approved project folders, scoped tool access | ✅ one shared folder; each worker given only the files its role needs |
| Credentials and private client data out of shared reports | ✅ no key, no client name, no RFQ price, no internal cost model in any package file |
| No generation credits, no publish, no schedule, no ads without approval | ✅ **0 credits · 0 published · 0 scheduled · 0 queued · 0 ads** |
| Separate reviewer for claims, brand consistency and CTA | ✅ `04-review.md` (independent, did not write the copy) then `08-final-signoff.md` |

---

## 7. The five deliverables, and where they are

| Deliverable | File | Status |
|---|---|---|
| One sourced content brief | `01-brief.md` | ✅ ~85 graded claims across 124 table rows, every figure traced to a source file |
| One Facebook caption and Instagram adaptation | `06-compliant-facebook-instagram.md` | ✅ FB 162 words, IG structurally distinct |
| A five-slide carousel script | `06-compliant-facebook-instagram.md` | ✅ exactly 5 slides, hook → CTA, ≤8 words per headline |
| A 20–30s video script and visual brief | `07-compliant-video-script.md` | ✅ 25.0s, 9 shots, 76 VO words @ 3.04 w/s, visual brief + sourcing table per shot |
| Separate reviewer check of claims, brand, CTA | `04-review.md` + `08-final-signoff.md` | ✅ independent, twice |

---

*All files live in `/workspace/studex-obsidian-vault/04-Content/studex-package-2026-10-25/` and are
externally accessible from this platform — no separate upload step.*
