#!/usr/bin/env python3
"""Restore the Blotato key from the running gateway's environment.

The redaction incident of 2026-10-28 05:30 wrote the literal text
`t = t.replace(secret, "***")` into the BLOTATO_API_KEY slots of .env,
scripts/daily-post.py and scripts/check_blotato_accounts.py. The API rejects
it (HTTP 401).

Publishing still worked after that because the gateway process had already
loaded the REAL key into its environment before .env was damaged - and both
publish paths prefer the environment over the file. A gateway restart would
therefore have loaded the broken value and taken the publish path down.

This reads the value out of the running gateway's /proc/<pid>/environ and
writes it back into .env and the two script fallbacks. THE VALUE IS NEVER
PRINTED: only HTTP status codes, lengths and shapes.

It refuses to write anything it has not first proved authenticates.
"""
import os
import pathlib
import re
import stat
import subprocess
import sys
import urllib.error
import urllib.request

REPO = pathlib.Path("/workspace")
BROKEN = 't = t.replace(secret, "***")'
KEY_NAME = "BLOTATO_API_KEY"
ACCOUNTS_URL = "https://backend.blotato.com/v2/users/me/accounts"


def probe(value):
    """Return (status_code, ok). Never prints the value."""
    if not value or len(value) < 8:
        return None, False
    req = urllib.request.Request(ACCOUNTS_URL, headers={"Authorization": value})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.status in (200, 201)
    except urllib.error.HTTPError as e:
        return e.code, False
    except Exception:
        return None, False


def gateway_env():
    """Find a running gateway process and read its environment."""
    out = subprocess.run(["ps", "-eo", "pid,args"], capture_output=True,
                         text=True).stdout
    for line in out.splitlines():
        if "openclaw" not in line.lower():
            continue
        if "grep" in line:
            continue
        pid = line.split()[0]
        if not pid.isdigit():
            continue
        try:
            raw = pathlib.Path("/proc/%s/environ" % pid).read_bytes()
        except OSError:
            continue
        env = {}
        for item in raw.split(b"\0"):
            if b"=" in item:
                k, v = item.split(b"=", 1)
                env[k.decode("utf-8", "replace")] = v.decode("utf-8", "replace")
        if KEY_NAME in env:
            return pid, env[KEY_NAME]
    return None, None


def write_env(value):
    p = REPO / ".env"
    text = p.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    hit = False
    for i, line in enumerate(lines):
        if line.split("=", 1)[0].strip() == KEY_NAME:
            lines[i] = "%s=%s" % (KEY_NAME, value)
            hit = True
    if not hit:
        lines.append("%s=%s" % (KEY_NAME, value))
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.chmod(p, stat.S_IRUSR | stat.S_IWUSR)
    return hit


def write_script(rel, value):
    p = REPO / rel
    text = p.read_text(encoding="utf-8", errors="replace")
    esc = value.replace("\\", "\\\\").replace('"', '\\"')
    new = re.sub(r'(?m)^(%s\s*=\s*")[^"]*(")' % KEY_NAME,
                 lambda m: m.group(1) + esc + m.group(2), text, count=1)
    if new == text:
        return False
    p.write_text(new, encoding="utf-8")
    return True


def main():
    print("### 1. is the current value usable?")
    cur = None
    for line in (REPO / ".env").read_text(errors="replace").splitlines():
        if line.split("=", 1)[0].strip() == KEY_NAME:
            cur = line.split("=", 1)[1].strip().strip('"').strip("'")
    st, ok = probe(cur)
    print("  .env value: length=%d status=%s usable=%s"
          % (len(cur or ""), st, ok))

    print()
    print("### 2. the running gateway's environment")
    pid, val = gateway_env()
    if not val:
        print("  no running gateway process exposes %s" % KEY_NAME)
        print("  -> the key must be supplied by hand (Tumelo)")
        return 2
    print("  gateway pid=%s  value length=%d" % (pid, len(val)))
    st, ok = probe(val)
    print("  probe: status=%s usable=%s" % (st, ok))
    if not ok:
        print("  -> the environment value does not authenticate either; "
              "the key must be rotated")
        return 2

    print()
    print("### 3. write it back (never printed)")
    print("  .env updated (existing slot): %s" % write_env(val))
    for rel in ["scripts/daily-post.py", "scripts/check_blotato_accounts.py"]:
        print("  %s updated: %s" % (rel, write_script(rel, val)))

    print()
    print("### 4. verify - by probing, not by reading")
    for line in (REPO / ".env").read_text(errors="replace").splitlines():
        if line.split("=", 1)[0].strip() == KEY_NAME:
            v = line.split("=", 1)[1].strip().strip('"').strip("'")
            st, ok = probe(v)
            print("  .env: length=%d status=%s usable=%s" % (len(v), st, ok))
    for rel in ["scripts/daily-post.py", "scripts/check_blotato_accounts.py"]:
        text = (REPO / rel).read_text(errors="replace")
        m = re.search(r'(?m)^%s\s*=\s*"([^"]*)"' % KEY_NAME, text)
        if m:
            st, ok = probe(m.group(1))
            print("  %s: length=%d status=%s usable=%s"
                  % (rel, len(m.group(1)), st, ok))
    return 0


if __name__ == "__main__":
    sys.exit(main())
