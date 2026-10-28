#!/usr/bin/env python3
"""Redact LIVE AgentMail key literals from the ACTIVE gateway log, in place.

Why in place, and not by replacing the file:
  The gateway holds this log open for append. Swapping the inode would leave
  the process writing to an orphaned file (the visible log silently freezes).
  Truncating it would destroy the diagnostic trail for no disk gain - there
  is 15G free and the file is not what is filling the disk.

  So: overwrite each match IN PLACE with a same-length mask. Byte offsets
  never shift, the inode is never replaced, the gateway's file descriptor
  and append position stay exactly as they were, and the secret is gone.

Only keys the PROVIDER confirms live are masked. Dead keys are left in
place: a 403 key is not a credential, and redaction is not the goal -
removing a usable secret is.
"""
import pathlib
import re
import urllib.error
import urllib.request

ENV_FILE = pathlib.Path("/workspace/.env")
KEY_RE = re.compile(rb"am_us_[A-Za-z0-9_]{20,}")
ACTIVE_LOG = pathlib.Path("/tmp/openclaw/openclaw-2026-10-23.log")
MASK = b"REDACTED_AM_KEY"


def load_env_keys():
    out = {}
    if not ENV_FILE.exists():
        return out
    for line in ENV_FILE.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        if v.startswith("am_us_") and len(v) > 20:
            out[k.strip()] = v
    return out


def probe(key):
    req = urllib.request.Request(
        "https://api.agentmail.to/v0/inboxes",
        headers={"Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, r.status == 200
    except urllib.error.HTTPError as e:
        return e.code, False
    except Exception:  # noqa: BLE001
        return 0, False


def main():
    live = set()
    for name, value in sorted(load_env_keys().items()):
        status, ok = probe(value)
        print(f"  {name:28} HTTP {status or '-':>3}  {'live' if ok else 'DEAD'}")
        if ok:
            live.add(value.encode())
    print()

    if not ACTIVE_LOG.exists():
        print("active log absent")
        return

    data = ACTIVE_LOG.read_bytes()
    matches = [m for m in KEY_RE.finditer(data) if m.group(0) in live]
    print(f"active log: {len(data)} bytes, {len(matches)} LIVE key literal(s) to mask")
    if not matches:
        print("nothing to mask")
        return

    before = ACTIVE_LOG.stat().st_size
    ino = ACTIVE_LOG.stat().st_ino
    masked = 0
    with open(ACTIVE_LOG, "r+b") as fh:
        for m in matches:
            length = len(m.group(0))
            fh.seek(m.start())
            fh.write((MASK + b"_" * length)[:length])
            masked += 1
        fh.flush()

    after = ACTIVE_LOG.stat().st_size
    print(f"masked {masked} literal(s)")
    print(f"size before={before} after={after} (unchanged: {before == after})")
    print(f"inode before={ino} after={ACTIVE_LOG.stat().st_ino} "
          f"(unchanged: {ino == ACTIVE_LOG.stat().st_ino})")

    # Verify.
    check = ACTIVE_LOG.read_bytes()
    remaining = [m for m in KEY_RE.finditer(check) if m.group(0) in live]
    print(f"verify: {len(remaining)} LIVE literal(s) remain in the log")


if __name__ == "__main__":
    main()
