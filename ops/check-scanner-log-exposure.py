#!/usr/bin/env python3
"""Did anything leak live values into the surfaces the agent actually uses?

FOUR surfaces are scanned: the gateway log, the cron run history, the session
transcripts, and the agent's own MEMORY DATABASE. 🔑 The fourth one was added
on 2026-10-28 after a live key was found sitting in main.sqlite while the other
three were clean - the scanner was looking in three of the four places the
thing lived, and reported CLEAN on the one it did not cover.

ops/measure-cred-shapes.py printed every matched candidate verbatim, and
its output ran into /tmp/openclaw/openclaw-2026-10-23.log 39 times. So
the question is not "did it print values" (it did) but "did it print a
value that still authenticates".

TWO QUESTIONS, because they miss different things:

1. WHAT DID THE SCANNER PRINT? Extract every candidate the shape scanner
   printed out of the gateway log, then classify each one:
     LIVE     - it matches a credential currently in .env  -> REAL exposure
     PREFIX   - it is a prefix of one                        -> truncated reference
     UNKNOWN  - it is not in .env at all                     -> may be a rotated
                credential no longer in .env, or unrelated data

2. WHAT IS IN THE LOG AT ALL? ⚠️ Question 1 alone was a FOURTH false green.
   It matches ONE scanner's line format (`<file>:<line>  '<value>'`), so it
   reported "0 candidates printed" over a log that the surface audit had
   just measured as holding 18 live and unknown credential literals - it
   did not recognise the format the OTHER tools printed in, so it could not
   see them. This section therefore scans the log for the FULL VALUE of
   every credential in .env, exactly as ops/tmp-credential-surface-audit.py
   does, and reuses that script's probe logic so both tools classify a
   credential the SAME way.

Only counts and verdicts are printed. No value is printed.
"""
import importlib.util
import pathlib
import re
import sys
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

WS = pathlib.Path("/workspace")
sys.path.insert(0, str(WS / "ops"))


def _load_audit():
    """Import the surface audit by PATH.

    Its filename carries hyphens, so it is not importable by name - and a
    hyphenated module name is exactly why two tools were free to drift
    apart and disagree about the same file. One definition, loaded
    explicitly.
    """
    spec = importlib.util.spec_from_file_location(
        "tmp_credential_surface_audit", WS / "ops" / "tmp-credential-surface-audit.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# One definition of "is this credential alive?" and "does this state count as
# exposure?" - shared with the surface audit, so the two tools cannot drift
# apart and disagree about the same file.
audit = _load_audit()

# The gateway writes a NEW log per day and never rotates the old ones, so a
# static list of two files silently stopped covering the logs written since.
# Glob instead: a checker that only reads the logs it was written for is a
# checker that proves nothing about the logs written after it.
_LOGS_DIR = pathlib.Path("/tmp/openclaw")

# The cron run history is a SECOND surface, and it is where the FEEDHIVE
# leak actually came from.
#
# On 2026-10-26 this checker found FEEDHIVE_API_KEY 13x in
# openclaw-2026-10-26.log. Redacting the log fixed the copy - and the leak
# came back the next day, because the SOURCE was never touched: the 09:00
# publish job's run history at
# /root/.openclaw/cron/runs/3816d7b1-...jsonl carries the literal in 13
# agent summaries going back to 2026-08-25, and the gateway copies the run
# history into the log on every read.
#
# Redacting a copy is not a fix. A checker that only scans the copy cannot
# see the source, so it reported CLEAN on a surface that was still dirty.
# Both surfaces must be scanned, or the verdict means nothing.
_CRON_RUNS_DIR = pathlib.Path("/root/.openclaw/cron/runs")

# The SESSION TRANSCRIPTS are a THIRD surface - and on 2026-10-27 they were
# the actual source of the FEEDHIVE leak.
#
# The chain, measured: the live key appeared in ~250 places across
# /root/.openclaw/agents/main/sessions/*.jsonl (and their .reset/.bak
# siblings). The gateway copies session content into the log on every read,
# so a credential sitting in a transcript re-enters the log WHENEVER that
# session is read - which is why the log copy came back after being masked,
# twice, and why "mask the log" never held.
#
# ⚠️ The surface audit already called these "session transcripts" as a
# category, but this scanner only read /tmp/openclaw and the cron run
# history. The transcripts were the one surface where the key lived, and
# the scanner that reported it was not looking there.
_SESSIONS_DIR = pathlib.Path("/root/.openclaw/agents")

# The AGENT'S MEMORY DATABASE is a FOURTH surface - and on 2026-10-28 it was
# the surface that actually held the leak.
#
# Measured this pass: a live Blotato key was printed into this session's own
# tool output, and the scanner reported CLEAN - because /tmp/openclaw, the
# cron run history and /root/.openclaw/agents/**/*.jsonl all came back
# clean, while the value sat in /root/.openclaw/memory/main.sqlite (35 MB).
# The session transcripts are NOT the same thing as the memory DB: the agent's
# conversation content is persisted into the DB, and the DB is not under
# /root/.openclaw/agents.
#
# 🔑 WHY THIS MATTERS BEYOND MY OWN SLIP: the memory DB is what an agent
# reads when it builds a summary, and the vault sync is AGENT-DRIVEN - so a
# credential in the DB is on the path to a published vault note. A scanner
# that does not look here cannot answer the question it exists to answer.
_MEMORY_DIR = pathlib.Path("/root/.openclaw/memory")


def log_files():
    if not _LOGS_DIR.is_dir():
        return []
    return sorted(_LOGS_DIR.glob("openclaw-*.log"),
                  key=lambda p: p.stat().st_mtime)


def cron_run_files():
    if not _CRON_RUNS_DIR.is_dir():
        return []
    return sorted(_CRON_RUNS_DIR.glob("*.jsonl"),
                  key=lambda p: p.stat().st_mtime)


def session_files():
    if not _SESSIONS_DIR.is_dir():
        return []
    out = []
    for p in _SESSIONS_DIR.rglob("*.jsonl*"):
        try:
            if p.is_file() and p.stat().st_size < 200 * 1024 * 1024:
                out.append(p)
        except OSError:
            continue
    return sorted(out, key=lambda p: p.stat().st_mtime)


def memory_db_files():
    """The agent's memory databases - a session-content surface of their own."""
    if not _MEMORY_DIR.is_dir():
        return []
    out = []
    for p in sorted(_MEMORY_DIR.glob("*.sqlite*")):
        try:
            if p.is_file() and p.stat().st_size < 200 * 1024 * 1024:
                out.append(p)
        except OSError:
            continue
    return out


LOGS = log_files()
CRON_RUNS = cron_run_files()
SESSIONS = session_files()
MEMORY_DBS = memory_db_files()

# The scanner's output line format:
#    <rel>:<line>  '<matched value>'
SCAN_LINE = re.compile(r"^\s*(\S+?):(\d+)\s+'([^']{12,})'\s*$")


def count_in_file(path, needles):
    """Count occurrences of each needle in a file WITHOUT loading it into RAM.

    The gateway log directory is ~378M and growing, and the old
    `log.read_bytes()` loaded a whole log into memory - the process was
    OOM-killed (exit -9) on the 2026-10-23 log. A checker that gets killed
    proves nothing: it prints no verdict at all, and a caller that treats
    "no output" as "no problem" is exactly the false-negative bug this
    tool exists to prevent.

    Chunked scan with a carry-over of (longest needle - 1) bytes so a
    needle straddling a chunk boundary is still counted.

    ⚠️ The carry correction is PER CHUNK, and there is NO final correction.
    The previous version added `buf.count(n)` for every chunk and then, at
    the very end, subtracted the count found in the FINAL carry. That is
    wrong in both directions:

      * it over-counts, because the carry bytes are counted again in the
        next chunk (a match fully inside the carry is counted twice), and
      * it under-counts, because the final subtraction removes matches that
        sit in the last (longest-1) bytes of the file - and those were
        never double counted.

    With 49 credential needles the longest one is far longer than most
    values, so the tail window swallowed real matches. A credential sitting
    near the end of a log was reported as absent - a false NEGATIVE in the
    exact check that decides whether a secret is exposed.

    The correct rule: for each chunk, count matches in (carry + chunk) and
    subtract the matches that lie entirely inside the carry, because those
    were counted in the previous chunk. `carry.count(n)` counts only
    matches fully contained in the carry, which is exactly the set to
    remove, so it is the right subtraction - applied per chunk, and never
    applied to the final carry.
    """
    counts = {}
    if not needles:
        return counts
    longest = max(len(n) for n in needles)
    carry = b""
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(1 << 20)          # 1 MiB
            if not chunk:
                break
            buf = carry + chunk
            for n in needles:
                c = buf.count(n)
                if carry:
                    c -= carry.count(n)
                counts[n] = counts.get(n, 0) + c
            carry = buf[-(longest - 1):] if longest > 1 else b""
    return counts


def env_values():
    out = {}
    name_re = _mod.CRED_NAME_RE
    env = WS / ".env"
    if not env.exists():
        return out
    for line in env.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        if len(v) >= 16 and name_re.match(k.strip()):
            out[k.strip()] = v
    return out


def get(url, headers):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:  # noqa: BLE001
        return 0


def value_scan(env):
    """Question 2: what credential VALUES does the log hold at all?

    ⚠️ This is the check that matters most, and it is the one that was
    missing. The scanner-line scan below only recognises ONE tool's output
    format, so it reported a clean log over a log the surface audit had
    measured as holding live credential literals in a DIFFERENT format.

    It reuses the surface audit's probe so both tools call the same
    credential the same thing. DEAD is not exposure (the provider rejects
    it); LIVE and UNKNOWN both are.

    Only the credentials actually FOUND in the log are probed - probing all
    of .env would cost a network round-trip per key on every run, and the
    ones that are not in the log have nothing to decide.
    """
    print()
    print("=== value scan: every .env credential value present in the log ===")

    found = {}
    for log in LOGS + CRON_RUNS + SESSIONS + MEMORY_DBS:
        if not log.exists():
            continue
        try:
            counts = count_in_file(log, [v.encode() for v in env.values()])
        except OSError:
            continue
        for name, value in env.items():
            n = counts.get(value.encode(), 0)
            if n:
                if log in LOGS:
                    label = log.name
                elif log in CRON_RUNS:
                    label = "cron-runs/" + log.name
                elif log in MEMORY_DBS:
                    label = "memory-db/" + log.name
                else:
                    label = "sessions/" + log.name
                found.setdefault(name, []).append((label, n, value))

    if not found:
        print("no .env credential value appears in the gateway log")
        return 0

    exposed = 0
    for name, hits in sorted(found.items()):
        _, verdict = audit.probe(name, hits[0][2], env)
        for fname, n, _ in hits:
            state = "EXPOSED" if audit.is_exposed(verdict) else "dead (not exposure)"
            print(f"   {name:28} {verdict:8} {n:>4}x in {fname}  -> {state}")
            if audit.is_exposed(verdict):
                exposed += 1
    print(f"credentials in an exposed state: {exposed}")
    return exposed


def main():
    env = env_values()
    printed = {}          # value -> count of times printed
    for log in LOGS + CRON_RUNS + SESSIONS + MEMORY_DBS:
        if not log.exists():
            continue
        # Stream the file line by line. read_text().splitlines() materialised
        # the whole log twice (bytes + a list of str) and was the other half
        # of the OOM.
        with open(log, "r", errors="ignore") as fh:
            for line in fh:
                m = SCAN_LINE.match(line)
                if not m:
                    continue
                val = m.group(3)
                if len(val) < 12:
                    continue
                printed[val] = printed.get(val, 0) + 1

    print(f"distinct candidates the scanner printed into the gateway log: {len(printed)}")
    total = sum(printed.values())
    print(f"total printed occurrences: {total}")
    print()

    live, prefix, unknown = [], [], []
    for val, n in printed.items():
        exact = [k for k, v in env.items() if v == val]
        pre = [k for k, v in env.items()
               if v != val and v.startswith(val) and len(val) >= 12]
        if exact:
            live.append((exact[0], val, n))
        elif pre:
            prefix.append((pre[0], val, n))
        else:
            unknown.append((val, n))

    print(f"  matches a LIVE .env credential exactly : {len(live)}")
    print(f"  is a PREFIX of a live .env credential   : {len(prefix)}")
    print(f"  not in .env at all                     : {len(unknown)}")
    print()

    if live:
        print("!! LIVE CREDENTIALS PRINTED INTO A SCANNED SURFACE !!")
        for name, val, n in live:
            print(f"   {name}: printed {n}x, len={len(val)}")
    else:
        print("No live .env credential was printed into any scanned surface.")

    if unknown:
        # Probe the distinctive ones (prefixed / brand-like) to see if any
        # still authenticates even though it is no longer in .env.
        print()
        print("probing unrecognised candidates that look like credentials (GET only)...")
        for val, n in sorted(unknown, key=lambda x: -x[1])[:6]:
            if val.startswith("blt_") or val.startswith("blotato"):
                st = get("https://backend.blotato.com/v2/users/me/accounts",
                         {"blotato-api-key": val})
                label = "blotato"
            elif val.startswith("ghp_") or val.startswith("github_pat_"):
                st = get("https://api.github.com/user",
                         {"Authorization": f"Bearer {val}", "User-Agent": "audit"})
                label = "github"
            elif val.startswith("am_us_"):
                st = get("https://api.agentmail.to/v0/inboxes",
                         {"Authorization": f"Bearer {val}"})
                label = "agentmail"
            else:
                continue
            state = ("LIVE" if st == 200 else "dead" if st in (401, 403)
                     else "inconclusive")
            print(f"   {label:10} printed {n}x  HTTP {st or '-'}  {state}")

    # Question 2 - the one that catches a leak in ANY tool's format, not just
    # the shape scanner's. Its exit code is what makes this a CHECK and not a
    # report: a leak that is found but does not fail the command gets
    # forgotten.
    exposed = value_scan(env)
    return 1 if exposed else 0


if __name__ == "__main__":
    _exit = main()
    sys.exit(_exit)
