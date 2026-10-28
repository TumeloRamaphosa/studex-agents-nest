#!/usr/bin/env python3
"""EOD 2026-10-26 — reconcile two conflicting counts before they go in the vault log.

My ad-hoc probe said storefront=30 products and blotato=0 posts; the morning/evening standups
said 48 and 8. Both cannot be right. This reconciles them once and records the truth.
"""
import json, os, urllib.request, urllib.error

ROOT = "/workspace"


def env(key):
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8", errors="replace"):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def http(url, headers=None, timeout=25):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0"})
    r = urllib.request.urlopen(req, timeout=timeout)
    return r.getcode(), r.read().decode("utf-8", "replace")


out = {}

# storefront: default limit vs explicit limit
for url in ["https://studexmeat.com/products.json",
            "https://studexmeat.com/products.json?limit=250"]:
    try:
        code, body = http(url)
        d = json.loads(body)
        prods = d.get("products", [])
        out[url] = {"status": code, "count": len(prods),
                    "handles": [p.get("handle") for p in prods][:60]}
    except Exception as e:
        out[url] = {"error": str(e)[:120]}

# blotato: check raw shape + header variants
btok = env("BLOTATO_API_KEY")
if btok:
    for label, headers in [("blotato-api-key", {"blotato-api-key": btok}),
                           ("raw-auth", {"Authorization": btok}),
                           ("bearer", {"Authorization": f"Bearer {btok}"})]:
        try:
            code, body = http("https://backend.blotato.com/v2/posts", headers)
            try:
                d = json.loads(body)
            except Exception:
                d = {}
            items = d.get("data") if isinstance(d, dict) else None
            if items is None and isinstance(d, dict):
                items = d.get("posts") or d.get("results") or []
            rec = {"status": code, "keys": list(d)[:8] if isinstance(d, dict) else type(d).__name__,
                   "count": len(items) if items is not None else None}
            if items:
                rec["sample"] = [{"id": p.get("id"), "published_at": p.get("published_at"),
                                  "text": (p.get("text") or "")[:60]} for p in items[:10]]
            out["blotato/" + label] = rec
        except urllib.error.HTTPError as e:
            out["blotato/" + label] = {"status": e.code, "body": e.read().decode("utf-8", "replace")[:160]}
        except Exception as e:
            out["blotato/" + label] = {"error": str(e)[:120]}

json.dump(out, open(os.path.join(ROOT, "memory/2026-10-26-eod-counts.json"), "w"), indent=2)
for k, v in out.items():
    print(k, "->", json.dumps({kk: vv for kk, vv in v.items() if kk != "handles"})[:700])
    if "handles" in v:
        print("   count:", v["count"])
