#!/usr/bin/env python3
"""EOD 2026-10-26 — bounded fact check of the live China copy before the vault log is written.

One script, one output file. Checks the two live copy files + the drift manifest for the
claim classes tonight's research brief says are now wrong.
"""
import json, os, re

ROOT = "/workspace"
OUT = os.path.join(ROOT, "memory", "2026-10-26-eod-fact-check.json")

FILES = {
    "sheet": os.path.join(ROOT, "china-coffee-sheet-copy-paste.md"),
    "outreach": os.path.join(ROOT, "china-coffee-outreach.md"),
}

CLAIMS = {
    "GROWTH_145": r"145\.7",
    "BOOTH_PROMISE": r"(we'?re exhibiting|our booth|CIIE booth|will be exhibiting|exhibitor registration)",
    "STALE_APPLY": r"NOT YET APPLIED",
    "DEADLINE_PASSED": r"PASSED",
    "HALL_STAND": r"(Hall\s*\d+\.\d+|Stand\s*[A-Z0-9\-]{3,})",
    "PROWTC": r"PROWTC",
    "RAINFOREST": r"Rainforest",
    "WILDLIFE": r"Wildlife Verified",
    "STALE_PRICE_480": r"USD ?4\.80",
    "WINDOW_JUL20": r"window opens July 20",
    "CO_CITATION": r"Certificate of Origin",
    "ROASTED_ORIGIN": r"[Rr]oast(ed|ing) at origin",
    "LDC_NO_EXPIRY": r"LDC",
}

result = {"scanned_at": "2026-10-26T22:0x:00Z", "files": {}, "manifest_pages": 0}

for key, path in FILES.items():
    rec = {"path": path, "exists": os.path.exists(path), "claims": {}}
    if rec["exists"]:
        text = open(path, encoding="utf-8", errors="replace").read()
        for name, pat in CLAIMS.items():
            hits = [m.start() for m in re.finditer(pat, text)]
            lines = []
            for h in hits[:4]:
                ln = text.count("\n", 0, h) + 1
                snippet = text[max(0, h - 60): h + 60].replace("\n", " ")
                lines.append({"line": ln, "snippet": snippet})
            rec["claims"][name] = {"count": len(hits), "samples": lines}
    result["files"][key] = rec

# drift manifest page list
try:
    man = json.load(open(os.path.join(ROOT, "ops/drift-manifest.json")))
    result["manifest_pages"] = len(man.get("pages", []))
except Exception as e:
    result["manifest_error"] = str(e)

# build artefacts tonight
for b in ["builds/2026-10-26.md", "research/2026-10-26.md", "memory/2026-10-26.md"]:
    p = os.path.join(ROOT, b)
    result.setdefault("artefacts", {})[b] = {"exists": os.path.exists(p),
                                             "size": os.path.getsize(p) if os.path.exists(p) else 0}

json.dump(result, open(OUT, "w"), indent=2)
print("wrote", OUT)
for key, rec in result["files"].items():
    if rec["exists"]:
        active = {k: v["count"] for k, v in rec["claims"].items() if v["count"]}
        print(key, "->", active)
print("manifest_pages:", result["manifest_pages"])
print("artefacts:", result["artefacts"])
