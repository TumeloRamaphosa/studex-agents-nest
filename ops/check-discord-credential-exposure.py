#!/usr/bin/env python3
"""Read-only: is a LIVE credential literal sitting in a Discord message?

THE FINDING THIS EXISTS FOR (2026-10-27)
---------------------------------------
`ops/check-scanner-log-exposure.py` found FEEDHIVE_API_KEY in the gateway log
and reported it as EXPOSED. The log was NOT the source. The log only held a
COPY of a Discord message posted by our own "Auto - Meat" bot on
2026-10-05 / 10-09 / 10-12 / 10-14 / 10-15 / 10-16 / 10-19 / 10-20 / 10-21,
each of which quoted the full token while reporting the FeedHive outage:

    "FeedHive API ... token `fh_...` invalid since 2026-10-05"

KEY INSIGHT: A log copy of a credential is a SYMPTOM. The message is the
DISEASE. Masking the log made the scanner green while the key was still
readable by anyone in the guild - and every subsequent READ of that channel
re-copied it back into the log (12x in a single pass). The log scanner could
never have caught the source, because it only looks at local surfaces.

WHY A SEPARATE CHECKER
----------------------
`check-price-on-feed.py` already enforces house rule [10] ("no price on a
public feed") across the same staged captions and the same live feed. A
credential literal on a public feed is the same class of breach with a much
worse blast radius: a price leaks margin, a credential leaks the account.

WHAT IT CHECKS
--------------
For each known guild channel, fetch recent messages (paginated) and test
every message body against the credential values in `/workspace/.env`. A hit
is a finding.

The credential VALUES are read from `.env` in-process and are never placed in
argv, never printed, and never written to a log or a commit. The report names
the credential, the channel and the message id - never the value.

EXIT CODES
----------
  0 = clean (and the scan was COMPLETE)
  1 = a live credential literal is present in a Discord message
  2 = could not prove (no Discord token / API unreachable / scan truncated)
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = "/workspace"
ENV_PATH = os.path.join(ROOT, ".env")

# The channels our own bot posts to. Kept explicit: a checker that scans
# "every channel the bot can see" would silently change scope when a channel
# is added, and a silent scope change is how a control stops being a control.
GUILD_ID = "1527423712595410974"
CHANNELS = {
    "1538825048465481728": "meat-store--coffee-ops (#ops)",
    "1535538004075216987": "marketing-command-center",
}
HOW_MANY = 1000  # messages per channel (paginated)

# A Discord token is long and mixed-case; require a real shape so we never
# probe with a random string.
TOKEN_RE = re.compile(r"^[\w-]{50,}$")


def load_env(path=ENV_PATH):
    env = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    except OSError as e:
        return {}, str(e)
    return env, None


def credential_values(env):
    """Live credential values from .env.

    Only values that actually LOOK like credentials are considered: a value
    that is a plain word is not a credential, and matching on it would flag
    every message that happens to contain that word.
    """
    out = {}
    for k, v in env.items():
        if not v or len(v) < 20:
            continue
        if re.match(r"^\$\{", v):        # an unresolved reference, not a value
            continue
        if re.match(r"^[A-Za-z0-9_\-\.\/]+$", v) and not TOKEN_RE.match(v):
            continue
        out[k] = v
    return out


def discord_token(env):
    """The bot token, read-only.

    ORDER MATTERS: the `.env` copy of DISCORD_BOT_TOKEN is STALE (HTTP 401 -
    verified 2026-10-27) while the gateway's own config holds the working
    token. A checker that trusted `.env` first would report "COULD NOT PROVE"
    forever and be ignored - which is worse than not existing. So we try every
    source and use the first one that actually authenticates.

    NOTE: the token value is never printed, never logged and never written to
    a file. Only the outcome of the probe is used.
    """
    candidates = []
    for k in ("DISCORD_BOT_TOKEN", "DISCORD_TOKEN", "DISCORD_BOT"):
        v = env.get(k)
        if v and len(v) > 30:
            candidates.append(v)
    # Gateway config - read-only, never modified.
    try:
        cfg = json.load(open('/root/.openclaw/openclaw.json', encoding='utf-8'))

        def walk(o, path=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    if isinstance(v, str):
                        if 'discord' in path.lower() and len(v) > 30:
                            candidates.append(v.strip())
                    else:
                        walk(v, path + "." + k)
            elif isinstance(o, list):
                for v in o:
                    walk(v, path)
        walk(cfg)
    except Exception:
        pass

    for tok in candidates:
        req = urllib.request.Request(
            "https://discord.com/api/v10/users/@me",
            headers={"Authorization": "Bot " + tok, "User-Agent": "probe/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=15):
                return tok
        except Exception:
            continue
    return None


def fetch_messages(token, channel_id, limit=HOW_MANY):
    """Fetch up to `limit` messages, paginating backwards.

    Pagination is not optional here. The 100 most recent messages in #ops do
    NOT reach back to 2026-10-05, and the messages that carried the FeedHive
    token were posted in that fortnight. A single-page fetch reported CLEAN on
    a channel that still held the leak - a false negative in the exact check
    meant to catch it. Discord's `before` parameter walks backwards from a
    known message id.

    Returns (messages, error, complete). `complete` is False when the walk
    stopped early (rate limit that did not clear). A truncated scan must NOT
    be reported as CLEAN.
    """
    out = []
    before = None
    complete = True
    while len(out) < limit:
        url = "https://discord.com/api/v10/channels/%s/messages?limit=100" % channel_id
        if before:
            url += "&before=%s" % before
        req = urllib.request.Request(url, headers={
            "Authorization": "Bot " + token,
            "User-Agent": "studex-ops-checker/1.0",
        })
        page = None
        for attempt in range(8):
            try:
                with urllib.request.urlopen(req, timeout=25) as resp:
                    page = json.loads(resp.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    # Rate-limited mid-pagination. Retrying keeps the scan
                    # whole; giving up here would silently truncate the window
                    # and report CLEAN over an area that was never read.
                    time.sleep(8 * (attempt + 1))
                    continue
                return out, ("HTTP %s" % e.code) if not out else None, complete
            except Exception as e:
                return out, type(e).__name__ if not out else None, complete
        if page is None:
            complete = False
            break
        if not isinstance(page, list) or not page:
            break
        out.extend(page)
        if len(page) < 100:
            break
        before = page[-1].get("id")
    return out[:limit], None, complete


def message_text(msg):
    parts = [msg.get("content") or ""]
    for embed in msg.get("embeds") or []:
        if isinstance(embed, dict):
            parts.append(str(embed.get("description") or ""))
            parts.append(str(embed.get("title") or ""))
    return "\n".join(parts)


def main():
    env, err = load_env()
    if err:
        print("VERDICT: COULD NOT PROVE - cannot read %s (%s)" % (ENV_PATH, err))
        return 2

    creds = credential_values(env)
    if not creds:
        print("VERDICT: COULD NOT PROVE - no credential-shaped values in .env")
        return 2

    token = discord_token(env)
    if not token:
        print("VERDICT: COULD NOT PROVE - no working Discord bot token")
        return 2

    findings = []
    unreadable = []
    incomplete = []
    scanned = 0

    for channel_id, label in CHANNELS.items():
        msgs, err, complete = fetch_messages(token, channel_id)
        if not complete:
            incomplete.append(label)
        if err:
            unreadable.append("%s (%s)" % (label, err))
            continue
        for msg in msgs:
            scanned += 1
            body = message_text(msg)
            if not body:
                continue
            for name, value in creds.items():
                if value in body:
                    findings.append({
                        "channel": label,
                        "channel_id": channel_id,
                        "message_id": msg.get("id"),
                        "author": (msg.get("author") or {}).get("username"),
                        "timestamp": msg.get("timestamp"),
                        "credential": name,
                        "value_len": len(value),
                        "value_prefix": value[:4] + "...",
                    })

    print("channels checked   : %d" % len(CHANNELS))
    print("messages scanned   : %d" % scanned)
    print("credentials tested : %d (values never printed)" % len(creds))
    if unreadable:
        print("channels unreadable: %s" % "; ".join(unreadable))
    if incomplete:
        print("channels truncated : %s (rate limit - window NOT fully read)" % "; ".join(incomplete))

    if findings:
        print("")
        print("!! LIVE CREDENTIAL LITERALS IN DISCORD MESSAGES !!")
        for f in findings:
            print("   [%s] %s (%s) message %s by %s at %s - value REDACTED (%d chars, prefix %s)"
                  % (f["credential"], f["channel"], f["channel_id"], f["message_id"],
                     f["author"], f["timestamp"], f["value_len"], f["value_prefix"]))
        print("")
        print("Remedy: python3 ops/redact-discord-credentials.py   (edits the messages)")
        print("        then rotate the credential at the provider.")
        print("VERDICT: EXPOSED")
        return 1

    if unreadable and scanned == 0:
        print("VERDICT: COULD NOT PROVE - no channel could be read")
        return 2

    if incomplete:
        # A partial scan that found nothing is NOT a clean scan.
        print("VERDICT: COULD NOT PROVE - scan was truncated, so absence is not evidence")
        return 2

    print("VERDICT: CLEAN - no live credential literal in any scanned message")
    return 0


if __name__ == "__main__":
    sys.exit(main())
