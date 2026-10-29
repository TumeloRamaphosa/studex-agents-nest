#!/usr/bin/env python3
"""Audit tracked source for FRAGMENTS of ANY live credential.

2026-10-28. This replaces `ops/audit-blotato-fragments.py`, which checked
exactly ONE credential - BLOTATO_API_KEY - and reported CLEAN.

In fact 22 tracked files held 12+ character slices of FIFTEEN different
credentials, and seven of those credentials were proven LIVE by an HTTP
probe the same night. The repository's remote is PUBLIC.

🔑 THE DEFECT WAS THE SCOPE, NOT THE BUG: a guard that watches one key
while the repo holds fifty is a guard for a key nobody else has. The old
checker was not broken - it was watching the wrong thing, and its "CLEAN"
was about one credential out of fifty.

This checker:
  * reads EVERY credential-shaped value in .env (16+ chars)
  * probes each for liveness, so a LIVE fragment is reported as an active
    breach and an UNKNOWN one as unproven (both block)
  * looks for any 12+ character contiguous slice of any of them, in EVERY
    tracked file
  * measures each hit against GROUND TRUTH - the longest contiguous run
    actually present - not against its own opinion of it
  * reports file names, credential NAMES and counts - never a value

🔑 AND THE DETECTION IS TWO-SIDED. A credential is a candidate when ANY
of its 4-byte windows appears in the file - not only when its FIRST
window does. A leak of a key's tail or middle contains none of its first
bytes, and that is the leak this exists to close.

Exit codes: 0 clean, 1 fragment found.
"""
import argparse
import importlib.util
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path("/workspace")
ENV_FILE = REPO / ".env"
MIN_SLICE = 12
WINDOW_LEN = 4
PROBE_DEADLINE_S = 120


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def longest_run(data, value):
    """The longest contiguous run of `value` present in `data` (0 if none).

    GROUND TRUTH: measured directly against the bytes, longest first. A
    checker that measures a leak with the same logic it uses to find it
    agrees with its own bugs.
    """
    vb = value.encode()
    for L in range(len(vb), MIN_SLICE - 1, -1):
        for i in range(len(vb) - L + 1):
            if vb[i:i + L] in data:
                return L
    return 0


def candidates(data, values):
    """The credentials that could have a fragment in `data`."""
    present = {data[i:i + WINDOW_LEN] for i in range(len(data) - WINDOW_LEN + 1)}
    out = []
    for name, value in values:
        vb = value.encode()
        if any(vb[i:i + WINDOW_LEN] in present
               for i in range(len(vb) - WINDOW_LEN + 1)):
            out.append((name, value))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--env", default=str(ENV_FILE))
    ap.add_argument("--no-probe", action="store_true",
                    help="skip the liveness probe (report every fragment as UNKNOWN)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    repo = pathlib.Path(args.repo)
    # 🔑 The helpers come from THIS FILE's directory, never from the repo
    # being scanned. A checker that loads its helpers out of the tree it
    # is auditing can only ever be run against itself - and when it is
    # pointed at a scratch repo it dies with a FileNotFoundError, which
    # looks exactly like a clean scan.
    HERE = pathlib.Path(__file__).resolve().parent
    m = load("ccs", HERE / "check-credential-slots.py")
    rl = load("rl", HERE / "redact-live-secrets-in-place.py")

    env = dict(m.read_env(str(args.env)))
    values = [(n, v) for n, v in env.items()
              if m.classify(v) == "CREDENTIAL" and len(v) >= 16]
    if not values:
        print("VERDICT: CLEAN - no credential-shaped value to look for")
        return 0

    # liveness, with a budget. UNKNOWN still blocks - only the urgency
    # differs - so a slow network makes this stricter, never laxer.
    states = {}
    if args.no_probe:
        for n, _v in values:
            states[n] = "UNKNOWN"
    else:
        deadline = time.monotonic() + PROBE_DEADLINE_S
        for n, v in values:
            if time.monotonic() > deadline:
                states[n] = "UNKNOWN"
                continue
            try:
                st, _d = rl.classify(v, env=env, name=n)
            except Exception:
                st = "UNKNOWN"
            states[n] = st

    p = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"],
                       capture_output=True, text=True, timeout=300)
    files = [f for f in p.stdout.split("\0") if f.strip()]

    hits = {}
    for rel in files:
        f = repo / rel
        try:
            if not f.is_file() or f.stat().st_size > 20_000_000:
                continue
            data = f.read_bytes()
        except OSError:
            continue
        if not data:
            continue
        for name, value in candidates(data, values):
            run = longest_run(data, value)
            if run:
                hits.setdefault(rel, {})[name] = run

    live = sorted({n for rel in hits for n in hits[rel] if states.get(n) == "LIVE"})
    unknown = sorted({n for rel in hits for n in hits[rel]
                      if states.get(n) != "LIVE"})

    if args.json:
        import json
        print(json.dumps({
            "files_scanned": len(files),
            "credentials_checked": len(values),
            "hits": {rel: hits[rel] for rel in sorted(hits)},
            "states": states,
            "live": live,
            "unknown": unknown,
        }, indent=2))
        return 1 if hits else 0

    print("scanned %d tracked file(s) for fragments of %d credential(s)"
          % (len(files), len(values)))
    print("min slice length: %d" % MIN_SLICE)
    print()
    if hits:
        print("FRAGMENT HITS:")
        for rel in sorted(hits):
            parts = []
            for n in sorted(hits[rel]):
                parts.append("%s(%s,%dc)" % (n, states.get(n, "UNKNOWN"), hits[rel][n]))
            print("  %-58s %s" % (rel[:58], ", ".join(parts)))
        print()
    if live:
        print("  CONFIRMED STILL AUTHENTICATING (active breach):")
        for n in live:
            print("    %-30s %d file(s)" % (n, len([r for r in hits if n in hits[r]])))
    if unknown:
        print("  LIVENESS UNPROVEN (blocked anyway - not provably safe):")
        for n in unknown:
            print("    %-30s %d file(s)" % (n, len([r for r in hits if n in hits[r]])))
    print()
    if hits:
        print("VERDICT: %d file(s) hold a fragment of a credential" % len(hits))
        return 1
    print("VERDICT: CLEAN - no fragment of any credential in tracked source.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
