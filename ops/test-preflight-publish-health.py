#!/usr/bin/env python3
"""The pre-flight must not certify an UNPUBLISHABLE platform as "connected".

🔴 THE GAP (found 2026-10-28 03:20 UTC)
-----------------------------------------
The publisher POSTs to a hardcoded Blotato account id per platform. The
pre-flight's account check asked ONE question:

    attempted = [a for a in rows if a.get("platform") in dp.BLOTATO_ACCOUNTS]
    print("  accounts for platforms we attempt: " + ...)

"Is SOME account of this platform connected?" - and it printed the result in
green. But a Blotato account can be CONNECTED and still be UNPUBLISHABLE: a
Meta or LinkedIn grant expires while the connection record survives.

The evidence is our own publish history (memory/published-<date>-<pillar>.json,
written by the publisher):

    2026-10-22  posted: instagram, threads   failed: facebook, linkedin
    2026-10-23  posted: instagram, threads   failed: facebook, linkedin
    2026-10-26  posted: instagram, threads   failed: facebook, linkedin
    2026-10-27  posted: instagram, threads   failed: facebook, linkedin

4 of 4 publishes, 2 of 4 platforms never published ONCE - while the
pre-flight printed facebook and linkedin as healthy. That is a false green
in the very block that exists to tell the truth about accounts.

The Blotato accounts API has NO grant-health field (verified live 2026-10-28:
the records for the working and the failing accounts are indistinguishable
apart from platform-idiomatic naming - facebook/linkedin carry a "fullname",
instagram/threads a "username"), so "connected" CANNOT answer this. The only
honest source is what our own last few publishes actually did.

🔑 AND THE FAILURE MUST NOT BLOCK THE POST. The publisher's loop records a
per-platform result and CONTINUES, so a failed platform does not stop the
others (facebook fails FIRST in the loop and instagram/threads still posted
every time). So this is a WARNING. Blocking would kill the two platforms
that DO work - the same over-reaction as refusing to publish when the
image-upload path is fragile.
"""
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path("/workspace")
spec = importlib.util.spec_from_file_location(
    "pf", ROOT / "ops" / "preflight-daily-post.py")
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)

PASSED = 0
FAILED = 0


def check(name, cond):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print("[PASS] " + name)
    else:
        FAILED += 1
        print("[FAIL] " + name)


# ---------------------------------------------------------------- the data
# 4 real publish days, exactly as the marker files record them.
REAL_MARKERS = [
    {"date": "2026-10-22", "posted": ["instagram", "threads"],
     "failed": ["facebook", "linkedin"]},
    {"date": "2026-10-23", "posted": ["instagram", "threads"],
     "failed": ["facebook", "linkedin"]},
    {"date": "2026-10-26", "posted": ["instagram", "threads"],
     "failed": ["facebook", "linkedin"]},
    {"date": "2026-10-27", "posted": ["instagram", "threads"],
     "failed": ["facebook", "linkedin"]},
]
PLATFORMS = ["facebook", "instagram", "linkedin", "threads"]


def original_connected_only_verdict(targeted, live_rows):
    """NEGATIVE CONTROL - the behaviour BEFORE this fix, reconstructed.

    It only knew "is some account of this platform connected?". It had no
    way to express grant health, so it stayed SILENT on exactly the case
    the fix catches.
    """
    attempted = [a for a in live_rows if a.get("platform") in targeted]
    missing = set(targeted) - {a.get("platform") for a in attempted}
    return sorted(missing)


# ------------------------------------------------------------- the checks
check("the pre-flight exposes publish_health()",
      callable(getattr(pf, "publish_health", None)))
check("the pre-flight exposes unpublishable()",
      callable(getattr(pf, "unpublishable", None)))
check("the pre-flight exposes read_publish_markers()",
      callable(getattr(pf, "read_publish_markers", None)))

health = pf.publish_health(REAL_MARKERS, PLATFORMS)
check("publish_health counts a platform that always posted",
      health["instagram"]["posted"] == 4 and health["instagram"]["failed"] == 0)
check("publish_health counts a platform that always failed",
      health["facebook"]["failed"] == 4 and health["facebook"]["posted"] == 0)
check("publish_health covers every platform asked about",
      set(health) == set(PLATFORMS))
check("publish_health on no markers is all zeroes",
      all(v["posted"] == 0 and v["failed"] == 0
          for v in pf.publish_health([], PLATFORMS).values()))

broken = pf.unpublishable(health)
check("a platform that failed 4/4 and never posted IS unpublishable",
      "facebook" in broken and "linkedin" in broken)
check("a platform that posted every time is NOT unpublishable",
      "instagram" not in broken and "threads" not in broken)

# a platform that both posted and failed is INTERMITTENT, not dead
flaky = pf.publish_health(
    [{"posted": ["instagram"], "failed": []},
     {"posted": [], "failed": ["instagram"]}], ["instagram"])
check("a platform that posted AND failed is not called unpublishable",
      pf.unpublishable(flaky) == [])

# a single failure is not enough to call a platform dead
once = pf.publish_health(
    [{"posted": ["instagram"], "failed": []},
     {"posted": ["instagram"], "failed": ["instagram"]}], ["instagram"])
check("a platform with any success is not called unpublishable",
      pf.unpublishable(once) == [])

# ------------------------------------------------------ the negative control
# The live accounts: facebook and linkedin ARE connected - that is the whole
# problem. The pre-fix code asked only "is it connected?" and said nothing.
LIVE_ROWS = [
    {"id": "38744", "platform": "facebook", "fullname": "Tumelo Ramaphosa"},
    {"id": "76978", "platform": "instagram", "username": "ramaphosatumelo"},
    {"id": "26628", "platform": "linkedin", "fullname": "Tumelo Ramaphosa"},
    {"id": "7701", "platform": "threads", "username": "ramaphosatumelo"},
]
old = original_connected_only_verdict(PLATFORMS, LIVE_ROWS)
check("NEGATIVE CONTROL: the pre-fix check was SILENT on a platform that "
      "is connected but has failed 4/4 publishes", old == [])
new = pf.unpublishable(pf.publish_health(REAL_MARKERS, PLATFORMS))
check("the new check DOES name that platform", "facebook" in new)

# ---------------------------------------------------- the real marker files
markers = pf.read_publish_markers()
check("read_publish_markers() returns a list", isinstance(markers, list))
check("every real marker has the expected shape",
      all(set(m) == {"date", "posted", "failed"} for m in markers))
check("real markers are ordered oldest first",
      [m["date"] for m in markers] == sorted(m["date"] for m in markers))
check("read_publish_markers() respects its limit",
      len(pf.read_publish_markers(limit=2)) <= 2)

print("\n%d passed, %d failed" % (PASSED, FAILED))
sys.exit(1 if FAILED else 0)
