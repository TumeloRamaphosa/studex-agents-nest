#!/usr/bin/env python3
"""A failed HTTP probe must NEVER print another probe's answer.

🔴 THE BUG (found 2026-10-27, 21:15 UTC)
---------------------------------------
`ops/check-content-agent.py` probed several LLM providers in sequence, each
writing its response to the SAME fixed path (`/tmp/llm.out`) and then reading
that path back.

curl only writes its `-o` target when it actually RECEIVES a response. On a
connection failure it exits non-zero and **leaves the previous file exactly
as it was** — proven directly:

    $ printf STALE > /tmp/probe-stale-test.out
    $ curl -s --max-time 5 -o /tmp/probe-stale-test.out -w "%{http_code}" \
          -X POST http://127.0.0.1:1/unreachable
    000
    $ cat /tmp/probe-stale-test.out
    STALE

So the checker printed the PREVIOUS provider's response body under the failed
provider's name:

    moonshot    HTTP 000  {"id":"chatcmpl-...", ...}   <- real
    openai      HTTP 000  {"id":"chatcmpl-...", ...}   <- MOONSHOT's body

A repair tool that shows a dead provider as alive misdirects the repair, and
it erred in the direction that HIDES a fault.

🔑 **THE ROOT CAUSE IS THE CHANNEL, NOT THE PATH.** A FILE carried the
response from curl to Python, so a stale read was possible. stdout is the
channel; the file was the accident. `ops/http_probe.py` uses stdout.

What this test asserts
----------------------
A. A probe against an unreachable host reports FAILURE and an EMPTY body.
B. The classic stale-file scenario: a pre-existing file full of a sentinel is
   NOT reported as the answer.
C. A probe against a real local server returns that server's body and its
   status code, correctly.
D. Neither checker references a fixed /tmp path for its response body.
E. NEGATIVE CONTROL: the ORIGINAL implementation (fixed path + read-back)
   DOES reproduce the stale answer, so this test is not vacuous.
"""
import http.server
import os
import pathlib
import re
import subprocess
import sys
import threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
OPS = ROOT / "ops"
sys.path.insert(0, str(OPS))

from http_probe import probe_json, format_line   # noqa: E402

PASSED, FAILED = [], []

STALE_SENTINEL = "STALE_RESPONSE_FROM_PREVIOUS_PROVIDER"


def check(name, cond, detail=""):
    if cond:
        PASSED.append(name)
        print("[PASS] %s" % name)
    else:
        FAILED.append(name)
        print("[FAIL] %s%s" % (name, ("  -> " + str(detail)[:300]) if detail else ""))


# --------------------------------------------------------------- local server

class _Handler(http.server.BaseHTTPRequestHandler):
    body = b'{"answer":"REAL_ANSWER_FROM_THE_SERVER"}'

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n:
            self.rfile.read(n)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(self.body)))
        self.end_headers()
        self.wfile.write(self.body)

    def log_message(self, *a):
        pass


def _start_server():
    srv = http.server.HTTPServer(("127.0.0.1", 0), _Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv


def main():
    # ---------------------------------------------------------- A + B
    # The stale-file scenario, exactly as it happened in the wild.
    stale = pathlib.Path("/tmp/llm.out")
    had_previous = stale.exists()
    prev = stale.read_bytes() if had_previous else b""
    try:
        stale.write_text(STALE_SENTINEL)
        res = probe_json("unreachable", "http://127.0.0.1:1/unreachable",
                         [], '{"ping":1}', timeout=30, max_time=5)
        line = format_line(res)
        check("A. an unreachable host reports FAILURE", res["ok"] is False,
              res)
        check("A. an unreachable host returns an EMPTY body",
              res["body"] == "", repr(res["body"])[:200])
        check("A. an unreachable host reports a transport error",
              bool(res["error"]), res)
        check("B. the STALE file's contents are NOT reported as the answer",
              STALE_SENTINEL not in line and STALE_SENTINEL not in res["body"],
              line[:200])
        check("B. the stale file was left alone (we never read it)",
              stale.read_text() == STALE_SENTINEL,
              "the probe consumed or rewrote the file")
    finally:
        if had_previous:
            stale.write_bytes(prev)
        elif stale.exists():
            stale.unlink()

    # ---------------------------------------------------------- C
    srv = _start_server()
    try:
        port = srv.server_address[1]
        res = probe_json("local", "http://127.0.0.1:%d/probe" % port,
                         [], '{"ping":1}', timeout=30, max_time=10)
        check("C. a reachable server returns its body",
              "REAL_ANSWER_FROM_THE_SERVER" in res["body"],
              repr(res["body"])[:200])
        check("C. a reachable server returns its status code",
              res["http"] == "200", res["http"])
        check("C. a 2xx is reported as ok", res["ok"] is True, res)
    finally:
        srv.shutdown()
        srv.server_close()

    # ---------------------------------------------------------- D
    # Structural: no checker may carry a response through a fixed /tmp file.
    bad = []
    for f in ("check-content-agent.py", "check-catalog.py"):
        t = (OPS / f).read_text(encoding="utf8")
        hits = re.findall(r'"-o",\s*"(/tmp/[^"]+)"', t)
        reads = re.findall(r'open\(\s*["\'](/tmp/[^"\']+)["\']\s*\)\.read',
                            t)
        if hits or reads:
            bad.append("%s -> writes=%s reads=%s" % (f, hits, reads))
    check("D. no checker carries an HTTP response through a fixed /tmp file",
          not bad, "; ".join(bad))

    # ---------------------------------------------------------- E
    # NEGATIVE CONTROL: the ORIGINAL implementation must still reproduce the
    # bug, or this test proves nothing.
    stale2 = pathlib.Path("/tmp/llm.out")
    had2 = stale2.exists()
    prev2 = stale2.read_bytes() if had2 else b""
    try:
        stale2.write_text(STALE_SENTINEL)
        cmd = ["curl", "-s", "--max-time", "5", "-o", str(stale2),
               "-w", "%{http_code}", "-X", "POST",
               "http://127.0.0.1:1/unreachable"]
        subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        old_body = stale2.read_text()[:200].replace("\n", " ")
        check("E. NEGATIVE: the ORIGINAL fixed-path implementation DOES return "
              "the stale body", STALE_SENTINEL in old_body,
              "the bug did not reproduce - this test is invalid")
    finally:
        if had2:
            stale2.write_bytes(prev2)
        elif stale2.exists():
            stale2.unlink()

    print("\n%d passed, %d failed" % (len(PASSED), len(FAILED)))
    if FAILED:
        print("VERDICT: BROKEN - a failed probe can still report a stale "
              "answer.")
        return 1
    print("VERDICT: CLEAN - a failed probe reports a failure and no body.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
