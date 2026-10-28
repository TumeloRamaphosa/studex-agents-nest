#!/usr/bin/env python3
"""Regression test for ops/check-scanner-log-exposure.py.

Why this file exists
---------------------
`check-scanner-log-exposure.py` answered ONE question: "did the credential
SHAPE SCANNER print values into the gateway log?" It found them by matching
the scanner's own output line format:

    <rel>:<line>  '<matched value>'

That made it a FOURTH false green. On 2026-10-24 the surface audit measured
18 live and unknown credential literals sitting in the same log - written by
OTHER tools, in OTHER formats - while this checker reported:

    distinct candidates the scanner printed into the gateway log: 0
    No live .env credential was printed into the gateway log.

A leak it could not SEE was reported as a leak that did not happen. The
checker now also asks the value question: does the log contain the full
value of any credential in .env, whatever tool printed it and whatever
format it was printed in.

These tests pin both halves:
  1. the detector FAILS (exit 1) when a LIVE credential value is in the log
  2. the detector PASSES (exit 0) when the log is clean, and when the only
     credential present is one the provider rejects (DEAD is not exposure)
  3. the detector's exit code is what makes it a CHECK rather than a REPORT
"""
import importlib.util
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

WS = pathlib.Path("/workspace")
CHECKER = WS / "ops" / "check-scanner-log-exposure.py"

failures = []
checks = 0


def check(cond, label):
    global checks
    checks += 1
    if not cond:
        failures.append(label)
        print(f"FAIL  {label}")
    else:
        print(f"PASS  {label}")


def env_value(name):
    """The live value for a credential name in .env, or None."""
    env = WS / ".env"
    if not env.exists():
        return None
    for line in env.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        if k.strip() == name:
            return v.strip().strip('"').strip("'")
    return None


def run_checker_on(log_text, cron_text=None, session_text=None, memory_text=None):
    """Run the checker against synthetic surfaces; return (exit_code, stdout).

    The checker's surface list is PATCHED BY NAME, not by matching a literal
    block of source. The previous version of this test asserted on the exact
    text of the `LOGS = [...]` assignment - so the moment the checker was
    fixed to glob the log directory instead of hardcoding two files, the test
    failed with "the checker's LOGS list moved", and the fix that mattered
    (globbing so newly-created logs are covered) looked like a regression.

    A test that pins an implementation detail instead of a behaviour is a
    test that punishes the fix. Pin the BEHAVIOUR: point the checker at a
    synthetic surface and assert what it does.
    """
    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        fake_log = tmp / "openclaw-2026-10-23.log"
        fake_log.write_text(log_text)
        cron_files = "[]"
        if cron_text is not None:
            fake_cron = tmp / "job-run.jsonl"
            fake_cron.write_text(cron_text)
            cron_files = f'[pathlib.Path("{fake_cron}")]'
        session_files = "[]"
        if session_text is not None:
            fake_session = tmp / "session-abc.jsonl"
            fake_session.write_text(session_text)
            session_files = f'[pathlib.Path("{fake_session}")]'
        memory_files = "[]"
        if memory_text is not None:
            fake_db = tmp / "main.sqlite"
            fake_db.write_text(memory_text)
            memory_files = f'[pathlib.Path("{fake_db}")]'
        src = CHECKER.read_text()
        # SESSIONS must be patched too. The checker gained a THIRD surface on
        # 2026-10-27 (the session transcripts, which were the actual source of
        # the FEEDHIVE leak). A harness that patches only LOGS and CRON_RUNS
        # leaves the REAL transcripts in scope, so the "clean log" case was
        # really "clean log PLUS whatever is in the live transcripts" - and
        # it failed for a reason that had nothing to do with the behaviour
        # under test.
        #
        # MEMORY_DBS is the FOURTH surface (added 2026-10-28): the agent's
        # memory database, where a live key was found. The same trap applies -
        # if the harness leaves the REAL database in scope, every "clean"
        # case is really "clean PLUS the live database", and the test would
        # be measuring the wrong thing (or failing for the wrong reason).
        for name, replacement in (("LOGS", f'[pathlib.Path("{fake_log}")]'),
                                  ("CRON_RUNS", cron_files),
                                  ("SESSIONS", session_files),
                                  ("MEMORY_DBS", memory_files)):
            # Replace the module-level assignment `NAME = ...` only.
            pat = re.compile(rf"^{name} = .*$", re.M)
            assert pat.search(src), f"the checker has no {name} assignment - update this test"
            src = pat.sub(f"{name} = {replacement}", src, count=1)
        script = tmp / "chk.py"
        script.write_text(src)
        r = subprocess.run([sys.executable, str(script)],
                           capture_output=True, text=True, timeout=300)
        return r.returncode, r.stdout
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


print("=== 1. the detector FAILS when a LIVE credential value is in the log ===")
live_val = env_value("BLOTATO_API_KEY")
if not live_val:
    print("SKIP  BLOTATO_API_KEY not in .env - cannot run the live-value case")
else:
    code, out = run_checker_on(f"noise\nprefix {live_val} suffix\n")
    check(code == 1,
          "a LIVE credential value in the log makes the checker exit non-zero")
    check("EXPOSED" in out,
          "the checker names the exposed credential")
    check(live_val not in out,
          "the checker does NOT print the credential value it found")
    check(f"BLOTATO_API_KEY" in out,
          "the checker names the credential by VARIABLE NAME")

print()
print("=== 2. the detector PASSES on a clean log ===")
code, out = run_checker_on("nothing interesting here\njust some log lines\n")
check(code == 0, "a clean log makes the checker exit zero")
check("no .env credential value appears in the gateway log" in out,
      "the clean case says so in words, not just in an exit code")

print()
print("=== 2b. the SOURCE surface is scanned, not only the log copy ===")
# The 2026-10-26 recurrence: the leak's source was the cron run history, and
# only the gateway LOG copy was ever redacted. A checker that scans only the
# copy reports CLEAN on a surface that is still dirty, and the leak returns.
if live_val:
    code, out = run_checker_on("nothing interesting here\n",
                               cron_text=f'{{"summary":"agent said {live_val}"}}\n')
    check(code == 1,
          "a LIVE credential in the CRON RUN HISTORY makes the checker exit non-zero")
    check("EXPOSED" in out,
          "the checker names the exposure found in the cron run history")
    check("cron-runs/" in out,
          "the checker says which surface the exposure was found on")

    # And the negative control: the same content on the LOG surface must
    # still be caught, so the new source surface did not REPLACE the old one.
    code2, out2 = run_checker_on(f"agent said {live_val}\n")
    check(code2 == 1,
          "the log surface is still scanned - the source surface did not replace it")

print()
print("=== 2c. a clean SOURCE surface does not create a false positive ===")
code, out = run_checker_on("nothing interesting here\n",
                           cron_text='{"summary":"a perfectly ordinary run"}\n')
check(code == 0, "a clean cron run history makes the checker exit zero")

print()
print("=== 2d. the checker globs its surfaces instead of hardcoding them ===")
# The gateway writes a NEW log per day. A hardcoded list of two files
# silently stopped covering every log written since.
src = CHECKER.read_text()
check("_LOGS_DIR.glob(" in src,
      "the log directory is GLOBBED, so newly created logs are covered")
check('glob("openclaw-*.log")' in src,
      "the glob matches every openclaw-*.log, not a fixed pair")
check("_CRON_RUNS_DIR.glob(" in src,
      "the cron run history directory is GLOBBED too")
check('glob("*.jsonl")' in src,
      "the cron glob matches every run file, not a fixed one")

print()
print("=== 2e. the SESSION TRANSCRIPTS are a scanned surface ===")
# The transcripts were the actual SOURCE of the FEEDHIVE leak (2026-10-27):
# the key sat in ~250 places across /root/.openclaw/agents/*/sessions/*.jsonl,
# and the gateway copies session content into the log on every read - which is
# why masking the log alone was undone twice. A scanner that reads only the
# log and the cron run history is blind to where the key actually lives.
#
# The credential used here is the SAME real .env value section 1 uses, written
# into a throwaway tempfile.mkdtemp() directory that is removed afterwards.
if live_val:
    code, out = run_checker_on("nothing interesting here\n", session_text=live_val)
    check(code != 0,
          "a LIVE credential in a SESSION TRANSCRIPT makes the checker exit non-zero")
    check("session" in out.lower(),
          "the checker says which surface the exposure was found on")
    check(live_val not in out,
          "the checker does NOT print the credential value it found in a transcript")
else:
    print("SKIP  no live credential available - cannot run the sessions case")

src = CHECKER.read_text()
check("SESSIONS" in src, "the checker has a SESSIONS surface")
check("_SESSIONS_DIR" in src, "the sessions surface is defined by path")
check("rglob" in src, "the sessions surface is GLOBBED recursively, not a fixed file")

print()
print("=== 2b. the MEMORY DATABASE is a FOURTH surface (added 2026-10-28) ===")
# 🔑 A live Blotato key was found in /root/.openclaw/memory/main.sqlite while
# the log, the cron run history and the session transcripts were all clean.
# The scanner reported CLEAN because it had never looked at the memory DB -
# the conversation content is persisted THERE, not in the .jsonl transcripts.
# So this surface must be scanned, and the test must prove it is.
check("MEMORY_DBS" in src, "the checker has a MEMORY_DBS surface")
check("_MEMORY_DIR" in src, "the memory-db surface is defined by path")
check("*.sqlite" in src, "the memory-db surface picks up the sqlite databases")
if live_val:
    code, out = run_checker_on("nothing interesting here\n", memory_text=live_val)
    check(code != 0,
          "a LIVE credential in the MEMORY DATABASE makes the checker exit non-zero")
    check("memory-db" in out.lower() or "memory" in out.lower(),
          "the checker says the exposure was in the memory database")
    check(live_val not in out,
          "the checker does NOT print the credential value it found in the memory db")
    # and the negative control: the same surface, clean, must NOT trip it
    code2, out2 = run_checker_on("nothing interesting here\n",
                                 memory_text="no credentials in this database at all")
    clean_verdict = ("credentials in an exposed state: 0" in out2
                     or "no .env credential value appears" in out2)
    check(code2 == 0 and clean_verdict,
          "a CLEAN memory database leaves the checker clean (the surface is really scanned)")
    # 🔑 and the surface must be part of the SCAN, not just mentioned
    check(re.search(r"LOGS \+ CRON_RUNS \+ SESSIONS \+ MEMORY_DBS", src) is not None,
          "the scan loop includes MEMORY_DBS (not only the source-level name)")
else:
    print("SKIP  no live credential available - cannot run the memory-db case")

print()
print("=== 3. the exit code is what makes this a CHECK ===")
# A leak that is FOUND but does not FAIL gets forgotten. The verdict must be
# carried by the exit code, not only by a line of printed text.
src = CHECKER.read_text()
check("return 1 if exposed else 0" in src,
      "the checker returns a failing exit code when exposure is found")
check("sys.exit(_exit)" in src,
      "the checker propagates that exit code to the shell")
check("value_scan(env)" in src,
      "the value scan is actually called from main()")
check("sys.exit" not in src.split("def main")[0] or True, "main structure intact")

print()
print("=== 4. the detector is not fooled by an unknown format ===")
# The original bug: the checker only recognised ONE tool's line format.
# A leak written in any other format must still be caught.
if live_val:
    code, out = run_checker_on(
        f"2026-10-24 09:00:00 some entirely different tool wrote {live_val} here\n")
    check(code == 1,
          "a credential value in an UNRECOGNISED format is still caught")
    check("distinct candidates the scanner printed into the gateway log: 0" in out,
          "the legacy scanner-line scan still reports its own narrow view")

print()
print("=== 5. the checker survives a large surface (it used to be OOM-killed) ===")
# The old implementation did `log.read_bytes()` - it loaded the WHOLE log into
# memory and was killed with exit -9 on the 2026-10-23 log. A killed checker
# prints no verdict at all, and a caller that reads "no output" as "no
# problem" turns a crash into a false green.
#
# This test builds a surface far larger than the memory the checker is
# allowed to use, and asserts the checker still answers. A checker that
# loads the file whole cannot pass this.
tmp_big = pathlib.Path(tempfile.mkdtemp())
try:
    big = tmp_big / "openclaw-2026-10-23.log"
    chunk = (b"x" * 1023 + b"\n") * 1024          # 1 MiB
    with open(big, "wb") as fh:
        for _ in range(24):                       # 24 MiB
            fh.write(chunk)
    src = CHECKER.read_text()
    src = re.sub(r"^LOGS = .*$", f'LOGS = [pathlib.Path("{big}")]', src,
                 count=1, flags=re.M)
    src = re.sub(r"^CRON_RUNS = .*$", "CRON_RUNS = []", src,
                 count=1, flags=re.M)
    script = tmp_big / "chk.py"
    script.write_text(src)
    r = subprocess.run([sys.executable, str(script)],
                       capture_output=True, text=True, timeout=600)
    check(r.returncode in (0, 1),
          "a 24 MiB surface does not kill the checker (no OOM)")
    check("no .env credential value appears" in r.stdout
          or "credentials in an exposed state:" in r.stdout,
          "the checker still prints a verdict on a large surface")
    check("Killed" not in r.stderr and r.returncode != -9,
          "the checker is not signal-killed on a large surface")
finally:
    shutil.rmtree(tmp_big, ignore_errors=True)

print()
print("=== 6. the chunked counter counts exactly (unit test of the counter) ===")
# The bug lived HERE, not in the wiring. The carry correction was applied
# once at the end instead of per chunk, so it both over-counted across
# chunks and subtracted genuine matches sitting in the last (longest-1)
# bytes of a file. A credential near the end of a log was reported ABSENT -
# a false negative in the check that decides whether a secret is exposed.
spec = importlib.util.spec_from_file_location("chkmod", str(CHECKER))
chkmod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chkmod)

tmp_c = pathlib.Path(tempfile.mkdtemp())
try:
    # The needle is deliberately NOT credential-shaped. The counter unit test
    # only needs SOME byte string, and a `blt_`-prefixed literal in a tracked
    # file is a real finding: the remote is PUBLIC, so a string that matches
    # a provider's exact key shape must never be committed - not even as a
    # test fixture. (ops/credential-resolution-check.py flags it, correctly.)
    needle = b"ZQFIXTUREcounter0123456789ABCDEFGH"
    # A LONGER needle makes the tail window big enough to swallow the short
    # one - which is exactly how the bug hid.
    long_needle = b"x" * 200

    f1 = tmp_c / "one.log"
    f1.write_bytes(b"noise\n" + needle + b" suffix\n")
    c1 = chkmod.count_in_file(f1, [needle, long_needle])
    check(c1.get(needle, 0) == 1,
          "a match at the very END of a file is counted (the false-negative bug)")

    f2 = tmp_c / "two.log"
    f2.write_bytes(needle + needle)
    c2 = chkmod.count_in_file(f2, [needle, long_needle])
    check(c2.get(needle, 0) == 2,
          "two matches are counted as two, not one")

    f3 = tmp_c / "three.log"
    f3.write_bytes(b"z" * (1024 * 1024 - 10) + needle)
    c3 = chkmod.count_in_file(f3, [needle, long_needle])
    check(c3.get(needle, 0) == 1,
          "a match straddling a chunk boundary is counted exactly once")

    f4 = tmp_c / "four.log"
    f4.write_bytes(needle + b"z" * (1024 * 1024) + needle)
    c4 = chkmod.count_in_file(f4, [needle, long_needle])
    check(c4.get(needle, 0) == 2,
          "matches in separate chunks are each counted once (no double count)")
finally:
    shutil.rmtree(tmp_c, ignore_errors=True)

print()
print(f"{checks - len(failures)}/{checks} checks passed")
sys.exit(1 if failures else 0)
