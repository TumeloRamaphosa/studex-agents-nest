#!/usr/bin/env python3
"""Regression test for the AgentMail key/inventory helpers.

Why this test exists (2026-10-26)
----------------------------------
`scripts/agentmail_keys.py::agentmail_keys()` referenced an undefined name
`CIIE_KEY`, so it raised `NameError` on every call. Nothing imported it, so
no test failed and the breakage was invisible -- the function was simply
dead code that could not run.

Two lessons are baked in here:

  1. A module that no test imports may be broken for months. This test
     imports it, so the NameError cannot come back.
  2. "Reachable on one key, 404 on another" is a DIFFERENT state from
     "404 on every key". The inventory notes must say which, or a sweep
     reports a coverage gap that does not exist (or hides one that does).

NO NETWORK. The helpers are exercised with an injected fake .env, so this
test is deterministic and cannot be affected by key rotation.

Run:  python3 ops/test-agentmail-inventory.py
"""
import hashlib
import importlib
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  PASS " if cond else "  FAIL ") + name + ((" -- " + detail) if detail and not cond else ""))


# ---------------------------------------------------------------- fixture
FAKE = {
    "AGENTMAIL_MAIN_API_KEY": "am_main_" + "m" * 40,
    "AGENTMAIL_API_KEY": "am_main_" + "m" * 40,          # same value as main
    "AGENTMAIL_WARMUP_API_KEY": "am_warm_" + "w" * 40,
    "AGENTMAIL_WARROOM_API_KEY": "am_room_" + "r" * 40,
    "AGENTMAIL_LEGACY_API_KEY": "am_legacy_" + "l" * 40,
    "AGENTMAIL_CIIE_KEY": "am_ciie_" + "c" * 40,          # different account
    "AGENTMAIL_DEAD_KEY": "am_dead_" + "d" * 40,          # never returned by the API
}


def load_with_env(monkey_env):
    """Reload agentmail_keys with a fake .env and no network."""
    import agentmail_keys as ak
    importlib.reload(ak)
    ak.ENV_FILE = pathlib.Path(tempfile.mkdtemp()) / ".env"
    ak.ENV_FILE.write_text(
        "\n".join("%s=%s" % (k, v) for k, v in monkey_env.items()), encoding="utf-8"
    )
    ak._load_env = lambda: dict(monkey_env)
    return ak


print("agentmail_keys.agentmail_keys()")
ak = load_with_env(FAKE)
try:
    keys = ak.agentmail_keys()
    check("agentmail_keys() returns without raising", True)
except Exception as e:
    check("agentmail_keys() returns without raising", False, "%s: %s" % (type(e).__name__, e))
    keys = []

if keys:
    check(
        "returns the main key",
        FAKE["AGENTMAIL_MAIN_API_KEY"] in keys,
    )
    check(
        "includes the CIIE account key (different account, must be swept too)",
        FAKE["AGENTMAIL_CIIE_KEY"] in keys,
    )
    check(
        "no duplicate keys (a live key identical to another is deduped)",
        len(keys) == len(set(keys)),
        "got %d keys, %d unique" % (len(keys), len(set(keys))),
    )
    check(
        "a key identical to the main key appears only once",
        keys.count(FAKE["AGENTMAIL_API_KEY"]) == 1,
    )
    check(
        "a dead key is never hardcoded into the returned set",
        FAKE["AGENTMAIL_DEAD_KEY"] not in keys,
    )
    check(
        "every returned key is non-empty",
        all(k for k in keys),
    )

# ---------------------------------------------------------------- watch notes
print("agentmail_watch.KNOWN_UNREACHABLE honesty")
import agentmail_watch as aw

ku = aw.KNOWN_UNREACHABLE
studex = ku.get("studex-2571@agentmail.to", "")
check(
    "studex-2571 note no longer ASSERTS 404 on all keys",
    "HTTP 404 on all 5 usable keys" not in studex,
    studex[:90],
)
check(
    "studex-2571 note states its actual state (200 on main key, 404 on CIIE)",
    "200" in studex and "404" in studex,
)
check(
    "naledi.cmo note does not claim 404 on all keys either",
    "on all 5 usable keys" not in ku.get("naledi.cmo@studex-group.com", ""),
)
check(
    "studex-2571 is still WATCHED (a live-but-empty inbox must stay watched)",
    "studex-2571@agentmail.to" in aw.WATCH,
)
check(
    "every KNOWN_UNREACHABLE address is also in WATCH",
    all(a in aw.WATCH for a in ku),
    str([a for a in ku if a not in aw.WATCH]),
)

# ---------------------------------------------------------------- coverage report
print("agentmail_watch.coverage_report")
try:
    lines, gap, missing = aw.coverage_report(
        aw.WATCH, {"robusca.romanov@studex-group.com"}, [], []
    )
    check("coverage_report() returns without raising", True)
    check("gap count is positive when watched addresses were not read", gap > 0)
    check("missing list is non-empty", bool(missing))
    check(
        "a missing watched address carries its note, not 'no note'",
        any("no note" not in l for l in lines if "@" in l),
    )
    ok_empty, gap0, _ = aw.coverage_report(aw.WATCH, set(aw.WATCH), [], [])
    check("zero gap when everything is readable", gap0 == 0, "gap=%d" % gap0)
    v = aw.verdict_lines([], 3, 5, 10)
    check(
        "an uncovered verdict is QUALIFIED, not a bare NOT_PAID",
        any("QUALIFIED" in x for x in v),
        " | ".join(v),
    )
    v2 = aw.verdict_lines([], 0, 11, 100)
    check(
        "a covered verdict states completeness",
        any("no coverage gaps" in x for x in v2),
        " | ".join(v2),
    )
except Exception as e:
    check("coverage_report() returns without raising", False, "%s: %s" % (type(e).__name__, e))

# ---------------------------------------------------------------- docs
print("TOOLS.md inventory honesty")
tools = (ROOT / "TOOLS.md").read_text(encoding="utf-8")
check(
    "TOOLS.md no longer claims AGENTMAIL_API_KEY is dead",
    "**Dead key:** `AGENTMAIL_API_KEY`" not in tools,
)
check(
    "TOOLS.md records the re-probe of studex-2571",
    "NO LONGER DEAD" in tools or "no longer dead" in tools.lower(),
)
check(
    "TOOLS.md no longer claims 404 on all 5 usable keys",
    "404 on all 5 usable keys" not in tools,
)

print()
print("%d passed, %d failed" % (len(PASS), len(FAIL)))
if FAIL:
    print("FAILED:")
    for f in FAIL:
        print("  -", f)
    sys.exit(1)
print("ALL TESTS PASS")
