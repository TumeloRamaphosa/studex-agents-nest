#!/usr/bin/env python3
import json, urllib.request, urllib.parse

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

_live = live_agentmail_keys()
KEYS = {
    "AGENTMAIL_MAIN_API_KEY": _live[0],
    "AGENTMAIL_API_KEY": _live[1],
    "AGENTMAIL_WARMUP_API_KEY": _live[2],
}

def get(url, key):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300].decode(errors="replace")
    except Exception as e:
        return None, str(e)

for key, boxes in KEYS.items():
    if not boxes: continue
    for ib in boxes:
        for path in [f"/v0/inboxes/{ib}/messages?limit=6", f"/v0/inboxes/{ib}/messages?limit=6&direction=incoming"]:
            st, body = get("https://api.agentmail.to/v0" + path.split("/v0",1)[1], key) if False else get("https://api.agentmail.to"+path, key)
            print(f"\n### {ib} [{path}] -> {st}")
            if isinstance(body, dict) and body.get("messages") is not None:
                for m in body["messages"]:
                    print("  ", m.get("timestamp"), m.get("direction"), "|", (m.get("subject") or "")[:70])
                    print("      from:", m.get("from"), "| to:", m.get("to"))
                    print("      ", ((m.get("preview") or m.get("text") or "")[:280]).replace("\n"," "))
                break
            else:
                print("   body:", str(body)[:250])
