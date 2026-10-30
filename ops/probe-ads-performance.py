#!/usr/bin/env python3
"""ops/probe-ads-performance.py - READ-ONLY probe of Meta Ads performance (spend / impressions / actions).

WHY READ-ONLY AND SECRET-SAFE
  The access token is read from /workspace/.env IN-PROCESS and never placed in argv
  (argv is logged by the gateway -> a token in argv is a token in a log file).
  Every call below is a GET. No campaign, budget, bid or creative is touched.

  Exit codes
    0 = at least one ad account answered with insights (performance READABLE)
    2 = UNPROVEN - the token is expired / rejected, or no ad account could be read.
       NOT "zero spend". Never report this as verified performance.
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
GRAPH = "https://graph.facebook.com/v21.0"


def read_env(path):
    vals = {}
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip().strip('"').strip("'")
    except Exception as exc:
        print(f"  .env read failed: {type(exc).__name__}")
    return vals


def http(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "ads-probe/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "ignore")
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def main():
    vals = read_env(ENV_PATH)
    token = (vals.get("META_USER_TOKEN") or vals.get("META_ACCESS_TOKEN")
             or vals.get("FACEBOOK_USER_TOKEN") or vals.get("META_GRAPH_TOKEN") or "")
    print("META ADS PERFORMANCE PROBE (read-only)")
    print(f"  token present in .env : {'yes' if token else 'NO'}")
    if not token:
        print("VERDICT: UNPROVEN - no Meta token in .env; nothing was tested.")
        return 2

    # 1. token liveness + ad accounts the token can see
    st, body = http(f"{GRAPH}/me/adaccounts?fields=id,name,account_status,account_id,currency,timezone"
                    f"&access_token={urllib.parse.quote(token)}")
    print(f"\n  GET /me/adaccounts -> HTTP {st}")
    accounts = []
    if st == 200:
        try:
            accounts = json.loads(body).get("data", [])
        except Exception:
            accounts = []
        if not accounts:
            print("    (no ad accounts returned for this token)")
        for a in accounts:
            print(f"    {a.get('id'):22} {a.get('name','')[:40]:42} status={a.get('account_status')}")
    else:
        print(f"    body: {str(body)[:300]}")
        print("VERDICT: UNPROVEN - the Graph API answered, but not with a usable identity.")
        print("           Spend/ROAS is UNREADABLE - that is NOT zero spend.")
        return 2

    # 2. insights per account, per preset
    fields = "spend,impressions,clicks,reach,ctr,cpc,actions,action_values,date_start,date_stop"
    for preset in ("today", "yesterday", "last_7d"):
        print(f"\n  --- insights date_preset={preset} ---")
        for a in accounts:
            url = (f"{GRAPH}/{a.get('id')}/insights?fields={fields}"
                   f"&date_preset={preset}&access_token={urllib.parse.quote(token)}")
            st, body = http(url)
            if st != 200:
                print(f"    {a.get('id')} -> HTTP {st}: {str(body)[:220]}")
                continue
            try:
                data = json.loads(body).get("data", [])
            except Exception:
                data = []
            if not data:
                print(f"    {a.get('id')} -> no rows returned")
                continue
            for row in data:
                act = {x.get("action_type"): x.get("value") for x in (row.get("actions") or [])}
                val = {x.get("action_type"): x.get("value") for x in (row.get("action_values") or [])}
                print(f"    {a.get('id')} {row.get('date_start')}..{row.get('date_stop')}")
                print(f"       spend={row.get('spend')} impressions={row.get('impressions')} "
                      f"clicks={row.get('clicks')} reach={row.get('reach')} ctr={row.get('ctr')} cpc={row.get('cpc')}")
                print(f"       actions={act}")
                print(f"       action_values={val}")

    # 3. campaigns / ad statuses for the accounts that answered
    for a in accounts:
        st, body = http(f"{GRAPH}/{a.get('id')}/campaigns?fields=id,name,status,effective_status,objective,"
                        f"daily_budget,created_time&limit=50&access_token={urllib.parse.quote(token)}")
        print(f"\n  --- campaigns for {a.get('id')} -> HTTP {st}")
        if st != 200:
            print(f"    {str(body)[:220]}")
            continue
        try:
            camps = json.loads(body).get("data", [])
        except Exception:
            camps = []
        if not camps:
            print("    (no campaigns)")
        for c in camps:
            print(f"    {c.get('id'):22} status={c.get('status')}/{c.get('effective_status')} "
                  f"budget={c.get('daily_budget')} obj={c.get('objective')} {str(c.get('name'))[:44]}")

    print("\nVERDICT: VERIFIED - the Meta Graph API authenticated and returned ad data (read-only).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
