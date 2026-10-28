# 2026-10-27 — the pre-flight measured its clock against TODAY, not the TARGET date

**Found:** 2026-10-27 ~19:58 SAST, while checking tomorrow's post (Wed 28 Oct) — which
`HEARTBEAT.md` itself flags as "the next live trigger".
**Fixed:** commit `3e7f5785` (2026-10-27 20:50 UTC).

## The bug

`ops/preflight-daily-post.py` decided whether a **missing** path-B pending file was *expected*
or a *failure* by comparing the **current** wall clock to 08:55 SAST — and never looked at
**which date was being checked**:

```
$ python3 ops/preflight-daily-post.py 2026-10-28        # at 19:58 SAST on 27 Oct
FAIL  no pending file at 2026-10-28.json - it should have been written at 08:55 SAST.
      The content agent did not run, so the fallback path (path B) has nothing to publish.
```

The content agent had **not failed to run** — it was scheduled to run the **next morning**.
The gate reported a defect for something **not yet due**.

The `RESULT` line had the same bug: it said *"the 09:00 SAST publish has already run"* about a
date whose publish had not happened yet.

## Blast radius

Small — **both crons pass today's date**, so this only fired when a human or an agent checked a
different date. But that is precisely the check `HEARTBEAT.md` tells the next reader to make, so
the next reader **would** have hit it.

🔑 **A gate that reports a defect for something that has not been due yet teaches the next reader
to ignore the gate** — which is exactly how a *real* failure gets missed. **A false alarm is not a
harmless false alarm.**

## The fix

`pending_absence_verdict(target_date, now_sast)`:

| target | verdict |
|---|---|
| in the FUTURE | expected — the agent has not been due |
| TODAY, before 08:55 SAST | expected — not due yet |
| TODAY, at/after 08:55 SAST | failed — the agent was due |
| in the PAST | failed — the agent was due |

The `RESULT` line now names FUTURE / PAST / TODAY separately, and never claims the publish
"already ran" for a date whose publish has not happened.

## 🔑 A bug I introduced while fixing this one — caught by the suite

`report()` takes **no arguments** and cannot see `main()`'s locals. Using `main()`'s `day` in the
new RESULT block raised `NameError: name 'day' is not defined` and killed the report **after** the
checks had run — so the gate printed **nothing at all** and exited non-zero.

`ops/test-media-check-targets.py` (check **F**, "no NameError when the pending file is absent")
caught it. Fixed by carrying the target date in a module-level `TARGET_DATE`.

🔑 **The precise rule now pinned by `ops/test-preflight-target-date.py`: `report()` must not READ a
name it never assigns.** A *local* assignment is fine — my first "fix" assigned `date_str` locally
inside `report()`, and a naive "must not mention the name" rule would have failed correct code.
The rule is about *reading unbound*, not about *spelling*.

## The test

`ops/test-preflight-target-date.py` — 22 assertions, wired into `ops/run-tests.sh`.
Negative controls:
1. reproduces the **original** buggy comparison and proves the checker catches it;
2. mutates the call site to ignore the target date;
3. mutates `report()` back to reading `main()`'s `day`.

## 🔑 The transferable lesson

🔑 **A checker that only ever sees today's data is untested on the axis that matters.** Any gate
that takes a date/ID argument needs at least one case where that argument is **not** today.
Most of our checkers are hardcoded to "now" — which is exactly why this bug survived every
previous review.

## Verification

- Suite: **ALL TESTS PASS (43 python + 3 other)**, `SUITE_RC=0`.
- Canonical heartbeat pass: 17 checkers · 13 clean · 4 known escalations · **0 new** · 0 broken ·
  0 could-not-prove.
- End-to-end: `2026-10-28` → exit 0 (was exit 1 with a false FAIL) · `2026-10-27` → exit 1 (the
  real price-on-feed failure, unchanged) · `2026-10-26` → exit 1 (unchanged).
- No Discord post — internal tooling, low blast radius, no action needed from Tumelo, and the four
  known escalations did **not** change in content.
