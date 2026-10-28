#!/usr/bin/env python3
"""EOD 2026-10-26 — identify the flagged live deploys: title, h1, and the exact claim text.

One run -> memory/2026-10-26-eod-flagged-deploys.json
"""
import json, os, re, urllib.request

ROOT = "/workspace"
DATA = json.load(open(os.path.join(ROOT, "memory/2026-10-26-eod-all-slug-sweep.json")))
flagged = [s for s, r in DATA["results"].items()
           if r.get("reachable") and any(v["count"] for v in r["claims"].values())]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=18).read().decode("utf-8", "replace")


out = {}
for slug in flagged:
    url = f"https://{slug}.space.mcode.io"
    rec = {"url": url, "claims": DATA["results"][slug]["claims"]}
    try:
        html = get(url)
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
        rec["title"] = (m.group(1).strip()[:120] if m else None)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
        rec["h1"] = re.sub(r"<[^>]+>", "", h1.group(1)).strip()[:140] if h1 else None
        rec["html_bytes"] = len(html)
    except Exception as e:
        rec["error"] = str(e)[:100]
    # pull the full claim context from the JS bundle
    try:
        raw = get(url)
        for m in re.finditer(r'src="(/assets/[^"]+\.js)"', raw):
            try:
                raw += "\n" + get(url.rstrip("/") + m.group(1))
            except Exception:
                pass
        ctx = []
        for pat in [r"[Ww]e[\u2019']?re exhibiting[^`\"']{0,90}", r"will be exhibiting[^`\"']{0,90}",
                    r"Hall\s*\d+\.\d+[^`\"']{0,40}", r"Stand\s*[A-Z0-9\-]{3,}[^`\"']{0,30}",
                    r"145\.7%[^`\"']{0,60}", r"bilateral protocol[^`\"']{0,60}",
                    r"deadline [A-Z][a-z]+ 31 2026[^`\"']{0,40}"]:
            for mm in list(re.finditer(pat, raw))[:2]:
                ctx.append(mm.group(0)[:120])
        rec["claim_context"] = sorted(set(ctx))
    except Exception:
        pass
    out[slug] = rec

json.dump(out, open(os.path.join(ROOT, "memory/2026-10-26-eod-flagged-deploys.json"), "w"), indent=2)
print("wrote", len(out), "flagged deploy records\n")
for slug, rec in out.items():
    hits = {k: v["count"] for k, v in rec["claims"].items() if v["count"]}
    print(f"{slug}  {hits}")
    print(f"    title: {rec.get('title')}")
    print(f"    h1   : {rec.get('h1')}")
    for c in rec.get("claim_context", [])[:6]:
        print(f"      - {c}")
    print()
