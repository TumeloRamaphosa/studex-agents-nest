#!/usr/bin/env python3
"""Which URLs did the CIIE nurture emails actually carry?

🔑 WHY THIS SCRIPT IS NOT A "GREP THE MAILBOX" SCRIPT
---------------------------------------------------
The AgentMail message-LIST endpoint returns only
`created_at, from, inbox_id, labels, message_id, organization_id, pod_id,
size, smtp_id, subject, thread_id, timestamp, to, updated_at` - **no body**.
So a body-based count from the list endpoint CANNOT measure anything: it
returns 0 and looks like a clean result. 🔑 *A count that cannot see the
evidence is not a count of zero - it is an absence of measurement.*

This script therefore does TWO things and says which one it used:

  1. It PROVES whether the bodies are available (it does not assume).
     If they are not, it says **COULD NOT PROVE** - it never prints a
     reassuring number it did not earn.
  2. It falls back to the source of truth that IS readable: the **git history
     of the template that was actually sent**. The sends ran 24 Sep - 3 Oct
     2026, so the template version in the tree as of 2026-10-03 is the one
     that produced those bodies.

Usage: python3 scripts/measure-china-link-breach.py
"""
import json
import pathlib
import subprocess
import sys
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from agentmail_keys import live_agentmail_keys

KEY = live_agentmail_keys()[-1]
BASE = "https://api.agentmail.to/v0"
INBOX = "project-2571-studex-agent-2077@agentmail.to"
TEMPLATE = "ciie-nurture/src/emails.ts"
SEND_WINDOW_END = "2026-10-04"          # the sends ran 24 Sep - 3 Oct 2026
RETIRED = ["lqzo3q09yntr", "eukr32nxiptw"]   # served the wrong tariff claim


def get(path):
    r = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + KEY})
    with urllib.request.urlopen(r, timeout=120) as x:
        return json.load(x)


def bodies_available():
    msgs = get("/inboxes/%s/messages?limit=5" % INBOX).get("messages", [])
    if not msgs:
        return None, []
    return any(k in msgs[0] for k in ("text", "html", "body")), msgs


def sent_template_rev():
    out = subprocess.run(
        ["git", "rev-list", "-1", "--before=" + SEND_WINDOW_END, "HEAD", "--", TEMPLATE],
        cwd="/workspace", capture_output=True, text=True, timeout=60).stdout.strip()
    return out


def main():
    print("=== 1. can the sent messages' bodies be read at all? ===")
    avail, msgs = bodies_available()
    if avail is None:
        print("   COULD NOT PROVE - the inbox returned no messages to inspect")
        return 2
    if not avail:
        print("   NO - the list endpoint carries no body field.")
        print("   => a body count from this endpoint would print 0 and look clean.")
        print("   => this script therefore does NOT report a count from mail.")
    else:
        print("   YES - bodies are present, the mailbox method applies.")

    print()
    print("=== 2. the template that was actually sent (git, as of %s) ===" % SEND_WINDOW_END)
    rev = sent_template_rev()
    if not rev:
        print("   COULD NOT PROVE - %s did not exist in the tree before %s"
              % (TEMPLATE, SEND_WINDOW_END))
        return 2
    blob = subprocess.run(["git", "show", "%s:%s" % (rev, TEMPLATE)],
                          cwd="/workspace", capture_output=True, text=True, timeout=60).stdout
    if not blob:
        print("   COULD NOT PROVE - could not read %s at %s" % (TEMPLATE, rev[:12]))
        return 2
    urls = sorted(set(u.rstrip("\"'`,)") for u in __import__("re").findall(
        r"https?://[^\s\"'`,)]+", blob)))
    print("   template %s at %s" % (TEMPLATE, rev[:12]))
    for u in urls:
        print("      " + u)
    hit = [u for u in urls if any(s in u for s in RETIRED)]
    print()
    if hit:
        print("   RESULT: the sent template DID link a page with the wrong claim: %s" % hit)
        print("   -> the buyers who received it need to be told, and the link replaced.")
        return 1
    print("   RESULT: the sent template carried NO link to a page with the wrong claim.")
    print("   -> no buyer was reached by the wrong claim; no buyer correction is owed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
