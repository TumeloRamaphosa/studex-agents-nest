#!/usr/bin/env python3
"""
test-client-secret-exposure.py — proves the client-secret guard actually fires.

A checker without positive and negative controls is unusable: it may pass for
the wrong reason, and "the suite is green" then means nothing.

Controls:
  1. NEGATIVE  a client file reading a non-secret VITE_ var  -> CLEAN (exit 0)
  2. POSITIVE  a client file reading VITE_CLICKUP_TOKEN     -> DRIFT (exit 1)
  3. ALLOWLIST VITE_SUPABASE_ANON_KEY                       -> CLEAN (exit 0)
  4. BRACKETS  import.meta.env['VITE_SHOPIFY_ACCESS_TOKEN'] -> DRIFT (exit 1)
  5. UNCHECKED an empty tree                                -> UNCHECKED (exit 2)
  6. SKIPPED   a secret read inside node_modules/           -> CLEAN (exit 0)
  7. LIVE      the real /workspace tree                     -> CLEAN (exit 0)

🔑 Every fixture is written to a TEMP SANDBOX. The rule-proving test must never
write into the live tree it checks - that is how the drift-rules test left a
deliberately-bad draft sitting in the live outbound-drafts approval queue.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKER = Path(__file__).resolve().parent / "check-client-secret-exposure.py"
LIVE_ROOT = Path("/workspace")

passed = 0
failed = 0


def report(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"PASS  {name}")
    else:
        failed += 1
        print(f"FAIL  {name}  {detail}")


def run_checker(root: Path):
    env = dict(os.environ)
    env["CLIENT_SECRET_CHECK_ROOT"] = str(root)
    p = subprocess.run(
        [sys.executable, str(CHECKER)],
        env=env, capture_output=True, text=True, timeout=120,
    )
    return p.returncode, (p.stdout + p.stderr)


def make_tree(files: dict) -> Path:
    d = Path(tempfile.mkdtemp(prefix="client-secret-check-"))
    for rel, content in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf8")
    return d


# ---------------------------------------------------------------- controls
def t_negative():
    root = make_tree({"src/App.tsx": "const u = import.meta.env.VITE_LEAD_PROXY_URL;\n"})
    code, out = run_checker(root)
    report("NEGATIVE  non-secret VITE_ var -> CLEAN", code == 0 and "CLEAN" in out, f"exit={code} {out[:120]}")


def t_positive():
    root = make_tree({"src/ClickUpTasks.tsx": "const T = import.meta.env.VITE_CLICKUP_TOKEN as string;\n"})
    code, out = run_checker(root)
    report("POSITIVE  VITE_CLICKUP_TOKEN -> DRIFT", code == 1 and "DRIFT" in out, f"exit={code} {out[:120]}")


def t_allowlist():
    root = make_tree({"src/db.ts": "const k = import.meta.env.VITE_SUPABASE_ANON_KEY;\n"})
    code, out = run_checker(root)
    report("ALLOWLIST VITE_SUPABASE_ANON_KEY -> CLEAN", code == 0 and "CLEAN" in out, f"exit={code} {out[:120]}")


def t_brackets():
    root = make_tree({"src/DeliveryKPIs.tsx": "const t = import.meta.env['VITE_SHOPIFY_ACCESS_TOKEN'];\n"})
    code, out = run_checker(root)
    report("BRACKETS  bracket notation -> DRIFT", code == 1 and "DRIFT" in out, f"exit={code} {out[:120]}")


def t_unchecked():
    root = make_tree({})
    code, out = run_checker(root)
    report("UNCHECKED empty tree -> UNCHECKED (not CLEAN)", code == 2 and "UNCHECKED" in out, f"exit={code} {out[:120]}")


def t_skipped_dir():
    # a secret read inside node_modules/ must be IGNORED, while a real client file
    # is still scanned - so the tree must contain both, or the answer is UNCHECKED
    root = make_tree({
        "node_modules/pkg/index.js": "const t = import.meta.env.VITE_CLICKUP_TOKEN;\n",
        "src/App.tsx": "const u = import.meta.env.VITE_LEAD_PROXY_URL;\n",
    })
    code, out = run_checker(root)
    report("SKIPPED   node_modules secret read ignored, real file scanned -> CLEAN",
           code == 0 and "CLEAN" in out, f"exit={code} {out[:160]}")


def t_live():
    code, out = run_checker(LIVE_ROOT)
    report("LIVE      /workspace -> CLEAN", code == 0 and "CLEAN" in out, f"exit={code} {out[:400]}")


for fn in (t_negative, t_positive, t_allowlist, t_brackets, t_unchecked, t_skipped_dir, t_live):
    try:
        fn()
    except Exception as e:  # noqa: BLE001
        report(fn.__name__, False, f"exception: {e}")

print()
print(f"{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
