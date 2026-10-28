#!/usr/bin/env python3
"""EOD 2026-10-26 — one bounded commerce probe for the EOD log.

Shopify storefront + Admin, Blotato posts + insights, local order ledger, AgentMail external
inbound. One run -> printed summary + memory/2026-10-26-eod-commerce.json
"""
import json, os, urllib.request, urllib.error, re

ROOT = "/workspace"
OUT = os.path.join(ROOT, "memory/2026-10-26-eod-commerce.json")


def env(key):
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8", errors="replace"):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def http(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0"})
    r = urllib.request.urlopen(req, timeout=timeout)
    return r.getcode(), r.read().decode("utf-8", "replace")


res = {}

# --- Shopify storefront ---
try:
    code, body = http("https://studexmeat.com/products.json")
    try:
        n = len(json.loads(body).get("products", []))
    except Exception:
        n = None
    res["storefront"] = {"status": code, "products": n}
except Exception as e:
    res["storefront"] = {"error": str(e)[:120]}

# --- Shopify Admin ---
tok = env("SHOPIFY_API_TOKEN")
if tok:
    try:
        code, body = http("https://studexmeat.myshopify.com/admin/api/2024-04/orders.json",
                          {"X-Shopify-Access-Token": tok, "User-Agent": "Mozilla/5.0"})
        res["shopify_admin"] = {"status": code, "body": body[:200]}
    except urllib.error.HTTPError as e:
        res["shopify_admin"] = {"status": e.code, "body": e.read().decode("utf-8", "replace")[:200]}
    except Exception as e:
        res["shopify_admin"] = {"error": str(e)[:120]}
else:
    res["shopify_admin"] = {"status": "no token in .env"}

# --- Blotato posts ---
btok = env("BLOTATO_API_KEY")
if btok:
    try:
        code, body = http("https://backend.blotato.com/v2/posts", {"blotato-api-key": btok})
        data = json.loads(body)
        posts = data.get("data") or data.get("posts") or []
        res["blotato"] = {"status": code, "count": len(posts),
                          "posts": [{"id": p.get("id"), "account": (p.get("account") or {}).get("id"),
                                     "published_at": p.get("published_at"),
                                     "text": (p.get("text") or "")[:70]}
                                    for p in posts]}
    except urllib.error.HTTPError as e:
        res["blotato"] = {"status": e.code, "body": e.read().decode("utf-8", "replace")[:200]}
    except Exception as e:
        res["blotato"] = {"error": str(e)[:120]}
else:
    res["blotato"] = {"status": "no key in .env"}

# --- local order ledger ---
for rel in ("studex-os/delivery-state.json", "studex-ops/orders", "studex-meat/orders"):
    p = os.path.join(ROOT, rel)
    if os.path.exists(p):
        if os.path.isfile(p):
            try:
                d = json.load(open(p))
                res.setdefault("ledgers", []).append(
                    {"path": rel, "orders": len(d) if isinstance(d, list) else len(d.get("orders", []))})
            except Exception:
                res.setdefault("ledgers", []).append({"path": rel, "read": "unparsed"})
        else:
            res.setdefault("ledgers", []).append({"path": rel, "files": len(os.listdir(p))})

json.dump(res, open(OUT, "w"), indent=2, default=str)
print(json.dumps(res, indent=2)[:2500])
