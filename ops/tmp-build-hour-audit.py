#!/usr/bin/env python3
"""Build Hour 2026-10-26 — audit live pages for the three NEW claim classes."""
import json, os, re, subprocess, urllib.request

ROOT = "/workspace"
MAN = json.load(open(os.path.join(ROOT, "ops/drift-manifest.json")))

CLAIM_CLASSES = {
    "CIIE_BOOTH": r"(Hall\s*\d+\.\d+|Stand\s*[A-Z0-9\-]+|CIIE\s+booth|our booth|will be exhibiting|CIIE\s+Featured|exhibitor)",
    "GROWTH_145": r"(145\.7|Import Surge|import surge)",
    "RUSSIAN": r"(Russian|Caspian)",
    "GOOD_PROV": r"(CITES|farmed|Chinese sturgeon|sturgeon farm)",
}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
    except Exception as e:
        return None, str(e)
    # SPA: pull the JS bundle too
    m = re.search(r'src="(/assets/[^"]+\.js)"', raw)
    if m:
        try:
            req = urllib.request.Request(url.rstrip("/") + m.group(1), headers={"User-Agent": "Mozilla/5.0"})
            raw += "\n" + urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
        except Exception:
            pass
    return raw, None

print("=" * 78)
print("A. MANIFEST-WATCHED PAGES — do they carry tonight's newly-false claims?")
print("=" * 78)
for p in MAN["pages"]:
    raw, err = fetch(p["url"])
    if raw is None:
        print(f"\n### {p['name']}  {p['url']}\n    FETCH FAIL: {err}")
        continue
    hits = []
    for label, pat in CLAIM_CLASSES.items():
        found = sorted(set(re.findall(pat, raw)))[:4]
        if found:
            hits.append(f"{label}={found}")
    src = p["source"]
    local = os.path.join(ROOT, src)
    srchits = []
    if os.path.isdir(local):
        for dirpath, _, files in os.walk(local):
            if "node_modules" in dirpath: continue
            for fn in files:
                if not fn.endswith((".js", ".jsx", ".ts", ".tsx", ".html", ".md")): continue
                try: t = open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace").read()
                except Exception: continue
                for label, pat in CLAIM_CLASSES.items():
                    f = sorted(set(re.findall(pat, t)))[:3]
                    if f: srchits.append(f"{fn}:{label}={f}")
    print(f"\n### {p['name']}\n    url={p['url']}\n    src={src}")
    if hits: print("    LIVE:", " | ".join(hits))
    else: print("    LIVE: clean of all four classes")
    if srchits: print("    SRC :", " | ".join(srchits[:6]))

print()
print("=" * 78)
print("B. EXTRA LIVE SLUGS (MEMORY.md / builds) not in manifest")
print("=" * 78)
watched = {p["url"].replace("https://", "").split("/")[0] for p in MAN["pages"]}
extra = ["y0r9ilfj96mj", "x2tvaieb5qgz", "klre58fvhmdc", "studexwar.pages.dev"]
for h in extra:
    if h in watched:
        print(f"\n### {h}: ALREADY WATCHED"); continue
    url = h if h.startswith("http") else f"https://{h}.space.mcode.io"
    raw, err = fetch(url)
    if raw is None:
        print(f"\n### {h}  {url}\n    FETCH FAIL: {err}"); continue
    hits = []
    for label, pat in CLAIM_CLASSES.items():
        found = sorted(set(re.findall(pat, raw)))[:4]
        if found: hits.append(f"{label}={found}")
    title = re.search(r"<title>([^<]*)</title>", raw)
    print(f"\n### {h}  {url}\n    title={title.group(1) if title else '?'}")
    print("    LIVE:", " | ".join(hits) if hits else "clean of all four classes")
