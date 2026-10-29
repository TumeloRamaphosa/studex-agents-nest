#!/usr/bin/env python3
"""Mask every 12+ character fragment of every live credential in tracked files.

2026-10-28. The fragments audit (`ops/audit-blotato-fragments.py`) checked
exactly ONE credential - BLOTATO_API_KEY - and reported CLEAN. In fact 22
tracked files held 12+ character slices of FIFTEEN different credentials,
and seven of those credentials were proven LIVE by an HTTP probe the same
night. The repository's remote is PUBLIC.

So the audit had the wrong scope, not just a bug: a guard that watches one
key while the repo holds fifty is a guard for a key nobody else has.

This tool masks, in every TRACKED file, every 12+ character contiguous
slice of every credential-shaped value in .env - with same-length
asterisks, in place, preserving the file's size AND its inode (the gateway
holds these files open for append).

Values are never printed. Only file names, credential NAMES and counts.

🔑 NO CONTEXT IS EVER PRINTED. An earlier preview of this tool printed the
bytes AROUND a match, and it leaked the tail of a Pinecone key into the
session log - which the scanner-log checker then had to redact. A tool
that shows you the neighbourhood of a secret is a tool that prints
secrets.

🔑 TWO BUGS FOUND BY ops/test-mask-credential-fragments.py, both in the
DETECTION (not the masking):

  1. THE PREFILTER WAS ONE-SIDED. It asked "does the credential's FIRST
     4 bytes appear in this file?". A leak of the credential's TAIL or
     MIDDLE contains none of its first 4 bytes, so it was invisible. The
     Pinecone key was present in `memory/2026-08-22.md` with 74 of its 75
     characters, and the masker masked 22 of them - because the tail was
     there but the head was not. 🔑 *A guard that only looks at the start
     of a key is a guard that misses the most common way a key leaks.*

  2. THE GROWTH INDEX WAS WRONG. `vi + (b - j)` instead of
     `vi + (b - a)`, so the right-hand extension stopped as soon as the
     match had been extended to the LEFT.

🔑 AND THE RE-SCAN SHARED BUG 1 WITH THE MASKER, so it agreed with it:
🔑 *two functions that share a bug agree with each other, and neither is
a control.* The re-scan is now measured against GROUND TRUTH - the
longest contiguous run actually present - not against the masker's own
opinion of it.

HOW IT IS FAST: one pass per file builds the set of 4-byte windows the
file contains; a credential is a candidate when ANY of its windows is in
that set. Only candidates get the full 12-character slice scan. A single
regex over all 2,665 slices is far too slow: Python's regex engine tries
every alternative at every byte position.
"""
import argparse
import importlib.util
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path("/workspace")
ENV_FILE = REPO / ".env"

# A fragment of this many characters or more is worth masking: enough to
# be a meaningful head start on the key, short enough that ordinary prose
# does not trip it.
MIN_SLICE = 12
WINDOW_LEN = 4


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m = load("ccs", REPO / "ops/check-credential-slots.py")


def credential_values(env_file):
    """[(name, value)] for every slot that holds a real credential."""
    out = []
    for name, value in m.read_env(str(env_file)):
        if m.classify(value) == "CREDENTIAL" and len(value) >= 16:
            out.append((name, value))
    return out


def windows(value):
    """Every WINDOW_LEN-byte window of a credential value."""
    vb = value.encode() if isinstance(value, str) else value
    return [vb[i:i + WINDOW_LEN] for i in range(len(vb) - WINDOW_LEN + 1)]


def candidate_credentials(data, values):
    """The credentials that could possibly have a fragment in `data`.

    🔑 A credential is a candidate when ANY of its windows appears in the
    file - not only when its FIRST window does. A tail leak contains
    none of the key's first bytes, and that is the leak this tool exists
    to close.
    """
    present = {data[i:i + WINDOW_LEN] for i in range(len(data) - WINDOW_LEN + 1)}
    out = []
    for name, value in values:
        if any(w in present for w in windows(value)):
            out.append((name, value))
    return out


def maximal_intervals(data, cands):
    """Maximal (start, end, name) intervals of credential material in data."""
    intervals = []
    for name, value in cands:
        vb = value.encode()
        for i in range(len(vb) - MIN_SLICE + 1):
            s = vb[i:i + MIN_SLICE]
            j = data.find(s)
            while j >= 0:
                # data[a] <-> vb[vi]; grow in both directions
                a, b = j, j + MIN_SLICE
                vi = i
                while a > 0 and vi > 0 and data[a - 1] == vb[vi - 1]:
                    a -= 1
                    vi -= 1
                while (b < len(data) and vi + (b - a) < len(vb)
                       and data[b] == vb[vi + (b - a)]):
                    b += 1
                intervals.append((a, b, name))
                j = data.find(s, j + 1)
    # merge overlapping/adjacent intervals
    intervals.sort()
    merged = []
    for a, b, name in intervals:
        if merged and a <= merged[-1][1]:
            pa, pb, pn = merged[-1]
            merged[-1] = (pa, max(pb, b), pn or name)
        else:
            merged.append((a, b, name))
    return merged


def mask_file(path, values, dry_run=False):
    """Mask every fragment in `path`. Returns {name: count}."""
    p = pathlib.Path(path)
    if not p.is_file():
        return {}
    try:
        if p.stat().st_size > 20_000_000:
            return {}
    except OSError:
        return {}
    data = p.read_bytes()
    if not data:
        return {}

    cands = candidate_credentials(data, values)
    if not cands:
        return {}
    merged = maximal_intervals(data, cands)
    if not merged:
        return {}

    out = bytearray(data)
    per_name = {}
    for a, b, name in merged:
        out[a:b] = b"*" * (b - a)
        per_name[name] = per_name.get(name, 0) + 1

    if dry_run:
        return per_name

    before = os.stat(p)
    with open(p, "r+b") as fh:
        fh.write(bytes(out))
        fh.flush()
    after = os.stat(p)
    # The inode must not change: the gateway holds these files open.
    assert before.st_ino == after.st_ino, "inode changed for %s" % p
    assert before.st_size == after.st_size, "size changed for %s" % p
    return per_name


def tracked_files(repo):
    p = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"],
                       capture_output=True, text=True, timeout=300)
    return [f for f in p.stdout.split("\0") if f.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--env", default=str(ENV_FILE))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="", help="limit to files whose path contains this")
    ap.add_argument("--skip", default="", help="comma-separated path fragments to skip")
    ap.add_argument("--no-rescan", action="store_true")
    args = ap.parse_args()

    repo = pathlib.Path(args.repo)
    values = credential_values(pathlib.Path(args.env))
    print("credentials in scope: %d   min slice: %d" % (len(values), MIN_SLICE))
    print("mode: %s" % ("DRY RUN" if args.dry_run else "WRITE"))

    files = tracked_files(repo)
    if args.only:
        files = [f for f in files if args.only in f]
    skip = [s for s in args.skip.split(",") if s]
    if skip:
        files = [f for f in files if not any(s in f for s in skip)]
    print("tracked files scanned: %d" % len(files))
    print()

    touched = 0
    total = 0
    for rel in files:
        per_name = mask_file(repo / rel, values, dry_run=args.dry_run)
        if per_name:
            n = sum(per_name.values())
            total += n
            touched += 1
            print("  %-60s %d fragment(s)  [%s]"
                  % (rel[:60], n, ", ".join(sorted(per_name))))

    print()
    print("files touched: %d   fragments masked: %d" % (touched, total))

    if args.no_rescan:
        return 0

    print()
    print("=== the re-scan, measured against GROUND TRUTH ===")
    remaining = []
    for rel in files:
        pth = repo / rel
        try:
            if not pth.is_file() or pth.stat().st_size > 20_000_000:
                continue
            data = pth.read_bytes()
        except OSError:
            continue
        if not data:
            continue
        for name, value in candidate_credentials(data, values):
            vb = value.encode()
            longest = 0
            for L in range(len(vb), MIN_SLICE - 1, -1):
                if any(vb[i:i + L] in data for i in range(len(vb) - L + 1)):
                    longest = L
                    break
            if longest:
                remaining.append((rel, name, longest))
    for rel, name, longest in remaining:
        print("  STILL PRESENT: %-52s [%s] %d char(s)" % (rel[:52], name, longest))
    print("  tracked files still holding a %d+ slice: %d" % (MIN_SLICE, len(remaining)))
    print("  VERDICT:", "CLEAN" if not remaining else "CONTAMINATED")
    return 0 if not remaining else 1


if __name__ == "__main__":
    sys.exit(main())
