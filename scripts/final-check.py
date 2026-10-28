#!/usr/bin/env python3
import json, urllib.request, os, glob, time

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

_live = live_agentmail_keys()
KEY = _live[0]
KEY2 = _live[-1]
BOXES = [(KEY,["meat@studex-group.com","naledi-cmo@studex-group.com","t-ramaphosa-ceo@studex-group.com","sales@studex-group.com","info@studex-group.com","support.superagents@studex-group.com"]),
         (KEY2,["t.ramaphosa@agentmail.to","project-2571-studex-agent-2077@agentmail.to"])]

def get(url, key):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer "+key})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)
    except Exception as e: return {"error": str(e)}

print("=== INBOUND (non-Tumelo) messages since 2026-10-15 ===")
found = False
for key, boxes in BOXES:
    for ib in boxes:
        d = get(f"https://api.agentmail.to/v0/inboxes/{ib}/messages?limit=60", key)
        for m in d.get("messages", []):
            ts = m.get("timestamp","")
            frm = m.get("from","")
            if ts >= "2026-10-15" and "tumelor001" not in frm:
                found = True
                print(f"  {ts} | {ib} | from {frm} | {m.get('subject')}")
                print("     ", ((m.get('preview') or m.get('text') or '')[:250]).replace("\n"," "))
if not found: print("  none — no inbound from anyone but Tumelo since 15 Oct")

print("\n=== charlie@ / ceo@agent.studexmeat.com status ===")
for ib in ["charlie@agent.studexmeat.com","ceo@agent.studexmeat.com","naledi@agent.studexmeat.com"]:
    for key,_ in BOXES:
        d = get(f"https://api.agentmail.to/v0/inboxes/{ib}", key)
        if "error" not in d and d.get("email"):
            print("  ", ib, "EXISTS"); break
    else:
        print("  ", ib, "-> does not exist / unreachable (DNS not set up)")

print("\n=== outbound-drafts awaiting approval ===")
for p in sorted(glob.glob("/workspace/outbound-drafts/*"), key=os.path.getmtime, reverse=True)[:8]:
    print("  ", time.strftime("%Y-%m-%d %H:%M", time.gmtime(os.path.getmtime(p))), p)

print("\n=== Shopify store health (storefront, no admin token) ===")
import urllib.error
def http(url):
    try:
        with urllib.request.urlopen(url, timeout=20) as r: return r.status, r.read()[:300].decode(errors="replace")
    except urllib.error.HTTPError as e: return e.code, e.read()[:200].decode(errors="replace")
    except Exception as e: return None, str(e)
for u in ["https://studexmeat.com/", "https://studexmeat.com/collections/coffee"]:
    st, b = http(u); print("  ", u, "->", st, len(b))
