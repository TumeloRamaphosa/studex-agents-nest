#!/usr/bin/env python3
"""Negative-test ops/test-publish-sanitize.py — prove it can actually FAIL.

THREE EARLIER VERSIONS OF THIS TEST WERE WRONG, and each one failed the same
way: it stayed green while the pipeline was broken.
  v1 injected markdown into the queue file and expected failure. Wrong layer —
     stripping markdown from the source is the sanitiser's whole job.
  v2 mutated the scripts but the test re-implemented the pipeline inline, so
     the test could not see the mutation at all.
  v3 mutated the scripts and the test called the real code, but the fixture
     only had BALANCED '**'. Every safety net masked every mutation, because
     the net only matters for UNPAIRED markers.

THIS VERSION uses a hostile fixture containing every construct the sanitiser
exists to handle:
  - a bold span that WRAPS A NEWLINE   (needs re.DOTALL to match)
  - an UNPAIRED '**' marker             (only the final net can catch it)
  - '__underscore__' and '`backticks`'  (marker stripping)
  - a '> ' blockquote prefix            (prefix stripping)
A correct sanitiser turns all of it into clean text. Each mutation removes one
guard, and each must turn the test RED.

Run: python3 ops/test-publish-sanitize-negative.py
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST_REL = "ops/test-publish-sanitize.py"
DP = "scripts/daily-post.py"
FB = "studex-content-automation/scripts/blotato-fallback.js"
# The caption policy module. daily-post.py imports it and the fallback
# spawns it, so a temp tree that omits it fails at import - which would make
# EVERY case fail for the wrong reason (the control included).
CP = "scripts/caption_policy.py"

# A hostile caption: every construct the sanitiser must handle.
HOSTILE = """## Generated Post Content

**Bold that wraps
across a newline** and then an unpaired ** marker at the end.
Some __underscored text__ and some `backticked text` here.
> A blockquoted line that must lose its prefix.
#StudexGM info@studexmeat.com
---
"""

# (label, relative file, [(old, new), ...])
MUTATIONS = [
    ("A. daily-post: sanitiser bypassed + net removed",
     DP,
     [("    clean = socialize(content)", "    clean = content  # MUTANT"),
      ('        text = text.replace("**", "").replace("__", "").replace("`", "")',
       "        # MUTANT: safety net removed")]),

    ("B. daily-post: bold regex loses re.DOTALL (the 8384191 cause) + net removed",
     DP,
     [('    t = re.sub(r"\\*\\*(.+?)\\*\\*", r"\\1", text, flags=re.S)',
       '    t = re.sub(r"\\*\\*(.+?)\\*\\*", r"\\1", text)  # MUTANT'),
      ('        text = text.replace("**", "").replace("__", "").replace("`", "")',
       "        # MUTANT: safety net removed")]),

    ("C. daily-post: final safety net removed (unpaired '**' survives)",
     DP,
     [('        text = text.replace("**", "").replace("__", "").replace("`", "")',
       "        # MUTANT: safety net removed")]),

    ("D. fallback: its own markdown net removed (unpaired '**' survives)",
     FB,
     [("  t = t.replace(/\\*\\*/g, '');", "  // MUTANT: net removed")]),

    ("E. fallback: pair regex loses the s flag + net removed",
     FB,
     [("  let t = text.replace(/\\*\\*(.+?)\\*\\*/gs, '$1');",
       "  let t = text.replace(/\\*\\*(.+?)\\*\\*/g, '$1'); // MUTANT"),
      ("  t = t.replace(/\\*\\*/g, '');", "  // MUTANT: net removed")]),

    ("F. fallback: blockquote-prefix strip removed",
     FB,
     [("  t = t.replace(/^\\s*>\\s?/gm, '');", "  // MUTANT: blockquote strip removed")]),
]

fails = []


def build_tree(dest, mutate=None):
    (dest / "ops").mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / TEST_REL, dest / TEST_REL)
    for rel in (DP, FB, CP):
        dst = dest / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, dst)
    qdir = dest / "memory" / "post-queue"
    qdir.mkdir(parents=True, exist_ok=True)
    for q in (ROOT / "memory" / "post-queue").glob("*.md"):
        shutil.copy(q, qdir / q.name)
    # the hostile fixture
    (qdir / "2026-10-24-saturday-community.md").write_text(HOSTILE, encoding="utf8")
    if mutate:
        rel, subs = mutate
        p = dest / rel
        t = p.read_text(encoding="utf8")
        for old, new in subs:
            if old not in t:
                raise SystemExit(f"!! mutation target not found in {rel}: {old[:70]!r}")
            t = t.replace(old, new, 1)
        p.write_text(t, encoding="utf8")
    return dest


def run_test(tree):
    return subprocess.run([sys.executable, str(tree / TEST_REL)],
                          capture_output=True, text=True, cwd=str(tree))


with tempfile.TemporaryDirectory() as td:
    tree = build_tree(pathlib.Path(td))
    r = run_test(tree)
    ok = r.returncode == 0
    print(f"  [{'PASS' if ok else 'FAIL'}] control (unmutated, hostile fixture) passes   exit={r.returncode}")
    if not ok:
        fails.append("control")
        print((r.stdout or "")[-1200:])

for label, rel, subs in MUTATIONS:
    with tempfile.TemporaryDirectory() as td:
        tree = build_tree(pathlib.Path(td), mutate=(rel, subs))
        r = run_test(tree)
        red = r.returncode != 0
        reported = "residue" in (r.stdout or "")
        ok = red and reported
        print(f"  [{'PASS' if ok else 'FAIL'}] caught: {label:62} exit={r.returncode}")
        if not ok:
            fails.append(label)
        for l in (r.stdout or "").splitlines():
            if "FAIL" in l and "residue=" in l:
                print(f"          {l.strip()[:130]}")
                break

print()
if fails:
    print(f"RESULT: {len(fails)} FAILURE(S): {fails}")
    sys.exit(1)
print("RESULT: the publish-sanitize test provably goes RED on every pipeline defect")
