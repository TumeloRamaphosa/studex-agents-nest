#!/usr/bin/env python3
"""ops/probe-shopify-admin.py - READ-ONLY authenticated probe of the Shopify Admin API.

WHY IT IS WRITTEN THIS WAY
  The credential must never appear in a command line. `curl -H "X-Shopify-Access-Token: $KEY"`
  puts the secret value in argv, and the gateway logs argv -- so the key ends up written into
  /tmp/openclaw/*.log by the probe itself. A credential check that prints the key into a command
  line is not a check, it is a leak.

  So this script reads /workspace/.env IN-PROCESS, sets the header in the Python process, and
  prints ONLY non-secret facts: HTTP status, shop identity, currency, and the granted scopes.
  The token is never echoed, never written to a file, and never appears in argv.

READ-ONLY
  GETs only. No order, no customer, no product write, no price change. The scope requested is
  read-scoped. It prints NO customer data and NO order data.

EXIT CODES
  0 = authenticated and the shop answered (identity + scopes printed)
  2 = UNPROVEN - could not prove the connection (no token, no store domain, network error,
      non-200). NOT "clean". Never report this as verified.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
STOREFRONT = os.environ.get("SHOPIFY_STOREFRONT", "https://studexmeat.com")
API_VERSION = "2024-10"


def read_env(path):
    """Parse .env without printing anything from it."""
    vals = {}
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            vals[k.strip()] = v
    except Exception as exc:
        print(f"  .env read failed: {type(exc).__name__}")
    return vals


def discover_shop_domain(vals):
    """The Admin API is called against the *.myshopify.com host, not the custom domain."""
    for key in ("SHOPIFY_STORE_DOMAIN", "SHOPIFY_STORE_URL", "SHOPIFY_SHOP_DOMAIN",
                "SHOPIFY_MYSHOPIFY_DOMAIN"):
        v = vals.get(key)
        if v:
            m = re.search(r"([a-z0-9][a-z0-9-]*)\.myshopify\.com", v)
            if m:
                return m.group(1) + ".myshopify.com"
            if re.fullmatch(r"[a-z0-9][a-z0-9-]*\.myshopify\.com", v):
                return v
    # Fall back to reading it off the storefront itself.
    try:
        req = urllib.request.Request(STOREFRONT, headers={"User-Agent": "shopify-probe/1.0"})
        with urllib.request.urlopen(req, timeout=25) as r:
            html = r.read().decode("utf-8", "ignore")
        hits = set(re.findall(r"[A-Za-z0-9][A-Za-z0-9-]*\.myshopify\.com", html))
        if len(hits) == 1:
            return hits.pop()
        if hits:
            return sorted(hits)[0]
    except Exception:
        pass
    return None


def main():
    vals = read_env(ENV_PATH)
    token = vals.get("SHOPIFY_API_TOKEN") or vals.get("SHOPIFY_ADMIN_TOKEN")
    domain = discover_shop_domain(vals)

    print("SHOPIFY ADMIN PROBE (read-only)")
    print(f"  token present in .env : {'yes' if token else 'NO'}")
    print(f"  store domain resolved  : {domain or 'NOT FOUND'}")

    if not token:
        print("VERDICT: UNPROVEN - no token in .env; nothing was tested.")
        return 2
    if not domain:
        print("VERDICT: UNPROVEN - the *.myshopify.com store domain is unknown; the Admin API")
        print("           cannot be called. The custom domain is not the API host.")
        return 2

    url = f"https://{domain}/admin/api/{API_VERSION}/shop.json"
    req = urllib.request.Request(url, headers={
        "X-Shopify-Access-Token": token,   # set in-process; never in argv
        "Accept": "application/json",
        "User-Agent": "shopify-probe/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "ignore")
            status = r.status
            granted = r.headers.get("X-Shopify-Granted-Scopes", "(not returned)")
            required = r.headers.get("X-Shopify-Scopes-Required", "(not returned)")
    except urllib.error.HTTPError as exc:
        print(f"  HTTP {exc.code} from {url}")
        msg = exc.read().decode("utf-8", "ignore")[:300]
        try:
            msg = json.loads(msg).get("errors", msg)
        except Exception:
            pass
        print(f"  body: {msg}")
        print("VERDICT: UNPROVEN - the API answered, but not with a usable identity.")
        return 2
    except Exception as exc:
        print(f"  request failed: {type(exc).__name__}: {exc}")
        print("VERDICT: UNPROVEN - could not reach the API.")
        return 2

    print(f"  HTTP {status}")
    print(f"  endpoint               : {url}")
    print(f"  granted scopes header  : {granted}")
    print(f"  required scopes header : {required}")
    try:
        shop = json.loads(body).get("shop", {})
    except Exception:
        shop = {}
    print("  --- authenticated shop identity (no customer/order data) ---")
    for k in ("id", "name", "email", "domain", "myshopify_domain", "country_code",
              "currency", "timezone", "shop_owner"):
        if k in shop:
            v = shop[k]
            if k == "shop_owner" and isinstance(v, dict):
                v = f"{v.get('first_name', '')} {v.get('last_name', '')}".strip() or "(present)"
            print(f"  {k:22}: {v}")
    print("VERDICT: VERIFIED - the Admin API authenticated and returned the shop identity.")
    print("           (read-only probe; no order, customer or product data was read or changed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
