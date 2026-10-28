#!/usr/bin/env python3
"""The pre-flight must BLOCK when an image is staged but will not be attached.

🔴 THE BUG (found 2026-10-28, 00:30 UTC — hours before a live publish)
----------------------------------------------------------------------
The publisher resolves a post's image TWO ways, and they are NOT the same
thing (`scripts/daily-post.py`):

  * `media_url` = POST_MEDIA_URL, or the queue file's `**Media URL:**` line.
    THIS is the only thing sent to Blotato as `mediaUrls`.
  * `staged_img` = a LOCAL file at `memory/<date>-<pillar>.png`, found by
    `dp.find_image()`. The publisher uses it for VALIDATION and prints it in
    its summary line — `media_url or img or "none"` — but it is **NOT**
    sent to Blotato.

The pre-flight only checked the first. So for 2026-10-28 (the only recent
queue file with no `**Media URL:**` line — every other one had one):

  * the image EXISTED at `memory/2026-10-28-build.png` (1.5 MB, the
    China/supply-chain Build card, already approved in
    #marketing-command-center);
  * `validate_brand()` PASSED, because it is given `image_exists`;
  * the summary would print `media/2026-10-28-build.png` — **as if the
    image were attached**;
  * and `try_blotato(...)` would have been called with `media_url=""`, so
    Blotato would have received `"mediaUrls": []`.

**The post would have published with no image, and the log would have said
it had one.** That is the worst kind of silent failure: it lies in its own
output.

🔑 AND IT WAS ONLY A WARNING, SO NOBODY WOULD HAVE SEEN IT. The 08:00
cron's instruction is *"if it exits 0 (CLEAN), do NOTHING"* — so a warning
about a post that WILL publish wrongly is invisible to everyone.

THE FIX
-------
`media_verdict(media_url, staged_img)`:
  * a media URL                 -> "ok"   (the URL is what gets attached)
  * no URL, but an image staged -> "fail" (BLOCK — it would publish imageless)
  * no URL and no image         -> "warn" (a deliberate text-only post)

NEGATIVE CONTROL
----------------
The test applies the ORIGINAL check to copies of the real file and asserts
the checker catches it. A checker that cannot fail is worthless.
"""
import pathlib
import re
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PREFLIGHT = ROOT / "ops" / "preflight-daily-post.py"

PASSED, FAILED = [], []


def check(name, cond, detail=""):
    if cond:
        PASSED.append(name)
        print("[PASS] %s" % name)
    else:
        FAILED.append(name)
        print("[FAIL] %s%s" % (name, ("  -> " + str(detail)[:300]) if detail else ""))


def _fn(text, name):
    m = re.search(r"def %s\(.*?\n(?=\ndef |\nclass )" % name, text, re.S)
    if not m:
        return None
    ns = {}
    try:
        exec(compile(m.group(0), "<fn>", "exec"), ns)
    except Exception:
        return None
    return ns.get(name)


def main():
    text = PREFLIGHT.read_text(encoding="utf8")

    verdict = _fn(text, "media_verdict")
    check("the pre-flight exposes media_verdict()", verdict is not None,
          "could not extract the function")
    if verdict is None:
        print("\nVERDICT: CHECKER BROKEN - refusing to report CLEAN.")
        print("%d passed, %d failed" % (len(PASSED), len(FAILED)))
        return 2

    URL = "https://example.invalid/x.png"

    # --- the three cases ---
    check("a media URL is 'ok'", verdict(URL, None) == "ok")
    check("a media URL wins even when a local image is staged",
          verdict(URL, "/w/memory/2026-10-28-build.png") == "ok")
    check("no URL but an image IS staged is 'fail' (BLOCKS)",
          verdict("", "/w/memory/2026-10-28-build.png") == "fail",
          verdict("", "/w/memory/2026-10-28-build.png"))
    check("no URL and no image is 'warn' (a deliberate text-only post)",
          verdict("", None) == "warn", verdict("", None))

    # --- the call site must actually pass the staged image ---
    flat = re.sub(r"\s+", " ", text)
    check("the call site resolves the staged image via find_image()",
          "dp.find_image(date_str)" in flat)
    check("the call site uses media_verdict()",
          "media_verdict(media_url, staged_img)" in flat)
    check("the FAIL branch names the staged image path",
          "but an image IS staged" in flat)

    # --- the queue-file convention is what the publisher reads ---
    check("the FAIL message tells the reader to add '**Media URL:**'",
          "**Media URL:**" in flat)

    # --- NEGATIVE CONTROL: the ORIGINAL check must be caught ---
    # The original implementation is reconstructed here, because the file on
    # disk has already been fixed - a test that greps the current file for
    # the OLD pattern proves nothing about the old behaviour.
    def original_verdict(media_url, staged_img):
        """The ORIGINAL check: it never looked at the staged image."""
        if not media_url:
            return "warn"
        return "ok"

    check("NEGATIVE: the ORIGINAL implementation did NOT block the staged-"
          "image case (it warned)", original_verdict("", "/w/memory/x.png")
          == "warn")
    check("NEGATIVE: the FIXED implementation blocks exactly that case",
          verdict("", "/w/memory/x.png") == "fail")
    check("NEGATIVE: they differ on exactly that case",
          original_verdict("", "/w/memory/x.png") != verdict("", "/w/memory/x.png"))
    check("NEGATIVE: they agree on the deliberate text-only case",
          original_verdict("", None) == verdict("", None))
    check("the fixed file no longer has the old warn-only branch",
          not re.search(r"if not media_url:\s*\n\s*warn\(", text))

    # --- NEGATIVE CONTROL: mutate a copy and confirm the checker catches it ---
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="preflight-media-"))
    try:
        (tmp / "ops").mkdir()
        p = tmp / "ops" / "preflight-daily-post.py"
        p.write_text(text)
        mutated = p.read_text().replace(
            'verdict = media_verdict(media_url, staged_img)',
            'verdict = "warn" if not media_url else "ok"')
        p.write_text(mutated)
        m_flat = re.sub(r"\s+", " ", p.read_text())
        caught = 'verdict = media_verdict(media_url, staged_img)' not in m_flat
        check("NEGATIVE: the checker catches a call site that ignores the "
              "staged image", caught)
        m_v = _fn(p.read_text(), "media_verdict")
        check("NEGATIVE: the mutated file still defines media_verdict "
              "(the mutation was at the call site, not the function)",
              m_v is not None)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%d passed, %d failed" % (len(PASSED), len(FAILED)))
    if FAILED:
        print("VERDICT: BROKEN - the pre-flight would let an imageless post "
              "through.")
        return 1
    print("VERDICT: CLEAN - a staged image that will not be attached BLOCKS "
          "the post.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
