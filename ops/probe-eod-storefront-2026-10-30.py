#!/usr/bin/env python3
"""ops/probe-eod-storefront-2026-10-30.py - READ-ONLY EOD storefront + content-metrics probe.

Three questions, one process, no secrets in argv:
  1. Is the buying path alive (storefront / products / cart)?
  2. What does the live price ladder actually say today?
  3. Do TODAY'S published posts carry metrics yet (reach / views / likes)?

Everything here is a GET. Nothing is written, bought, published or changed.
"""
import json
import urllib.error
import urllib.parse
import urllib.request

STORE = "https://studexmeat.com"
API = "https://backend.blotato.com/v2"


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "eod-probe/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "ignore")
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def env():
    vals = {}
    for line in open("/workspace/.env", errors="ignore"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals


print("=== 1. STOREFRONT (buying path) ===")
st, _ = get(STORE)
print(f"  GET /                     -> HTTP {st}")
st, body = get(f"{STORE}/products.json?limit=250")
if st == 200:
    try:
        prods = json.loads(body).get("products", [])
    except Exception:
        prods = []
    print(f"  GET /products.json        -> HTTP {st} — {len(prods)} products")
    caviar = [p for p in prods if "caviar" in (p.get("title") or "").lower()]
    print(f"  caviar products on storefront: {len(caviar)}  (trade-only, expected 0)")
    print("  --- live price ladder (biltong + gold) ---")
    for p in prods:
        t = p.get("title") or ""
        if any(k in t for k in ("Biltong", "Gold", "Ribeye", "Coffee")):
            variants = p.get("variants") or []
            for v in variants[:6]:
                print(f"    {t[:44]:46} {str(v.get('title'))[:26]:28} R{v.get('price')}  avail={v.get('available')}")
else:
    print(f"  GET /products.json        -> HTTP {st}: {str(body)[:160]}")

st, body = get(f"{STORE}/cart.js")
print(f"  GET /cart.js              -> HTTP {st}")

print("\n=== 2. CONTENT METRICS (Blotato) ===")
e = env()
key = e.get("BLOTATO_API_KEY", "")
H = {"blotato-api-key": key, "Content-Type": "application/json"}
for acct, name in (("76978", "instagram"), ("7701", "threads")):
    st, body = get(f"{API}/analytics?accountId={acct}&days=1", headers=H)
    print(f"  {name} ({acct}) analytics?days=1 -> HTTP {st}")
    if st != 200:
        print(f"    {str(body)[:160]}")
        continue
    try:
        items = json.loads(body).get("items", [])
    except Exception:
        items = []
    if not items:
        print("    (no analytics rows in the last day)")
    for it in items[:6]:
        lm = it.get("latestMetrics") or {}
        m = lm.get("metrics", {}) or {}
        print(f"    {str(it.get('createdAt'))[:19]} id={it.get('id')} "
              f"fetched={str(lm.get('fetchedAt'))[:19]} {json.dumps(m)}")
    if not items:
        print("    NOTE: no analytics row for TODAY's post yet - metrics lag the publish.")

print("\n=== 3. PUBLISHED POSTS TODAY (authoritative publish record) ===")
st, body = get(f"{API}/posts?limit=50", headers=H)
print(f"  GET /posts -> HTTP {st}")
if st == 200:
    # The API returns a bare list (or items/posts) and IGNORES ?accountId=.
    # Filtering by account MUST be done client-side on post["account"]["id"].
    try:
        parsed = json.loads(body)
    except Exception:
        parsed = []
    if isinstance(parsed, list):
        posts = parsed
    else:
        posts = parsed.get("items") or parsed.get("posts") or []
    if not posts:
        print("  ERROR: post list came back empty - that is a FAILED probe, not 'nothing published'.")
    today = [p for p in posts if str(p.get("postTime") or p.get("publishedAt") or p.get("createdAt") or "").startswith("2026-10-30")]
    print(f"  total posts returned: {len(posts)} | published 2026-10-30: {len(today)}")
    for p in today:
        acct = p.get("account") if isinstance(p.get("account"), dict) else {}
        st2 = p.get("state") or {}
        print(f"    {str(p.get('postTime') or p.get('createdAt'))[:19]}  "
              f"acct={acct.get('id')} id={p.get('id')} state={st2.get('type') if isinstance(st2, dict) else st2} "
              f"url={(st2.get('postUrl') if isinstance(st2, dict) else '') or ''}")
    fut = [p for p in posts if str(p.get("postTime") or "") > "2026-10-30T23"]
    print(f"  posts with a FUTURE postTime (scheduled): {len(fut)}")
else:
    print(f"    {str(body)[:200]}")
