#!/usr/bin/env python3
"""Rewrite Discord messages that contain a live credential literal.

The credential value is read from `.env` in-process and applied with a string
replace BEFORE the message body is ever printed or passed on a command line.
Nothing credential-shaped reaches argv, stdout, a log or a commit.

This is the remediation half of `ops/check-discord-credential-exposure.py`.
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = "/workspace"
GUILD_ID = "1527423712595410974"
CHANNELS = ["1538825048465481728", "1535538004075216987"]
HOW_MANY = 1000
PLACEHOLDER = "[credential removed]"


def load_env(path=os.path.join(ROOT, ".env")):
    env = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def discord_token(env):
    cands = []
    for k in ("DISCORD_BOT_TOKEN", "DISCORD_TOKEN", "DISCORD_BOT"):
        v = env.get(k)
        if v and len(v) > 30:
            cands.append(v)
    try:
        cfg = json.load(open('/root/.openclaw/openclaw.json', encoding='utf-8'))

        def walk(o, path=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    if isinstance(v, str):
                        if 'discord' in path.lower() and len(v) > 30:
                            cands.append(v.strip())
                    else:
                        walk(v, path + "." + k)
            elif isinstance(o, list):
                for v in o:
                    walk(v, path)
        walk(cfg)
    except Exception:
        pass
    for tok in cands:
        req = urllib.request.Request(
            "https://discord.com/api/v10/users/@me",
            headers={"Authorization": "Bot " + tok, "User-Agent": "probe/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=15):
                return tok
        except Exception:
            continue
    return None


def credential_values(env):
    out = {}
    for k, v in env.items():
        if not v or len(v) < 20 or v.startswith("${"):
            continue
        if re.match(r"^[A-Za-z0-9_\-\.\/]+$", v) and not re.match(r"^[\w-]{50,}$", v):
            continue
        out[k] = v
    return out


def fetch_all(token, channel_id, limit):
    out, before = [], None
    while len(out) < limit:
        url = "https://discord.com/api/v10/channels/%s/messages?limit=100" % channel_id
        if before:
            url += "&before=%s" % before
        req = urllib.request.Request(url, headers={
            "Authorization": "Bot " + token, "User-Agent": "redactor/1.0"})
        page = None
        for attempt in range(6):
            try:
                with urllib.request.urlopen(req, timeout=25) as resp:
                    page = json.loads(resp.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as e:
                # Discord rate-limits per-route. Back off and retry rather than
                # aborting the whole sweep on a 429.
                if e.code != 429 or attempt == 5:
                    raise
                time.sleep(5 * (attempt + 1))
        if page is None:
            break
        if not page:
            break
        out.extend(page)
        if len(page) < 100:
            break
        before = page[-1].get("id")
    return out[:limit]


def patch(token, channel_id, message_id, content):
    url = "https://discord.com/api/v10/channels/%s/messages/%s" % (channel_id, message_id)
    body = json.dumps({"content": content}).encode()
    for attempt in range(8):
        req = urllib.request.Request(url, data=body, method="PATCH", headers={
            "Authorization": "Bot " + token,
            "Content-Type": "application/json",
            "User-Agent": "redactor/1.0",
        })
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            # Discord rate-limits writes hard. A partial sweep that gives up on
            # 429 leaves the channel half-cleaned, which is the worst state:
            # the checker still fires, and nobody can tell which half is real.
            if e.code != 429 or attempt == 7:
                raise
            time.sleep(10 * (attempt + 1))
    raise RuntimeError("unreachable")


def main():
    dry = "--dry-run" in sys.argv
    env = load_env()
    creds = credential_values(env)
    token = discord_token(env)
    if not token:
        print("no working Discord token")
        return 2

    changed = scanned = 0
    for channel_id in CHANNELS:
        msgs = fetch_all(token, channel_id, HOW_MANY)
        for msg in msgs:
            scanned += 1
            content = msg.get("content") or ""
            if not content:
                continue
            hits = [name for name, val in creds.items() if val in content]
            if not hits:
                continue
            new = content
            for name, val in creds.items():
                new = new.replace(val, PLACEHOLDER)
            mid = msg.get("id")
            print("channel %s message %s: %s -> %s" % (channel_id, mid, ",".join(hits),
                                                       "DRY-RUN" if dry else "redacting"))
            if not dry:
                try:
                    patch(token, channel_id, mid, new)
                    changed += 1
                except urllib.error.HTTPError as e:
                    print("   FAILED HTTP %s" % e.code)
    print("scanned %d messages | %d message(s) redacted%s"
          % (scanned, changed, "" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
