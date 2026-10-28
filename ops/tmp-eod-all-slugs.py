#!/usr/bin/env python3
"""EOD 2026-10-26 — the complete live sweep.

Extracts EVERY *.space.mcode.io slug referenced anywhere in the workspace (not just the 14
in the drift manifest), then fetches each one (HTML + its JS bundle) and scans for the claim
classes. One run -> JSON + printed table. This closes the "no gate scans the retired set"
gap for the CIIE booth / Hall-Stand / 145.7 claims.
"""
import json, os, re, urllib.request

ROOT = "/workspace"
OUT = os.path.join(ROOT, "memory/2026-10-26-eod-all-slug-sweep.json")
CLAIMS = {
    "EXHIBITING": r"[Ww]e[\u2019']?re exhibiting|will be exhibiting|our booth|CIIE booth",
    "HALL_STAND": r"Hall\s*\d+\.\d+|Stand\s*[A-Z0-9\-]{3,}",
    "SURGE_145": r"145\.7",
}
SKIP_DIRS = ("/node_modules", "/.git", "/dist", "/.matrix-session-memory")

slugs = set()
pat = re.compile(r"https://([a-z0-9]{10,14})\.space\.mcode\.io")
for d, dirs, files in os.walk(ROOT):
    dirs[:] = [x for x in dirs if not any(s in os.path.join(d, x) for s in SKIP_DIRS)]
    for fn in files:
        if not fn.endswith((".md", ".json", ".html", ".js", ".ts", ".tsx", ".py", ".sh", ".txt", ".tsv")):
            continue
        p = os.path.join(d, fn)
        try:
            t = open(p, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        for m in pat.finditer(t):
            slugs.add(m.group(1))

print("distinct slugs referenced in workspace:", len(slugs))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=18).read().decode("utf-8", "replace")
    for m in re.finditer(r'src="(/assets/[^"]+\.js)"', raw):
        try:
            req2 = urllib.request.Request(url.rstrip("/") + m.group(1), headers={"User-Agent": "Mozilla/5.0"})
            raw += "\n" + urllib.request.urlopen(req2, timeout=18).read().decode("utf-8", "replace")
        except Exception:
            pass
    return raw


results = {}
for slug in sorted(slugs):
    url = f"https://{slug}.space.mcode.io"
    rec = {"reachable": False, "claims": {}}
    try:
        raw = fetch(url)
        rec["reachable"] = True
        rec["bytes"] = len(raw)
        for name, cp in CLAIMS.items():
            ms = list(re.finditer(cp, raw))
            rec["claims"][name] = {
                "count": len(ms),
                "snippet": raw[max(0, ms[0].start() - 90): ms[0].start() + 90].replace("\n", " ") if ms else None,
            }
    except Exception as e:
        rec["error"] = str(e)[:100]
    results[slug] = rec

json.dump({"slugs": sorted(slugs), "results": results}, open(OUT, "w"), indent=2)
print("wrote", OUT, "\n")
flag = False
for slug, rec in results.items():
    if not rec["reachable"]:
        print(f"  {slug}  UNREACHABLE")
        continue
    hits = {k: v["count"] for k, v in rec["claims"].items() if v["count"]}
    if hits:
        flag = True
        print(f"  {slug}  {hits}")
        for k, v in rec["claims"].items():
            if v["count"]:
                print(f"      {k}: ...{v['snippet']}...")
if not flag:
    print("  NO live slug carries the booth / Hall-Stand / 145.7 claims.")
