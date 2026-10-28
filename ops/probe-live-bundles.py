#!/usr/bin/env python3
"""
Probe live customer-facing URLs for FORBIDDEN claim strings — in the BUNDLES,
not just the HTML shell.

WHY: a React SPA returns ~150 characters of HTML. Asserting against that proves
nothing. On 2026-10-21 two SPAs were live and unchecked, and they published
"Rainforest Alliance certified" and "certified Russian caviar houses". A plain
HTML grep reported those pages as clean.

So for every URL we fetch:
  1. fetch the HTML,
  2. extract every <script src=...> asset,
  3. fetch those assets too,
  4. search the UNION of html + assets for the forbidden strings.

Read-only. Never edits, never deploys.
"""
import re
import ssl
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (compatible; StudexBundleProbe/1.0)"

FORBIDDEN = [
    "Rainforest Alliance",
    "PROWTC",
    "EUDR compliant",
    "certified farms",
    "ethically sourced",
    "exhibiting at CIIE",
    "is exhibiting",
    "CIIE 2026 exhibitor",
    "agent.studexmeat.com",
    "Sevruga Premium",
    "Siberian Reserve",
    "per 250g",
    "market is opening via CIIE",
]

URLS = [
    "https://psq9xaisb9kf.space.mcode.io",   # Coffee SA hospitality (canonical)
    "https://de6xdoikz95g.space.mcode.io",   # Coffee B2B green
    "https://fr7m7fzyailo.space.mcode.io",   # Coffee China / CIIE
    "https://9yk65ajlg1s9.space.mcode.io",   # CIIE coffee landing (React)
    "https://qefqcvvpd8al.space.mcode.io",   # Coffee noir B2B landing (React)
    "https://jqbgl8pu0uyh.space.mcode.io",   # China coffee lead capture (React)
    "https://jgk62vzamgtk.space.mcode.io",   # Caviar trade (React)
    "https://9xms7l52m71c.space.mcode.io",   # SA Hospitality coffee shell (RETIRED)
    "https://anvkfflansa9.space.mcode.io",   # coffee B2B (RETIRED)
    "https://1bl06cgsu643.space.mcode.io",   # China lead capture (RETIRED, leaked key)
    "https://2hkb7k7q2gni.space.mcode.io",   # caviar trade (RETIRED, leaked key)
]


def fetch(url, timeout=25):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.status, r.read().decode("utf-8", "ignore")


def probe(base):
    out = {"url": base, "status": None, "assets": 0, "hits": [], "error": None}
    try:
        status, html = fetch(base)
        out["status"] = status
    except Exception as e:
        out["error"] = f"html: {e}"
        return out

    blob = html
    for src in re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html):
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = base + src
        elif not src.startswith("http"):
            src = base + "/" + src
        try:
            _, asset = fetch(src)
            blob += "\n" + asset
            out["assets"] += 1
        except Exception:
            pass

    low = blob.lower()
    for f in FORBIDDEN:
        if f.lower() in low:
            i = low.index(f.lower())
            out["hits"].append((f, re.sub(r"\s+", " ", blob[max(0, i - 70): i + 90])))
    return out


def main():
    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(probe, URLS))

    bad = 0
    for r in results:
        tag = "OK  "
        if r["error"] and not r["status"]:
            tag = "ERR "
        elif r["hits"]:
            tag = "HIT "
            bad += 1
        print(f'{tag} {r["status"]} assets={r["assets"]:<3} {r["url"]}')
        if r["error"]:
            print(f'      error: {r["error"]}')
        for f, ctx in r["hits"]:
            print(f'      FORBIDDEN {f!r} :: ...{ctx}...')

    print(f"\n{bad} URL(s) carry a forbidden claim.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
