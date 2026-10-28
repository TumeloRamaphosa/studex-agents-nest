import json, re, sys, urllib.request, urllib.error
sys.path.insert(0, "/workspace/scripts")
from agentmail_keys import live_agentmail_keys, assert_not_truncated

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

# Broad financial/payment vocabulary across subject + preview + from + to.
BROAD = re.compile(r"(pay|paid|payment|receipt|transfer|remitt|bank|invoice|"
                   r"付款|转账|收款|凭证|交易回执|¥|cny|rmb|usd|\$|\b200\b)", re.I)
CIIE = re.compile(r"(c\s*i\s*i\s*e|badge|进博会|import expo|入场)", re.I)

seen = {}
total = 0
for k in KEYS:
    c, d = get("https://api.agentmail.to/v0/inboxes", k)
    if c != 200:
        continue
    for ib in d.get("inboxes", []):
        iid = ib.get("inbox_id") or ib.get("id")
        addr = ib.get("address") or ib.get("name") or iid
        c2, m = get(f"https://api.agentmail.to/v0/inboxes/{iid}/messages?limit=1000", k)
        if c2 != 200:
            continue
        msgs = m.get("messages") or m.get("items") or []
        assert_not_truncated(len(msgs), 1000)
        total += len(msgs)
        for msg in msgs:
            frm = msg.get("from") or ""
            if isinstance(frm, list):
                frm = " ".join(map(str, frm))
            blob = " ".join([str(msg.get("subject") or ""), str(msg.get("preview") or ""),
                             str(frm), str(msg.get("to") or "")])
            if not BROAD.search(blob):
                continue
            mid = msg.get("message_id")
            if mid in seen:
                continue
            seen[mid] = 1
            tag = "CIIE" if CIIE.search(blob) else "    "
            print(f"{tag} {str(msg.get('created_at') or msg.get('sent_at'))[:19]} | {msg.get('size')}B | "
                  f"{addr[:26]:26} | {str(frm)[:34]:34} | {str(msg.get('subject'))[:48]:48} | "
                  f"{str(msg.get('preview'))[:70]}")
print("TOTAL MSGS:", total, "| FLAGGED:", len(seen))
