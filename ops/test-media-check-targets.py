#!/usr/bin/env python3
"""Prove the pending-MEDIA check is TARGET-AWARE, not a blanket FAIL.

THE BUG THIS GUARDS AGAINST
---------------------------
`ops/preflight-daily-post.py` used to hard-FAIL whenever the path B pending
file had no `media.image`. That fired EVERY DAY, for two reasons:

  1. `studex-content-automation/scripts/daily-content-agent.js` NEVER writes
     `media` - it only writes a caption.
  2. `blotato-fallback.js` TARGETS are linkedin + threads, and NEITHER
     platform requires an image. (Instagram does: 422 code 20000.)

The 2026-10-22 pending file DID carry `media`, but that was written by the
ad-hoc /tmp/ig2.js script - not by the content agent. So the check was
passing by luck on one day and would fail on every other.

A check that cries wolf daily is a check nobody reads. It also BLOCKS a
publish that is completely fine, which is worse than crying wolf.

WHAT MUST HOLD
--------------
  A. With the real fallback TARGETS (linkedin, threads) and no media ->
     a WARN, not a FAIL, and the pre-flight must not report a blocking
     issue.
  B. If Instagram is ever ADDED to the fallback TARGETS, a missing image
     must become a FAIL again - the rule has to be derived from the
     targets, not hardcoded, so it can never drift.
  C. NEGATIVE CONTROL: the OLD blanket implementation FAILS case A. A
     checker that cannot fail is worthless.

The test edits a COPY of the fallback script and of the pre-flight, so it
never touches the live ones.
"""
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path("/workspace")
PF = ROOT / "ops" / "preflight-daily-post.py"
FB = ROOT / "studex-content-automation" / "scripts" / "blotato-fallback.js"

PASSED = []
FAILED = []

# A PRICE-FREE pending caption used to isolate the MEDIA dimension.
# The real 2026-10-23 caption carries "From R1,950" and the pre-flight now
# correctly FAILS it under rule [10]; this test is about media, so it uses a
# caption with no price. Case D covers the price check on its own.
_PRICE_FREE_CAP = ("Slow-aged Wagyu, sealed at the source and sealed again in "
                   "Cape Town. Order on the store or talk to us on WhatsApp. "
                   "#studexmeat #wagyu #southafrica")


def _write_price_free_pending(tmpdir, caption=_PRICE_FREE_CAP):
    """Write a pending file with no price, no media, no markdown residue."""
    import json as _json
    p = pathlib.Path(tmpdir) / "2026-10-23.json"
    p.write_text(_json.dumps({
        "caption": caption,
        "status": "APPROVED_PENDING_FB_TOKEN",
        "productName": "Test Product",
        "media": {},
    }), encoding="utf8")
    return p


# The fixture directory lives for the whole test run.
_FIXTURE_DIR = tempfile.mkdtemp(prefix="media-fixture-")
tmp_pending = str(_write_price_free_pending(_FIXTURE_DIR))


def check(name, ok, detail=""):
    (PASSED if ok else FAILED).append(name)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
          + (f" -> {detail}" if detail else ""))


def run_preflight(env_overrides=None):
    """Run the pre-flight against a given fallback TARGETS set.

    The pre-flight reads FB_SCRIPT from the module, so we point that at a
    temp copy of the fallback script with the TARGETS we want to test.

    It also reads the pending caption from ROOT, and the REAL 2026-10-23
    caption carries "From R1,950" - which the pre-flight now correctly
    FAILS under rule [10] ("no price on a public feed"). This test is about
    the MEDIA dimension, so we point the copy at a PRICE-FREE caption; the
    price check has its own case (D) below.
    """
    tmp = tempfile.mkdtemp(prefix="media-check-")
    try:
        fb_copy = pathlib.Path(tmp) / "blotato-fallback.js"
        shutil.copy(FB, fb_copy)
        pf_copy = pathlib.Path(tmp) / "preflight-daily-post.py"
        shutil.copy(PF, pf_copy)
        # Point the pre-flight at the copied fallback script.
        src = pf_copy.read_text(encoding="utf8")
        src = src.replace(
            'FB_SCRIPT = pathlib.Path(\n    "/workspace/studex-content-automation/scripts/blotato-fallback.js")',
            'FB_SCRIPT = pathlib.Path(%r)' % str(fb_copy),
        )
        # Point the pending-caption lookup at a price-free caption, so this
        # test isolates the MEDIA dimension (see case D for the price check).
        src = src.replace(
            'pending = ROOT / "studex-content-automation" / "posts" / "pending" / f"{date_str}.json"',
            'pending = pathlib.Path(%r)' % str(tmp_pending),
        )
        src = src.replace(
            'pend_path = ROOT / "studex-content-automation" / "posts" / "pending" / f"{date_str}.json"',
            'pend_path = pathlib.Path(%r)' % str(tmp_pending),
        )
        pf_copy.write_text(src, encoding="utf8")

        env = dict(__import__("os").environ)
        env.update(env_overrides or {})
        r = subprocess.run(
            [sys.executable, str(pf_copy), "2026-10-23"],
            capture_output=True, text=True, timeout=180, env=env)
        return r.stdout + r.stderr
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def has_blocking(out):
    """True if the pre-flight raised a BLOCKING issue.

    🔑 A blocking issue is a line whose MARKER is FAIL - the pre-flight
    prints "  FAIL  <text>". A warning or a note that merely CONTAINS the
    word "fail" is NOT a blocking issue and must never be mistaken for one.
    Scanning the whole output for the bare token "FAIL" is exactly that
    mistake: it turned a WARN about an expired Blotato grant into a false
    "the pre-flight blocked the post".
    """
    return any(l.strip().startswith("FAIL") for l in out.splitlines())


def rewrite_targets(fb_text, targets):
    """Replace the TARGETS block with the given platforms."""
    block = "const TARGETS = [\n"
    for acct, plat in targets:
        block += "  { accountId: '%s', platform: '%s', media: [] },\n" % (acct, plat)
    block += "];"
    return re.sub(r"const\s+TARGETS\s*=\s*\[.*?\];", block, fb_text, count=1, flags=re.S)


print("=== A. real fallback TARGETS (linkedin, threads) + no media -> WARN not FAIL ===")
out = run_preflight()
has_fail_media = "no media image" in out and has_blocking(out)
check("A. missing media is NOT a blocking FAIL with the real targets",
      not has_fail_media,
      "no FAIL for media" if not has_fail_media else out[-400:])
check("A. the WARN explains WHY it is safe",
      "none of them require an image" in out or "no media image, but the fallback" in out)
check("A. pre-flight reports no blocking issue",
      "RESULT: pre-flight CLEAN" in out,
      out.strip().splitlines()[-1] if out.strip() else "no output")

print("\n=== B. if Instagram is added to the TARGETS, missing media must FAIL again ===")
# Build a temp fallback with instagram added, and point the pre-flight at it.
tmp = tempfile.mkdtemp(prefix="media-ig-")
try:
    fb_copy = pathlib.Path(tmp) / "blotato-fallback.js"
    shutil.copy(FB, fb_copy)
    fb_copy.write_text(
        rewrite_targets(fb_copy.read_text(encoding="utf8"),
                        [("26628", "linkedin"), ("7701", "threads"), ("76978", "instagram")]),
        encoding="utf8")
    pf_copy = pathlib.Path(tmp) / "preflight-daily-post.py"
    shutil.copy(PF, pf_copy)
    src = pf_copy.read_text(encoding="utf8")
    src = src.replace(
        'FB_SCRIPT = pathlib.Path(\n    "/workspace/studex-content-automation/scripts/blotato-fallback.js")',
        'FB_SCRIPT = pathlib.Path(%r)' % str(fb_copy))
    pf_copy.write_text(src, encoding="utf8")
    r = subprocess.run([sys.executable, str(pf_copy), "2026-10-23"],
                       capture_output=True, text=True, timeout=180)
    out_b = r.stdout + r.stderr
    check("B. with Instagram as a target, missing media IS a FAIL",
          ("no media image" in out_b and "requires one" in out_b and has_blocking(out_b)),
          "FAIL raised as expected" if "requires one" in out_b else out_b[-400:])
    check("B. it names the offending platform", "instagram" in out_b)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== C. NEGATIVE CONTROL: the OLD blanket implementation FAILS case A ===")
tmp = tempfile.mkdtemp(prefix="media-old-")
try:
    pf_copy = pathlib.Path(tmp) / "preflight-daily-post.py"
    shutil.copy(PF, pf_copy)
    src = pf_copy.read_text(encoding="utf8")
    # Restore the old blanket behaviour.
    src = re.sub(
        r"            else:\n                # Is any IMAGE-REQUIRING.*?added as a target\.\"\)\n",
        "            else:\n                fail(\"pending file has no media image - the post would publish \"\n                     \"without a picture.\")\n",
        src, count=1, flags=re.S)
    pf_copy.write_text(src, encoding="utf8")
    r = subprocess.run([sys.executable, str(pf_copy), "2026-10-23"],
                       capture_output=True, text=True, timeout=180)
    out_c = r.stdout + r.stderr
    check("C. OLD implementation blocks the publish (control is real)",
          "without a picture" in out_c,
          "old impl FAILs as expected" if "without a picture" in out_c else out_c[-300:])
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== D. rule [10]: a caption WITH a price must FAIL the pre-flight ===")
# The pre-flight is the LAST gate before the pending caption is published,
# and path B (the content agent) has NO price guard of its own. So this check
# is the only thing standing between a staged price and the public feed.
# Live proof of the breach: the 2026-10-22 caption published R1,450 publicly
# (IG 8383092 + Threads 8383081) while every status stayed green.
tmp_d = tempfile.mkdtemp(prefix="media-price-")
try:
    priced = _write_price_free_pending(
        tmp_d, caption="Wagyu Biltong Gold 1kg. R1,450 for the case. Order now.")
    pf_copy = pathlib.Path(tmp_d) / "preflight-daily-post.py"
    shutil.copy(PF, pf_copy)
    src = pf_copy.read_text(encoding="utf8")
    src = src.replace(
        'pending = ROOT / "studex-content-automation" / "posts" / "pending" / f"{date_str}.json"',
        'pending = pathlib.Path(%r)' % str(priced),
    )
    src = src.replace(
        'pend_path = ROOT / "studex-content-automation" / "posts" / "pending" / f"{date_str}.json"',
        'pend_path = pathlib.Path(%r)' % str(priced),
    )
    pf_copy.write_text(src, encoding="utf8")
    r = subprocess.run([sys.executable, str(pf_copy), "2026-10-23"],
                       capture_output=True, text=True, timeout=180)
    out_d = r.stdout + r.stderr
    check("D. a priced caption FAILS the pre-flight",
          ("carries a price" in out_d and has_blocking(out_d)),
          "price FAIL raised" if "carries a price" in out_d else out_d[-400:])
    check("D. it names the rule", "rule [10]" in out_d, out_d[-300:])
    check("D. it names the amount", "R1,450" in out_d, out_d[-300:])
    check("D. the pre-flight reports a blocking issue",
          "blocking issue" in out_d, out_d.strip().splitlines()[-1] if out_d.strip() else "")

    # NEGATIVE CONTROL: the same caption with the price removed must NOT fail.
    clean = _write_price_free_pending(tmp_d, caption="Wagyu Biltong Gold 1kg. Order now.")
    pf2 = pathlib.Path(tmp_d) / "preflight-clean.py"
    shutil.copy(PF, pf2)
    src2 = pf2.read_text(encoding="utf8")
    src2 = src2.replace(
        'pending = ROOT / "studex-content-automation" / "posts" / "pending" / f"{date_str}.json"',
        'pending = pathlib.Path(%r)' % str(clean),
    )
    src2 = src2.replace(
        'pend_path = ROOT / "studex-content-automation" / "posts" / "pending" / f"{date_str}.json"',
        'pend_path = pathlib.Path(%r)' % str(clean),
    )
    pf2.write_text(src2, encoding="utf8")
    r2 = subprocess.run([sys.executable, str(pf2), "2026-10-23"],
                        capture_output=True, text=True, timeout=180)
    out_d2 = r2.stdout + r2.stderr
    check("D. CONTROL: the same caption WITHOUT a price does not fail",
          "carries a price" not in out_d2,
          "no price FAIL" if "carries a price" not in out_d2 else out_d2[-300:])
finally:
    shutil.rmtree(tmp_d, ignore_errors=True)

print("\n=== E. the RESULT line must not name a publish that already fired ===")
# The same script runs twice a day: 08:00 SAST pre-flights path A (the 09:00
# publish) and 09:20 SAST audits path B AFTER 09:00 has already run. A shared
# "the 09:00 SAST publish would go out wrong" line is false in the 09:20 run -
# it reads as "a bad post went out at 09:00" when the 09:00 post was fine and
# the real risk is the pending caption. The wording must follow the clock.
import datetime as _dt
_now_sast = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=2)))
_after_0900 = _now_sast.hour * 60 + _now_sast.minute >= 9 * 60
_res_e = run_preflight()  # clean fixture, so no FAIL branch is exercised
check("E. the pre-flight source contains clock-dependent RESULT wording",
      "would go out wrong" in PF.read_text(encoding="utf8")
      and "has already run" in PF.read_text(encoding="utf8"),
      "both wordings present in source")
# Exercise the FAIL branch with a priced caption and check which wording fired.
_tmp_e = tempfile.mkdtemp(prefix="media-word-")
try:
    _priced_e = _write_price_free_pending(
        _tmp_e, caption="Wagyu Biltong Gold 1kg. R1,450 for the case. Order now.")
    _pf_e = pathlib.Path(_tmp_e) / "preflight-e.py"
    shutil.copy(PF, _pf_e)
    _s = _pf_e.read_text(encoding="utf8")
    _s = _s.replace(
        'pending = ROOT / "studex-content-automation" / "posts" / "pending" / f"{date_str}.json"',
        'pending = pathlib.Path(%r)' % str(_priced_e),
    )
    _s = _s.replace(
        'pend_path = ROOT / "studex-content-automation" / "posts" / "pending" / f"{date_str}.json"',
        'pend_path = pathlib.Path(%r)' % str(_priced_e),
    )
    # 🔑 INJECT THE CLOCK. The old test branched on the WALL CLOCK, so it
    # only passed in the second half of every day: after 09:00 SAST it
    # expected the PAST wording, before 09:00 it expected the pre-09:00
    # wording. But the pre-flight keys its wording off the TARGET DATE -
    # for a PAST target the publish has already run whatever the time is -
    # so the "before 09:00" expectation was simply wrong, and this test
    # FAILED on every run between midnight and 09:00 SAST.
    # The clock is now injected, and every case is asserted unconditionally.
    _s = _pf_e.read_text(encoding="utf8")
    _s = _s.replace("now_sast = dp.datetime.now(dp.SAST)",
                    "now_sast = dp.datetime(2026, 10, 27, 8, 0, tzinfo=dp.SAST)")
    _pf_e.write_text(_s, encoding="utf8")
    _r = subprocess.run([sys.executable, str(_pf_e), "2026-10-23"],
                        capture_output=True, text=True, timeout=180)
    _out_e = _r.stdout + _r.stderr
    check("E. a PAST target date says the 09:00 publish already ran, "
          "whatever the wall clock is",
          "has already run" in _out_e and "would go out wrong" not in _out_e,
          "correct: PAST wording" if "has already run" in _out_e
          else _out_e[-300:])

    # TODAY, clock injected at 08:00 -> the pre-09:00 wording must appear.
    # 🔑 REBUILD FROM THE PRISTINE SOURCE. The previous case already wrote
    # the 08:00 injection into _pf_e, so a second replace of the same
    # string was a SILENT NO-OP and the 10:00 case below was still running
    # the 08:00 clock. It passed only by accident.
    def _run_e(date_str, y, mo, d, h, mi):
        _pf_x = pathlib.Path(_tmp_e) / ("preflight-e-%s-%02d%02d.py"
                                         % (date_str, h, mi))
        shutil.copy(PF, _pf_x)
        _sx = _pf_x.read_text(encoding="utf8")
        _sx = _sx.replace(
            'pending = ROOT / "studex-content-automation" / "posts" / "pending" / f"{date_str}.json"',
            'pending = pathlib.Path(%r)' % str(_priced_e))
        _sx = _sx.replace(
            'pend_path = ROOT / "studex-content-automation" / "posts" / "pending" / f"{date_str}.json"',
            'pend_path = pathlib.Path(%r)' % str(_priced_e))
        _sx = _sx.replace(
            "now_sast = dp.datetime.now(dp.SAST)",
            "now_sast = dp.datetime(%d, %d, %d, %d, %d, tzinfo=dp.SAST)"
            % (y, mo, d, h, mi))
        _pf_x.write_text(_sx, encoding="utf8")
        _rx = subprocess.run([sys.executable, str(_pf_x), date_str],
                             capture_output=True, text=True, timeout=180)
        return _rx.stdout + _rx.stderr

    _out_t1 = _run_e("2026-10-27", 2026, 10, 27, 8, 0)
    check("E. TODAY before 09:00 SAST names the 09:00 publish",
          "would go out wrong" in _out_t1,
          "correct: pre-09:00 wording" if "would go out wrong" in _out_t1
          else _out_t1[-300:])

    # TODAY, clock injected at 10:00 -> it must NOT claim it would go out wrong.
    _out_t2 = _run_e("2026-10-27", 2026, 10, 27, 10, 0)
    check("E. TODAY after 09:00 SAST does NOT claim the 09:00 publish "
          "would go out",
          "would go out wrong" not in _out_t2,
          "correct: post-09:00 wording" if "would go out wrong" not in _out_t2
          else _out_t2[-300:])
finally:
    shutil.rmtree(_tmp_e, ignore_errors=True)

print("\n=== F. the pre-flight must not CRASH when the pending file is absent ===")
# Regression: the missing-pending branch used `datetime.now(SAST)`, but this
# module never imports datetime/SAST - they live in the daily_post module as
# dp.datetime / dp.SAST. So the 08:00 SAST run (when the pending file
# legitimately does not exist yet) died with a NameError instead of printing
# "expected at this time" - and the whole pre-flight aborted, taking every
# later check with it. Proven with a negative control: the pre-fix source
# raised "NameError: name 'datetime' is not defined".
_tmp_f = tempfile.mkdtemp(prefix="media-nopending-")
try:
    _missing = pathlib.Path(_tmp_f) / "does-not-exist.json"
    _pf_f = pathlib.Path(_tmp_f) / "preflight-f.py"
    shutil.copy(PF, _pf_f)
    _s = _pf_f.read_text(encoding="utf8")
    _s = _s.replace(
        'pending = ROOT / "studex-content-automation" / "posts" / "pending" / f"{date_str}.json"',
        'pending = pathlib.Path(%r)' % str(_missing),
    )
    _s = _s.replace(
        'pend_path = ROOT / "studex-content-automation" / "posts" / "pending" / f"{date_str}.json"',
        'pend_path = pathlib.Path(%r)' % str(_missing),
    )
    _pf_f.write_text(_s, encoding="utf8")
    _r = subprocess.run([sys.executable, str(_pf_f), "2026-10-23"],
                        capture_output=True, text=True, timeout=180)
    _out_f = _r.stdout + _r.stderr
    check("F. no NameError when the pending file is absent",
          "NameError" not in _out_f,
          "no crash" if "NameError" not in _out_f else _out_f[-300:])
    check("F. it explains the missing pending file instead of crashing",
          "pending file" in _out_f,
          "diagnostic present" if "pending file" in _out_f else _out_f[-300:])
    # And the pre-fix source must still crash - otherwise this test proves nothing.
    _pf_fold = pathlib.Path(_tmp_f) / "preflight-old.py"
    shutil.copy(PF, _pf_fold)
    _s2 = _pf_fold.read_text(encoding="utf8")
    _s2 = _s2.replace("now_sast = dp.datetime.now(dp.SAST)",
                       "now_sast = datetime.now(SAST)")
    _pf_fold.write_text(_s2, encoding="utf8")
    _r2 = subprocess.run([sys.executable, str(_pf_fold), "2026-10-23"],
                         capture_output=True, text=True, timeout=180)
    _out_f2 = _r2.stdout + _r2.stderr
    check("F. CONTROL: the pre-fix source DOES crash (the bug was real)",
          "NameError" in _out_f2,
          "old source raises NameError" if "NameError" in _out_f2 else _out_f2[-300:])
finally:
    shutil.rmtree(_tmp_f, ignore_errors=True)

print("\n" + "=" * 60)
print(f"{len(PASSED)} passed, {len(FAILED)} failed")
if FAILED:
    print("FAILURES:", FAILED)
    sys.exit(1)
print("the media check is target-aware: it warns when it is safe, fails when it is not")
