# The orphan-control bug class was STILL open — the discovery rule was a list of names

**2026-10-28 00:30 SAST (2026-10-27 22:30 UTC) · heartbeat pass**

## What I went looking for
HEARTBEAT.md records that the "orphaned checker" bug bit us **three times**:
1. `blotato-fallback.js` — no cron, no checklist entry, nothing invoked it.
2. `ops/dead-inbox-check.py` — a working, tested checker HEARTBEAT.md named NOWHERE.
3. `ops/run-heartbeat-checks.py` — hardcoded its own checker list, so a checker
   added later was silently orphaned. *I committed that same bug one commit
   after fixing it.*

The stated fix was the registry `ops/heartbeat-checkers.tsv` plus
`ops/test-heartbeat-registry.py`, which "discovers every checker-like file in
`ops/`" and **fails the suite if one is unclassified**.

## What was actually true
🔑 **The discovery rule was `check-*.py` plus THREE HARDCODED NAMES** —
`drift-check.py`, `dead-inbox-check.py`, `tmp-shape-surface-audit.py`.

So `dead-inbox-check.py` — the file whose omission *caused* the bug — was only
ever caught because someone added its name to the list. **The pattern was never
generalised.** Any future checker named `foo-check.py`, `foo-guard.py`,
`foo-audit.py`, `probe-foo.py` or `preflight-foo.py` would have been
**invisible and silently orphaned** — the exact thing the test exists to
prevent, still possible, one rename away.

A hardcoded list of names is not a discovery rule. It is the bug wearing a
control's clothes.

## The blast radius
The generalised rule found **36** checker-like files. The registry classified
**22**. Fourteen were unclassified — and two of them were **standing security
controls that nothing ran**:

| File | What it is | Was it run by anything? |
|---|---|---|
| `ops/audit-blotato-fragments.py` | finds a **fragment of the LIVE Blotato key** in tracked source — the exact blind spot `check-tracked-live-credentials.py` documents but cannot see (its regex is prefix-anchored) | **NO. Orphaned.** |
| `ops/credential-resolution-check.py` | the language-aware **shape** checker, complementary to the value-based one | **NO. Orphaned.** |
| `ops/probe-shopify-admin.py` | read-only Shopify Admin check — the probe I used tonight | no |
| `ops/preflight-daily-post.py` | the 08:00/09:20 gate | yes — the crons |
| `ops/git-pre-push-guard.py` | the pre-push hook | yes — git invokes it |
| `ops/memory-shrink-guard.py` | memory-shrink guard | yes — the suite |
| `ops/secret_leak_scan.py` | credential-shaped literals in browser assets | yes — a library imported by `drift-check.py` |
| `ops/probe-*.py` (4) | ad-hoc read-only probes | no |
| `ops/heartbeat-check.py` | superseded by `run-heartbeat-checks.py` | no |
| `ops/patch-*-scan.py` (2) | one-off patch audits | no |
| `ops/eod-blotato-check.py` | one-off end-of-day diagnostic | no |

## 🔑 THE FINDING: A CONTROL THAT CANNOT FAIL
`audit-blotato-fragments.py` **always exited 0.** It printed its findings and
returned success — so it could never be a checker; promoting it as-is would
have made it a control that reports CLEAN by construction. The same class as
the counter bug in the scanner (2026-10-26): a checker whose own code cannot
express failure.

Fixed: exit **0** clean · **1** fragment/split-key found · **2** could not
prove. It also had a second trap: the key is resolved at **module import**, so
an unresolvable key raised an exception → exit 1 → the runner would read
**"FINDING"** for a checker that had proved nothing. Now it exits **2**
("could not prove"), which is what it actually is.

🔑 **The key's material is in tracked source and the key still authenticates.**
Run tonight: `3 split-key candidate file(s) + 42 fragment hit(s)` across the
tracked tree, and the live key returned **HTTP 200** against
`backend.blotato.com/v2/users/me/accounts`. The full key is already published
in the public remote — this is the **same escalation family** as
`public-exposure`, whose standing instruction is *"Rotate first (immediate),
then rewrite (durable)."* Re-writing the fragments without rotating would
leave a working credential that someone may already have cached.

**Action for Tumelo: rotate the Blotato key.** I cannot rotate a credential.

## What I changed
1. **`ops/test-heartbeat-registry.py`** — the discovery rule is now a set of
   **name SHAPES**, not a list of names:
   `check-*.py` · `*-check.py` · `*_check.py` · `*-guard.py` · `audit-*.py` ·
   `*-audit.py` · `*_scan.py` · `*-scan.py` · `probe-*.py` · `preflight-*.py`
   (`test-*.py` and `tmp-*.py` excluded — a test and a scratch script are not
   controls).
2. **🔑 My first version of that rule was STILL incomplete.** It listed only
   the *suffix* forms and therefore missed `audit-blotato-fragments.py` (a
   **prefix** form) and `secret_leak_scan.py` (an **underscore** form) — the
   two files the change was *for*. A name-shape rule is only as good as the
   shapes you thought of, so the shapes are now broad on purpose. This is the
   clearest argument I have for writing the rule, running it, and reading the
   list — rather than writing the rule and assuming.
3. **Negative controls that prove the generalisation.** The existing control
   used `check-orphan.py` — a name the **original** rule also caught, so it
   would have passed *before* the fix and proved nothing. The new control
   asserts the generalised rule finds six names the original rule missed, AND
   that the original rule really would have missed them (so the control cannot
   be vacuous). **101 assertions, 0 failed.**
4. **`ops/heartbeat-checkers.tsv`** — all 14 newly-discovered files classified.
   `audit-blotato-fragments.py` and `credential-resolution-check.py` promoted
   to **PASS** (with `known=yes` on the fragment one — it re-verifies the
   known exposure every pass, and the escalation disappears on its own when
   the key is rotated). The other 12 classified **SCOPE with a stated reason**.
5. **`ops/credential-resolution-check.py`** — added a `VERDICT:` line so the
   runner reports a verdict instead of falling back to a prose sentence about
   credential syntax.

## 🔑 THE GENERAL LESSON
> **Prose does not fix a structural omission, and neither does a list of names.**

The registry was a genuine improvement over "HEARTBEAT.md remembers to run
these three scripts". But the *discovery* half of the control was still
hardcoded, so the control only protected the names someone remembered to
write down. The three historical orphans shared a shape — **a working
control that nothing invoked** — and the fourth one was hiding in the
protection mechanism itself.

🔑 **A negative control must fail against the code that is being replaced.**
Mine passed against the old rule too. That is how a control becomes
decoration: it proves a property that was already true.
