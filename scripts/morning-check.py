#!/usr/bin/env python3
import json, urllib.request, urllib.error, os, glob, subprocess

def http(url, headers=None, method="GET", data=None):
    req = urllib.request.Request(url, headers=headers or {}, method=method, data=data)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read()[:800].decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:400].decode(errors="replace")
    except Exception as e:
        return None, str(e)

print("=== SHOPIFY ===")
TOK = os.environ.get("SHOPIFY_ADMIN_TOKEN","")
for store in ["studexmeat.myshopify.com","studex-meat.myshopify.com"]:
    st, body = http(f"https://{store}/admin/api/2024-07/orders.json?status=any&limit=5",
                    {"X-Shopify-Access-Token": TOK})
    print(store, "->", st, body[:200] if body else "")

print("\n=== SHOPIFY TOKEN LOCATIONS ===")
for p in ["/root/.env", os.path.expanduser("~/.env"), "/workspace/.env"]:
    if os.path.exists(p):
        for line in open(p, errors="replace"):
            if "SHOPIFY" in line.upper():
                k = line.split("=")[0]
                v = line.split("=",1)[1].strip() if "=" in line else ""
                print(p, k, "len", len(v))

print("\n=== LOCAL ORDER LEDGERS ===")
for p in glob.glob("/workspace/**/delivery-state.json", recursive=True):
    print(p)
    try:
        d = json.load(open(p))
        print("   last_sync", d.get("last_sync"), "orders", len(d.get("orders",{}) or {}))
    except Exception as e: print("  err", e)

print("\n=== META ADS (graph) ===")
FB = os.environ.get("META_USER_TOKEN", "")
for acct in ["act_560666565541381","act_1069308327357613"]:
    st, body = http(f"https://graph.facebook.com/v21.0/{acct}/insights?fields=spend,impressions,clicks,actions&date_preset=yesterday&access_token={FB}")
    print(acct, "->", st, body[:200] if body else "")
