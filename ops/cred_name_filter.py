"""THE canonical credential-name filter. One place, imported by every tool.

WHY THIS MODULE EXISTS (2026-10-27)
------------------------------------
Nine tools select credentials from `.env` BY NAME. Each one used to carry its
own copy of this regex:

    ^(?:[A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD)[A-Z0-9_]*)$

`GITHUB_PAT` does not match it - it contains none of KEY/SECRET/TOKEN/PASSWORD.
So a LIVE, push-capable GitHub PAT sitting in `.env` was invisible to every
scanner and every redactor we own. Not a bug in one tool: a bug in nine
identical copies of the same filter, which is why fixing one of them would
have changed nothing.

That PAT was found by accident, in a session transcript, while chasing an
unrelated leak. It had `admin: True, push: True` on a PUBLIC repository.

THE PATTERN
-----------
    KEY / SECRET / TOKEN / PASSWORD  as a substring of the name
      -> unchanged behaviour, so no tool loses a credential it used to catch.

    PAT  as a WHOLE underscore-delimited segment
      -> GITHUB_PAT, GH_PAT, PAT_TOKEN all match.
      -> PATH does NOT: "PATH" is one segment, and it is not "PAT".
      -> COMPAT / PATCH / PATTERN do NOT, for the same reason.

The segment rule is deliberate. A plain substring "PAT" would match "PATH"
(`GITHUB_PATH`, `PATH` itself) and turn every PATH-shaped variable in the
environment into a "credential" - which would make the scanners hunt for
`/usr/local/bin:/usr/bin` inside the logs and drown the real findings in
noise. A rule that fires on correct code teaches people to ignore it.

Import it; do not re-inline it. If this file and a tool disagree, the tool
is wrong.
"""
import re

CRED_NAME_RE = re.compile(
    r"^(?:[A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD)[A-Z0-9_]*)$"
    r"|^(?:[A-Z0-9]+_)*PAT(?:_[A-Z0-9]+)*$"
)

# The same rule for a credential VARIABLE REFERENCE inside code, e.g.
# ${GITHUB_PAT}. Group 1 is the variable name in both alternatives.
CRED_REF_RE = re.compile(
    r"\$\{(?![A-Z_]*\})"
    r"([A-Z_]*(?:(?:KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL)[A-Z_]*"
    r"|(?:[A-Z0-9]+_)*PAT(?:_[A-Z0-9]+)*))\}"
)


def is_cred_name(name):
    """True when a .env variable NAME looks like a credential."""
    return bool(CRED_NAME_RE.match(str(name).strip()))


def is_cred_ref(name):
    """True when a referenced VARIABLE NAME looks like a credential."""
    return bool(CRED_REF_RE.search(str(name)))
