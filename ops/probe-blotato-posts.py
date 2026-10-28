#!/usr/bin/env python3
"""Read-only: what actually published to our buyer-facing Blotato accounts?

HEARTBEAT.md rule: "memory/published-<date>-<pillar>.json is local state; the
Blotato API is the truth." So ask the API.

TWO TRAPS THIS SCRIPT EXISTS TO AVOID
-------------------------------------
1. AUTH HEADER. The Blotato API is authenticated with the header
   ``blotato-api-key: <key>`` - NOT ``Authorization: Bearer <key>``. The
   Bearer form returns **HTTP 401** and an empty list, which looks exactly
   like "we have published nothing". An earlier version of this probe used
   Bearer and reported a confident, wrong "0 posts". (The repo's own
   scripts/blotato-accounts.py and scripts/blotato-posts.py already use the
   correct header - follow them, not this comment.)

2. ``?accountId=`` IS IGNORED BY THE API. The posts endpoint returns the
   GLOBAL post list regardless of the query parameter. Filtering by account
   must be done CLIENT-SIDE on ``post["account"]["id"]``.

Neither trap may ever masquerade as "nothing published": an unreachable API
prints an explicit ERROR and exits non-zero. It never prints an empty
success. A false "we published nothing" causes a duplicate post on every
channel.

Reads BLOTATO_API_KEY from /workspace/.env IN-PROCESS -- never on a command
line (a literal key in argv is written to the gateway log by the probe itself).
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://backend.blotato.com/v2"
ENV = "/workspace/.env"
LIMIT = 12


def env_key(name):
    try:
        with open(ENV) as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == name:
                    return v.strip().strip('"').strip("'")
    except OSError:
        pass
    return ""


def get(path, key):
    req = urllib.request.Request(
        BASE + path, headers={"blotato-api-key": key, "accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.load(resp)


def main():
    key = env_key("BLOTATO_API_KEY")
    if not key:
        print("ERROR: BLOTATO_API_KEY not set in %s - cannot probe." % ENV)
        return 2

    # --- accounts (header: blotato-api-key) --------------------------------
    try:
        accts = get("/users/me/accounts", key)
    except urllib.error.HTTPError as e:
        print("ERROR: accounts HTTP %s - wrong header or expired key." % e.code)
        return 2
    except Exception as e:  # noqa: BLE001
        print("ERROR: accounts request failed: %s" % e)
        return 2
    rows = accts if isinstance(accts, list) else (accts.get("items") or accts.get("accounts") or [])
    if not rows:
        print("ERROR: accounts list came back empty - treating as a failure, not as 'no accounts'.")
        return 2

    print("=== connected accounts ===")
    ids = {}
    for a in rows:
        aid = str(a.get("id") or a.get("accountId") or "")
        plat = a.get("platform") or ""
        name = a.get("name") or a.get("username") or a.get("displayName") or ""
        ids[aid] = (plat, name)
        print("  %-10s id=%-10s %s" % (plat, aid, name))

    # --- global post list (the API ignores ?accountId=) --------------------
    try:
        d = get("/posts?limit=50", key)
    except urllib.error.HTTPError as e:
        print("ERROR: posts HTTP %s - cannot prove what published." % e.code)
        return 2
    except Exception as e:  # noqa: BLE001
        print("ERROR: posts request failed: %s" % e)
        return 2
    items = d if isinstance(d, list) else (d.get("items") or d.get("posts") or [])
    if not items:
        print("ERROR: post list came back empty - treating as a failure, not as 'nothing published'.")
        return 2

    print("\n=== recent posts (authoritative publish record) ===")
    for aid, (plat, name) in ids.items():
        mine = []
        for it in items:
            acct = it.get("account")
            acc_id = str(acct.get("id")) if isinstance(acct, dict) else str(it.get("accountId") or "")
            if acc_id == aid:
                mine.append(it)
        print("  -- %s (%s) %s   [%d post(s)]" % (plat, aid, name, len(mine)))
        for it in mine[:LIMIT]:
            ts = str(it.get("postTime") or it.get("publishedAt") or it.get("createdAt") or "")[:26]
            state = it.get("state") or ""
            txt = (it.get("text") or it.get("content") or "")[:58].replace("\n", " ")
            print("     %-26s %-10s %s" % (ts, state, txt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
