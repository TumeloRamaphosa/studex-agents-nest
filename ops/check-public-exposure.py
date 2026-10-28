#!/usr/bin/env python3
"""Check the PUBLIC REMOTE for credential exposure - not the working tree.

Why this exists
---------------
`ops/credential-resolution-check.py` scans TRACKED FILES in the working tree
and it reported CLEAN over 4166 files. It was right, and it was still blind:
the repository is PUBLIC, and the credentials it had removed were already
PUBLISHED - in the pushed branches, and in their history. A clean working tree
is not a clean public repo.

So this checker asks the only question that matters for a public remote:
"if a stranger cloned the pushed refs right now, what credential-shaped values
would they receive, and do any of them still authenticate?"

It scans every unique blob reachable from the pushed refs (the tip AND its
history - a credential removed in the last commit is still in the last
hundred commits), then probes each distinct value against its provider.

Output states:
  CLEAN       - nothing reachable from the pushed refs still works
  DRIFT       - at least one reachable value still authenticates (LIVE)
  UNVERIFIED  - reachable values whose liveness could not be established.
                This is NOT a pass: "we could not prove it works" is not "it is
                safe". A reachable credential is treated as live until revoked.

Exit codes: 0 only for CLEAN. 1 for DRIFT and UNVERIFIED.

Secrets are never printed. Only a provider name and the last 4 characters.

Usage:
  python3 ops/check-public-exposure.py [--refs origin/master,origin/main]
                                        [--no-probe]   # shape-only, offline
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

MAX_BLOB_BYTES = 512 * 1024

# Credential families, with a cheap liveness probe for each.
# The probe must use the provider's REAL contract - a 400/404 means "my request
# was malformed", NOT "the credential is dead". Only 200 proves it works.
FAMILIES: list[tuple[str, re.Pattern, object]] = [
    ("AgentMail", re.compile(r"am_us_[A-Za-z0-9]{30,}"),
     lambda t: _get("https://api.agentmail.to/v0/inboxes", {"Authorization": f"Bearer {t}"})),
    ("Blotato", re.compile(r"blt_[A-Za-z0-9+/=]{30,}"),
     lambda t: _get("https://backend.blotato.com/v2/users/me/accounts", {"blotato-api-key": t})),
    ("Orgo", re.compile(r"sk_live_[A-Za-z0-9]{20,}"),
     lambda t: _post("https://www.orgo.ai/api/computers/946b3156-cab9-4187-a94b-056dfab35105/bash",
                     {"Authorization": f"Bearer {t}", "Content-Type": "application/json"},
                     b'{"command":"echo probe"}')),
    ("ElevenLabs", re.compile(r"sk_[0-9a-f]{32}"),
     lambda t: _get("https://api.elevenlabs.io/v1/user", {"xi-api-key": t})),
    ("Meta", re.compile(r"EAAS[A-Za-z0-9]{40,}"),
     lambda t: _get(f"https://graph.facebook.com/v21.0/me?access_token={t}", {})),
    ("ClickUp", re.compile(r"pk_\d{9}_[A-Za-z0-9]{20,}"),
     lambda t: _get("https://api.clickup.com/api/v2/user", {"Authorization": t})),
    ("Perplexity", re.compile(r"pplx-[A-Za-z0-9_\-]{20,}"),
     lambda t: _get("https://api.perplexity.ai/chat/completions", {"Authorization": f"Bearer {t}"})),
    ("Cloudflare", re.compile(r"cfat_[A-Za-z0-9_\-]{20,}"),
     lambda t: _get("https://api.cloudflare.com/client/v4/user/tokens/verify", {"Authorization": f"Bearer {t}"})),
    ("Pinecone", re.compile(r"pcsk_[A-Za-z0-9]{20,}"),
     lambda t: _get("https://api.pinecone.io/indexes", {"Api-Key": t})),
    ("NVIDIA", re.compile(r"nvapi-[A-Za-z0-9_\-]{20,}"),
     lambda t: _get("https://integrate.api.nvidia.com/v1/models", {"Authorization": f"Bearer {t}"})),
    ("FeedHive", re.compile(r"fh_[0-9a-f]{40,}"),
     lambda t: _get("https://api.feedhive.com/v1/accounts", {"Authorization": f"Bearer {t}"})),
    ("Composio", re.compile(r"ak_[0-9A-Za-z]{24,}"),
     lambda t: _get("https://backend.composio.dev/api/v3/connected_accounts", {"x-api-key": t})),
    ("Hyvare", re.compile(r"hyrve_ak_[A-Za-z0-9]{30,}"),
     lambda t: _get("https://api.hyvare.ai/v1/models", {"Authorization": f"Bearer {t}"})),
    ("Alibaba", re.compile(r"LTAI[A-Za-z0-9]{16,}"), None),
    ("GoogleAPI", re.compile(r"AIza[0-9A-Za-z_\-]{30,}"),
     lambda t: _get(f"https://maps.googleapis.com/maps/api/geocode/json?address=Cape+Town&key={t}", {})),
    ("DiscordBot", re.compile(r"MTU[A-Za-z0-9_\-]{40,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}"),
     lambda t: _get("https://discord.com/api/v10/users/@me", {"Authorization": f"Bot {t}"})),
    # GoDaddy sso-key. The key carries NO recognisable prefix, so a
    # prefix-anchored pattern cannot see it - and the checker had no GoDaddy
    # family at all, which is why a live GoDaddy key+secret sat in the public
    # remote while the checker reported CLEAN. The shape here is the pair as
    # it appears on the wire: "sso-key <key>:<secret>". A key and secret
    # stored as separate variables are caught by the assignment rule in
    # ops/credential-resolution-check.py; this family covers the wire form.
    ("GoDaddy", re.compile(r"sso-key\s+([A-Za-z0-9_\-]{16,64}:[A-Za-z0-9_\-]{16,64})"),
     lambda t: _get("https://api.godaddy.com/v1/domains?statuses=ACTIVE",
                    {"Authorization": f"sso-key {t}"})),
    # GitHub PAT. The checker had NO GitHub family at all, which is the same
    # blind spot the GoDaddy entry above documents: a PAT-shaped literal in
    # the PUBLIC remote is exactly the credential you most want to find, and
    # the checker could never see it because it only knows shapes it has a
    # family for. A classic PAT is 40 chars after the ghp_ prefix; a fine-
    # grained one is github_pat_ + underscore-separated segments and can run
    # much longer, so both are matched separately.
    #
    # Liveness: GET /user returns 200 only for a token that still works, and
    # the response body names the account. A push-capable PAT published to
    # the world means a stranger can WRITE to the repo, not just read it.
    ("GitHubPAT", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),
     lambda t: _get("https://api.github.com/user", {"Authorization": f"Bearer {t}"})),
    ("GitHubFinePAT", re.compile(r"github_pat_[A-Za-z0-9_]{50,}"),
     lambda t: _get("https://api.github.com/user", {"Authorization": f"Bearer {t}"})),
]

# Families whose 200 does not mean "valid" - they need a body check.
BODY_VALIDATORS = {
    "GoogleAPI": lambda body: '"status"\s*:\s*"OK"' in body,
}

# Bodies that prove a credential is genuinely dead, even on a 4xx status.
# (A 400 with "invalid_api_key" is a rejection; a 400 with a schema error is
# not. Only the explicit rejection counts.)
BODY_REJECTIONS = (
    "invalid_api_key",
    "invalid api key",
    "invalid authentication",
    "unauthorized",
    "invalid token",
    "not authenticated",
)


# Obvious placeholders, judged against the MATCHED TEXT ONLY - the same rule
# the pre-commit guard uses. A context-based rule lets a real key through
# whenever it happens to sit near the word "example"; judging the match itself
# does not. Without this filter the checker would flag its OWN test fixture.
DUMMY = re.compile(
    r"(xxx+|YOUR_|_YOUR_|REDACTED|placeholder|dummy|fake|test[-_]?key|"
    r"sk_xxxxxxxxx|example)",
    re.I,
)


def is_placeholder(value: str) -> bool:
    return bool(DUMMY.search(value))


# A GoDaddy sso-key is a key and a secret stored as two separate variables.
# The variable names have to be the bare credential words - GODADDY_API_KEY
# and friends - because a name with a prefix is too generic to pair up
# safely (KEY could be any dictionary key).
GD_KEY = re.compile(
    r"^\s*(?:GODADDY_[A-Z_]*)?KEY\s*[:=]\s*[\"']?([A-Za-z0-9_\-]{16,64})[\"']?\s*$",
    re.M,
)
GD_SECRET = re.compile(
    r"^\s*(?:GODADDY_[A-Z_]*)?SEC(?:RET)?\s*[:=]\s*[\"']?([A-Za-z0-9_\-]{16,64})[\"']?\s*$",
    re.M,
)


def godaddy_pairs(text: str) -> list[str]:
    """Reconstruct 'key:secret' pairs from a blob that stores them apart.

    A prefix-less credential cannot be found by shape. What CAN be found is
    the ASSIGNMENT: a bare KEY and a bare SEC in the same file. That is the
    shape GoDaddy's sso-key takes, and it is the shape that was published.
    """
    out = []
    for k in GD_KEY.findall(text):
        if is_placeholder(k):
            continue
        for s in GD_SECRET.findall(text):
            if is_placeholder(s):
                continue
            out.append(f"{k}:{s}")
    return out


def _get(url, headers, timeout=12):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}"


def _post(url, headers, data, timeout=12):
    try:
        req = urllib.request.Request(url, headers=headers, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}"


def git(*args, check=False):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=check)


def pushed_refs(explicit: str | None = None) -> list[str]:
    """Refs that a stranger could clone."""
    if explicit:
        return [r.strip() for r in explicit.split(",") if r.strip()]
    out = git("for-each-ref", "--format=%(refname:short)", "refs/remotes").stdout
    refs = [r for r in out.splitlines() if r and not r.endswith("/HEAD")]
    return sorted(refs)


def reachable_blobs(refs: list[str]) -> dict[str, str]:
    """Every unique blob reachable from the given refs -> {blob_sha: first_path}."""
    if not refs:
        return {}
    res = git("rev-list", "--objects", *refs)
    blobs: dict[str, str] = {}
    for line in res.stdout.splitlines():
        parts = line.split(" ", 1)
        sha = parts[0]
        path = parts[1] if len(parts) > 1 else ""
        if not path:
            continue  # commit / tree, not a blob
        blobs.setdefault(sha, path)
    return blobs


def blob_text(sha: str) -> str | None:
    res = subprocess.run(["git", "cat-file", "-s", sha], capture_output=True, text=True)
    try:
        size = int(res.stdout.strip())
    except ValueError:
        return None
    if size > MAX_BLOB_BYTES:
        return None
    out = subprocess.run(["git", "cat-file", "blob", sha], capture_output=True)
    if out.returncode != 0:
        return None
    return out.stdout.decode("utf-8", "replace")


def scan(refs: list[str], probe: bool):
    blobs = reachable_blobs(refs)
    found: dict[tuple[str, str], dict] = {}

    for sha, path in blobs.items():
        text = blob_text(sha)
        if not text:
            continue
        for provider, pattern, _ in FAMILIES:
            for m in pattern.findall(text):
                key = (provider, m)
                if key in found:
                    found[key]["paths"].add(path)
                    continue
                if is_placeholder(m):
                    continue  # an obvious placeholder, not a credential
                found[key] = {"provider": provider, "value": m, "paths": {path}}

        # GoDaddy sso-keys have NO prefix, so no shape-only pattern can find
        # them. In the repo they were stored as two separate variables
        # (KEY = "..." / SEC = "...") in the same file, so the pair is
        # recoverable from the blob even though neither half is
        # recognisable on its own. This pass reconstructs the pair and
        # probes it against the provider's real contract.
        for pair in godaddy_pairs(text):
            key = ("GoDaddy", pair)
            if key in found:
                found[key]["paths"].add(path)
                continue
            found[key] = {"provider": "GoDaddy", "value": pair, "paths": {path}}

    live, dead, unknown = [], [], []
    for (provider, value), info in found.items():
        entry = {"provider": provider, "value": value, "paths": sorted(info["paths"])}
        if not probe:
            unknown.append(entry)
            continue
        probe_fn = next((p for pr, _, p in FAMILIES if pr == provider), None)
        if probe_fn is None:
            unknown.append(entry)
            continue
        status, body = probe_fn(value)
        validator = BODY_VALIDATORS.get(provider)
        if status == 200 and (validator is None or validator(body)):
            live.append(entry)
        elif status in (401, 403):
            dead.append(entry)
        elif any(rej in body.lower() for rej in BODY_REJECTIONS):
            dead.append(entry)
        else:
            unknown.append(entry)

    return live, dead, unknown, len(blobs)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refs", default=None,
                    help="comma-separated refs to scan (default: all remote-tracking refs)")
    ap.add_argument("--no-probe", action="store_true",
                    help="shape-only scan, no network liveness probe")
    args = ap.parse_args()

    refs = pushed_refs(args.refs)
    if not refs:
        print("  [WARN] no remote-tracking refs found - nothing to scan")
        return 0

    print(f"scanning pushed refs: {', '.join(refs)}")
    live, dead, unknown, nblobs = scan(refs, probe=not args.no_probe)
    print(f"  {nblobs} unique blob(s) reachable from the pushed refs")

    def show(title, items, sev):
        if not items:
            return
        print(f"\n{title}")
        for e in items:
            paths = ", ".join(e["paths"][:3])
            more = f" (+{len(e['paths']) - 3} more)" if len(e["paths"]) > 3 else ""
            print(f"  [{sev}] {e['provider']} ...{e['value'][-4:]}  in {paths}{more}")

    show("STILL AUTHENTICATING - reachable from the public remote:", live, "LIVE")
    show("credential-shaped but rejected by the provider:", dead, "DEAD")
    show("credential-shaped, liveness UNDETERMINED:", unknown, "?????")

    if live:
        print("\nRESULT: DRIFT")
        print("  A credential that still authenticates is reachable from the public remote.")
        print("  Rotate/revoke it at the provider FIRST (that is immediate), then")
        print("  rewrite the published history and push.")
        return 1
    if unknown:
        # A reachable credential whose liveness we could not establish is NOT a
        # pass. "We could not prove it works" is not "it is safe" - a green tick
        # that asserted nothing is worse than no checker.
        print("\nRESULT: UNVERIFIED")
        print("  Credential-shaped values are reachable from the public remote and")
        print("  their liveness could not be established (probe disabled, or the")
        print("  provider gave an inconclusive response). Treat every one as live")
        print("  until it is revoked.")
        return 1
    print("\nRESULT: CLEAN")
    print("  No credential-shaped value reachable from the pushed refs still works.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
