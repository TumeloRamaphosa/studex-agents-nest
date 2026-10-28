"""Wide external-inbound audit + CIIE badge confirmation check.

The Oct 21 sweep used limit=6 and 13 inboxes and MISSED the Zatsepilov reply.
This pass uses limit=200 across every inbox every key can see, and looks for:
  1. every external inbound, with size (reliable) and a replied/answered heuristic
  2. any CIIE badge payment / registration confirmation (deadline 2026-10-23 16:00 UTC)
"""
import json, re, urllib.request, urllib.error, pathlib

import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys, assert_not_truncated

KEYS = live_agentmail_keys()
SELF = re.compile(r"(studex-group\.com|agentmail\.to|tumelor001@gmail\.com|mailer-daemon|"
                  r"basecamp|privy\.io|no-reply|noreply|notifications@)", re.I)
BADGE = re.compile(r"(badge|cIIE|CN¥|CNY\s*200|payment\s*(confirm|receipt)|registration\s*confirm|"
                   r"visiting\s*card|入场|门票)", re.I)


def get(url, key):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as e:
        return 0, {"error": str(e)[:90]}


# ---- enumerate every inbox any key can see -------------------------------
inbox_key = {}
for k in KEYS:
    code, d = get("https://api.agentmail.to/v0/inboxes", k)
    print(f"[key {k[:12]}…] /v0/inboxes -> {code} count={d.get('count')}")
    for ib in d.get("inboxes", []):
        iid = ib.get("inbox_id") or ib.get("id")
        if iid and iid not in inbox_key:
            inbox_key[iid] = (ib.get("address") or ib.get("name") or iid, k)
print(f"\nINBOXES VISIBLE: {len(inbox_key)}\n")

# ---- pull wide ----------------------------------------------------------
external = []
total = 0
LIMIT = 1000
for iid, (addr, k) in inbox_key.items():
    code, d = get(f"https://api.agentmail.to/v0/inboxes/{iid}/messages?limit={LIMIT}", k)
    if code != 200:
        print(f"  !! {addr} -> HTTP {code} {d.get('error','')}")
        continue
    msgs = d.get("messages") or d.get("items") or []
    # A truncated sweep does not error - it just returns a smaller world.
    assert_not_truncated(len(msgs), LIMIT)
    total += len(msgs)
    for m in msgs:
        frm = m.get("from") or ""
        if isinstance(frm, list):
            frm = " ".join(str(x) for x in frm)
        frm = str(frm)
        if SELF.search(frm):
            continue
        external.append({
            "inbox": addr,
            "date": m.get("sent_at") or m.get("created_at") or "",
            "from": frm,
            "subject": m.get("subject") or "",
            "size": m.get("size"),
            "message_id": m.get("message_id") or m.get("id"),
        })

print(f"TOTAL MESSAGES SCANNED: {total}")
print(f"EXTERNAL (non-self senders): {len(external)}\n")

external.sort(key=lambda x: x["date"], reverse=True)
for e in external:
    flag = "  <-- BADGE/CIIE" if BADGE.search(e["subject"] + " " + e["from"]) else ""
    print(f"  {e['date'][:19]} | {e['size']}B | {e['from'][:58]:58} | {e['subject'][:52]}{flag}")

json.dump(external, open("/tmp/external_inbound.json", "w"), indent=2)
print("\nwrote /tmp/external_inbound.json")
