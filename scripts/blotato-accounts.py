#!/usr/bin/env python3
"""Which platforms can path B's pending caption still reach today?

Path B = blotato-fallback.js -> TARGETS linkedin + threads.
Both may already be taken by path A, and the Blotato account connections
may be expired. This asks the Blotato accounts API for the real connection
state so we do not guess.
"""
import json
import sys
import urllib.request

sys.path.insert(0, "/workspace/scripts")
from agentmail_keys import _load_env  # noqa: E402

KEY = _load_env()["BLOTATO_API_KEY"]
REQ = urllib.request.Request(
    "https://backend.blotato.com/v2/users/me/accounts",
    headers={"blotato-api-key": KEY},
)
with urllib.request.urlopen(REQ, timeout=30) as resp:
    accounts = json.load(resp)

if isinstance(accounts, dict):
    accounts = accounts.get("items") or accounts.get("accounts") or []

print(f"{len(accounts)} connected account(s)\n")
for a in accounts:
    print(f"  id={a.get('id'):>6}  platform={str(a.get('platform')):<10} "
          f"username={a.get('username','')!r:<24}")
    for key in ("status", "connected", "connectionStatus", "expired",
                "active", "enabled", "error"):
        if key in a:
            print(f"      {key} = {a[key]!r}")
    extra = {k: v for k, v in a.items()
             if k not in ("id", "platform", "username", "fullname", "media")}
    if extra:
        print(f"      other: {json.dumps(extra)[:400]}")
    print()
