#!/usr/bin/env python3
"""ops/test-cost-model-exposure.py - prove the exposure checker's grammar.

CONTROLS
  positive  a page whose BUNDLE carries a cost-model token must be EXPOSED (exit 1).
            🔑 The token is in the JS bundle, NOT in the HTML - this is the control that
            catches a checker that only reads the HTML and reports CLEAN while asserting
            nothing. (That is exactly the bug the first version of this checker had.)
  negative  a clean page must NOT be flagged (exit 0).
  near-miss a token that merely LOOKS like one must not match ("farm gates" is not "farm gate").
  case      matching is case-insensitive (FARM GATE must be caught).
  unchecked an empty page list must return UNCHECKED (exit 2), never CLEAN.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "ops" / "check-cost-model-exposure.py"
results = []


def check(label, ok, detail=""):
    results.append((label, ok))
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", label, (" - " + detail) if detail and not ok else ""))


def run(urls, extra_env=None):
    env = dict(os.environ)
    env["COST_MODEL_CHECK_PAGES"] = urls
    if extra_env:
        env.update(extra_env)
    r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True, text=True, env=env, cwd=str(ROOT))
    return r.returncode, r.stdout + r.stderr


with tempfile.TemporaryDirectory() as td:
    d = Path(td)

    # a page whose HTML says nothing but whose bundle leaks the model
    (d / "index.html").write_text("<html><body><div id=root></div><script type=module src=\"bundle.js\"></script></body></html>", encoding="utf8")
    (d / "bundle.js").write_text("const m={farmGateUsdPerKg:1000,landedZarPerKg:23042,floorZarPerKg:32917,marginPct:0.34,belowFloor:true};", encoding="utf8")
    leaky = "file://" + str(d / "index.html")
    rc, out = run(leaky)
    check("positive: cost-model keys in the BUNDLE -> EXPOSED (exit 1)", rc == 1 and "EXPOSED" in out, "rc=%s out=%s" % (rc, out[:300]))
    check("positive: the bundle was actually read (token named in the report)", "farmgateusdperkg" in out.lower() or "farm gate" in out.lower(), out[:300])

    # a clean page
    c = Path(td) / "clean"
    c.mkdir()
    (c / "index.html").write_text("<html><body>Retail prices only.<script type=module src=\"bundle.js\"></script></body></html>", encoding="utf8")
    (c / "bundle.js").write_text("const price={oscietra:4200,kaluga:2800,sevtruga:1600};", encoding="utf8")
    rc, out = run("file://" + str(c / "index.html"))
    check("negative: a clean page is not flagged (exit 0)", rc == 0 and "CLEAN" in out, "rc=%s out=%s" % (rc, out[:300]))

    # a near-miss token
    n = Path(td) / "near"
    n.mkdir()
    (n / "index.html").write_text("<html><body>Fresh farm gates daily.<script type=module src=\"bundle.js\"></script></body></html>", encoding="utf8")
    (n / "bundle.js").write_text("const copy='we sell farm gates and margin floors of produce';", encoding="utf8")
    rc, out = run("file://" + str(n / "index.html"))
    check("near-miss: 'farm gates' is not the token 'farm gate'", rc == 0, "rc=%s out=%s" % (rc, out[:300]))

    # case-insensitivity
    u = Path(td) / "upper"
    u.mkdir()
    (u / "index.html").write_text("<html><body><script type=module src=\"bundle.js\"></script></body></html>", encoding="utf8")
    (u / "bundle.js").write_text("const M={FARMGATEUSDPERKG:1000};", encoding="utf8")
    rc, out = run("file://" + str(u / "index.html"))
    check("case: matching is case-insensitive (FARM_GATE caught)", rc == 1, "rc=%s out=%s" % (rc, out[:300]))

    # empty list -> UNCHECKED, never CLEAN
    rc, out = run("", extra_env={"COST_MODEL_CHECK_PAGES": ""})
    check("unchecked: an empty page list returns UNCHECKED (exit 2), never CLEAN", rc == 2 and "UNCHECKED" in out and "CLEAN" not in out.replace("UNCHECKED", ""), "rc=%s out=%s" % (rc, out[:300]))

failed = [l for l, ok in results if not ok]
print("")
if failed:
    print("RESULT: %d FAILURE(S): %s" % (len(failed), failed))
    sys.exit(1)
print("RESULT: %d passed, 0 failed" % len(results))
