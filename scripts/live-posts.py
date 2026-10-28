#!/usr/bin/env python3
"""Read the live Blotato posts and print what actually shipped.

Answers the only question that matters after a publish: did the exact text we
intended reach the platform? Prints id, platform, time, char count, hashtag
count and any markdown residue.
"""
import json
import re
import sys
import urllib.request

sys.path.insert(0, "/workspace/scripts")
from agentmail_keys import _load_env  # noqa: E402

KEY = _load_env()["BLOTATO_API_KEY"]
REQ = urllib.request.Request(
    "https://backend.blotato.com/v2/posts",
    headers={"blotato-api-key": KEY},
)

with urllib.request.urlopen(REQ, timeout=30) as resp:
    data = json.load(resp)

items = data.get("items") or []
print(f"live posts returned: {len(items)}")
for p in items:
    text = p.get("text") or ""
    tags = re.findall(r"#\w+", text)
    residue = re.findall(r"\*\*|__|`", text)
    acct = p.get("account") or {}
    print(f"\n id {p.get('id')} | {p.get('platform')} | acct {acct.get('id')} "
          f"| {str(p.get('postTime'))[:19]}")
    print(f"   chars={len(text)} tags={len(tags)} residue={residue}")
    if tags:
        print(f"   tags: {tags}")
    print(f"   head: {text[:100]!r}")
    print(f"   tail: {text[-80:]!r}")
