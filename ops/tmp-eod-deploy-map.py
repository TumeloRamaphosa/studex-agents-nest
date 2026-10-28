#!/usr/bin/env python3
"""EOD 2026-10-26 — one bounded lookup: which live URL serves the studex-ciie-coffee build
(the local dist that still carries the booth / Hall-Stand / 145.7 claims)?

Searches only the workspace's own deploy bookkeeping files (ops/*.json, ops/*.tsv, *.md deploy
ledgers) for the string 'studex-ciie-coffee'. One run -> printed answer.
"""
import json, os, re

ROOT = "/workspace"
HITS = []

def scan(p):
    try:
        t = open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return
    if "studex-ciie-coffee" in t:
        urls = sorted(set(re.findall(r"https://[a-z0-9]+\.space\.mcode\.io", t)))
        HITS.append({"file": os.path.relpath(p, ROOT), "urls": urls})

for d, _, files in os.walk(ROOT):
    if any(part in d for part in ("/node_modules", "/.git", "/dist")):
        continue
    for fn in files:
        if fn.endswith((".json", ".tsv", ".md", ".txt", ".yaml", ".yml", ".py", ".sh")):
            scan(os.path.join(d, fn))

# also check the deploy manifest sources: is studex-ciie-coffee a source of any manifest page?
man = json.load(open(os.path.join(ROOT, "ops/drift-manifest.json")))
manifest_sources = {p.get("source"): p.get("url") for p in man.get("pages", [])}

print("=== files mentioning studex-ciie-coffee ===")
for h in HITS:
    print(f"  {h['file']}  urls={h['urls']}")
print("\n=== manifest sources ===")
for s, u in manifest_sources.items():
    print(f"  {s} -> {u}")
print("\nstudex-ciie-coffee in manifest:", manifest_sources.get("studex-ciie-coffee/dist"),
      "|", manifest_sources.get("studex-ciie-coffee"))
json.dump({"hits": HITS, "manifest_sources": manifest_sources},
          open(os.path.join(ROOT, "memory/2026-10-26-eod-deploy-map.json"), "w"), indent=2)
