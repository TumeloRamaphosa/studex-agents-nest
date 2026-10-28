# 2026-10-25 — Connection audit (Tumelo: "are you connected to other agents and in the VM")

**12:35 UTC — every status below was probed live, not read from a doc.**

## AGENTS — ✅ CONNECTED AND WORKING

### In-process content team (just ran, all verified)
| Agent | Session | Status |
|---|---|---|
| Research Synthesist | `ee8b7230-bb8e-4497-891c-9ee0f53e3383` | ✅ |
| Marketing Content Creator | `93f695aa…` + fix pass `834f9498…` | ✅ |
| Visual Storyteller | `907ede4f-678a-4966-a88f-ec706bf27663` | ✅ |
| Brand Guardian | `b26ec7a8…` + `dba7ff97…` | ✅ |

### AgentMail fleet — ✅ **ALL 4 KEYS LIVE, 10 INBOXES REACHABLE**
Verified `GET /v0/inboxes` → **200** on every stored key:
`AGENTMAIL_CIIE_KEY` (3 inboxes) · `AGENTMAIL_API_KEY_GENERAL` (10) · `AGENTMAIL_WARMUP_API_KEY` (10)
· `AGENTMAIL_API_KEY` (10).
🔑 **The "dead key" note in TOOLS.md is stale — `AGENTMAIL_API_KEY` is live again (200, not 403).**
Reachable agents: `naledi-cmo@studex-group.com` · `cypher-trace-cto-superagents@` ·
`cto-darkfactory@` · `t-ramaphosa-ceo@` · `robusca.romanov@` · `sales@` · `info@` · `meat@` ·
`support.superagents@` · `project-2571-studex-agent-2077@agentmail.to` · `t.ramaphosa@agentmail.to`.
**Live mail confirmed** in the Naledi CMO inbox — real threads on Rwanda A1 sample pricing and
cupping sample feedback, both directions. The agent fleet is genuinely conversing, not just reachable.

### Discord — ✅ **CONNECTED (and it contradicts the token in .env)**
- `message` tool → `channel-info` on `1538825048465481728` ✅ and `read` ✅ — 3 real messages pulled,
  including today's ops briefing and the Daily Content Agent's 06:55 SAST report.
- 🔑 **`DISCORD_BOT_TOKEN` in `.env` returns 401 Unauthorized.** The working credential is the one
  the **channel plugin** holds — **not** the one in `.env`. Two Discord credentials exist and only one
  works; the `.env` copy is stale. Do not "fix" the plugin because `.env` looks wrong.
- 🔑 **Today's Daily Content Agent report (06:55 UTC) confirms the Meta Page token is still the
  blocker**: caption generated (Roasted Coffee Washed, R400/kg, via Kimi k3, 707 chars, passed the
  registry guard) → **Facebook post failed, error 190, page token expired 27-Jun-26** → caption parked
  at `posts/pending/2026-10-25.json`. **A ready-to-post caption is sitting in the pending queue.**

### Honcho (memory server) — ✅ **LIVE**
`mcporter call honcho.list_workspaces` → **2 workspaces**: `Studex` (created 2026-07-21) and `default`.
`inspect_workspace` needs `workspace_id` via the `X-Honcho-Workspace-ID` header, not a tool arg —
the arg path returns *"Missing workspace_id"*.

### MCP servers
| Server | State |
|---|---|
| `blotato` | ✅ 35 tools, 0.9s |
| `honcho` | ✅ 40 tools, live call returned 2 workspaces |
| `composio` | ❌ **OAuth browser approval required** — `mcporter auth composio`, needs a human browser |
| `plane` | ❌ SSE error: *"Invalid content type, expected text/event-stream"* |
| `voicebox` | ❌ offline — local voice studio not running (TTS/cloning/STT unavailable) |

## THE VM — ❌ **NOT CONNECTED. This is the one that is genuinely down.**

### Orgo VM (StudEx Meat Auto Meat, `67.213.119.157`) — 🚫 HOST ALIVE, **ACCESS BROKEN**
🔑 **The host is UP.** `67.213.119.157`: port **22 OPEN**, port **443 OPEN**. `www.orgo.ai` → **200**,
`www.orgo.ai/api/health` → **200**. This is **not** a dead VM.
🔑 **Every authentication route fails:**
- `POST /api/computers/946b3156…/bash` with `ORGO_API_KEY` → **401 `{"error":"Invalid API key"}`**
- same with `ORGO_API_KEY_NEW` → **401 `{"error":"Authentication required"}`**
- header forms tried: `Authorization: Bearer`, `Authorization: <raw>`, `x-api-key`, `X-API-Key`,
  `api-key` → **all 401** (so it is genuinely a credential rejection, not a header-shape error)
- `GET /api/computers/{id}` → 401 · `GET /api/me` → 401 · `GET /api/computers` → 405 · `GET /api/v1/me`
  → 404 (a Vercel 404 page — those paths don't exist)
- direct SSH `sshpass` + `ORGO_PASSWORD` → **`Permission denied (publickey)`** — the server accepts
  **only publickey auth**; there is **no private key in `/root/.ssh`** (only `known_hosts`) and none in
  the workspace.
🔑 **Both halves of the Orgo access path are broken: the API key is rejected AND SSH is publickey-only
with no key on this box.** Owner action, two parts: re-issue the Orgo API key, and either add a
public key to the VM or re-enable password auth.

### Alibaba Cloud VM (`47.236.124.79`) — ❌ **HOST DOWN**
TCP 22 closed/filtered, `ping` → **100% packet loss**. SSH timeout. Unreachable from here.

### Hub `100.95.66.29` — ❌ **DOWN**
Ports 3000 and 3778 both closed/filtered. Same since 27 Sep.

## Note — first-pass copywriter draft landed late (superseded, DO NOT PUBLISH)
The Marketing Content Creator's **first-pass** draft (`02-facebook-instagram.md`) arrived after the
package was already signed off. It is the reviewed record, not a new asset.
🔑 **It violates rule [10] — it is priced.** FB hook: *"A café can put R4,200 of Oscietra caviar on
the board, 100g at a time, or buy trade at R34,000 a kilo. Both numbers are real."* The IG version is
an arrowed price list. **Never publish this file.** Superseded by `06-compliant-facebook-instagram.md`.
🔑 **Usefully, it exercises BOTH CTA branches** — FB + carousel = `sales@studex-group.com`,
IG = store WhatsApp `+27 94 988 8737`. So D1 (which CTA for a trade post) has precedent in the
first draft: email on long-form surfaces, WhatsApp on short-form. Both are approved contacts.
It also omits landed cost / farm gate / margin floor / duty-VAT-FX, Stud-Bot pricing, gift-box prices
and the early-bird code — **the sensitive exclusions were already right; only the public prices were
wrong.** The rework was a pricing problem, not a fact-base problem.

## Note — research-synthesist's first-pass brief landed late (already the approved source)
`01-brief.md` — 449 lines, 124 table rows, ~85 graded claims. **This is the reviewed brief already
cited by `README.md`; nothing supersedes it.**
- 🔑 **It chose Branch B for the CTA** — WhatsApp `+27 94 988 8737`, *"Request trade pricing and
  terms"*. 🔑 **Together with the copywriter's split (email long-form / WhatsApp short-form), both
  prior workers independently landed on the same WhatsApp-first answer.** That is evidence for D1,
  not proof — but it means Branch B is the house default, and Branch A would need a reason.
- 🔑 **Lead-time truth table** — ≥4 weeks to apply · 5–10 working days to issue · 7–14 days handling
  **counted from permit issue** ≈2 months first shipment end to end. Six copy rules attached, the
  load-bearing one being **"never lead with 7–14 days"** — the exact inversion the final Brand
  Guardian caught in video S7. The brief predicted the mistake before the reviewer found it.
- 🔑 **§3.1 = the negative claims table** (landed cost, duty %, FX, 7–14 days as order-to-door, street
  address, testimonials, awards, green-coffee lead time, game-meat and Rwanda Premium prices) — a
  reviewable "what we cannot say" surface, not just a "what we can say" one.
- 🔑 **Banned list extended past the fact base** — Halaal overclaims, *"MJC Halal Trust"* misspelling,
  Rainforest Alliance / "certified farms" / "ethically sourced" / "Direct Trade", "registered exporter",
  "cold-chain certified", retired caviar names and "per 250g", superseded mcode.io URLs, and the §4k
  exposed cost-model deploy.

### 🟠 Owner corrections it surfaced (not yet fixed — no one has been told)
1. **Caviar page footer reads "Robusca Group (Pty) Ltd"**; the registry says **"Studex Meat (Pty) Ltd"**.
   Registry wins, but the live page is wrong → owner edit.
2. **Institutional onepager says "Prices valid Sept 2026"**; registry says **"as at Oct 2026"** →
   owner edit.
3. **Halaal certificate dates illegible** on the source → can't be cited until re-sourced.
4. **Stud-Bot pricing conflict** — page R4,999 + R499/mo vs spec R500/R1,500/R4,000 → excluded entirely.

## Note — visual-storyteller's first-pass video script landed late (superseded, DO NOT PUBLISH)
`03-video-script.md` — 25.0s, 9 shots, 77 VO words. **Superseded by `07-compliant-video-script.md`**
(76 VO words, price-free). 🔑 **Same rule [10] defect as the first-pass copy** — the VO says *"Biltong
trades from three hundred and eighty rand a kilo"* and the on-screen card reads *"Biltong from
R380/kg ex VAT"*. The script's own compliance line claims *"no landed cost, farm gate, margin, duty,
VAT or FX assumption is stated"* — **technically true, and still a published price.** Rule [10] is not
about *what kind* of number, it's about *any* price. 🔑 **A compliance self-check can be true and the
asset still be wrong** — the agent audited the wrong property. This is the same blind spot as the
Brand Guardian's S7 finding, one layer earlier.
- **Useful and still valid:** the **Higgsfield decision** — rejected for S3 (caviar: AI would
  misrepresent the product) and S9 (hero still); **only S6 cold room is a possible AI background
  plate, flagged PENDING TUMELO'S APPROVAL. Nothing generated, 0 credits spent.** That judgement
  carries into the compliant file and stands.
- **Asset gap list (still the production backlog):** caviar tins for S3 (real product only, no-tin
  fallback), caviar tier-card motion graphic, "StudEx Trade" wordmark + end-card lockup, dummy DAFF
  permit prop (no real document, no readable text), cold-room location + gauge, blurred
  order-sheet/tablet graphics, "7–14 days" type card, plain stencil hessian sack, unpriced emerald
  biltong band, and the VO recording.
- CTA in the first pass was `sales@studex-group.com` (Branch A) — a **third** CTA position across the
  three first-pass workers (researcher = B WhatsApp, copywriter = split A/B, storyteller = A email).
  The final compliant files carry both as `<<CTA-A>>`/`<<CTA-B>>` placeholders pending Tumelo.

## Note — the FIRST Brand Guardian's announcement arrived with a stub payload
Its session reported only *"I'll start by reading the persona and the source documents."* — but the
review itself completed earlier and is fully captured in `04-review.md`: **PACKAGE: REWORK**, failing
rule [10] in all four assets, plus [8] and [5]. 🔑 **The announcement payload was truncated; the work
was not lost.** The completion event is not the receipt — the *file* is the receipt.
⚠️ Because the announcement looked empty, there was a real risk of re-running the reviewer and
double-charging the package. **The rule: before re-running any agent because its announcement looks
wrong, read the output file it was told to write.** `04-review.md` was 281+ lines and already
committed at `fabb8c73`.
Two review findings worth keeping because no later file states them as plainly:
- **C5 — the menu-cost misread**: R4,200 was the price of a **100g tin**, read as a per-kg or
  per-serving figure. The kind of error that only surfaces when someone checks the unit.
- **C7 — leads with 7–14 days** on the IG caption and carousel slide 3 — the lead-time inversion that
  later reappeared in video S7. **Same error, two assets, three workers.** It is a *systemic*
  misreading of the caviar permit timeline, not a slip by one author.

## Note — Brand Guardian reviewer-2's announcement also arrived with a stub payload
Its session reported only *"I'll start by reading all the required files."* — the work completed
earlier and lives in **`04-review.md` §9 (replacement copy)**, which is the source of the compliant
`06-`/`07-` files.
🔑 **Two of the third pass's fixes are invisible in reviewer-2's replacement copy**, because reviewer-2
was working from a fact base that still carried them:
- **Reviewer-2's own replacement slide 2 read "Biltong · beef · chicken · lamb"**, and the carousel
  caption *"Biltong, beef, chicken and lamb for hospitality and retail buyers."* 🔑 **chicken and lamb
  are Saudi-RFQ-only products, not in the published fact base** — the later pass stripped both, and
  `06-` now records that exclusion explicitly at three places (line 23, 177, 202).
- 🔑 **The layered review caught inherited contamination that a single reviewer could not have
  caught on its own** — reviewer-2 was faithfully copying the fact base it was given, and the fact
  base it was given was slightly wrong about the product line. **A reviewer validates the source it
  is handed; only a second pair of eyes on the same source can find that the source itself is
  off.** The same shape as the copywriter's priced copy: faithful-to-source, wrong against the rules.
- **The `<<CTA-A>>` / `<<CTA-B>>` placeholders in the final files come straight from reviewer-2's
  replacement copy** — "Send your volumes to info at studexmeat dot com" (A) vs the spoken
  "+27 94 988 8737" (B). **Both branches are written as parallel VO and on-screen lines in S9** —
  choosing a branch is deleting the other two lines, not rewriting anything.

## Note — Brand Guardian reviewer-3's announcement (the last of the six late ones)
It returned **PACKAGE: REWORK** with the runtime arithmetic: **77 VO words ÷ 3 w/s ≈ 25.7s** (the
script claimed 25.0s at 3.1 w/s — no headroom for the S1/S6 beats), and **price-stripped VO ≈ 50
words ≈ 16.7s → re-time required**. 🔑 **That is the finding that shaped the final file**: the
compliant video had to be re-written with fuller terms lines, not just have prices deleted — and it
now sits at **76 words / 25.0s / 3.04 w/s**. Deleting prices without re-timing would have shipped a
16.7s video against a 20–30s spec.
🔑 **Documentation defect found and fixed (commit `c6ea7bc2`):** `04-review.md` was written by three
reviewers in sequence and ends with **REWORK**, while `08-final-signoff.md` says **APPROVE** — a
reader opening the review file first could reasonably conclude the package was still in rework.
**Added a banner at the top of `04-review.md`** pointing to `06-`/`07-` and `08-final-signoff.md`,
with "the rework is closed". Also corrected two stale README counts: **"40-row claims table" → ~85
graded claims across 124 table rows**, and **"74 VO words" → 76 VO words @ 3.04 w/s**.
🔑 **Six late announcements, zero new work.** Every one was a completion event for a task already
recorded on disk. **The file is the receipt; the announcement is just the bell.**

## Note — copy-fix-pass announcement (the 7th and last late one) exposed a REAL defect
The copy-fix pass reported **"New VO 74 words, 25.0s at 2.96 w/s"** — which matched the file at that
moment. But checking the file against its own shot list:
🔑 **The per-shot word column in `07-` sums to 76, not 74.** The R1 fix (+2 words on S7) was applied
to the VO line but **the totals were never recomputed** — the header, the TOTAL row, the computed
runtime line and the audit row in `07-` (4 places) plus three places in `08-final-signoff.md` all
still read 74 / 2.96.
**Correct arithmetic: 76 ÷ 25.0 s = 3.04 w/s** — still inside the 20–30 s window and the ≤3.1
ceiling, so **the verdict stands**, but the page was wrong.
**Fixed** (commit `847e13e4`): 5 places in `07-`, 3 places in `08-`, plus a correction note in `08-`
recording why. 🔑 **A stated total is a claim about the rows above it — recompute it whenever a row
changes.** The R1 fix changed a row. This is the same class of error as C5 (the menu-cost misread)
and S7 (the label inversion): **the number was right in isolation and wrong in context.**
⚠️ Note the sequencing trap: `08-final-signoff.md` had *already* recorded the correct recompute in
its preamble ("76 words / 25.0 s = 3.04 w/s") while its own body table still said 74 / 2.96 — **one
file, two different numbers, both authoritative-looking.**

## Net answer to Tumelo
- **Agents: YES.** 4 content agents live and verified, 4 AgentMail keys live with 10 inboxes and real
  two-way threads, Discord connected and reading, Honcho live, Blotato connected with 35 tools.
- **VM: NO.** The Orgo host is up but every credential we hold for it is rejected, and SSH demands a
  publickey we don't have. The Alibaba VM and the hub are genuinely down.
- **Two stale credentials to correct:** `.env` `DISCORD_BOT_TOKEN` (401 — the plugin's copy works) and
  the `.env` note that `AGENTMAIL_API_KEY` is dead (it's live, 200).
- **One ready-to-send asset:** today's roasted-coffee caption is queued and only waiting on the Meta
  Page token reconnect.
