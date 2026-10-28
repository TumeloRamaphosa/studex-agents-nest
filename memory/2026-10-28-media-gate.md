# 2026-10-28 — a post can publish WITHOUT its image while the log says it has one

**Found:** 2026-10-28 ~00:30 UTC — roughly **6 hours** before the 09:00 SAST publish, on the
day `HEARTBEAT.md` had flagged as "the next live trigger".
**Fixed:** commit `93ce2a23`.

## The bug

The publisher resolves a post's image **two** ways, and they are **not** the same thing
(`scripts/daily-post.py`):

| | what it is | what happens to it |
|---|---|---|
| `media_url` | `POST_MEDIA_URL`, or the queue file's `**Media URL:**` line | **the only thing sent to Blotato as `mediaUrls`** |
| `staged_img` | a local file `memory/<date>-<pillar>.png`, found by `dp.find_image()` | used for **validation** and **printed in the summary** (`media_url or img or "none"`) — but **not sent to Blotato** |

The pre-flight only checked the first. For **2026-10-28** — the only recent queue file with
no `**Media URL:**` line, every other one had one:

* the image **existed** (`memory/2026-10-28-build.png`, 1.5 MB, the China/supply-chain Build
  card, already approved in #marketing-command-center);
* `validate_brand()` **passed**, because it is given `image_exists`;
* the summary would print the local path — **as if the image were attached**;
* and `try_blotato(...)` would have been called with `media_url=""`, so Blotato would have
  received `"mediaUrls": []`.

🔑 **The post would have gone out with no image and the log would have said it had one** —
the worst kind of silent failure, because it lies in its own output.

🔑 **And it was only a WARNING, so nobody would have seen it.** The 08:00 cron's instruction
is *"if it exits 0 (CLEAN), do NOTHING"* — so a warning about a post that **will** publish
wrongly is invisible to everyone. A warn that nobody reads is the same as no check.

## The fix

1. `media_verdict(media_url, staged_img)` in `ops/preflight-daily-post.py`:
   * a media URL → `ok`
   * **no URL but an image IS staged → `fail`** (blocks, and names the path + what to add)
   * no URL and no image → `warn` (a deliberate text-only post)
2. Tomorrow's queue file given a real, fetchable **Media URL** — the image was uploaded to the
   CDN and `**Media URL:**` added in the same convention the other queue files use. The
   pre-flight now reports `[ OK ] media URL 200 image/png` for 2026-10-28 with **0 warnings**.
3. `ops/test-preflight-media-gate.py` — 16 assertions, with a negative control that
   **reconstructs** the original warn-only implementation and proves the fixed one blocks the
   staged-image case. Wired into the suite.

## Verification

* **End-to-end** with a *temporary future-dated* queue file (staged image, no Media URL) → the
  pre-flight FAILS with the actionable message. The live queue file was never modified to
  produce that.
* Swept every other queue file — none has the same defect.
* Pre-flight for 2026-10-28: CLEAN, 0 warnings, exit 0.
* Suite: **ALL TESTS PASS (45 python + 4 other)**.

## 🔑 The transferable lessons

🔑 **A warning nobody reads is the same as no check.** The 08:00 cron does nothing on exit 0,
so anything that must be acted on has to **BLOCK**. Decide by severity, not by how it feels:
"the post will publish wrongly" is a blocker; "no image was intended" is a warning.

🔑 **Two ways of resolving the same value are not the same value.** The publisher had an
image in hand and a URL in hand, and only one of them was ever sent. Any time a system holds
a value in two forms, ask **which form reaches the outside world** — and make the gate check
*that* form.

🔑 **A summary line can lie.** `media_url or img or "none"` printed the local path as if the
image were attached. Whatever you print to a log is a **claim**; make it say what actually
happened.

## 🔑 Standing rule

**A queue file that has an image MUST declare `**Media URL:** <public url>`.** A local
`**Image:**` path is for validation and humans only — it is **not** what gets attached.

## Also: a regression from my own 27-Oct change, repaired by the concurrent session

My target-date fix (the pre-flight now keys its wording off the *target date*, not the wall
clock) broke `ops/test-media-check-targets.py` — that test branched on the **wall clock**, so
it only passed in the second half of every day and **failed on every run between midnight and
09:00 SAST**. The concurrent session fixed it by **injecting the clock** so every case is
asserted unconditionally; their fix was in the working tree when my suite ran and is now
committed with this work.

🔑 **A change that alters the logic a test depends on will usually break that test in a
window you are not watching.** The 21:00–23:00 SAST runs never touched the broken window —
only the midnight run did.
