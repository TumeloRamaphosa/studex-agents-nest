import json, sys, urllib.request, urllib.error
sys.path.insert(0, "/workspace/scripts")
from agentmail_keys import live_agentmail_keys

KEYS = live_agentmail_keys()

def get(u, k):
    r = urllib.request.Request(u, headers={"Authorization": f"Bearer {k}"})
    try:
        with urllib.request.urlopen(r, timeout=30) as x:
            return x.status, json.loads(x.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as e:
        return 0, {"err": str(e)[:80]}

stats = {"total": 0, "preview_none": 0, "preview_present": 0, "text_field": 0}
for k in KEYS:
    c, d = get("https://api.agentmail.to/v0/inboxes", k)
    if c != 200:
        continue
    for ib in d.get("inboxes", []):
        iid = ib.get("inbox_id") or ib.get("id")
        c2, m = get(f"https://api.agentmail.to/v0/inboxes/{iid}/messages?limit=1000", k)
        if c2 != 200:
            continue
        for msg in (m.get("messages") or m.get("items") or []):
            stats["total"] += 1
            if "text" in msg:
                stats["text_field"] += 1
            p = msg.get("preview")
            if p:
                stats["preview_present"] += 1
            else:
                stats["preview_none"] += 1
print(json.dumps(stats, indent=2))
print("previews are populated:", stats["preview_present"], "/", stats["total"])
