#!/usr/bin/env python3
"""Shape-based credential surface audit for /tmp.

GAP THIS FILLS: `ops/tmp-credential-surface-audit.py` scans /tmp for the FULL
VALUE of every credential that is CURRENTLY in .env. A credential-shaped literal
that is NOT in .env - e.g. a key rotated out of .env whose value still sits in
a backup file - is invisible to it. Same class as "a drift checker only covers
the files it scans".

This audit scans by SHAPE first, then classifies each hit:
  IN .env      -> already covered by the value-based audit
  ORPHAN       -> present in /tmp, not in .env
and probes each orphan against its provider: LIVE / DEAD / UNKNOWN.
UNKNOWN counts as exposure - a key we cannot probe is not thereby safe.

TWO BUGS THIS VERSION FIXES (the first version of this file printed CLEAN while
its own table showed UNKNOWN rows - a checker that asserts nothing and prints
green is worse than no checker):
  1. The counters compared `verdict == "UNKNOWN"`, but probe() returns
     "UNKNOWN (no probe)" / "UNKNOWN (timeout)" - so UNKNOWN rows were never
     counted. Now uses startswith("UNKNOWN").
  2. The shape regexes were greedy, so a long alnum blob after a prefix matched
     as a 6956-char "key". Each provider now has a plausible LENGTH RANGE; a
     maximal run outside that range is a shape COLLISION and is ignored.

Never prints a credential value: only names, lengths, verdicts and file:line.

Test hooks (used by ops/test-tmp-shape-surface-audit.py so a test run never
contacts a real provider):
  AUDIT_ENV_PATH    - path to the .env to read
  AUDIT_SCAN_ROOT   - directory to scan instead of /tmp
  AUDIT_NO_PROBE=1  - never contact a provider; every orphan is UNKNOWN
"""
import os
import re
import stat
import sys
import urllib.error
import urllib.request

ENV = os.environ.get("AUDIT_ENV_PATH", "/workspace/.env")
WORKSPACE = "/workspace"
SCAN_ROOTS = [os.environ.get("AUDIT_SCAN_ROOT", "/tmp")]
NO_PROBE = os.environ.get("AUDIT_NO_PROBE") == "1"

# label, regex for the maximal run, plausible length range for the WHOLE match
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

# --- STREAMING SCAN PARAMETERS ------------------------------------------------
# WHY LINE-BY-LINE: the previous version did `fh.read()` on every file and then
# decoded the whole thing to str. On this host /tmp holds a 377 MB gateway log
# and a 485 MB git pack, so ONE file allocated ~750 MB+ (bytes + decoded str)
# and was OOM-killed by the 4 GB cgroup - the checker proved NOTHING while the
# pass still looked like it had run. A checker that cannot complete is not a
# clean result.
#
# Scanning LINE BY LINE is EXACTLY equivalent, not an approximation: every
# shape character class is [A-Za-z0-9._-], which excludes newline and
# carriage return, so a shape match can never span a line boundary. The
# greedy run is confined to its line either way.
CHUNK = 4 * 1024 * 1024     # read size
MAX_LINE = 32 * 1024 * 1024  # a single line longer than this is segmented
SEAM_OVERLAP = 4096         # so a literal on a segment seam is still found

# same patterns, compiled to bytes (no decode -> no 2x memory blow-up)
SHAPES_BYTES = [(label, re.compile(rx.encode("utf8")), (lo, hi))
                 for label, rx, (lo, hi) in SHAPES]


def classify_line(raw, path, line_no, env_blob, tracked_cache, orphans,
                  tracked, counters, seen=None):
    """Scan one line for shape hits. `raw` is bytes, no newlines."""
    for label, rx, (lo, hi) in SHAPES_BYTES:
        for m in rx.finditer(raw):
            val = m.group(0)
            if not (lo <= len(val) <= hi):
                counters["collisions"] += 1
                continue
            # The scan runs on bytes, but every key we compare against - the
            # .env blob, the tracked-literal map, the orphan table - is str,
            # exactly as it was when the whole file was decoded before
            # matching. Decode the hit, not the file.
            val = val.decode("utf-8", "replace")
            if seen is not None:
                key = (label, val)
                if key in seen:
                    continue
                seen.add(key)
            if val in env_blob:
                counters["covered"] += 1
                continue
            if is_fixture(path):
                counters["fixtures"] += 1
                continue
            if val in tracked_cache:
                tracked.setdefault(val, tracked_cache[val])
                continue
            locs = orphans.setdefault(label, {}).setdefault(val, [])
            if len(locs) < 4:
                locs.append("%s:%d" % (path, line_no))


PROBES = {
    "FeedHive": ("https://api.feedhive.com/v1/accounts", "Authorization", "Bearer %s"),
    "AgentMail": ("https://api.agentmail.to/v0/inboxes", "X-API-Key", "%s"),
    "ClickUp": ("https://api.clickup.com/api/v2/user", "Authorization", "%s"),
    "Blotato": ("https://backend.blotato.com/v2/users/me/accounts", "blotato-api-key", "%s"),
    "Meta/Facebook": ("https://graph.facebook.com/v19.0/me", "Authorization", "Bearer %s"),
}

# Our own test fixtures - these contain SYNTHETIC tokens, not real credentials.
#
# 🔑 THIS LIST IS DERIVED, NOT HAND-MAINTAINED.
# It used to be a hand-written tuple of 7 prefixes, and it was WRONG: the
# audit's own test writes a synthetic `am_us_...` literal into
# /tmp/shape-audit-test-*/leak.txt, and that prefix was not in the list. So
# when the test suite ran CONCURRENTLY with a heartbeat pass, the audit
# classified our own synthetic fixture as a real orphan and reported
# `VERDICT: EXPOSED` - a false positive caused entirely by our own test
# harness.
#
# That is the same failure class as the orphaned-publisher bug: a hand-kept
# list drifts from reality, and the drift is invisible until a pass happens
# to run at the wrong moment. The list is now DERIVED from the test files
# themselves, so a new test that writes a fixture is covered the moment it
# is written.
#
# The derived set is unioned with the historical hard-coded entries, so
# nothing that used to be ignored becomes ignored no longer.
_HARDCODED_FIXTURE_DIRS = (
    "/tmp/cred-fence-", "/tmp/ccheck", "/tmp/c_fenced", "/tmp/c_inline",
    "/tmp/c_plain", "/tmp/leaktest", "/tmp/dbg2",
)


def _derive_fixture_dirs():
    """Collect every /tmp/<prefix>- our own tests create.

    Scans the tracked test files for `tempfile.mkdtemp(prefix="...")` and
    `TemporaryDirectory(prefix="...")` and turns each into the /tmp prefix
    the audit must ignore.
    """
    import re
    import subprocess
    found = set()
    files = set()
    # Tracked tests (a glob, not a directory prefix - "ops/test-" matches
    # nothing in git's pathspec rules).
    try:
        r = subprocess.run(["git", "ls-files", "ops/test-*"], cwd=WORKSPACE,
                           capture_output=True, text=True, timeout=60)
        files.update(f for f in r.stdout.split() if f.endswith(".py"))
    except Exception:
        pass
    # Plus any test file on disk that is not tracked - a new test must be
    # covered the moment it is WRITTEN, not the moment it is committed.
    try:
        for p in sorted(os.listdir(os.path.join(WORKSPACE, "ops"))):
            if p.startswith("test-") and p.endswith(".py"):
                files.add(os.path.join("ops", p))
    except Exception:
        pass
    rx = re.compile(rb"""prefix\s*=\s*["']([A-Za-z0-9_.-]+)["']""")
    for f in files:
        try:
            with open(os.path.join(WORKSPACE, f), "rb") as fh:
                data = fh.read()
        except Exception:
            continue
        for m in rx.finditer(data):
            found.add("/tmp/" + m.group(1).decode("ascii", "replace"))
    return found


FIXTURE_DIRS = tuple(sorted(set(_HARDCODED_FIXTURE_DIRS) | _derive_fixture_dirs()))


def tracked_literals():
    """Credential-shaped literals that also exist in a TRACKED workspace file.

    A value that is present in tracked source has an authoritative copy that
    ops/check-tracked-live-credentials.py already owns and audits. The /tmp
    audit must not double-report it as an ORPHAN, but it also must not
    DOWNGRADE it silently: it is reported in its own class and the canonical
    checker is named in the output.
    """
    import subprocess
    found = {}
    try:
        r = subprocess.run(["git", "ls-files"], cwd=WORKSPACE,
                           capture_output=True, text=True, timeout=60)
        files = r.stdout.split()
    except Exception:
        return found
    for f in files:
        if not f.endswith((".py", ".js", ".ts", ".sh", ".json", ".md",
                            ".html", ".txt", ".yml", ".yaml", ".env", ".cfg", ".toml")):
            continue
        try:
            with open(os.path.join(WORKSPACE, f), "rb") as fh:
                for raw in fh:          # line by line - never slurp the file
                    for label, rx, (lo, hi) in SHAPES_BYTES:
                        for m in rx.finditer(raw):
                            val = m.group(0)
                            if lo <= len(val) <= hi:
                                found.setdefault(val.decode("utf-8", "replace"), f)
        except Exception:
            continue
    return found


def is_fixture(path):
    # The audit's OWN test needs to see a synthetic orphan, so it opts in
    # explicitly. Production runs never do - which is what stops a test
    # suite running concurrently with a heartbeat pass from reporting our
    # own fixture as a real exposure.
    if os.environ.get("AUDIT_INCLUDE_FIXTURES") == "1":
        return False
    return any(path.startswith(d) for d in FIXTURE_DIRS)


def env_values():
    vals = {}
    try:
        with open(ENV) as fh:
            for line in fh:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    vals[k.strip()] = v.strip().strip('"').strip("'")
    except Exception as e:
        print("cannot read .env:", e)
    return vals


def probe(label, value):
    if NO_PROBE:
        return None, "UNKNOWN (no probe)"
    if label not in PROBES:
        return None, "UNKNOWN (no probe)"
    url, hdr, fmt = PROBES[label]
    try:
        req = urllib.request.Request(url, headers={hdr: fmt % value})
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.status, "LIVE"
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return e.code, "DEAD"
        return e.code, "UNKNOWN"
    except Exception:
        return None, "UNKNOWN"


def main():
    envs = env_values()
    env_blob = "\n".join(envs.values())
    tracked_literals_cache = tracked_literals()
    orphans = {}      # label -> value -> locations
    tracked = {}      # value -> tracked file
    collisions = 0
    covered = 0
    scanned = 0
    bytes_scanned = 0
    biggest = [0, ""]
    counters = {"collisions": 0, "covered": 0, "fixtures": 0}
    for root in SCAN_ROOTS:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ("node_modules", "__pycache__")]
            for fn in filenames:
                p = os.path.join(dirpath, fn)
                try:
                    st = os.stat(p)
                    if not stat.S_ISREG(st.st_mode):
                        continue
                except Exception:
                    continue
                try:
                    fh = open(p, "rb")
                except Exception:
                    continue
                with fh:
                    scanned += 1
                    bytes_scanned += st.st_size
                    if st.st_size > biggest[0]:
                        biggest[:] = [st.st_size, p]
                    carry = b""
                    line_no = 1
                    chunk = fh.read(CHUNK)
                    while chunk:
                        buf = carry + chunk
                        # Index-scan the buffer instead of buf.split(b"\n"):
                        # split() materialises EVERY line of the chunk as a
                        # separate bytes object all at once (~550k of them
                        # for a 4 MB chunk) - a second memory spike on top of
                        # the buffer itself. Slicing one line at a time keeps
                        # the footprint at one chunk.
                        pos = 0
                        while True:
                            nl = buf.find(b"\n", pos)
                            if nl < 0:
                                break
                            raw = buf[pos:nl]
                            pos = nl + 1
                            if raw:
                                classify_line(raw, p, line_no, env_blob,
                                              tracked_literals_cache, orphans,
                                              tracked, counters)
                            line_no += 1
                        carry = buf[pos:]            # partial line, no newline yet
                        del buf
                        if len(carry) > MAX_LINE:
                            # one line longer than MAX_LINE. No credential
                            # literal spans it; segment with an overlap so a
                            # literal on a seam is still found.
                            seen = set()
                            seg = carry
                            while len(seg) > MAX_LINE:
                                classify_line(seg[:MAX_LINE], p, line_no,
                                              env_blob, tracked_literals_cache,
                                              orphans, tracked, counters, seen)
                                seg = seg[MAX_LINE - SEAM_OVERLAP:]
                            carry = seg
                        chunk = fh.read(CHUNK)
                    if carry:
                        classify_line(carry, p, line_no, env_blob,
                                      tracked_literals_cache, orphans,
                                      tracked, counters)
    print("=== SHAPE-BASED SCAN of %s ===" % ", ".join(SCAN_ROOTS))
    collisions = counters["collisions"]
    covered = counters["covered"]
    fixtures = counters["fixtures"]
    print("  files read                    : %d" % scanned)
    print("  bytes scanned                 : %.1f MB"
          % (bytes_scanned / 1048576.0))
    if biggest[0]:
        print("  largest file scanned          : %.1f MB  %s"
              % (biggest[0] / 1048576.0, biggest[1]))
    print("  shape hits already in .env    : %d" % covered)
    print("  synthetic fixture hits ignored: %d" % fixtures)
    print("  shape collisions (bad length) : %d" % collisions)
    print("  hits owned by tracked source  : %d (audited by ops/check-tracked-live-credentials.py)" % len(tracked))
    print()
    if tracked:
        print("  TRACKED-SOURCE LITERALS (not orphans - canonical checker owns these):")
        for val, f in sorted(tracked.items(), key=lambda kv: kv[1]):
            print("   %-14s len=%-4d %s" % ("(tracked)", len(val), f))
        print()
    total_live = total_unknown = total_dead = 0
    if orphans:
        print("  ORPHAN literals (shape in /tmp, NOT in .env):")
        for label in sorted(orphans):
            for val, locs in orphans[label].items():
                status, verdict = probe(label, val)
                print("   %-14s len=%-4d %-24s %s" % (label, len(val), verdict, ", ".join(locs)))
                if verdict == "LIVE":
                    total_live += 1
                elif verdict.startswith("UNKNOWN"):
                    total_unknown += 1
                else:
                    total_dead += 1
        print()
    print("  orphan LIVE     : %d" % total_live)
    print("  orphan DEAD     : %d" % total_dead)
    print("  orphan UNKNOWN  : %d" % total_unknown)
    exposed = total_live + total_unknown
    print("VERDICT: %s" % ("EXPOSED" if exposed else "CLEAN"))
    if exposed:
        print("Remedy: python3 ops/redact-orphan-secrets-in-place.py <files>")
    return 3 if exposed else 0


if __name__ == "__main__":
    sys.exit(main())
