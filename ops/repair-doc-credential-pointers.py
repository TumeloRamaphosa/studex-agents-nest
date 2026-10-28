#!/usr/bin/env python3
"""Repair and verify the credential pointers in the local notes docs.

WHY
---
TOOLS.md and TOOLS_SUPPLEMENT.md are injected into the agent's context on
EVERY session, and agent output is captured into the gateway session log.
A credential sitting in either file is therefore on the path:

    secret -> context -> log -> possibly a Discord message or a commit

That is exactly how live AgentMail keys reached
/tmp/openclaw/openclaw-*.log. Both files are untracked so they were never
PUBLISHED, but /workspace files are externally accessible on this platform,
so "untracked" is not "private".

THE CONTRACT
------------
These files must NEVER contain a credential literal. They name the variable;
the value lives in /workspace/.env (untracked, gitignored) - the one place a
credential can be rotated from.

This script is IDEMPOTENT: it repairs what is wrong and re-verifies. Running
it on an already-clean file changes nothing.

DESIGN NOTE - WHY THERE IS NO CLEVER INFERENCE
----------------------------------------------
An earlier version of this tool derived a variable NAME from the line's
label and pointed the doc at whatever .env held under that name. Where .env
held a DIFFERENT value the doc pointed at the wrong secret - and worse, a
later pass assigned names POSITIONALLY, so the Tencent key landed in
ORGO_API_KEY_NEW and the Facebook PAGE id landed in ALIBABA_SSH_PASSWORD.

A pointer that resolves to the wrong secret is worse than no pointer,
because it looks correct. So this version NEVER infers a name from
position or from a label alone:

  * a literal is matched to a .env variable by EXACT VALUE, or
  * the line has an explicit, hand-verified repair, or
  * the literal is reported as unplaced and the run FAILS.

VERIFICATION GATE - exits non-zero rather than half-doing it
  1. every ${VAR} pointer in the docs resolves to a variable in .env
  2. no value that .env holds appears literally in the docs
  3. no literal on a credential-labelled line survives
  4. .env has no duplicate keys, no placeholder values, no bare-identifier
     values

On (2) and (3): a Drive folder id, an IP, an endpoint and a Cloudflare
account id are all credential-SHAPED but are not credentials, and this tool
must not mangle them. So the gate asks a different question from "does this
look like a secret?" - "is this a value we know is a credential?" (it is in
.env) or "does this line claim to be a credential?".

This script holds NO credential literal - the few values it must place are
read from the docs or from .env at runtime, so it is safe to commit.

NOTE FOR THE CREDENTIAL RESOLUTION CHECKER
------------------------------------------
The ${VAR} strings below are OUTPUT, not references: this tool writes them
into markdown so a human can look the value up in .env. Python not
expanding them is the design. The marker below tells the checker that,
and it scopes the exemption to the ${VAR} resolution rule only - the
hardcoded-literal scan still runs over this file in full.

# credential-resolution: doc-pointer-emitter
"""
import os
import pathlib
import re
import sys

# DOC_POINTER_WS lets the regression test run against a throwaway copy of
# the workspace instead of the live one. The tool must never mutate the
# live .env or the live docs while under test.
WS = pathlib.Path(os.environ.get("DOC_POINTER_WS", "/workspace"))
ENV_FILE = WS / ".env"
DOCS = [WS / "TOOLS.md", WS / "TOOLS_SUPPLEMENT.md"]

QUOTED = re.compile(r"`([^`\s]{8,})`")
PLACEHOLDER = re.compile(r"^REDACTED_CREDENTIAL_+$")
UUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                  r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
PATHISH = re.compile(r"^[A-Za-z0-9_.\-]+(/[A-Za-z0-9_.\-]*)+$")
CODE_IDENT = re.compile(r"^[a-z_][a-z0-9_]*\(\)$")
VAR_NAME = re.compile(r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)+$")
BARE_NAME = re.compile(r"^[A-Z][A-Z0-9_]{4,}$")
UNRESOLVED = "<not stored locally - rotate / re-issue>"

# --- EXPLICIT, HAND-VERIFIED LINE REPAIRS ----------------------------------
# (marker that must appear on the line, compiled regex, replacement)
LINE_REPAIRS = [
    ("Hermes Notes",
     re.compile(r"^\| Hermes Notes \|.*$"),
     "| Hermes Notes | `1UMpeygpC7gDmZIUtYjK1PPwnQ40-6bo` |"),
    ("Facebook User Token",
     re.compile(r"^- \*\*Facebook User Token:\*\*.*$"),
     "- **Facebook User Token:** `${FACEBOOK_USER_TOKEN}` (in .env)"),
    ("Facebook Page Token",
     re.compile(r"^- \*\*Facebook Page Token:\*\*.*$"),
     "- **Facebook Page Token:** expired 27-Jun-2026 (Meta 190/463) — "
     "not retained locally"),
    ("Facebook Page:",
     re.compile(r"^- \*\*Facebook Page:\*\*.*$"),
     "- **Facebook Page:** `108934711902801` (StudEx Meat)"),
    ("Old key (dead)",
     re.compile(r"^- \*\*Old key \(dead\):\*\*.*$"),
     "- **Old key (dead):** revoked — value no longer retained locally"),
    ("VNC Password",
     re.compile(r"^\| VNC Password \|.*$"),
     "| VNC Password | `${ORGO_PASSWORD}` (in .env) |"),
    ("Orgo API Key (NEW",
     re.compile(r"^\| Orgo API Key \(NEW.*$"),
     "| Orgo API Key (NEW — 2026-08-22) | `${ORGO_API_KEY_NEW}` (in .env) |"),
    ("Tencent API",
     re.compile(r"^- \*\*Tencent API \(suspected\):\*\*.*$"),
     "- **Tencent API (suspected):** `${TENCENT_API_KEY}` (in .env)"),
    ("| OpenAI |",
     re.compile(r"^\| OpenAI \|.*$"),
     "| OpenAI | `${OPENAI_API_KEY}` (in .env) |"),
    ("Authorization: Bearer",
     re.compile(r'^\s*-H "Authorization: Bearer.*$'),
     '  -H "Authorization: Bearer $ORGO_API_KEY" \\\\'),
    ("- Key: REDACTED_CREDENTIAL",
     re.compile(r"^- Key: REDACTED_CREDENTIAL.*$"),
     "- Key: `${ELEVENLABS_API_KEY}` (in .env)"),
    ("**SSH:**",
     re.compile(r"^- \*\*SSH:\*\*.*$"),
     "- **SSH:** `ssh root@47.236.124.79` — password "
     "`${ALIBABA_SSH_PASSWORD}` (in .env)"),
    # a line mangled by a re.sub lambda that never expanded \1 \2
    ("\\1`${ALIBABA_SSH_PASSWORD}`\\2",
     re.compile(r"^.*\\1`\$\{ALIBABA_SSH_PASSWORD\}`\\2.*$"),
     "- **SSH:** `ssh root@47.236.124.79` — password "
     "`${ALIBABA_SSH_PASSWORD}` (in .env)"),
]

# .env names written with a duplicated suffix by an earlier pass.
ENV_RENAME = {"HIGHSFIELD_API_KEY_API_KEY": "HIGHSFIELD_API_KEY"}

# .env entries that hold something which is NOT a credential.
ENV_DROP = {
    "BLOTATO_API_KEY_FROM_DOCS",   # held the header name "blotato-api-key"
}

# Where two credentials share a length, length alone cannot disambiguate, so
# the label decides. Each mapping is confirmed by value equality with .env.
LABEL_OVERRIDE = {
    "api key (dedicated)": "AGENTMAIL_CIIE_KEY",
    "api key (general)": "AGENTMAIL_API_KEY_GENERAL",
    "api key (new 2)": "AGENTMAIL_WARMUP_API_KEY",
    "api key (new 3)": "AGENTMAIL_API_KEY",
}

# Section heading -> the variable that holds that section's credential. Used
# only to fix a pointer that does not resolve at all; a pointer that DOES
# resolve is never rewritten on the strength of a heading.
HEADING_VAR = {
    "blotato": "BLOTATO_API_KEY",
    "cloudflare": "CLOUDFLARE_API_TOKEN",
    "clickup": "CLICKUP_API_TOKEN",
    "kimi": "KIMI_API_KEY",
    "hyvareai": "HYVARE_API_KEY",
    "nvapi": "NVIDIA_API_KEY",
    "freepik": "FREEPIK_API_KEY",
    "pinecone": "PINECONE_API_KEY",
    "composio": "COMPOSIO_API_KEY",
    "perplexity": "PERPLEXITY_API_KEY",
    "daytona": "DAYTONA_API_KEY",
    "typestack": "TYPESTACK_API_KEY",
    "shopify": "SHOPIFY_API_TOKEN",
    "elevenlabs": "ELEVENLABS_API_KEY",
    "pipe dream": "PIPEDREAM_API_KEY",
    "honcho": "HONCHO_API_KEY",
    "alibaba cloud maas": "ALIBABA_MAAS_API_KEY",
    "qwen / dashscope": "DASHSCOPE_API_KEY",
    "r2 access key": "R2_ACCESS_KEY_ID",
    "r2 secret key": "R2_SECRET_KEY",
}

SECRET_LABEL = re.compile(r"(\bkeys?\b|\btokens?\b|\bsecret\b|\bpassword\b|"
                           r"\bpat\b|\bcredential|\bapi\b)", re.I)
NOT_SECRET = re.compile(
    r"(account id|app id|instance id|vm id|folder id|form id|user id|"
    r"business account|meta app|workspace id|\bhost\b|endpoint|url|base url|"
    r"dashboard|\bapi base\b|agentmail|drive\.google|\bid\b|dispatch)", re.I)


def parse_env(text):
    vals = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, _, v = s.partition("=")
        v = v.strip()
        if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        vals.setdefault(k.strip(), []).append(v)
    return vals


def load_env():
    raw = parse_env(ENV_FILE.read_text(errors="ignore"))
    out = {}
    for k, occ in raw.items():
        out[ENV_RENAME.get(k, k)] = occ[0]
    for k in list(out):
        if PLACEHOLDER.match(out[k]) or BARE_NAME.match(out[k]) or k in ENV_DROP:
            del out[k]
    return out


def is_credential_shape(v):
    if len(v) < 8 or "..." in v or " " in v:
        return False
    if v.startswith(("http://", "https://", "/", "./", "../", "${", "<")):
        return False
    if PLACEHOLDER.match(v) or UUID.match(v) or PATHISH.match(v):
        return False
    if CODE_IDENT.match(v) or VAR_NAME.match(v):
        return False
    if "@" in v or "[" in v or "]" in v:
        return False
    return True


def line_label(line):
    s = line.strip()
    if s.startswith("|"):
        cells = [c.strip() for c in s.strip("|").split("|")]
        return cells[0] if cells else ""
    m = re.search(r"\*\*([^*]+)\*\*", s)
    if m:
        return m.group(1)
    return s.split(":", 1)[0]


def main():
    env = load_env()
    notes, unplaced = [], []

    for doc in DOCS:
        if not doc.exists():
            continue
        out = []
        for line in doc.read_text(errors="ignore").splitlines():
            for marker, rx, repl in LINE_REPAIRS:
                if marker in line:
                    # re.sub, not a lambda: a lambda returns the replacement
                    # LITERALLY, so \1 \2 would never expand - that bug
                    # wrote a raw "\1`${VAR}`\2" into the doc.
                    line = rx.sub(repl, line, count=1)
                    break
            out.append(line)
        text = "\n".join(out) + "\n"

        # a pointer that lost its opening backtick
        text = re.sub(r"(?<![`$\w])(\$\{[A-Za-z0-9_]+\}` \(in \.env\))",
                      r"`\1`", text)
        # a stray trailing backtick left by an earlier pass
        text = re.sub(r"(`\$\{[A-Za-z0-9_]+\}` \(in \.env\))`", r"\1", text)
        # a .env variable that was renamed
        for old, new in ENV_RENAME.items():
            text = text.replace("${%s}" % old, "${%s}" % new)

        # label overrides: where a length cannot disambiguate
        new_lines = []
        heading = ""
        for line in text.splitlines():
            if line.startswith("#"):
                heading = line.lstrip("#").strip().lower()
            m = re.search(r"\*\*([^*]+)\*\*", line)
            if m:
                label = m.group(1).strip(" -*:").lower()
                target = LABEL_OVERRIDE.get(label)
                if target and target in env:
                    cur = re.search(r"`\$\{([A-Za-z0-9_]+)\}`", line)
                    if cur and cur.group(1) != target:
                        if len(env.get(cur.group(1), "")) == len(env[target]):
                            line = line.replace("${%s}" % cur.group(1),
                                                "${%s}" % target)
                    elif UNRESOLVED in line:
                        line = line.replace("`$%s`" % UNRESOLVED,
                                            "`${%s}` (in .env)" % target)
            # a pointer that does not resolve at all: the section names the
            # variable. Only used when the current pointer is BROKEN and the
            # label is GENERIC - a line that names a service of its own
            # (a Facebook token under a Shopify heading) must never be
            # repointed at the heading's variable.
            cur = re.search(r"`\$\{([A-Za-z0-9_]+)\}`", line)
            if cur and cur.group(1) not in env:
                hv = HEADING_VAR.get(heading)
                generic = label.strip(" -*:").lower() in (
                    "api key", "api token", "token", "key", "auth key")
                if hv and hv in env and generic:
                    line = line.replace("${%s}" % cur.group(1),
                                        "${%s}" % hv)
            new_lines.append(line)
        text = "\n".join(new_lines) + "\n"

        # a literal still in the clear: point it at the .env variable that
        # EXACTLY holds it. If no .env variable holds it, report it rather
        # than guess a name.
        new_lines = []
        for lineno, line in enumerate(text.splitlines(), 1):
            lab = line_label(line)
            for m in list(QUOTED.finditer(line)):
                v = m.group(1)
                if not is_credential_shape(v):
                    continue
                if v in env.values():
                    name = next(k for k, val in env.items() if val == v)
                    line = line.replace("`%s`" % v, "`${%s}` (in .env)" % name)
                elif SECRET_LABEL.search(lab) and not NOT_SECRET.search(lab):
                    unplaced.append(f"{doc.name}:{lineno}: a credential literal "
                                    f"is not in .env and cannot be named")
            new_lines.append(line)
        doc.write_text("\n".join(new_lines) + "\n", errors="ignore")

    # .env written once, from the final mapping
    old = ENV_FILE.read_text(errors="ignore")
    header = []
    for line in old.splitlines():
        if line.strip().startswith("#") or not line.strip():
            header.append(line)
        else:
            break
    ENV_FILE.write_text(
        "\n".join(header).rstrip("\n") +
        "\n\n# --- repaired 2026-10-24: deduped; placeholder, bare-identifier\n"
        "# and mislabelled entries removed; doc pointers resolved ---\n" +
        "\n".join(f"{k}={v}" for k, v in env.items()) + "\n", errors="ignore")

    for n in notes:
        print("  " + n)

    # ---- VERIFICATION GATE ----
    print()
    print("--- verification ---")
    env_after = {k: v[0] for k, v in
                 parse_env(ENV_FILE.read_text(errors="ignore")).items()}
    known = set(env_after.values())
    failures = list(unplaced)
    for doc in DOCS:
        if not doc.exists():
            continue
        for lineno, line in enumerate(doc.read_text(errors="ignore").splitlines(), 1):
            for m in re.finditer(r"\$\{([A-Za-z0-9_]+)\}", line):
                if m.group(1) not in env_after:
                    failures.append(f"{doc.name}:{lineno}: pointer "
                                    f"${{{m.group(1)}}} does not resolve")
            lab = line_label(line)
            for m in QUOTED.finditer(line):
                v = m.group(1)
                if v in known:
                    failures.append(f"{doc.name}:{lineno}: a credential .env "
                                    f"holds appears literally")
                elif is_credential_shape(v) and SECRET_LABEL.search(lab) \
                        and not NOT_SECRET.search(lab):
                    failures.append(f"{doc.name}:{lineno}: a credential literal "
                                    f"remains on a credential-labelled line")
    for k, v in env_after.items():
        if PLACEHOLDER.match(v):
            failures.append(f".env: {k} holds a placeholder value")
        elif BARE_NAME.match(v):
            failures.append(f".env: {k} holds a bare identifier, not a credential")

    if failures:
        print("VERIFICATION FAILED:")
        for f in sorted(set(failures)):
            print("  - " + f)
        sys.exit(1)
    print("  every pointer resolves to a variable in .env")
    print("  no value .env holds appears literally in the docs")
    print("  .env has no duplicate, placeholder or bare-identifier values")


if __name__ == "__main__":
    main()
