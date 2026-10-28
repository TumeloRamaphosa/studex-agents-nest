#!/usr/bin/env python3
"""EOD 2026-10-26 — one bounded live sweep: does any live deploy still carry the
CIIE booth / Hall-Stand / 145.7-surge claims?

Fetches the canonical drift-manifest URLs plus the known retired slugs, pulls each page's
JS bundle, and scans for the claim classes. One run -> one JSON + one printed table.
"""
import json, os, re, urllib.request

ROOT = "/workspace"
OUT = os.path.join(ROOT, "memory", "2026-10-26-eod-live-claim-sweep.json")

CLAIMS = {
    "EXHIBITING": r"[Ww]e[\u2019']?re exhibiting|will be exhibiting|our booth|CIIE booth",
    "HALL_STAND": r"Hall\s*\d+\.\d+|Stand\s*[A-Z0-9\-]{3,}",
    "SURGE_145": r"145\.7",
}

CANON = ["https://3zryumjeuemk.space.mcode.io", "https://4mak476g6rmo.space.mcode.io",
         "https://9yk65ajlg1s9.space.mcode.io", "https://ess0ocgcd9f0.space.mcode.io",
         "https://eukr32nxiptw.space.mcode.io", "https://hhsmhunf1xci.space.mcode.io",
         "https://jgk62vzamgtk.space.mcode.io", "https://jisom3k4i126.space.mcode.io",
         "https://jqbgl8pu0uyh.space.mcode.io", "https://lqzo3q09yntr.space.mcode.io",
         "https://nudsduvyrc12.space.mcode.io", "https://oi28dhtke3yk.space.mcode.io",
         "https://psq9xaisb9kf.space.mcode.io", "https://qefqcvvpd8al.space.mcode.io"]
RETIRED = ["https://awyjxfplygag.space.mcode.io", "https://x2tvaieb5qgz.space.mcode.io",
           "https://y0r9ilfj96mj.space.mcode.io", "https://nhlcdtr7ritv.space.mcode.io",
           "https://6hchke5o5dui.space.mcode.io", "https://fu8qyf0qg18j.space.mcode.io",
           "https://fa4xt0vnu67u.space.mcode.io", "https://anvkfflansa9.space.mcode.io",
           "https://klre58fvhmdc.space.mcode.io", "https://hketvigqcs2f.space.mcode.io"]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
    for m in re.finditer(r'src="(/assets/[^"]+\.js)"', raw):
        try:
            req2 = urllib.request.Request(url.rstrip("/") + m.group(1),
                                          headers={"User-Agent": "Mozilla/5.0"})
            raw += "\n" + urllib.request.urlopen(req2, timeout=20).read().decode("utf-8", "replace")
        except Exception:
            pass
    return raw


out = {"scanned_at": "2026-10-26T22:10:00Z", "canonical": {}, "retired": {}}

for label, urls in (("canonical", CANON), ("retired", RETIRED)):
    for url in urls:
        rec = {"reachable": False, "claims": {}}
        try:
            raw = fetch(url)
            rec["reachable"] = True
            rec["bytes"] = len(raw)
            for name, pat in CLAIMS.items():
                m = re.search(pat, raw)
                rec["claims"][name] = {
                    "count": len(re.findall(pat, raw)),
                    "snippet": raw[max(0, m.start() - 80): m.start() + 80].replace("\n", " ") if m else None,
                }
        except Exception as e:
            rec["error"] = str(e)[:120]
        out[label][url] = rec

json.dump(out, open(OUT, "w"), indent=2)
print("wrote", OUT)
for label in ("canonical", "retired"):
    print("\n==", label)
    for url, rec in out[label].items():
        if not rec["reachable"]:
            print(f"  {url}  UNREACHABLE ({rec.get('error','')[:60]})")
            continue
        hits = {k: v["count"] for k, v in rec["claims"].items() if v["count"]}
        print(f"  {url}  {hits or 'clean'}")
        for k, v in rec["claims"].items():
            if v["count"] and v["snippet"]:
                print(f"      {k}: ...{v['snippet']}...")
