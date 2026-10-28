#!/usr/bin/env python3
"""One HTTP probe, done so that a FAILED probe can never print another
probe's answer.

🔑 THE BUG THIS EXISTS TO PREVENT (found 2026-10-27, 21:15 UTC)
-------------------------------------------------------------
`ops/check-content-agent.py` probed several LLM providers in sequence, each
writing its response to the SAME fixed path:

    cmd = ["curl", "-s", "-o", "/tmp/llm.out", "-w", "%{http_code}", ...]
    ...
    out = open("/tmp/llm.out").read()[:200]

curl only creates/writes its `-o` target when it actually RECEIVES a
response. On a connection failure (DNS, refused, timeout) it exits non-zero
and **leaves the previous file exactly as it was** — proven, not assumed:

    $ printf STALE > /tmp/probe-stale-test.out
    $ curl -s --max-time 5 -o /tmp/probe-stale-test.out -w "%{http_code}" \\
          -X POST http://127.0.0.1:1/unreachable
    000
    $ cat /tmp/probe-stale-test.out
    STALE

So a failed probe printed the **previous provider's response body** under the
failed provider's name:

    moonshot    HTTP 000  {"id":"chatcmpl-...","choices":[...]}   <- real
    openai      HTTP 000  {"id":"chatcmpl-...","choices":[...]}   <- MOONSHOT's

A repair tool that shows a dead provider as alive misdirects the repair —
and it erred in the direction that **hides** a fault. `check-catalog.py` had
the same shape (one probe, but a stale file from a *previous run*).

🔑 **THE ROOT CAUSE IS THE CHANNEL, NOT THE PATH.** Using a FILE to carry a
response from curl to Python is what allowed a stale read. stdout is the
channel; the file was the accident. This module uses stdout, so there is no
file to go stale, two concurrent probes cannot collide, and nothing is left
behind in /tmp for the credential-surface audit to trip over.

Never prints a credential value: this module is handed the body by the
caller and returns it; the callers decide what to show.
"""
import subprocess

# The marker curl appends after the body. It starts with a newline so the
# body never has to be trimmed, and it is improbable enough that rpartition
# will not split a body that happens to contain it.
MARKER = "\n__HTTP_STATUS__"


def probe_json(name, url, headers, body=None, method="POST", timeout=60,
               max_time=45):
    """Call one JSON endpoint.

    Returns a dict:
        name    - the label given
        http    - the status code as a string, or "000" if there was none
        ok      - True only when curl completed AND the status is 2xx
        body    - up to 200 chars of the response, single-lined
        error   - "" when there was no transport failure, else why

    🔑 On a transport failure `body` is ALWAYS empty. There is no answer to
    report, so none is reported.
    """
    cmd = ["curl", "-s", "--max-time", str(max_time),
           "-w", MARKER + "%{http_code}", "-X", method, url]
    for h in headers:
        cmd += ["-H", h]
    if body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", body]
    try:
        rr = subprocess.run(cmd, capture_output=True, text=True,
                            timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"name": name, "http": "000", "ok": False, "body": "",
                "error": "timeout after %ss" % timeout}
    except Exception as e:                      # noqa: BLE001
        return {"name": name, "http": "000", "ok": False, "body": "",
                "error": "%s: %s" % (type(e).__name__, e)}
    if rr.returncode != 0:
        # 🔑 A FAILED REQUEST HAS NO ANSWER. Say so; do not print a body.
        return {"name": name, "http": "000", "ok": False, "body": "",
                "error": "curl rc=%d %s" % (rr.returncode,
                                            (rr.stderr or "").strip()[:160])}
    payload, sep, code = (rr.stdout or "").rpartition(MARKER)
    if not sep:
        return {"name": name, "http": "000", "ok": False, "body": "",
                "error": "curl produced no status marker"}
    code = code.strip()
    return {"name": name, "http": code, "ok": code.startswith("2"),
            "body": payload[:200].replace("\n", " "), "error": ""}


def format_line(res, width=12):
    """Render one probe result for a human. A failure says FAILED, not a body."""
    if res.get("error"):
        return "  %-*s FAILED  %s" % (width, res.get("name", "?"),
                                      res["error"])
    return "  %-*s HTTP %s  %s" % (width, res.get("name", "?"),
                                  res.get("http", "?"), res.get("body", ""))
