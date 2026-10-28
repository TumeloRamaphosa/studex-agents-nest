#!/usr/bin/env python3
"""Build Hour 2026-10-26 — one consolidated fact pass before building."""
import re, urllib.request, json, os

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
    m = re.search(r'src="(/assets/[^"]+\.js)"', raw)
    if m:
        try:
            req = urllib.request.Request(url.rstrip("/") + m.group(1), headers={"User-Agent": "Mozilla/5.0"})
            raw += "\n" + urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
        except Exception:
            pass
    return raw

CLAIMS = {
    "HALL_STAND": r"(Hall\s*7\.2|Stand\s*A5-01|Hall\s*\d+\.\d+|Stand\s*[A-Z0-9\-]{3,})",
    "SURGE145":   r"145\.7",
    "BOOTH_PROMISE": r"(your CIIE booth|CIIE booth|CIIE Featured|CIIE sample eligible|sample eligible)",
    "SHIP_DATE":  r"(October 20[^\"<]{0,12}28|Oct(?:ober)?\s*20[^\"<]{0,4}28)",
    "WHITELABEL_PRICE": r"FOB \$1[2-8]",
    "RUSSIAN":    r"Russian|Caspian",
}

print("### 1. LIVE China/caviar candidate slugs — what do they actually publish? ###")
for h in ["9740b80crsuu", "s6msv8j0whmx", "klre58fvhmdc", "jqbgl8pu0uyh", "9yk65ajlg1s9", "qefqcvvpd8al", "3zryumjeuemk"]:
    try:
        raw = fetch(f"https://{h}.space.mcode.io/")
    except Exception as e:
        print(f"\n{h}: FAIL {e}"); continue
    t = re.search(r"<title>([^<]*)</title>", raw)
    hits = {k: sorted(set(re.findall(v, raw)))[:3] for k, v in CLAIMS.items() if re.search(v, raw)}
    print(f"\n{h}  title={t.group(1) if t else '?'}")
    print("   ", hits if hits else "CLEAN of all claim classes")

print()
print("### 2. REGISTRY page map — which live slugs are watched? ###")
reg = open("/workspace/studex-meat/PRICE-SOURCE-REGISTRY.md", encoding="utf-8").read()
watched = set(re.findall(r"([a-z0-9]+)\.space\.mcode\.io", reg))
for h in ["9740b80crsuu", "s6msv8j0whmx", "klre58fvhmdc", "jqbgl8pu0uyh", "9yk65ajlg1s9", "qefqcvvpd8al", "3zryumjeuemk", "lqzo3q09yntr", "eukr32nxiptw", "ess0ocgcd9f0", "jgk62vzamgtk", "nudsduvyrc12", "psq9xaisb9kf"]:
    print(f"   {'WATCHED  ' if h in watched else 'UNWATCHED'} {h}")

print()
print("### 3. White-label pack price + lead-time: is there a source? ###")
for needle in ["15–18", "15-18", "white-label", "White-label", "lead time", "Lead time", "FOB $"]:
    hits = []
    for fn in ["/workspace/studex-meat/PRICE-SOURCE-REGISTRY.md",
               "/workspace/china-coffee-sheet-copy-paste.md",
               "/workspace/research/2026-10-26.md"]:
        txt = open(fn, encoding="utf-8", errors="replace").read()
        for m in re.finditer(re.escape(needle), txt):
            line = txt[:m.start()].count("\n") + 1
            hits.append(f"{os.path.basename(fn)}:{line}")
            break
    print(f"   {needle!r}: {hits if hits else 'NO SOURCE FOUND'}")

print()
print("### 4. drift-check.py FORBIDDEN local-scan list ###")
src = open("/workspace/ops/drift-check.py", encoding="utf-8").read()
m = re.search(r"FORBIDDEN = \[(.*?)\]", src, re.S)
print(m.group(1).strip() if m else "not found")
