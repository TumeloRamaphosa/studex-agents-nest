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

## 🎯 PLAN FOR TODAY — 29 Oct 2026
**Owner's five minutes (each releases something):** Shopify Admin token for `57228b-3` (P1 — the
only revenue blind spot + the biltong ladder sync; the store still sells R450/R1,450/R12,500 with
the 19% case arbitrage live) · caviar sign-off + take `ess0ocgcd9f0` down (**Christmas window
closes 13–15 Nov**) · **one word and the 3 parked captions publish** (26/25/27 Oct, price-stripped)
· edit Threads `8633885` ("marble score 8+ to 11+", ONE post) · confirm the phone digits
`+27 94 988 8737` on 8 live pages · delete 4 public deploys (`awyjxfplygag` cost model,
`nudsduvyrc12`+`bkqn328wj5a6` old prices, `ess0ocgcd9f0` caviar) · GitHub PAT + rotate Blotato &
GoDaddy · reconnect Blotato fb `38744` + LinkedIn `26628` · coffee FOB re-base now or at CIIE (5 days).
**My build list:** make the canonical pass a **cron job** (today it was silent 3 h 45 m because it
only runs when a session is awake) · fix the vault-sync payload (drop the PAT-gated `git push`,
bound the turn's scope) · caption set ready for one-word release · build the caviar-free gifting
page but **do not deploy** before sign-off · propose `git gc`/prune (219 MiB loose objects).
**Money order:** see the money → stop selling below the site's own prices → capture Christmas before
15 Nov → turn reach into replies → take the cost model off the public internet.

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

### Christmas Gifting + Biltong Ladder — 2026-10-28
- **Deploy divergence (urgent):** `studex-corporate-gifting/src/App.tsx` defines Silver R3,000 / Gold R7,000 / Platinum R15,000 with **caviar in Gold ("50g Oscietra, CITES-certified") and Platinum ("100g Imperial Beluga")**. The **live page `oi28dhtke3yk` and `dist/` still show the older R1,299 / R2,499 / R4,999 (no caviar)**. The caviar source has **never been built or deployed**. Do not ship it as-is — the SA caviar permit stack (DFFE → ITAC → DAFF → SARS → CITES) is unassembled.
- **Price-ladder defects on studexmeat.com:** "Luxury Wagyu Biltong" 1kg R650 (R650/kg, well-placed) but **500g R450 = R900/kg — inverted**; "Wagyu Biltong Gold" 1kg box R1,450/kg and **7kg case R12,500 = R1,785/kg, but 7×1kg at list = R10,150 → 19% case arbitrage**. Highest visible SA biltong benchmark is Woolworths R1,053/kg (150g chilli snapsticks).
- SA market ladder 2026: Butcher Brothers R269.99/kg · Vanni Vrystaat R279.90/kg · Biltong Boytjies slabs R349.99–R449.99/kg · Mooiplaats Wagyu R600/kg · Woolworths sliced 400g R279.99 (R700/kg) · gift hampers R199.95–R720 · Angus Biltong owns the corporate-gifting keyword.
- Caviar is **not** in `studex-products-catalog.csv`. **Resolved 2026-10-28 22:00 SAST:** the live storefront catalogue has **30 products, 0 caviar → caviar is NOT purchasable on studexmeat.com.** But caviar IS still advertised with live retail+trade prices (R4,200/R2,800/R1,600 and R34,000/R22,000/R12,500) on the public caviar trade page `ess0ocgcd9f0.space.mcode.io` — that page has **no cart** (WhatsApp + mailto only), so it is lead-gen, not checkout. "Advertised ≠ purchasable" — but the trade page is public.
- **Festive close = 13–15 Nov 2026** (SA hamper window opened 29 Oct). Caviar-free biltong+coffee box is the 2026 product; caviar is 2027.

### Credential Fragments in the PUBLIC Remote — 2026-10-29 🔴 OPEN
- **Re-probed 2026-10-29 08:40 UTC against the published remote (3967 blobs across 4 pushed refs): the live set is 1 + 1, not 7.** **Blotato** (LIVE, 13+ files) and **GoDaddy** (LIVE — *not on the earlier list*: `fix_spf_exchange.py`, `godaddy_dns_setup.py`, `godaddy_final.py` + 1). **DEAD now:** AgentMail ×5, ClickUp (401 on `/user` *and* `/team`), Orgo, Cloudflare, ElevenLabs, GitHubPAT ×3. **Undeterminable:** Meta/Facebook ×4, FeedHive, Google, Perplexity. Posted to `#ops` (`1565284029555810445`).
- 🔑 **A rotation list is only worth the owner's time if it is re-probed, not carried.** "7 live" was true at 01:00 and wrong by 08:40: five had been revoked under us, and one live one was missing from the list. The working tree is masked (892 files / 50 credentials → CLEAN); the **published history is not un-published**.
- 🔑 **ROTATION is the fix and only Tumelo can rotate a credential.** Everything else is hygiene. Posted to `#ops` (`1565186632305606747`).
- The guard that should have caught it watched **ONE** key out of fifty (`ops/audit-blotato-fragments.py`) — **retired**. Use `ops/audit-credential-fragments.py` (all 50 × all tracked files) and `ops/mask-credential-fragments.py` (masks in place, preserves inode).
- 🔑 **A guard's SCOPE is part of its contract.** Watching one key while the repo holds fifty is a guard for a key nobody else has.
- 🔑 **A test fixture that holds a live credential is a leak**, even when it is labelled "synthetic" — my own two new fixtures did exactly that and the pre-commit guard caught it.
- 🔑 **`classify()` must test MASK before LENGTH** — `TOO-SHORT` is a class `require()` ALLOWS, so a 12-asterisk mask was being handed to callers as a live key.

### Cron Runs Are Losing Their Memory Write — 2026-10-29
- **Two cron jobs did their work and were still marked `error`** because the agent's trailing sidecar memory-write failed: `ceo-standup-2200` (28 Oct 22:00 SAST → `📝 Edit: in /workspace/MEMORY.md failed`) and `ae77d9f3` Email Warmup (29 Oct 07:00 SAST → `📝 Edit: in /workspace/AGENTS.md failed`). Both produced their full report — the **write** was lost, not the work.
- **The class is long-standing, not new:** 12 `Edit … failed` events across 5 jobs in `~/.openclaw/cron/runs/*.jsonl`, 6 of them on `memory/heartbeat-state.json` (Vault Sync, all before 9 Oct). The two newest are the first against the **workspace-root, platform-managed** files.
- **It has already cost a false fact:** MEMORY.md carried the "guard regression" line above for ~8 hours *after* the fix landed — the write that would have corrected it is exactly the one that failed.
- 🔑 **A cron job that finishes its work and then fails its bookkeeping is still a failed job** — and the error names the *bookkeeping*, which is why the real failure (a lost note) reads as a side issue.
- **Fix applied:** both payloads now append the run record to `/workspace/memory/$(date +%Y-%m-%d).md` and must **not** edit `MEMORY.md`/`AGENTS.md` from a cron run.

### Git / GitHub
- Git is **diverged**: `master` has no upstream, **928 local-only commits**, and **106 remote-only commits**. Plain push is rejected non-fast-forward.
- Reconcile only after Tumelo approves; resetting could discard remote work.
- GitHub PAT unavailable: credential store empty, no `gh`, no SSH key, no token in `.env`.
- Fix: Tumelo creates a fine-grained PAT with `contents:write`, provided securely rather than committed to `TOOLS.md`.
- ⚠️ **The remote is PUBLIC.** Any commit is a publication. The pre-commit guard blocks credential-bearing commits — never `--no-verify` it.
- **A local commit does not survive a container reset** — only a push to GitHub does.

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
| `i09hd71cvt06.space.mcode.io` | South African hospitality coffee |
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
- **Price ladder verified live 2026-10-28 22:00 SAST** (storefront `products.json` variants): Luxury Wagyu Biltong 1kg **R650** vs 500g **R450 = R900/kg** (inverted) · Wagyu Biltong Gold 1kg **R1,450** vs 7kg case **R12,500 = R1,785/kg**, while 7×1kg = R10,150 (**19% case arbitrage**) · Fire & Feast R999 · StudBot Rise R4,599. Live prices live in **Shopify** → every fix needs the Admin token (401 as of 28 Oct).
- ✅ **Guard regression RESOLVED — re-verified 2026-10-29 05:55 UTC:** the "hardcoded ClickUp token no longer trips the checker" hole is **CLOSED**. `ops/test-credential-resolution.py` is **30 passed / 0 failed**, including `hardcoded ClickUp token -> checker RED`, `real ClickUp token in a .md file -> checker RED`, `hardcoded AgentMail key -> checker RED`. 🔑 *A memory line recorded at 22:00 was TRUE then and FALSE later, and nothing ever re-verified it — the note outlived the defect. (The 22:00 cron run's own edit to this file FAILED — see the cron memory-write note below.)*
- Caviar floor tool was built

## Recent Session Notes (2026-10-28 12:01)

**The repo was never a repo, and three guards reported FALSE GREENS on an empty repo.**

I raised an incident on `#ops` (`1564944007178625126`) claiming the 928-commit history had
been destroyed overnight by a re-`git init`. **That claim was wrong about the cause** and I
corrected it publicly (`1564945978618945541`). The corrected finding is worse, and it is
the real defect.

**The evidence.**
* `/workspace/.git/HEAD` and `/workspace/.git/config` were **born 2026-10-26 13:24:25** —
  every internal of that `.git` is dated 26 Oct.
* the object store holds **0 loose objects, 0 pack files, 0 refs, no reflog** — 🔑 **it has
  never held a single commit.**
* the commit ids I reported earlier that morning (`0e4f603b`, `443a2949`) are **not valid
  objects anywhere on this machine** — I could not verify them, and I should have.
* forensics: **`/workspace` is on the container's overlay root filesystem, not a persistent
  volume** — the container's PID 1 started 2026-10-26 12:53 and the `.git` appeared 31
  minutes later. 🔑 **the history was lost on 26 Oct, at a container/overlay reset — not
  tonight, and not by a test.**

⇒ 🔑 **This workspace has never been under version control in this container.** 🔑 And
**a local commit does not survive a container reset** — only a push to GitHub does. The
remote is `https://github.com/TumeloRamaphosa/studex-agents-nest.git` (PUBLIC — 13 refs in
the tree), so the remote's history can be restored as tracking refs **without a PAT**; the
PUSH still needs one (Tumelo).

**🔑 THE REAL DEFECT: three guards reported FALSE GREENS on an empty repo.**

| guard | said | truth |
|---|---|---|
| `ops/check-git-index.py` | `VERDICT: CLEAN - the index is intact` | `tracked=0` and `head_count=-1` (no HEAD) fell through every branch — 🔑 **`0 == 0` read as "consistent"** |
| `ops/credential-resolution-check.py` | `VERDICT: CLEAN - 0 credential-bearing tracked file(s) scanned` | 🔑 **a vacuous scan** — "found nothing" proved nothing |
| the pre-push guard | `CLEAN` | 🔑 **there was no history to scan for a leaked credential** |

🔑 *A guard that cannot fail is a comment.* 🔑 *An assertion that proves presence does not
prove validity.* (MEMORY.md already carries the second one; it applied to the guards too.)

**🔑 THE ONE THREAD STILL WORTH PULLING:** **is any path on this box persistent?** If so,
the baseline can live there and survive a container reset.

---

## Build Hour 2026-10-28 — LADDER LOCK (shipped 23:00 SAST)

**Shipped:** live price & provenance sheet `ujlho19swr48` · redeployed retail page
`t56b7vkncytt` (supersedes `nudsduvyrc12`) · `ops/price-ladder-guard.py` ·
`builds/2026-10-28.md` · caviar-stripped gifting tiers in
`studex-corporate-gifting/src/tiers.compliant.tsx`.

### 🔑 Git safety in this repo — learned the hard way tonight
- **`git add .` in `/workspace` stages 14,612 files.** It sweeps in vendored projects
  (`gstack`, `headroom`, `studex-os`) and test fixtures full of key-shaped strings.
  The pre-commit credential hook **correctly BLOCKED the commit**. 🔑 *Stage files
  explicitly; never `git add .`; never `--no-verify`.*
- **The remote `master` has NO merge base with the local repo** — local was re-baselined
  26 Oct after the container reset lost history; remote `master` still holds the
  Jul-2026 lineage (106 commits). 🔑 **Never force-push `master`.** Push to the dated
  branch that already tracks the lineage (`standup/2026-10-28` fast-forwards cleanly).
- **GitHub push auth:** `GITHUB_PAT` is in `.env` **and** in the environment. Push via an
  inline `credential.helper` (`username=x-access-token`) so the token is never written to
  disk or echoed. `git push` alone fails with `could not read Username`.

### 🔑 Platform facts worth keeping
- **Shopify Admin API returns HTTP 401** (invalid key) → live storefront prices
  **cannot** be changed from this box. Source-of-truth edits + an owner action only.
- **The `deploy` tool creates a NEW space ID per deploy** — it cannot update an existing
  deploy in place. Correcting a live page means deploying a replacement and retiring the
  old URL. (That is why `nudsduvyrc12` is still live with the old prices.)
- **The corporate-gifting source was never deployed.** The live page `oi28dhtke3yk` shows
  the older caviar-free R1,299/R2,499/R4,999 build. Building the source would have
  *introduced* the caviar exposure. 🔑 *Diff source against live before shipping it.*

### 🔑 Guard design — the three false-positive traps
A guard that cries wolf gets switched off. Three traps closed in `price-ladder-guard.py`:
1. **Category** — a *biltong* market ceiling must not be applied to coffee pods or beef.
   Shopify's `product_type` is often the literal `"simple"`, so category must be inferred
   from title/handle.
2. **Form** — a 10x50g pod (R2,000/kg) is not the same product as a 1kg bag (R350/kg).
   Per-kg comparison requires the same pack form and a minimum weight.
3. **Context** — "is caviar priced?" must be tied to a caviar **grade**, not the word
   "caviar" near any price. Matching `R1,250 / 1kg` flagged our own clean page.

Also: a per-kg premium on a smaller pack is normal SA butcher merchandising, not
automatically a defect. 🔑 *Category-scoped severity limits — biltong and coffee strict,
beef lenient — beat one global threshold.*

### 🔑 Heartbeat 22:24 UTC — "the page was fine, the REGISTRY was stale" (ladder-lock drift)

The Build Hour redeployed the retail page at 21:20 with the new ladder
(R325 / R1,250 / R8,400) and caviar off the retail sale path. The drift checker
then failed 4 pages — and the live pages were **not** the problem:
`studex-meat/PRICE-SOURCE-REGISTRY.md` §2.1 still pointed every retail
"Must appear on" at the **retired** build `nudsduvyrc12`. Consequences:
- the live v5 page carried **zero assertions** ("NO ASSERTIONS — registry slug
  no longer resolves") — a green that meant nothing;
- the retired build was being policed for prices it could never change again;
- the per-kg prose figures `R1,200` and `R8,750` were parsed as prices that must
  appear on the page, so they could never pass.

Fixed at source, then redeployed: registry page map + §2.1 ladder rows + §2.3
caviar scope + prose de-assertions; `studex-biltong/index.html` re-synced with
`dist/` (the Build Hour had edited the deploy copy only); SA-hospitality page
rebuilt (ladder synced, caviar prices removed, two dead links repointed) →
`i09hd71cvt06`; `ops/price-ladder-guard.py` repointed at the live pages; new
control `ops/test-ladder-lock.py` (67 assertions, in the suite); two orphaned
checkers classified in `ops/heartbeat-checkers.tsv`.
**Result: drift 18/18 CLEAN · ladder-lock test 67/67.**

🔑 *Three rules from it:*
1. **A deploy changes the URL — the registry's page map changes in the SAME
   commit.** The registry is the contract; a stale map is a false green.
2. **"Must appear on" may only name pages you are willing to redeploy.** Point it
   at a retired URL and you have built permanent drift.
3. **Keep the hand-edited master and the deploy copy byte-identical.** Editing
   `dist/` only lets the two drift apart within the hour — and the next rebuild
   silently reverts the change.

⏳ Owner action still open: the live **Shopify storefront still sells the old
ladder** (500g R450 · 1kg R1,450 · 7kg case R12,500) while the site now says
R325 / R1,250 / R8,400. Shopify Admin API is 401 from this box.
