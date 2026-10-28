#!/usr/bin/env python3
"""End-to-end proof that no markdown reaches a live social post.

THE DEFECT THIS GUARDS:
Live post 8384191 (Instagram) and 8384240 (Threads) shipped with literal '**'
in the caption. Two separate causes:
  1. The Threads 500-char limit cut a bold span IN HALF. The opening '**' lost
     its closing partner, so the pair regex could no longer match it, and the
     asterisks survived onto the live post.
  2. A platform-specific suffix was appended AFTER sanitising, re-introducing
     markup.

Two paths can publish:
  - scripts/daily-post.py       -> build_platform_texts() then truncate
  - studex-content-automation/scripts/blotato-fallback.js -> its own sanitize()

IMPORTANT: this test CALLS THE REAL CODE. The first version of this file
re-implemented the pipeline inline, which meant it stayed green even when the
real script was broken — a test that mirrors the thing it tests proves
nothing. daily-post.py now exposes build_platform_texts() precisely so the
exact text that ships can be checked without publishing anything.

Run: python3 ops/test-publish-sanitize.py
"""
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
QUEUE = [
    "memory/post-queue/2026-10-22-thursday-business.md",
    "memory/post-queue/2026-10-23-friday-agents.md",
]
RESIDUE = re.compile(r"\*\*|__|`|^\s*>", re.M)

# A BUILT-IN hostile caption, always tested regardless of what is in the queue
# directory. It contains every construct the sanitiser exists to handle:
#   - a bold span that WRAPS A NEWLINE  (needs re.DOTALL to match)
#   - an UNPAIRED '**' marker            (only the final net can catch it)
#   - '__underscore__' and '`backticks`' (marker stripping)
#   - a '> ' blockquote prefix           (prefix stripping)
# Without this, the test only proves what the queue files happen to contain,
# and a guard could be removed without the test noticing.
HOSTILE = (
    "**Bold that wraps\nacross a newline** and then an unpaired ** marker at the end.\n"
    "Some __underscored text__ and some `backticked text` here.\n"
    "> A blockquoted line that must lose its prefix.\n"
    "#StudexGM info@studexmeat.com\n"
)


def load_daily_post():
    spec = importlib.util.spec_from_file_location("dp", ROOT / "scripts" / "daily-post.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fallback_sanitize(content):
    """Run the fallback script's OWN sanitize() under node, verbatim."""
    js = (ROOT / "studex-content-automation" / "scripts" / "blotato-fallback.js").read_text(encoding="utf8")
    m = re.search(r"function sanitize\(text\) \{.*?\n\}", js, re.S)
    if not m:
        raise SystemExit("!! fallback sanitize() not found - it must not be removed")
    harness = m.group(0) + r"""
const fs = require('fs');
const raw = fs.readFileSync(process.argv[2], 'utf8');
process.stdout.write(sanitize(raw));
"""
    pathlib.Path("/tmp/pub_san_harness.js").write_text(harness, encoding="utf8")
    src = pathlib.Path("/tmp/pub_san_input.md")
    src.write_text(content, encoding="utf8")
    r = subprocess.run(["node", "/tmp/pub_san_harness.js", str(src)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("node harness failed: " + r.stderr[:400])
    return r.stdout


def fallback_truncate(text, maxlen=500):
    """The fallback's own 500-char truncate, with emoji counted as 2."""
    def weight(ch):
        cp = ord(ch)
        return 2 if (cp > 0x2E80 or (0x1F300 <= cp <= 0x1FAFF)) else 1
    out, n = "", 0
    for ch in text:
        w = weight(ch)
        if n + w > maxlen - 3:
            break
        out += ch
        n += w
    return out.rstrip(" ,.") + "..."


def main():
    dp = load_daily_post()
    fails = []
    checked = 0

    cases = []
    for q in QUEUE:
        p = ROOT / q
        if not p.exists():
            print(f"  [SKIP] {q} not found")
            continue
        md = p.read_text(encoding="utf8")
        m = re.search(r"##\s*Generated Post Content\s*\n+(.*?)\n---", md, re.S)
        cases.append((p.name, m.group(1).strip() if m else md))
    # the built-in hostile caption is ALWAYS tested, so a guard cannot be
    # removed without the test noticing
    cases.append(("[hostile built-in]", HOSTILE))

    for label, content in cases:
        print(f"\n  {label}  (source len={len(content)}, '**'={content.count('**')})")

        # --- path 1: the REAL daily-post.py code
        for platform, text in dp.build_platform_texts(content).items():
            checked += 1
            bad = RESIDUE.search(text)
            if bad:
                fails.append(f"{label} daily-post/{platform}: {bad.group(0)!r}")
            print(f"    [{'PASS' if not bad else 'FAIL'}] daily-post  {platform:9} len={len(text):5} "
                  f"residue={(bad.group(0) if bad else 'none')!r}")

        # --- path 2: the REAL fallback sanitize(), then its own truncate
        t = fallback_sanitize(content)
        for sub, text in (("pre-trunc", t), ("threads", fallback_truncate(t))):
            checked += 1
            bad = RESIDUE.search(text)
            if bad:
                fails.append(f"{label} fallback/{sub}: {bad.group(0)!r}")
            print(f"    [{'PASS' if not bad else 'FAIL'}] fallback    {sub:9} len={len(text):5} "
                  f"residue={(bad.group(0) if bad else 'none')!r}")

    print(f"\n  checked {checked} output(s) across {len(cases)} caption(s)")
    if fails:
        print(f"  RESULT: {len(fails)} FAILURE(S):")
        for f in fails:
            print("    - " + f)
        sys.exit(1)
    print("  RESULT: no markdown residue in any publish path — all clear")


if __name__ == "__main__":
    main()
