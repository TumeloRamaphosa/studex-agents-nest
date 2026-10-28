#!/usr/bin/env python3
"""Negative-test the SPA bundle check in ops/drift-check.py.

A checker that cannot fail is trusted for nothing. Four cases, all against the
REAL check_spa() imported from the production script:

  control  a clean bundle + a live page serving that build  -> CLEAN
  A        a forbidden string inside the bundle             -> DRIFT
  B        the live page serving an OLDER bundle             -> DRIFT (STALE BUILD)
  C        a page with no assertions at all                 -> DRIFT (UNCHECKED)

Usage: python3 ops/test-spa-bundle-check.py
"""
import importlib.util, json, pathlib, shutil, sys, tempfile

ROOT = pathlib.Path("/workspace")

spec = importlib.util.spec_from_file_location("driftcheck", ROOT / "ops" / "drift-check.py")
dc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dc)

fails = []


def build_bundle(tmp: pathlib.Path, js_name: str, body: str):
    dist = tmp / "dist"
    (dist / "assets").mkdir(parents=True, exist_ok=True)
    (dist / "assets" / js_name).write_text(body, encoding="utf8")
    (dist / "index.html").write_text(
        f'<!doctype html><html><head><script type="module" '
        f'src="/assets/{js_name}"></script></head><body></body></html>', encoding="utf8")
    return dist


def run(dist, live_html, page=None):
    p = page or {"name": "Test SPA", "url": "https://example.space.mcode.io",
                 "must": [], "must_not": ["Rainforest Alliance"], "spa": True}
    return dc.check_spa(p, live_html, dist=str(dist))


with tempfile.TemporaryDirectory() as td:
    tmp = pathlib.Path(td)

    # ---------------- control ----------------
    dist = build_bundle(tmp / "ctl", "index-AAA111.js", "var x='Studex Meat';")
    live = '<html><script src="/assets/index-AAA111.js"></script></html>'
    r = run(dist, live)
    ok = r["state"] == "CLEAN"
    print(f"  [{'PASS' if ok else 'FAIL'}] control: clean bundle, live serves this build -> CLEAN "
          f"(got {r['state']})")
    if not ok:
        fails.append("control")
        print("        issues:", r["issues"])

    # ---------------- A: forbidden string in the bundle ----------------
    dist = build_bundle(tmp / "forb", "index-BBB222.js",
                        "var x='Rainforest Alliance certified';")
    live = '<html><script src="/assets/index-BBB222.js"></script></html>'
    r = run(dist, live)
    caught = r["state"] == "DRIFT" and any("FORBIDDEN PRESENT" in i for i in r["issues"])
    print(f"  [{'PASS' if caught else 'FAIL'}] A: forbidden string in the bundle caught "
          f"(got {r['state']})")
    if not caught:
        fails.append("A")
    for i in r["issues"]:
        print(f"        - {i}")

    # ---------------- B: live site serving an OLDER bundle ----------------
    dist = build_bundle(tmp / "stale", "index-CCC333.js", "var x='Studex Meat';")
    live = '<html><script src="/assets/index-OLD999.js"></script></html>'
    r = run(dist, live)
    caught = r["state"] == "DRIFT" and any("STALE BUILD" in i for i in r["issues"])
    print(f"  [{'PASS' if caught else 'FAIL'}] B: live serving an older bundle caught "
          f"(got {r['state']})")
    if not caught:
        fails.append("B")
    for i in r["issues"]:
        print(f"        - {i}")

    # ---------------- C: zero assertions ----------------
    dist = build_bundle(tmp / "noassert", "index-DDD444.js", "var x='Studex Meat';")
    live = '<html><script src="/assets/index-DDD444.js"></script></html>'
    page = {"name": "No assertions", "url": "https://example.space.mcode.io",
            "must": [], "must_not": [], "spa": True}
    r = run(dist, live, page=page)
    caught = r["state"] == "DRIFT" and any("NO ASSERTIONS" in i for i in r["issues"])
    print(f"  [{'PASS' if caught else 'FAIL'}] C: a page with no assertions caught "
          f"(got {r['state']})")
    if not caught:
        fails.append("C")
    for i in r["issues"]:
        print(f"        - {i}")

    # ---------------- D: a required string missing from the bundle ----------------
    dist = build_bundle(tmp / "miss", "index-EEE555.js", "var x='Studex Meat';")
    live = '<html><script src="/assets/index-EEE555.js"></script></html>'
    page = {"name": "Missing required", "url": "https://example.space.mcode.io",
            "must": ["info@studexmeat.com"], "must_not": [], "spa": True}
    r = run(dist, live, page=page)
    caught = r["state"] == "DRIFT" and any("MISSING" in i for i in r["issues"])
    print(f"  [{'PASS' if caught else 'FAIL'}] D: a required string missing from the bundle caught "
          f"(got {r['state']})")
    if not caught:
        fails.append("D")
    for i in r["issues"]:
        print(f"        - {i}")

print()
if fails:
    print(f"RESULT: {len(fails)} FAILURE(S): {fails}")
    sys.exit(1)
print("RESULT: the SPA bundle check provably fails on every failure mode")
