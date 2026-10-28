#!/usr/bin/env python3
"""Append the credential-leak lesson to HEARTBEAT.md (idempotent)."""
import io

P = "/workspace/HEARTBEAT.md"
MARKER = "NEVER SHIP A CREDENTIAL IN A LANDING PAGE"

BLOCK = """
### 🚨 NEVER SHIP A CREDENTIAL IN A LANDING PAGE (2026-10-23, verified + fixed)
A landing page is a **public document**. Two React landing pages hardcoded the AgentMail GENERAL key
and baked it into their **public JS bundle** (`y0r9ilfj96mj`, `q3afz51say2o`). The key could list all
10 inboxes, read buyer correspondence and send mail as us. **Revoked and verified 401.**
**The rule: credentials belong server-side.** All lead forms now POST to `studex-lead-proxy/`
(Cloudflare Worker) which holds the credential as a **secret**. `ops/secret_leak_scan.py` runs on every
drift check and fails the build if any credential appears in a browser-served file (negative-tested).
🔑 **Rotation is not a fix** — revoking stops the bleeding, but the next deploy ships the next key.
The fix had to be architectural.
🔑 **A green form that silently fails is the same bug as a green cron that produces nothing.** Three of
the five pages posted to routes that **404** and then showed "Enquiry Received ✅" regardless — one
carried the literal comment *"Fallback: still show success so the user isn't lost"*, another fell back to
a `mailto:` on a domain with **no DNS record**. **A visitor's enquiry was never delivered and the page
said it was.** Always read what the code *does*, never what it *claims*.
🔑 **The AgentMail send route is `/v0/inboxes/{inbox}/messages/send`.** `/v0/messages`,
`/v0/messages/send` and `/v0/webhook/lead` all **404**. A 404 from AgentMail is a *routing* error,
not a permissions error — do not debug auth when the path is wrong.
"""

s = io.open(P, encoding="utf-8").read()
if MARKER in s:
    print("already present")
else:
    io.open(P, "w", encoding="utf-8").write(s.rstrip("\n") + "\n" + BLOCK)
    print("HEARTBEAT.md updated")
