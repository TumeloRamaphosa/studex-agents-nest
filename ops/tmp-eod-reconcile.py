#!/usr/bin/env python3
"""EOD 2026-10-26 — final bounded reconciliation of two count discrepancies.

(a) storefront products: my probe said 30, the standups said 48 -> check pagination.
(b) blotato posts: my probe said 0, the standups said 8 -> check response shape.
One run, prints the truth, writes memory/2026-10-26-eod-reconcile.json
"""
import json, os, urllib.request

ROOT = "/workspace"


def env(key):
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8", errors="replace"):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def http(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0"})
    r = urllib.request.urlopen(req, timeout=25)
    return r.getcode(), r.read().decode("utf-8", "replace")


out = {}

# (a) storefront pagination
for u in ["https://studexmeat.com/products.json",
          "https://studexmeat.com/products.json?limit=250",
          "https://studexmeat.com/collections/all/products.json?limit=250"]:
    try:
        c, b = http(u)
        d = json.loads(b)
        p = d.get("products", [])
        out[u] = {"status": c, "count": len(p),
                  "note": "collections/all" if "collections" in u else "root feed"}
    except Exception as e:
        out[u] = {"error": str(e)[:100]}

# (b) blotato response shape
bt = env("BLOTATO_API_KEY")
if bt:
    try:
        c, b = http("https://backend.blotato.com/v2/posts", {"blotato-api-key": bt})
        d = json.loads(b)
        rec = {"status": c, "top_level_keys": list(d) if isinstance(d, dict) else type(d).__name__}
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, list):
                    rec[f"list_{k}"] = len(v)
            # pagination hints
            for k in ("meta", "pagination", "page", "total", "count", "limit"):
                if k in d:
                    rec[k] = d[k] if not isinstance(d[k], (list, dict)) else str(d[k])[:120]
        out["blotato"] = rec
    except Exception as e:
        out["blotato"] = {"error": str(e)[:100]}

json.dump(out, open(os.path.join(ROOT, "memory/2026-10-26-eod-reconcile.json"), "w"), indent=2)
print(json.dumps(out, indent=2)[:2000])
