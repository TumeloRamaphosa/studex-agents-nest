#!/usr/bin/env python3
"""Is the /tmp audit actually covering /tmp?

The 04:47 audit fixed the audit's FAMILY blindness (it now matches the full
value of every credential in .env, not just an `am_us_` regex). But it
still scans a HARDCODED LIST of five files, while the redactor was run
over nine. So the audit can report CLEAN while a live credential sits in
any /tmp file that is not on that list - including the quarantine
directory, which is a RENAME, not a deletion: moving a file to
/tmp/quarantine-* does not remove the secret from it.

This walks /tmp for real, and reports which files hold a live credential
value. Read-only. It never prints a credential value - only the file, the
env var name, and the count.
"""
import os
import pathlib
import re
import urllib.error
import urllib.request

# The canonical credential-name filter lives in ONE place so these tools
# cannot drift apart. See ops/cred_name_filter.py for why a copy-pasted
# regex in nine files was a real security bug.
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "_cred_name_filter", "/workspace/ops/cred_name_filter.py")
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

WORKSPACE = pathlib.Path("/workspace")
ENV_FILE = WORKSPACE / ".env"
CRED_NAME_RE = _mod.CRED_NAME_RE
MIN_LEN = 16

PROBES = {
    "am_us_": ("https://api.agentmail.to/v0/inboxes", "Authorization"),
    "blt_": ("https://backend.blotato.com/v2/users/me/accounts", "blotato-api-key"),
}

# The hardcoded list the current audit script scans.
AUDIT_LIST = [
    "/tmp/openclaw/openclaw-2026-10-21.log",
    "/tmp/openclaw/openclaw-2026-10-23.log",
    "/tmp/openclaw/openclaw-2026-10-24.log",
    "/tmp/part2_probe.py",
    "/tmp/pub_creds.txt",
]


def load_env_creds():
    out = {}
    if not ENV_FILE.exists():
        return out
    for line in ENV_FILE.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        if len(v) >= MIN_LEN and CRED_NAME_RE.match(k.strip()):
            out[k.strip()] = v
    return out


def probe(value):
    for prefix, (url, header) in PROBES.items():
        if not value.startswith(prefix):
            continue
        req = urllib.request.Request(url, headers={header: value})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.status, "LIVE" if r.status == 200 else "unknown"
        except urllib.error.HTTPError as e:
            return e.code, "DEAD" if e.code in (401, 403) else "unknown"
        except Exception:  # noqa: BLE001
            return 0, "unknown"
    return 0, "unknown"


def main():
    creds = load_env_creds()
    live, dead, unknown = [], [], []
    for name, value in sorted(creds.items()):
        status, state = probe(value)
        (live if state == "LIVE" else dead if state == "DEAD" else unknown).append(
            (name, value))
    print(f"credentials in .env: {len(live)} LIVE, {len(dead)} DEAD, {len(unknown)} UNKNOWN")
    print("  (DEAD and UNKNOWN values are NOT masked and do not count as exposure)")
    print()

    targets = [(n, v) for n, v in live]
    if not targets:
        print("no live credential to look for")
        return

    listed = set(AUDIT_LIST)
    found = {}
    scanned = 0
    for root, dirs, files in os.walk("/tmp"):
        # Do not descend into the concurrent session's 1.4G worktree's .git
        for d in list(dirs):
            if d == ".git":
                dirs.remove(d)
        for fname in files:
            path = os.path.join(root, fname)
            try:
                if os.path.getsize(path) > 400_000_000:
                    continue
                data = pathlib.Path(path).read_bytes()
            except OSError:
                continue
            scanned += 1
            for name, value in targets:
                n = data.count(value.encode())
                if n:
                    found.setdefault(path, []).append((name, n))

    print(f"walked /tmp: {scanned} files readable")
    print()
    if not found:
        print("NO live credential literal anywhere under /tmp")
        return

    print("FILES HOLDING A LIVE CREDENTIAL:")
    for path, hits in sorted(found.items()):
        on_list = "on audit list" if path in listed else "*** NOT ON THE AUDIT LIST ***"
        print(f"  {path}  [{on_list}]")
        for name, n in hits:
            print(f"      {name}: {n} occurrence(s)")
    missed = [p for p in found if p not in listed]
    print()
    if missed:
        print(f"VERDICT: the current audit would report CLEAN while {len(missed)} "
              f"file(s) still hold a live credential.")
    else:
        print("VERDICT: every file holding a live credential is on the audit list.")


if __name__ == "__main__":
    main()
