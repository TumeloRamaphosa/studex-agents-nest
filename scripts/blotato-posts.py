#!/usr/bin/env python3
"""Query Blotato's posts API — the authoritative source for 'did this publish?'.

Blotato returns {"items": [...]} (NOT {"posts": [...]}) — an earlier version of this
script read the wrong key and reported "0 posts", which looks identical to
"nothing published". Both are failure modes worth naming:
  - wrong response key -> false "0 posts"
  - pending-file `status` field -> only records the Facebook outcome
Always read `items`, and always query this API before claiming a post is unpublished.

Usage: python3 scripts/blotato-posts.py [count]
"""
import json, sys, urllib.request, urllib.error, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import blotato_key

KEY = blotato_key()
COUNT = int(sys.argv[1]) if len(sys.argv) > 1 else 12


def get(url):
    req = urllib.request.Request(url, headers={"blotato-api-key": KEY})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300].decode("utf8", "replace")
    except Exception as e:
        return "ERR", str(e)[:200]


# NOTE: `?accountId=` is IGNORED by this endpoint - every accountId returns
# the SAME list. Filter CLIENT-SIDE. The authoritative platform attribution
# is the TOP-LEVEL `platform` field on each record (`account.platform` is null
# on every record); `account.id` identifies the account (7701=threads,
# 76978=instagram).
code, d = get("https://backend.blotato.com/v2/posts")
if code != 200:
    print("posts ->", code, d)
    raise SystemExit(1)

items = d.get("items", [])
print(f"HTTP {code} | keys={list(d.keys())} | items={len(items)}\n")
for p in items[:COUNT]:
    st = p.get("state") or {}
    txt = (p.get("text") or "").replace("\n", " ")[:66]
    print(f"id {p.get('id'):>9} | {str(p.get('platform')):9} | {str(st.get('type')):9} | {str(p.get('postTime'))[:19]}")
    print(f"    {txt}")
    if st.get("postUrl"):
        print(f"    {st['postUrl']}")
print()
