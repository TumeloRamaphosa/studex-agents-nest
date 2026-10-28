"""Resolve AgentMail / Blotato credentials from the workspace .env at runtime.

Why this exists: several checker scripts were committed with literal
`${AGENTMAIL_MAIN_API_KEY}` / `${BLOTATO_API_KEY}` placeholders. Run them
as-is and they send the *placeholder string* as the credential, get HTTP 403 /
401 back, and print "0 messages" / "0 posts" — which is byte-identical to
"nothing there". That is the exact false-negative trap documented in
HEARTBEAT.md: a checker that swallows an auth error manufactures false
reassurance.

So: never hardcode a key literal in a script, and never leave a template
placeholder in one. Read the secret from the untracked .env at call time.

Usage:
    from agentmail_keys import agentmail_keys, blotato_key
"""
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"

# The main AgentMail account key. Alternatives are excluded when they are
# DEAD (a 403 key makes a sweep look empty rather than failing loudly), and
# deduplicated when they are live but identical to a key already held.
MAIN_KEY_ENV = "AGENTMAIL_MAIN_API_KEY"
# The CIIE account key. It belongs to a DIFFERENT AgentMail account: its inbox
# (project-2571-studex-agent-2077@agentmail.to) 404s for the main key and does
# not appear in GET /v0/inboxes for the main key. Sweeping one account cannot
# see the other — sweep both.
# It lives in the UNTRACKED .env as AGENTMAIL_CIIE_KEY. Never hardcode it here:
# this repo's remote is PUBLIC and the pre-commit guard is right to block that.
CIIE_KEY_ENV = "AGENTMAIL_CIIE_KEY"


def _load_env():
    env = dict(os.environ)
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def agentmail_keys():
    """Return every AgentMail key worth sweeping, de-duplicated, main first."""
    env = _load_env()
    keys = []
    for name in (MAIN_KEY_ENV, "AGENTMAIL_WARMUP_API_KEY", "AGENTMAIL_WARROOM_API_KEY"):
        v = env.get(name)
        if v and v not in keys:
            keys.append(v)
    cii = env.get(CIIE_KEY_ENV)
    if cii and cii not in keys:
        keys.append(cii)
    return keys


def blotato_key():
    env = _load_env()
    k = env.get("BLOTATO_API_KEY")
    if not k:
        raise SystemExit("BLOTATO_API_KEY not found in .env or environment")
    return k


def live_agentmail_keys(probe=True):
    """Return only the AgentMail keys that actually WORK, verified by probing.

    A key that returns HTTP 403 is dead. Sweeping with it yields zero
    inboxes, which prints identically to "there is no mail" - a false
    all-clear. So we probe GET /v0/inboxes for every candidate and keep only
    the ones that answer 200.

    `AGENTMAIL_API_KEY` in .env was once dead (403); it has since been
    REPLACED and now answers 200, byte-identical to the main key (same
    sha256 prefix, re-probed 2026-10-26), so it only duplicates. The CIIE
    account key is a DIFFERENT account and IS in .env as AGENTMAIL_CIIE_KEY.
    The CIIE account's inbox does not appear under the main key and vice
    versa: sweep both or the answer is structurally wrong.
    """
    env = _load_env()
    candidates = []
    for name in (
        MAIN_KEY_ENV,
        "AGENTMAIL_API_KEY",
        "AGENTMAIL_WARMUP_API_KEY",
        "AGENTMAIL_WARROOM_API_KEY",
        "AGENTMAIL_LEGACY_API_KEY",
        CIIE_KEY_ENV,
    ):
        v = env.get(name)
        if v and v not in candidates:
            candidates.append(v)

    if not probe:
        return candidates

    import urllib.error
    import urllib.request

    live, dead = [], []
    for k in candidates:
        req = urllib.request.Request(
            "https://api.agentmail.to/v0/inboxes", headers={"Authorization": f"Bearer {k}"}
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                if r.status == 200:
                    live.append(k)
                else:
                    dead.append((k, r.status))
        except urllib.error.HTTPError as e:
            dead.append((k, e.code))
        except Exception:
            dead.append((k, 0))

    if not live:
        raise SystemExit(
            "NO LIVE AGENTMAIL KEY. Every candidate failed "
            + ", ".join(f"{k[:12]}...->{c}" for k, c in dead)
            + ". Refusing to report '0 messages' on a broken sweep."
        )
    for k, c in dead:
        print(f"[key {k[:12]}...] DEAD (HTTP {c}) - excluded from this sweep")
    return live


def assert_not_truncated(count, limit):
    """A truncated sweep does not error — it just returns a smaller world.

    GET /v0/inboxes/{id}/messages?limit=N silently truncates at N. If the
    returned count equals the limit you are NOT finished. Fail loud.
    """
    if count >= limit:
        raise SystemExit(
            f"TRUNCATED: got {count} messages for limit {limit}. "
            "Raise the limit and re-run before trusting this result."
        )
