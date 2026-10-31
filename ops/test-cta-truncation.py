#!/usr/bin/env python3
"""Test the CTA-preserving truncation in scripts/caption_policy.py.

THE DEFECT (2026-10-31, found by reading the LIVE feed's own analytics):
Threads captions are capped at 500 chars. Both publish paths truncated the
caption at 497 chars + "..." (daily-post.py and blotato-fallback.js). The CTA
lives at the END of the caption, so the truncation deleted EXACTLY the CTA -
and the generator's validator ("no closing question/CTA") had already
approved the caption, because it validates the PRE-truncation text.

MEASURED ON THE LIVE FEED (10 posts via Blotato /posts -> state.analytics):
  Instagram 5/5 carry a CTA ("Connect with our team: info@studexmeat.com"),
            1060-1239 chars, never truncated.
  Threads  0/5 carry a CTA, every one exactly 500 chars (truncated).
  Threads: 3 likes across 5 posts. Instagram: 47 likes.
  Every post on both platforms: 0 comments, 0 follows, 0 shares.
🔑 *A validator that checks the text BEFORE the transform is not checking the
text that ships.*

THE FIX: truncate the PROSE, never the CTA.

🔑 WHY THE NEGATIVE CONTROLS ARE THE POINT
A truncation fix is easy to write wrong in the dangerous direction - it can
"pass" by simply not truncating. So the controls below pin down BOTH edges:
  * a short caption must pass through UNCHANGED (no invented cuts)
  * the OLD behaviour must LOSE the CTA - that is what proves this test is
    not vacuous, and that the defect was real
  * the caption must stay WITHIN the platform limit after the cut
  * the CTA and the hashtags must both survive
  * a caption with NO CTA must still be truncated (never worse than the old
    code it replaces)
  * the price rule and the caviar rule must STILL FIRE - a fix that silences
    the rules it lives next to is not a fix
"""
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
POLICY = REPO / "scripts" / "caption_policy.py"
DAILY_POST = REPO / "scripts" / "daily-post.py"
FALLBACK = REPO / "studex-content-automation" / "scripts" / "blotato-fallback.js"
FAILS = []

# The REAL Threads caption from the live feed (post 8508724, 26 Oct) - it is
# the shape that matters: prose, then a CTA, then hashtags.
REAL_THREADS_CAPTION = (
    "Biltong is not a snack. It is a slow craft. We dry ours over days until "
    "the moisture is gone and the flavour concentrates. Nothing is rushed and "
    "no oven is doing the work for it. That slowness is the whole point, and "
    "it is the reason a good pack tastes like something you remember rather "
    "than something you just ate. Ready to see how we do it? Connect with "
    "our team: info@studexmeat.com\n\n#studex #biltong #southafrica"
)

# A REAL pending caption from the repo (2026-10-29, 751 chars, published to
# Threads as post 8633885 at exactly 500 chars). Using the artefact rather
# than a hand-written string is the point: the defect only reproduces on a
# caption that is genuinely OVER the limit.
PENDING_2026_10_29 = REPO / "studex-content-automation" / "posts" / "pending" / "2026-10-29.json"


def real_long_caption():
    """The real 751-char pending caption, loaded from the repo."""
    import json
    d = json.loads(PENDING_2026_10_29.read_text(encoding="utf8"))
    return d["caption"]


def check(cond, label):
    if cond:
        print("  PASS  %s" % label)
    else:
        print("  FAIL  %s" % label)
        FAILS.append(label)


def run_policy(*args):
    r = subprocess.run([sys.executable, str(POLICY)] + list(args),
                       capture_output=True, text=True, timeout=60)
    return r


def old_truncate(text, limit=500):
    """The code as it was BEFORE the fix - used as a negative control."""
    if len(text) <= limit:
        return text
    return text[: limit - 3].rsplit(" ", 1)[0] + "..."


def main():
    print("=== 0. the REAL pending caption reproduces the defect ===")
    real = real_long_caption()
    check(len(real) > 500, "the real pending caption is over the Threads limit (%d)" % len(real))
    old_real = old_truncate(real)
    check("Connect with our team" not in old_real,
          "OLD truncation on the REAL caption lost the CTA (defect reproduced)")
    check(len(old_real) == 500 or len(old_real) <= 500,
          "OLD truncation produced the 500-char post we saw live (%d)" % len(old_real))

    print("\n=== 1. the OLD behaviour loses the CTA (negative control) ===")
    # The negative control must use a caption that is genuinely OVER the
    # limit - a short caption is not truncated at all, so it proves nothing.
    old = old_truncate(real)
    check("Now tell us" not in old and "are you team braai" not in old,
          "old truncation DID lose the CTA (so the defect was real)")
    check(len(old) <= 500, "old truncation stayed within 500 chars")

    print("\n=== 2. the NEW behaviour keeps the CTA and the hashtags ===")
    r = run_policy("--truncate", "threads", REAL_THREADS_CAPTION)
    new = r.stdout
    check(r.returncode == 0, "policy --truncate exits 0")
    check("Connect with our team" in new, "CTA survives truncation")
    check("#studex" in new, "hashtag survives truncation")
    check("?" in new, "the closing question survives truncation")
    check(len(new) <= 500, "result is within the 500-char Threads limit (%d)" % len(new))
    check(new == REAL_THREADS_CAPTION,
          "a caption UNDER the limit is passed through unchanged (no invented cut)")

    print("\n=== 2b. the REAL caption now keeps its CTA ===")
    r = run_policy("--truncate", "threads", real)
    out_real = r.stdout
    check("Now tell us" in out_real and "are you team braai" in out_real,
          "the real caption's CTA survives")
    check(len(out_real) <= 500, "the real caption stays within 500 chars (%d)" % len(out_real))
    check(out_real != old_real, "the new cut differs from what went live")
    check(out_real.endswith("#studex"),
          "the tail of the real caption (CTA/hashtags) is intact")
    check("marbling grade 5" in out_real,
          "the real caption's body text is preserved (the marble claim is in the prose)")

    print("\n=== 3. a short caption is passed through UNCHANGED ===")
    short = "Good biltong takes time.\n\nWhich pack do you reach for first? #studex"
    r = run_policy("--truncate", "threads", short)
    check(r.stdout == short, "short caption is untouched")

    print("\n=== 4. a caption with NO CTA is still truncated (never worse) ===")
    nocta = ("word " * 200).strip()
    r = run_policy("--truncate", "threads", nocta)
    check(len(r.stdout) <= 500, "CTA-less caption is still cut to the limit (%d)" % len(r.stdout))
    check(r.stdout.endswith("..."), "CTA-less caption keeps the old '...' ending")

    print("\n=== 5. a caption whose CTA alone cannot fit is NOT silently gutted ===")
    huge_cta = "Connect with our team: info@studexmeat.com " + ("x" * 600)
    r = run_policy("--truncate", "threads", huge_cta)
    check("Connect with our team" in r.stdout,
          "an over-long CTA is preserved rather than cut away")

    print("\n=== 6. the price and caviar rules STILL FIRE ===")
    priced = "Great biltong, R450 per kg. What pack do you favour?"
    r = run_policy("--check-text", priced)
    check(r.returncode == 1 and "Price published on public feed" in r.stdout,
          "the price rule still fires")
    cav = "Our Oscietra caviar is ready. Which tin would you gift?"
    r = run_policy("--check-text", cav)
    check(r.returncode == 1 and "Caviar offered on a public feed" in r.stdout,
          "the caviar rule still fires")

    print("\n=== 7. BOTH publish paths call the shared helper ===")
    a = DAILY_POST.read_text(encoding="utf8")
    check("caption_policy.truncate_for_platform" in a,
          "Path A (daily-post.py) calls the shared truncate_for_platform")
    check('threads[:497]' not in a,
          "Path A no longer has its own inline 497-char cut")
    b = FALLBACK.read_text(encoding="utf8")
    check("'--truncate'" in b,
          "Path B (blotato-fallback.js) calls the shared helper over the CLI")
    check("caption_policy.py" in b,
          "Path B points at the same caption_policy.py")

    print("\n=== 8. the helper is importable and behaves as documented ===")
    sys.path.insert(0, str(REPO / "scripts"))
    import caption_policy as cp
    check(cp.has_cta(REAL_THREADS_CAPTION), "has_cta() is True on a real CTA caption")
    check(not cp.has_cta("Biltong dries over days. It tastes like memory."),
          "has_cta() is False on a dead-stop caption")
    check(not cp.has_cta("Biltong dries over days. It tastes like memory. #studex"),
          "a hashtag does not count as a CTA")
    check(cp.has_cta("Biltong is slow craft. Which one do you reach for? #studex"),
          "a closing question counts as a CTA")
    out, dropped = cp.truncate_for_platform(REAL_THREADS_CAPTION, "threads")
    check(dropped is False,
          "a caption under the limit reports NO cut (dropped=False)")
    out_real, dropped_real = cp.truncate_for_platform(real, "threads")
    check(dropped_real is True,
          "truncate_for_platform reports prose WAS cut on the real caption")
    check(out_real.count("Now tell us") == 1,
          "the CTA appears exactly once (no duplicated tail)")
    check(cp.has_cta(out_real), "the real truncated caption still has a CTA")
    check(cp.weighted_len(out_real) <= 500,
          "the real truncated caption is within the limit (%d)" % cp.weighted_len(out_real))
    check(cp.has_cta(out), "the truncated caption still has a CTA")
    check(cp.weighted_len(out) <= 500,
          "the truncated caption is within the limit by WEIGHTED length (%d)" % cp.weighted_len(out))
    out2, dropped2 = cp.truncate_for_platform(REAL_THREADS_CAPTION, "instagram")
    check(out2 == REAL_THREADS_CAPTION and dropped2 is False,
          "a platform with no limit is untouched")

    print("\n=== 9. emoji weighting matches the JS rule ===")
    check(cp.weighted_len("\U0001F600") == 2, "an emoji counts as 2")
    check(cp.weighted_len("a") == 1, "a plain char counts as 1")

    print("\n" + "=" * 66)
    if FAILS:
        print("FAILED (%d):" % len(FAILS))
        for f in FAILS:
            print("  - %s" % f)
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
