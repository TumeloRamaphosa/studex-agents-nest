#!/usr/bin/env python3
import json, os, urllib.request, urllib.error

def http(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:500].decode(errors="replace")
    except Exception as e:
        return None, str(e)

PAGE = os.environ.get("META_PAGE_TOKEN", "")
USER = os.environ.get("META_USER_TOKEN", "")

print("=== ad accounts with PAGE token ===")
st, body = http(f"https://graph.facebook.com/v21.0/me/adaccounts?access_token={PAGE}")
print(st, body[:300])
try:
    for a in json.loads(body).get("data", []):
        print("  acct:", a.get("id"), a.get("name"))
except: pass

print("\n=== ad accounts with USER token ===")
st, body = http(f"https://graph.facebook.com/v21.0/me/adaccounts?access_token={USER}")
print(st, body[:300])
try:
    for a in json.loads(body).get("data", []):
        print("  acct:", a.get("id"), a.get("name"))
except: pass

print("\n=== page token identity ===")
for tok_name, tok in [("PAGE", PAGE), ("USER", USER)]:
    st, body = http(f"https://graph.facebook.com/v21.0/me?access_token={tok}")
    print(tok_name, st, body[:220])

print("\n=== FeedHive ===")
_fh = os.environ.get("FEEDHIVE_API_KEY", "")
if not _fh:
    print("feedhive -> SKIPPED (FEEDHIVE_API_KEY not set)")
else:
    st, body = http("https://api.feedhive.io/v1/posts?limit=2", {"Authorization": "Bearer " + _fh})
    print("feedhive ->", st, body[:200])
print("feadhive ->", st, body[:200])
