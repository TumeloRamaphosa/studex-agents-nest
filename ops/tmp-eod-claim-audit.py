#!/usr/bin/env python3
"""EOD 2026-10-26 — bounded claim audit (live copy + local page sources).

Answers one question: which CIIE-booth / growth-surge claims are still present in files a
buyer or a public deploy could reach? One run, one JSON output.
"""
import json, os, re

ROOT = "/workspace"
OUT = os.path.join(ROOT, "memory", "2026-10-26-eod-claim-audit.json")

PATTERNS = {
    "EXHIBITING_CLAIM": r"[Ww]e[\u2019']?re exhibiting|will be exhibiting|our booth|CIIE booth",
    "APPLY_INSTRUCTION": r"exhibitor registration|APPLY at ciie",
    "STATUS_NOT_APPLIED": r"NOT YET APPLIED",
    "HALL_STAND": r"Hall\s*\d+\.\d+|Stand\s*[A-Z0-9\-]{3,}",
    "SURGE_145": r"145\.7",
}

# 1. live copy files
COPY = [
    "china-coffee-sheet-copy-paste.md",
    "china-coffee-outreach.md",
    "ciie-bundle-pitch.md",
    "ciie-nurture/prospects.json",
    "ciie-nurture/send-sequence.js",
]

# 2. local page sources that ship to public deploys
PAGE_DIRS = [
    "ciie-buyer-brief/src",
    "ciie-coffee-landing/src",
    "ciie-nurture/src",
    "studex-ciie-coffee/src",
]

result = {"copy_files": {}, "page_sources": {}, "public_dist": {}}

def scan(path, base):
    rec = {"claims": {}}
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except Exception as e:
        rec["error"] = str(e)
        return rec
    for name, pat in PATTERNS.items():
        hits = []
        for m in re.finditer(pat, text):
            ln = text.count("\n", 0, m.start()) + 1
            snip = text[max(0, m.start() - 70): m.start() + 70].replace("\n", " ")
            hits.append({"line": ln, "snippet": snip})
        rec["claims"][name] = {"count": len(hits), "hits": hits[:5]}
    return rec

for rel in COPY:
    p = os.path.join(ROOT, rel)
    if os.path.exists(p):
        result["copy_files"][rel] = scan(p, ROOT)

for d in PAGE_DIRS:
    full = os.path.join(ROOT, d)
    if not os.path.isdir(full):
        continue
    for dirpath, _, files in os.walk(full):
        for fn in files:
            if not fn.endswith((".tsx", ".ts", ".jsx", ".js", ".html", ".md")):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
            r = scan(os.path.join(dirpath, fn), ROOT)
            if any(v["count"] for v in r.get("claims", {}).values()):
                result["page_sources"][rel] = r

# 3. built dist bundles that are already deployed publicly
for d in ["ciie-buyer-brief/dist", "ciie-coffee-landing/dist", "studex-ciie-coffee/dist"]:
    full = os.path.join(ROOT, d)
    if not os.path.isdir(full):
        continue
    for dirpath, _, files in os.walk(full):
        for fn in files:
            if not fn.endswith((".js", ".html")):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
            r = scan(os.path.join(dirpath, fn), ROOT)
            if any(v["count"] for v in r.get("claims", {}).values()):
                result["public_dist"][rel] = r

json.dump(result, open(OUT, "w"), indent=2)
print("wrote", OUT)
print("\n-- COPY FILES --")
for f, r in result["copy_files"].items():
    hits = {k: v["count"] for k, v in r.get("claims", {}).items() if v["count"]}
    print(f, "->", hits or "clean")
print("\n-- PAGE SOURCES (local, would ship to a public deploy) --")
for f, r in result["page_sources"].items():
    hits = {k: v["count"] for k, v in r.get("claims", {}).items() if v["count"]}
    print(f, "->", hits)
print("\n-- BUILT DIST (already deployed) --")
for f, r in result["public_dist"].items():
    hits = {k: v["count"] for k, v in r.get("claims", {}).items() if v["count"]}
    print(f, "->", hits)
