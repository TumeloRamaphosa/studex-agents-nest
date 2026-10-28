"""Who are the external senders in BOTH AgentMail accounts? Any CIIE organiser /
bank / payment-party address that could carry a badge payment record?

Also lists every message whose subject matches confirmation-ish vocabulary, so a
payment email with a generic subject still surfaces.
"""
import json, re, sys, urllib.request, urllib.error
sys.path.insert(0, "/workspace/scripts")
from agentmail_keys import live_agentmail_keys, assert_not_truncated

KEYS = live_agentmail_keys()
SELF = re.compile(r"(studex-group\.com|agentmail\.to|tumelor001@gmail\.com|mailer-daemon|"
                  r"basecamp|privy\.io|no-reply|noreply|notifications@|openclaw|cashclaw|"
                  r"studexmeat\.com)", re.I)
CONFIRM = re.compile(r"(confirm|receipt|invoice|payment|pay|paid|order|transfer|remit|"
                     r"badge|pass|ticket|entry|registration|申请|付款|转账|确认|凭证|回执|门票)", re.I)


def get(u, k):
    r = urllib.request.Request(u, headers={"Authorization": f"Bearer {k}"})
    try:
        with urllib.request.urlopen(r, timeout=30) as x:
            return x.status, json.loads(x.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as e:
        return 0, {"err": str(e)[:80]}


senders = {}
conf = []
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
        for msg in (m.get("messages") or m.get("items") or []):
            frm = msg.get("from") or ""
            if isinstance(frm, list):
                frm = " ".join(map(str, frm))
            frm = str(frm)
            subj = str(msg.get("subject") or "")
            if frm and not SELF.search(frm):
                senders.setdefault(frm, []).append(
                    (str(msg.get("created_at") or msg.get("sent_at"))[:19], addr, subj[:70], msg.get("size")))
            if CONFIRM.search(subj):
                conf.append((str(msg.get("created_at") or msg.get("sent_at"))[:19], addr, frm[:40], subj[:80], msg.get("size")))

print("=== EXTERNAL SENDERS (non-self) ===")
for f, rows in sorted(senders.items()):
    rows.sort(reverse=True)
    print(f"\n{f}  ({len(rows)} msgs)")
    for r in rows[:3]:
        print(f"   {r[0]} | {r[1][:30]:30} | {r[2]}")

print("\n\n=== CONFIRMATION-SUBJECT MESSAGES (newest 40) ===")
conf.sort(reverse=True)
for r in conf[:40]:
    print(f"  {r[0]} | {r[4]}B | {r[1][:26]:26} | {r[2][:34]:34} | {r[3]}")
print(f"\ntotal confirmation-subject msgs: {len(conf)}")
