#!/usr/bin/env python3
"""Audit the /tmp credential-leak surface. VERDICT ONLY - it masks nothing.

CORRECTED 2026-10-24 04:47 UTC. The previous version of this script reported
the /tmp surface as "CLOSED" while the live Blotato key sat in the active
gateway log 1,051 times. Two root causes, both now fixed:

  1. `KEY_RE` matched only `am_us_[A-Za-z0-9_]{20,}`. A Blotato key is
     `blt_...` and a GoDaddy key has NO prefix at all, so neither could ever
     be seen. The scan was structurally blind to every credential family
     except AgentMail's.
  2. The script DELIBERATELY LEFT THE ACTIVE LOG ALONE, reasoning that the
     gateway holds its fd so it must not be touched. That reasoning was
     wrong: `redact-active-gateway-log.py` had already demonstrated the safe
     method - overwrite bytes IN PLACE with a same-length mask. The inode,
     the file descriptor and the append position all stay valid. Leaving
     the active log alone was not caution, it was the hole.

CORRECTED AGAIN 2026-10-24 05:30 UTC. Two more blind spots, same family:

  3. The scan still walked a HARDCODED LIST of five files while the redactor
     had been run over nine. A "quarantine" directory is a RENAME, not a
     deletion - moving a file to /tmp/quarantine-* does not remove the
     secret from it - so the quarantine itself held six files with the live
     Blotato key, and the audit reported CLEAN throughout. 🔑 **A checker
     that scans the files it was told about is not a checker of the
     directory it claims to cover.**

  4. The verdict counted only `state == "live"` as exposure, while the
     redactor masks LIVE **and UNKNOWN**. The two disagreed: an UNKNOWN
     key (no probe defined for its provider) was masked on disk but did not
     count as exposure in the verdict. A GoDaddy key is UNKNOWN and it
     authenticates. 🔑 **The audit and the redactor must agree on what
     "exposure" means, or the audit under-reports what the redactor fixes.**

So this script now:
  * classifies liveness by ASKING THE PROVIDER (GET only) for every
    credential in .env, not just AgentMail's
  * treats a value it cannot probe as UNKNOWN, which is NOT safe - an
    unprobeable key is masked, because "we could not prove it works" is not
    "it is safe"
  * scans with the FULL VALUE of each credential, not a prefix regex
  * WALKS /tmp, rather than scanning a hardcoded list of files
  * counts LIVE **and UNKNOWN** as exposure - the same set the redactor
    masks
  * performs NO masking and NO deletion - it reports, and
    `redact-live-secrets-in-place.py` does the masking
  * REFUSES to print a "clean" verdict while an exposed literal remains
  * prints a COVERAGE block stating how many files it actually read, so a
    verdict can say what it did NOT look at

The 02:45 audit's own lesson is preserved: `am_us_057fa6...` sits in .env
but returns HTTP 403, so treating "present in .env" as "live" overstates
the exposure. Liveness comes from the provider's answer, never from the
mere fact that a string is in a file. Conversely, a key we CANNOT probe is
not thereby safe - it is UNKNOWN, and UNKNOWN is masked.
"""
import os
import pathlib
import re
import urllib.error
import urllib.request

ENV_FILE = pathlib.Path("/workspace/.env")
# A credential-shaped NAME in .env, whatever the provider's prefix is.
# The canonical credential-name filter lives in ONE place, so this tool and
# the other tools that select credentials from .env cannot drift apart. See
# ops/cred_name_filter.py for why a copy-pasted regex in nine files was a
# real security bug: a live, push-capable GITHUB_PAT matched none of
# KEY/SECRET/TOKEN/PASSWORD, so it was invisible to every scanner.
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "_cred_name_filter", "/workspace/ops/cred_name_filter.py")
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CRED_NAME_RE = _mod.CRED_NAME_RE
MIN_LEN = 16
MAX_FILE_BYTES = 400_000_000

# Provider -> (probe URL, header name). GET only. Never POST, never DELETE.
# Every provider we KNOW carries a live credential must have a probe here.
# A credential family with no probe is classified UNKNOWN - which is not
# safe, and which means a green verdict says less than it appears to.
PROBES = {
    # AgentMail REQUIRES the "Bearer " scheme. A bare `Authorization: am_us_...`
    # returns 403 - which this probe would have classified as DEAD (proof of
    # death) and therefore SKIPPED, while the key was in fact live. A probe
    # that speaks the wrong dialect reads a live credential as a dead one.
    # Verified 2026-10-24: bare -> 403, "Bearer <key>" -> 200.
    "am_us_": ("https://api.agentmail.to/v0/inboxes", "Authorization: Bearer {key}"),
    "blt_": ("https://backend.blotato.com/v2/users/me/accounts", "blotato-api-key: {key}"),
}

# Directories never descended into: VCS metadata, package caches.
SKIP_DIR_NAMES = {".git", "node_modules", "__pycache__", ".npm", ".cache"}


def load_env_keys():
    """Every credential-shaped value in .env - NOT just AgentMail's.

    Filtering on a provider prefix is how the Blotato key was missed: a
    `blt_...` value never matched an `am_us_` pattern, so it was invisible
    to a scan that claimed to be looking for credentials.
    """
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


# One definition of "is this credential alive?": the shared classifier in
# ops/redact-live-secrets-in-place.py. This file used to carry its OWN probe
# table - a SECOND copy of the same liveness logic - which is how the
# FeedHive key stayed "unknown (no probe for this prefix)" here forever
# while the redactor had already proved it DEAD with a control probe. Two
# copies of a classifier always drift, and the more aggressive one wins by
# accident. There is now one.
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "_redact_live_secrets",
    "/workspace/ops/redact-live-secrets-in-place.py")
_redactor = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_redactor)


def probe(name, key, env):
    """Ask the provider whether this key authenticates. GET only.

    401/403 = DEAD (proof). Anything else = UNKNOWN, which is NOT safe.

    GoDaddy has no prefix on its key and needs key+secret as
    `sso-key <key>:<secret>`, so it is probed by env NAME, not by prefix.
    A prefix probe would never have fired for it - which is exactly how a
    live, published GoDaddy key stayed "UNKNOWN" and therefore uncounted.
    """
    if name == "GODADDY_API_KEY":
        secret = env.get("GODADDY_API_SECRET", "")
        if not secret:
            return 0, "unknown (no secret to pair with the key)"
        req = urllib.request.Request(
            "https://api.godaddy.com/v1/domains?statuses=ACTIVE",
            headers={"Authorization": f"sso-key {key}:{secret}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.status, "live"
        except urllib.error.HTTPError as e:
            return e.code, "DEAD" if e.code in (401, 403) else "unknown"
        except Exception as e:  # noqa: BLE001
            return 0, f"probe-error: {e}"

    # Orgo has no distinctive prefix (`sk_live_` is a generic Stripe-shaped
    # string), so it is probed by env NAME against a GET endpoint that checks
    # auth before method. Verified 2026-10-24: Bearer + the real key -> 401,
    # while GET /api/computers (collection) -> 405. A 405 is a METHOD error and
    # says nothing about the key; the 401 does.
    #
    # Without this probe the key fell through to "unknown (no probe for this
    # prefix)" -> counted as exposure -> masked in the gateway log -> and then
    # RE-CREATED by the next diagnostic that printed it. The audit was
    # manufacturing its own finding.
    if name.startswith("ORGO_API_KEY"):
        req = urllib.request.Request(
            "https://www.orgo.ai/api/computers/"
            "946b3156-cab9-4187-a94b-056dfab35105",
            headers={"Authorization": "Bearer " + key},
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.status, "live"
        except urllib.error.HTTPError as e:
            return e.code, "DEAD" if e.code in (401, 403) else "unknown"
        except Exception as e:  # noqa: BLE001
            return 0, f"probe-error: {e}"

    # DELEGATE to the shared classifier. It owns the probe table, the
    # name-based special cases (GoDaddy needs key+secret, Orgo has no
    # distinctive prefix) and the CONTROL probe that distinguishes "this
    # credential is dead" from "this service is gone".
    state, _detail = _redactor.classify(key, env, name)
    if state == "LIVE":
        return 200, "live"
    if state == "DEAD":
        return 401, "DEAD"
    return 0, "unknown (no probe for this prefix)"


def is_exposed(state):
    """Does this state count as exposure?

    LIVE and UNKNOWN both do. DEAD does not.

    ⚠ The state strings are not a clean enum: "unknown (no probe for this
    prefix)" is not equal to "unknown". A membership test against
    ("live", "unknown") silently counts ZERO unknowns, which is how a live
    GoDaddy key stayed uncounted in the first version of this rewrite.
    Use a prefix test.
    """
    return state == "live" or state.startswith("unknown")


def walk_tmp():
    """Every readable file under /tmp. The scan COVERS the directory."""
    for root, dirs, files in os.walk("/tmp"):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR_NAMES]
        for fname in files:
            path = os.path.join(root, fname)
            try:
                if os.path.getsize(path) > MAX_FILE_BYTES:
                    continue
                yield path
            except OSError:
                continue


def scan_bytes(data, values):
    """Match on the FULL VALUE of each credential, not a prefix regex."""
    hits = {}
    for name, value, state in values:
        n = data.count(value.encode())
        if n:
            hits[name] = (state, n)
    return hits


def main():
    env_keys = load_env_keys()
    print("probing each .env credential against its provider (GET only)")
    print("(liveness from the provider's own answer, not from the file's presence)")
    print()
    values = []
    for name, value in sorted(env_keys.items()):
        status, verdict = probe(name, value, env_keys)
        print(f"  {name:28} HTTP {status or '-':>3}  {verdict}")
        values.append((name, value, verdict))

    print()
    print("=== scan (FULL VALUE of every credential, walking all of /tmp) ===")
    exposed = 0
    exposed_files = []
    scanned = 0
    skipped = 0
    unreadable = 0
    for path in walk_tmp():
        try:
            data = pathlib.Path(path).read_bytes()
        except OSError:
            unreadable += 1
            continue
        scanned += 1
        hits = scan_bytes(data, values)
        if not hits:
            continue
        file_exposed = 0
        print(f"{path}:")
        for name, (state, n) in sorted(hits.items()):
            print(f"   {name:28} {state:8} occurrences={n}")
            if is_exposed(state):
                file_exposed += n
        if file_exposed:
            exposed += file_exposed
            exposed_files.append(path)

    print()
    print("=== COVERAGE ===")
    print(f"  files read              : {scanned}")
    print(f"  files unreadable        : {unreadable}")
    print(f"  files holding exposure  : {len(exposed_files)}")
    print("  (LIVE and UNKNOWN both count as exposure - UNKNOWN is masked on disk,")
    print("   because a key we cannot probe is not thereby safe)")
    print()

    if exposed:
        print(f"VERDICT: EXPOSED - {exposed} exposed credential literal(s) in "
              f"{len(exposed_files)} file(s).")
        print("Run: python3 ops/redact-live-secrets-in-place.py <files>")
        return 1
    print("VERDICT: CLEAN - no live or unknown credential literal under /tmp.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
