#!/usr/bin/env python3
"""Fail when code references a mailbox that nobody can read.

WHY THIS EXISTS
---------------
AgentMail ACCEPTS a send to an address that no key can read, and returns
success. The message becomes unreachable by anyone. Every monitoring surface
stays green. A website lead sent to such an address is simply gone.

Four such addresses have been found so far, all one or two characters from a
live one:
    studex-2571@agentmail.to        - 404 on every key, invisible to all
    naledi.cmo@studex-group.com     - 404 on every key (live one: naledi-cmo@)
    robusca@studex-group.com        - 404 on every key (live: robusca.romanov@)
    charlie@agent.studexmeat.com    - no DNS at all; mail bounces

Fixing them one address at a time does not converge - a new one appears with
every sweep. This checker makes the class of bug a build failure instead.

RULES
-----
1. An address on our own domains, appearing in a code/config file, must be
   either:
     a. listed in ops/live-inbox-allowlist.txt  (proven reachable), or
     b. listed in ops/dead-inbox-exceptions.txt for THAT EXACT FILE
        (a deliberate reference - e.g. a watcher that must keep watching a
        dead address so we can detect it).
2. Anything else is a FINDING and this exits non-zero.
3. Markdown and dated history are NOT scanned: prose may legitimately describe
   what used to be true. Code may not.

Run:  python3 ops/dead-inbox-check.py
      python3 ops/dead-inbox-check.py --verify   (re-prove the allowlist live)
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The regression test points this at a throwaway scratch tree. It must NEVER
# default to the live tree when the test runs - a rule-proving test that
# writes into the directory it checks leaves its own fixture behind.
ROOT = Path(os.environ.get("DEAD_INBOX_CHECK_ROOT", str(ROOT)))
ALLOWLIST = ROOT / "ops" / "live-inbox-allowlist.txt"
EXCEPTIONS = ROOT / "ops" / "dead-inbox-exceptions.txt"

# Our own domains only. External addresses (gmail etc.) cannot be probed by
# our AgentMail keys, so they are out of scope - the checker cannot prove
# anything about them and a rule that cannot be proved is not a rule.
# AgentMail-hosted domains. The API can PROVE who can read these, so an
# unreachable address here is a proven bug and fails the build.
AGENTMAIL_DOMAINS = (
    "studex-group.com",
    "agentmail.to",
    "agent.studexmeat.com",
)

# Plain domain mailboxes. SMTP egress from this host is blocked, so their
# deliverability cannot be proven from here - they are reported against a
# dated backlog instead of failing the build, because a rule that cannot be
# satisfied is a rule people ignore.
DOMAIN_MAILBOX_DOMAINS = ("studexmeat.com",)

OWN_DOMAINS = AGENTMAIL_DOMAINS + DOMAIN_MAILBOX_DOMAINS

# Code and config only. Markdown is excluded on purpose.
CODE_SUFFIXES = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".json", ".html",
    ".sh", ".bash", ".py", ".toml", ".yaml", ".yml", ".env", ".example",
    ".service", ".conf", ".ini", ".txt",
}

# Dated history and prose. A dead address in these is a record, not a bug.
#
# NOTE: "dist" and "build" are deliberately NOT skipped. A browser bundle is
# the thing a customer actually downloads, and a stale bundle sitting in a
# dist/ folder is exactly what a later `deploy` will publish. Skipping them
# was a hole in this rule: a rebuilt mirror still shipped charlie@ (found
# 2026-10-24). A rule that only covers what it scans is decoration.
SKIP_DIRS = {
    ".git", "node_modules", ".archive", "__pycache__",
    "memory", "research", "builds", "studex-obsidian-vault", ".matrix-session-memory",
    "reports", "quarantine",
    # Files the user supplied. Not our code to correct.
    "user_input_files",
}

# A leading backslash means the character before the address is part of an
# ESCAPE, not part of the address. Without this, the JSON string "...Team\n"
# followed by "sales@studex-group.com" reads as one bogus address
# "nsales@studex-group.com" - and a repair script written against that
# misreading ate the escape and broke the file. The lookbehind stops the
# escape from being swallowed into the local part.
# The local part may not BEGIN with a hyphen. Shell-compose default-value
# syntax (${VAR:-default@host}) and list markers put a "-" immediately
# before the address. A lookbehind for "-" cannot help here: the bogus
# match STARTS AT the hyphen (its previous char is ":"), so a lookbehind
# would pass and "-ceo" would still be swallowed into the local part.
# Forbidding "-" as the FIRST character of the local part is what actually
# separates the separator from the address - the match then starts at
# "ceo" and yields the real address instead of a fabricated one.
EMAIL_RE = re.compile(r"(?<!\\)[A-Za-z0-9._%+][A-Za-z0-9._%+\-]*@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def _read_list(path: Path) -> list[str]:
    if not path.exists():
        return []
    out = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    return out


def live_addresses() -> set[str]:
    """Addresses proven reachable."""
    return {line.split("#")[0].strip().lower() for line in _read_list(ALLOWLIST) if line.split("#")[0].strip()}


def exceptions() -> list[tuple[str, str]]:
    """(address_lower, path_glob) pairs - a deliberate reference."""
    out = []
    for line in _read_list(EXCEPTIONS):
        if "|" not in line:
            continue
        addr, glob = line.split("|", 1)
        out.append((addr.strip().lower(), glob.strip()))
    return out


def in_scope(addr: str) -> bool:
    domain = addr.rsplit("@", 1)[-1].lower()
    return any(domain == d or domain.endswith("." + d) for d in OWN_DOMAINS)


def tier(addr: str) -> str:
    """hard = provably unreachable. soft = deliverability unprovable here."""
    domain = addr.rsplit("@", 1)[-1].lower()
    if any(domain == d or domain.endswith("." + d) for d in AGENTMAIL_DOMAINS):
        return "hard"
    return "soft"


def iter_code_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
        for fn in filenames:
            p = Path(dirpath) / fn
            suffix = p.suffix.lower()
            if suffix not in CODE_SUFFIXES:
                continue
            if fn in {ALLOWLIST.name, EXCEPTIONS.name, Path(__file__).name}:
                continue
            yield p


def scan() -> list[tuple[str, int, str, str]]:
    """Return (relpath, lineno, address, reason) for every finding."""
    live = live_addresses()
    excs = exceptions()
    findings = []
    for path in iter_code_files():
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(path.relative_to(ROOT))
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in EMAIL_RE.finditer(line):
                addr = m.group(0).lower()
                if not in_scope(addr):
                    continue
                if addr in live:
                    continue
                exempt = False
                for eaddr, glob in excs:
                    if eaddr == addr and (fnmatch.fnmatch(rel, glob) or rel == glob):
                        exempt = True
                        break
                if exempt:
                    continue
                if addr in live:
                    continue
                findings.append((rel, lineno, addr,
                                 "not in live allowlist and not excepted for this file",
                                 tier(addr)))
    return findings


def verify_live() -> int:
    """Re-prove every allowlist entry against the live AgentMail API."""
    import json
    import urllib.error
    import urllib.request

    env = {}
    envfile = ROOT / ".env"
    if envfile.exists():
        for raw in envfile.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    names = [
        "AGENTMAIL_MAIN_API_KEY", "AGENTMAIL_WARROOM_API_KEY",
        "AGENTMAIL_CIIE_KEY", "AGENTMAIL_WARMUP_API_KEY",
        "AGENTMAIL_LEGACY_API_KEY", "AGENTMAIL_API_KEY",
    ]
    keys = [env[n] for n in names if env.get(n)]

    visible: set[str] = set()
    for k in keys:
        req = urllib.request.Request(
            "https://api.agentmail.to/v0/inboxes?limit=200",
            headers={"Authorization": "Bearer " + k},
        )
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.loads(r.read())
        except Exception:
            continue
        for it in data.get("inboxes") or data.get("data") or []:
            a = it.get("inbox_id") or it.get("address") or it.get("email")
            if a:
                visible.add(a.lower())

    print("visible inboxes via AgentMail API: %d" % len(visible))
    bad = 0
    for addr in sorted(live_addresses()):
        if addr.endswith("@studexmeat.com"):
            print("  %-46s domain mailbox (not an AgentMail inbox - verified by publication)" % addr)
            continue
        if addr in visible:
            print("  %-46s OK - visible to a live key" % addr)
        else:
            print("  %-46s NOT VISIBLE - the allowlist is lying" % addr)
            bad += 1
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="re-prove the allowlist against the live API")
    args = ap.parse_args()

    if args.verify:
        return verify_live()

    findings = scan()
    hard = [f for f in findings if f[4] == "hard"]
    soft = [f for f in findings if f[4] == "soft"]

    backlog = set()
    bl = ROOT / "ops" / "domain-mailbox-backlog.txt"
    if bl.exists():
        for line in bl.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                backlog.add(line.lower())

    soft_addrs = sorted({f[2] for f in soft})
    new_soft = [a for a in soft_addrs if a not in backlog]

    if soft_addrs:
        print("[WARN] dead inbox check   %d unverified DOMAIN mailbox address(es):"
              % len(soft_addrs))
        for a in soft_addrs:
            n = len([f for f in soft if f[2] == a])
            mark = "NEW - not in the backlog" if a in new_soft else "in backlog"
            print("  %-40s %2d site(s)  [%s]" % (a, n, mark))
        print("-" * 72)
        print("These are plain domain mailboxes on a domain whose mail route")
        print("could not be verified from this host (SMTP egress blocked).")
        print("They do not fail the build, but the backlog must not grow.")
        print("Verify them in the domain's mail provider, then either promote")
        print("them to ops/live-inbox-allowlist.txt or repoint them.")

    if not hard:
        print("[ OK ] dead inbox check   CLEAN   no provably-unreachable mailbox "
              "referenced in code")
        return 1 if new_soft else 0

    print("[FAIL] dead inbox check   %d provably-unreachable finding(s):" % len(hard))
    seen = set()
    for rel, lineno, addr, reason, _t in hard:
        key = (rel, addr)
        if key in seen:
            continue
        seen.add(key)
        print("  %s:%d  %s  (%s)" % (rel, lineno, addr, reason))
    print("-" * 72)
    print("An address here is unreachable: no AgentMail key can read it. A send")
    print("to it is ACCEPTED and reports success, so a lead disappears silently.")
    print("Fix: use a live address, or record a deliberate exception in")
    print("     ops/dead-inbox-exceptions.txt as '<address>|<path-glob>'.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
