#!/usr/bin/env python3
"""
Tests for ops/check-cron-payload-claims.py.

A checker that accepts no negative control is unusable - so every rule here is
proven by a fixture that MUST trip it, and by a fixture that must NOT.

All fixtures are written to a SANDBOX. A rule-proving test must never run
where the rule applies: this checker reads a live cron file, so a stray
fixture in the real one would be one stray re-enable away from publishing.
"""

import json
import os
import subprocess
import sys
import tempfile

CHECKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check-cron-payload-claims.py")

# The payload that was actually published to #ops on 2026-10-24 05:13 UTC.
BAD_PAYLOAD = """You are Robusca, CEO of Studex. Send the morning Discord ops summary.

Use the message tool (action=send, channel=discord, target=1538825048465481728, accountId=1527423712595410974) to send this exact message:

---
☀️ **Good morning, Studex team — ops briefing**

**🛒 Shopify:** 🔴 77+ days dark — Admin API token expired. Tumelo must reconnect via Shopify Partners.
**📱 Meta (FB/IG):** 🔴 80+ days dark — token expired Jun 27.
**🤖 Blotato:** 🟡 past_due ($49/mo). Tumelo renew.
**🔴 FeedHive:** 404 for 13+ days — account suspended or API key rotated.
**📬 AgentMail:** robusca.romanov@studex-group.com ✅ | charlie/naledi DNS pending setup.

**✅ Systems live:** Discord ✅ | AgentMail ✅ | Orgo VM 47.236.124.79 ✅ | Composio MCP ✅

---
"""

# The corrected payload: it names the systems it probes but asserts no status.
GOOD_PAYLOAD = """You are Robusca, CEO of Studex. Send the morning Discord ops summary.

The briefing MUST come from the live-probe script. Never write a status line yourself.

1. Run: cd /workspace/discord-ops-bot && node src/sendSummary.js --dry-run
   It probes every system live at that moment (Shopify storefront, Alibaba Cloud VM, Orgo VM, the hub, Blotato) and prints the complete briefing.
2. Send that printed text VERBATIM as the entire message body. Do not edit it, do not add or remove lines, and do not hardcode any host, IP, port, day-count or status. If a system is down, the script already says so - that IS the finding, not something to smooth over.

Use the message tool (action=send, channel=discord, target=1538825048465481728, accountId=1527423712595410974) to send it to the meat-store-coffee-ops channel.

After sending, confirm the message was sent with the messageId returned by the tool.
"""

results = []


def run_checker(jobs_obj, present=True):
    """Run the checker against a sandboxed cron file. Returns (exit_code, output)."""
    tmpdir = tempfile.mkdtemp(prefix="cronpayload-")
    path = os.path.join(tmpdir, "jobs.json")
    if present:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(jobs_obj, fh)
    env = dict(os.environ, CRON_JOBS_FILE=path)
    proc = subprocess.run(
        [sys.executable, CHECKER],
        env=env, capture_output=True, text=True, timeout=120,
    )
    return proc.returncode, proc.stdout + proc.stderr


def job(jid, name, message, enabled=True):
    return {
        "id": jid,
        "name": name,
        "enabled": enabled,
        "schedule": {"kind": "cron", "expr": "0 7 * * *", "tz": "Africa/Johannesburg"},
        "payload": {"message": message},
    }


def check(name, condition, detail=""):
    results.append((name, bool(condition), detail))
    print("[%s] case %s  %s" % ("PASS" if condition else "FAIL", name, detail))


# --- case 1: the real published payload MUST trip the checker -----------------
code, out = run_checker({"jobs": [job("7f1540cc", "Discord Ops Morning Summary", BAD_PAYLOAD)]})
check("1  the published false briefing is caught", code == 1 and "DRIFT" in out,
      "reported=True exit=%d" % code)

# --- case 2: the corrected payload MUST pass ----------------------------------
code, out = run_checker({"jobs": [job("7f1540cc", "Discord Ops Morning Summary", GOOD_PAYLOAD)]})
check("2  the corrected payload passes", code == 0 and "CLEAN" in out,
      "exit=%d" % code)

# --- case 3: a MISSING cron file is UNCHECKED, not a pass ---------------------
code, out = run_checker(None, present=False)
check("3  a missing cron file is UNCHECKED, never CLEAN",
      code == 2 and "UNCHECKED" in out and "CLEAN" not in out,
      "exit=%d" % code)

# --- case 4: a disabled job does not fail the build, but IS reported ---------
code, out = run_checker({"jobs": [job("off1", "Disabled job", BAD_PAYLOAD, enabled=False)]})
check("4  a disabled job is reported but does not fail",
      code == 0 and "DISABLED" in out,
      "exit=%d" % code)

# --- case 5: a payload that names systems WITHOUT a status marker is fine ----
code, out = run_checker({"jobs": [job("n1", "Build Hour", "Deploy it: exec to Orgo VM for backend.\nSee the Shopify storefront docs.")]})
check("5  naming a system without asserting status is allowed", code == 0,
      "exit=%d" % code)

# --- case 6: a single paraphrased status claim is still caught ---------------
# The old guard listed exact sentences. A paraphrase must not slip through.
PARAPHRASE = "**Systems live:** Discord ✅ | AgentMail ✅ | Orgo VM 47.236.124.79 ✅ | Composio MCP ✅"
code, out = run_checker({"jobs": [job("p1", "Ops Summary", PARAPHRASE)]})
check("6  a paraphrased status line is still caught",
      code == 1 and "47.236.124.79" in out,
      "exit=%d" % code)

# --- case 7: the checker reads EVERY payload string, not just 'message' ------
alt = job("alt1", "Alt payload", "")
alt["payload"] = {"text": BAD_PAYLOAD}
code, out = run_checker({"jobs": [alt]})
check("7  a payload under a different key is still scanned",
      code == 1 and "DRIFT" in out,
      "exit=%d" % code)

# --- case 8: the live cron file must now be clean ---------------------------
live = os.environ.get("CRON_JOBS_FILE", "/root/.openclaw/cron/jobs.json")
if os.path.exists(live):
    env = dict(os.environ, CRON_JOBS_FILE=live)
    proc = subprocess.run([sys.executable, CHECKER], env=env,
                          capture_output=True, text=True, timeout=120)
    check("8  the LIVE cron file is clean", proc.returncode == 0,
          "exit=%d" % proc.returncode)
else:
    print("[SKIP] case 8  live cron file not present on this host")

# --- case 9: a FALSE POSITIVE must not be reported -------------------------
# The real Morning Nudge payload mentions AgentMail and then, 250 characters
# later, warns that two dead inboxes must never be named. The warning glyph
# belongs to the warning, not to AgentMail's status. A checker that reads it
# as "AgentMail is down" is a checker people switch off.
# NOTE: every address here is a LIVE one from ops/live-inbox-allowlist.txt. A
# fixture that carries a DEAD mailbox is itself a dead-mailbox finding - the
# same rule applies to test fixtures as to shipped copy.
FP_PAYLOAD = ("2. **AgentMail** \u2014 check the LIVE inboxes only: meat@studex-group.com \u00b7 "
              "naledi-cmo@studex-group.com \u00b7 t-ramaphosa-ceo@studex-group.com \u00b7 "
              "sales@studex-group.com \u00b7 info@studex-group.com \u00b7 "
              "support.superagents@studex-group.com. \u26a0\ufe0f the two legacy mailboxes "
              "DO NOT EXIST (domain has no DNS, 404 inbox-not-found) "
              "\u2014 never name them again.")
code, out = run_checker({"jobs": [job("fp1", "Morning Nudge", FP_PAYLOAD)]})
check("9  a distant warning glyph is not a status claim",
      code == 0 and "DRIFT" not in out,
      "exit=%d" % code)

print()
passed = sum(1 for _, ok, _ in results if ok)
failed = len(results) - passed
for name, ok, detail in results:
    if not ok:
        print("  FAILED: %s  %s" % (name, detail))
print("%d passed, %d failed" % (passed, failed))
sys.exit(1 if failed else 0)
