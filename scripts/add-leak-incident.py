#!/usr/bin/env python3
"""Append the API-key-leak incident to the 2026-10-22 vault daily log."""
import io

P = "/workspace/studex-obsidian-vault/daily/2026-10-22.md"
ANCHOR = "### ⚠️ The empty-email defect is now FIXED"

BLOCK = """### 🚨 CRITICAL: A LIVE API KEY WAS SHIPPED IN PUBLIC JAVASCRIPT — found + fixed 23 Oct 01:20 UTC

**What was exposed.** The AgentMail **GENERAL** key (`am_us_24fcb0…`) was hardcoded in the source of
**five React landing pages** and baked into the **public JS bundle** of two of them that were live:
- `y0r9ilfj96mj.space.mcode.io` (CIIE coffee landing)
- `q3afz51say2o.space.mcode.io` (coffee noir B2B landing)

**What an attacker could do with it — all verified against the live key:**
- List **all 10 AgentMail inboxes** (`GET /v0/inboxes` → 200, 10 inboxes incl. `sales@`, `naledi-cmo@`)
- **Read buyer correspondence** — including the 4 partner threads and all CIIE buyer emails
- **Send mail as us** from any of those inboxes (`POST /v0/inboxes/{inbox}/messages/send` → 200)

**Fixed:**
1. **Key revoked** — `DELETE /v0/api-keys/e80920a2…` → 204. Verified dead: `GET /v0/inboxes` → **401**,
   `POST …/messages/send` → **401**. Replacement key created (`************…`).
2. **Key removed from every source and build** — 5 landing pages + 6 scripts + TOOLS.md + n8n workflows
   + env files. **0 matches for `am_us_` in any built bundle.**
3. **Server-side proxy built and deployed** — `studex-lead-proxy/` (Cloudflare Worker), the AgentMail
   credential stored as a **Worker secret**, never in a bundle. Live: `studex-lead-proxy.tumelor001.workers.dev`
4. **Broken endpoints fixed** — all 5 pages posted to routes that **404** (`/v0/messages/send`,
   `/v0/messages`, `/v0/webhook/lead`). The real route is `/v0/inboxes/{inbox}/messages/send`.
5. **Fake success removed** — 3 of the pages swallowed the error and showed a green ✅ regardless.
   `coffee-noir-landing` had the comment *"Fallback: still show success so the user isn't lost"* and
   `china-coffee-lead-capture` opened a `mailto:ceo@agent.studexmeat.com` — a domain with **no DNS record**.
   **The pages now report a real failure** instead of a fake success.
6. **Guard rail added** — `ops/secret_leak_scan.py`, wired into the drift check (**13 pages** now).
   **Negative-tested**: injecting a key into a bundle makes it report DRIFT and exit 1.

🔑 **THE LESSON: a landing page is a PUBLIC document. Never put a credential in one.**
This is the same class of error as the empty-email defect — **a green check that meant nothing**. The
lead form showed "Enquiry Received ✅" while posting to a 404 route. A visitor's enquiry was **never
delivered and the page said it was**. Both the leak and the fake-success had to be found by looking at
what the code *actually did*, not at what it *claimed*.
🔑 **Rotation is not a fix.** Revoking the key stops the bleeding; it does not stop the next deploy from
shipping the next key. The fix had to be **architectural** — credentials belong server-side.

### ⚠️ The empty-email defect is now FIXED"""

s = io.open(P, encoding="utf-8").read()
if "CRITICAL: A LIVE API KEY WAS SHIPPED" in s:
    print("already present")
elif ANCHOR in s:
    s = s.replace(ANCHOR, BLOCK, 1)
    io.open(P, "w", encoding="utf-8").write(s)
    print("vault updated")
else:
    raise SystemExit("ANCHOR MISSING")
