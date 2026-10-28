#!/usr/bin/env python3
"""Mask ORPHAN credential literals under /tmp in place.

`ops/redact-live-secrets-in-place.py` can only mask values it finds in .env.
An ORPHAN literal - credential-shaped, present in /tmp, NOT in .env - is
invisible to it. This tool finds those by SHAPE and masks them in place with a
same-length mask, so byte offsets and the inode never shift and the gateway's
open append handle stays valid.

DEAD orphans are left in place (a key the provider rejects is not exposure).
LIVE and UNKNOWN orphans are masked: a key we cannot probe is not thereby safe.

Usage: python3 ops/redact-orphan-secrets-in-place.py [--dry-run] [file ...]
"""
import os
import re
import sys
import urllib.error
import urllib.request

ENV = os.environ.get("REDACT_ENV_PATH", "/workspace/.env")
NO_PROBE = os.environ.get("REDACT_NO_PROBE") == "1"

SHAPES = [
    ("FeedHive", r"fh_[A-Za-z0-9]{12,}", (40, 80)),
    ("AgentMail", r"am_us_[A-Za-z0-9]{12,}", (40, 80)),
    ("Stripe/live", r"sk_live_[A-Za-z0-9]{12,}", (20, 200)),
    ("OpenAI-style", r"sk-r[A-Za-z0-9]{12,}", (40, 120)),
    ("Meta/Facebook", r"EAAS[A-Za-z0-9]{12,}", (40, 400)),
    ("ClickUp", r"pk_[0-9]{6,}_[A-Za-z0-9]{12,}", (40, 120)),
    ("Blotato", r"blt_[A-Za-z0-9]{12,}", (40, 120)),
    ("Alibaba-MAAS", r"sk-ws-[A-Za-z0-9._-]{12,}", (40, 200)),
]

PROBES = {
    "FeedHive": ("https://api.feedhive.com/v1/accounts", "Authorization", "Bearer %s"),
    "AgentMail": ("https://api.agentmail.to/v0/inboxes", "X-API-Key", "%s"),
    "ClickUp": ("https://api.clickup.com/api/v2/user", "Authorization", "%s"),
    "Blotato": ("https://backend.blotato.com/v2/users/me/accounts", "blotato-api-key", "%s"),
    "Meta/Facebook": ("https://graph.facebook.com/v19.0/me", "Authorization", "Bearer %s"),
}

FIXTURE_DIRS = (
    "/tmp/cred-fence-", "/tmp/ccheck", "/tmp/c_fenced", "/tmp/c_inline",
    "/tmp/c_plain", "/tmp/leaktest", "/tmp/dbg2",
)


def env_blob():
    out = []
    try:
        with open(ENV) as fh:
            for line in fh:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    out.append(line.split("=", 1)[1].strip().strip('"').strip("'"))
    except Exception:
        pass
    return "\n".join(out)


def probe(label, value):
    if NO_PROBE:
        return "UNKNOWN"
    if label not in PROBES:
        return "UNKNOWN"
    url, hdr, fmt = PROBES[label]
    try:
        req = urllib.request.Request(url, headers={hdr: fmt % value})
        with urllib.request.urlopen(req, timeout=12) as r:
            return "LIVE"
    except urllib.error.HTTPError as e:
        return "DEAD" if e.code in (401, 403) else "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def mask_in_place(path, value):
    vb = value.encode()
    repl = (b"REDACTED" + b"_" * len(vb))[:len(vb)]
    with open(path, "r+b") as fh:
        data = fh.read()
        n = data.count(vb)
        if n:
            fh.seek(0)
            fh.write(data.replace(vb, repl))
            fh.flush()
            os.fsync(fh.fileno())
    return n


def main():
    dry = "--dry-run" in sys.argv
    targets = ([a for a in sys.argv[1:] if not a.startswith("--")]
               or [os.environ.get("REDACT_SCAN_ROOT", "/tmp")])
    blob = env_blob()
    orphans = {}
    for root in targets:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ("node_modules", "__pycache__")]
            for fn in filenames:
                p = os.path.join(dirpath, fn)
                if any(p.startswith(d) for d in FIXTURE_DIRS):
                    continue
                try:
                    st = os.stat(p)
                    if st.st_size > 400 * 1024 * 1024:
                        continue
                    with open(p, "rb") as fh:
                        txt = fh.read().decode("utf-8", "replace")
                except Exception:
                    continue
                for label, rx, (lo, hi) in SHAPES:
                    for m in re.finditer(rx, txt):
                        val = m.group(0)
                        if not (lo <= len(val) <= hi):
                            continue
                        if val in blob:
                            continue
                        orphans.setdefault(label, {}).setdefault(val, set()).add(p)
    print("=== orphan literals found ===")
    todo = []
    for label in sorted(orphans):
        for val, files in orphans[label].items():
            verdict = probe(label, val)
            mark = "MASK" if verdict in ("LIVE", "UNKNOWN") else "leave (DEAD)"
            print("  %-14s len=%-4d %-8s %s -> %s" % (
                label, len(val), verdict, ", ".join(sorted(files)[:3]), mark))
            if verdict in ("LIVE", "UNKNOWN"):
                todo.append((label, val, sorted(files)))
    if dry:
        print("\nDRY RUN - nothing masked")
        return 0
    print("\n=== masking in place ===")
    total = 0
    for label, val, files in todo:
        for p in files:
            before = os.stat(p)
            n = mask_in_place(p, val)
            after = os.stat(p)
            total += n
            print("  %-60s %-14s masked=%d size %d->%d inode %s->%s" % (
                p, label, n, before.st_size, after.st_size, before.st_ino, after.st_ino))
    print("\ntotal masked occurrences:", total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
