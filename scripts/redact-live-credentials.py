#!/usr/bin/env python3
"""
Redact LIVE credential values from tracked source, using EXACT VALUE
replacement driven by the untracked /workspace/.env.

WHY EXACT VALUE, NOT A SHAPE REGEX
----------------------------------
The first redaction pass used shape regexes like blt_[A-Za-z0-9]{20,}.
That regex does NOT consume the base64 padding "=" at the end of the key,
so it replaced the PREFIX and left the real suffix in the file:

    blt_<28 chars>N*******************
    -> [REDACTED:28 chars - rotate this key]N*******************

That is the exact bug class this whole exercise exists to eliminate: a
placeholder pasted over part of a key, leaving live material behind. A
redactor that reintroduces it is worse than no redactor, because it
reports that it cleaned the file.

So: collect the LITERAL credential values (whole, including any trailing
"=" that belongs to the value) and replace those exact strings. No shape
matching at all.

Idempotent: running it twice changes nothing the second time.
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path("/workspace")
ENV = ROOT / ".env"

# Third-party vendored trees. They carry their own upstream test fixtures
# (dummy keys that happen to be credential-shaped). They are not ours to
# redact, and editing them creates upstream merge conflicts.
VENDOR = re.compile(
    r"^(Decepticon|OpenJarvis|gstack|headroom|OBLITERATUS|Agent-Reach|"
    r"OpenClawHomeAssistant|odysseus|core/)"
)

# Obvious dummies - a redactor that eats a test fixture teaches people to
# distrust it.
DUMMY = re.compile(
    r"(xxx+|YOUR_|_YOUR_|REDACTED|placeholder|dummy|fake|test[-_]?key|"
    r"sk_xxxxxxxxx|example|DeadBeef|abcdef|ABCDEF|0123456789|realkey|"
    r"realtoken|deadbeef|LEAKED|FORBIDDEN|random-secure-string)",
    re.I,
)

# Shape used only to LOCATE candidate literals. The value that gets
# replaced is the matched text EXTENDED over trailing '=' or '-' characters,
# because those are part of the credential (base64 padding), not
# punctuation.
SHAPE = re.compile(
    r"(?:am_us_[A-Za-z0-9]{30,}"
    r"|sk-r[A-Za-z0-9]{30,}"
    r"|sk_live_[A-Za-z0-9]{20,}"
    r"|blt_[A-Za-z0-9]{20,}"
    r"|sk_[0-9a-f]{32}"
    r"|EAAS[A-Za-z0-9]{40,}"
    r"|pk_\d{9}_[A-Za-z0-9]{20,}"
    r"|tskey-[A-Za-z0-9\-_]{20,}"
    r"|cfat_[A-Za-z0-9_\-]{20,}"
    r"|pplx-[A-Za-z0-9_\-]{20,}"
    r"|nvapi-[A-Za-z0-9_\-]{20,}"
    r"|LTAI[0-9A-Za-z]{12,}"
    r"|AIza[A-Za-z0-9_\-]{30,}"
    r"|hyrve_ak_[A-Za-z0-9_]{20,}"
    r"|pcsk_[A-Za-z0-9]{30,}"
    r"|prtapi_[A-Za-z0-9]{20,}"
    r"|rl_sk_[A-Za-z0-9_\-]{20,}"
    r"|sk-ws-[A-Za-z0-9._\-]{20,}"
    r"|sk-proj-[A-Za-z0-9_\-]{20,}"
    r"|ghp_[A-Za-z0-9]{30,}"
    r"|sk-ant-[A-Za-z0-9_\-]{20,}"
    r"|xox[baprs]-[A-Za-z0-9-]{20,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|glpat-[A-Za-z0-9_\-]{20,}"
    r"|fh_[0-9a-f]{40,}"
    r"|\b[0-9a-f]{64}\b"
    r")"
)


def env_values():
    """Live credential values from the untracked env file."""
    out = set()
    if not ENV.exists():
        return out
    for line in ENV.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        _, v = s.split("=", 1)
        v = v.strip().strip('"').strip("'")
        if len(v) >= 16:
            out.add(v)
    return out


def tracked_files():
    r = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "HEAD"],
        capture_output=True, text=True, cwd=ROOT,
    )
    return [f for f in r.stdout.split("\n") if f.strip()]


def collect_literals(files):
    """Whole credential literals present in tracked files."""
    found = set()
    for rel in files:
        if VENDOR.match(rel):
            continue
        p = ROOT / rel
        if not p.is_file():
            continue
        try:
            text = p.read_text(errors="replace")
        except OSError:
            continue
        if len(text) > 4_000_000:
            continue
        for m in SHAPE.finditer(text):
            v = m.group(0)
            if DUMMY.search(v):
                continue
            # Extend over trailing '=' / '-' so the ENTIRE credential is
            # replaced and no live suffix can survive.
            j = m.end()
            while j < len(text) and text[j] in "=-":
                v += text[j]
                j += 1
            found.add(v)
    return found


def main():
    files = tracked_files()
    values = collect_literals(files)
    # Live values from .env, in case one is in a file the shape regex
    # did not match (e.g. an opaque token with no known prefix).
    values |= {v for v in env_values() if len(v) >= 20}
    values = {v for v in values if not DUMMY.search(v)}
    # Longest first, so a value that contains another is replaced whole.
    ordered = sorted(values, key=len, reverse=True)

    changed = 0
    for rel in files:
        if VENDOR.match(rel):
            continue
        p = ROOT / rel
        if not p.is_file():
            continue
        try:
            text = p.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        original = text
        for v in ordered:
            if v in text:
                text = text.replace(v, f"[REDACTED:{len(v)} chars - rotate this key]")
        if text != original:
            p.write_text(text)
            changed += 1

    print(f"redacted {len(ordered)} distinct live value(s) across {changed} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
