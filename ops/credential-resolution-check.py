#!/usr/bin/env python3
"""
Does every credential reference in tracked source ACTUALLY RESOLVE?

THE BUG THIS GUARDS
-------------------
On 2026-10-23 a credential scrub (`scripts/scrub-tracked-credentials.py`) replaced
live credential literals with the text `${VAR_NAME}`. That is a SHELL
interpolation idiom. The scrub applied it blindly, so in every other language it
produced a literal string that never resolves:

  * Python  - `KEY = '${VAR}'` is a plain string. Python does not expand `${}`.
              In an f-string it is even worse: `f"...${VAR}"` raises
              **NameError at import time** - the script dies before it runs.
  * JS/TS   - `'${VAR}'` in single/double quotes is a literal string. Only a
              backtick template literal expands.
  * shell   - `"${VAR}"` expands, but NOT inside a single-quoted string and NOT
              inside a QUOTED heredoc (`<< 'EOF'`). Inside either it is written
              out literally.

The failure mode this creates is the repo's own documented trap: **a
placeholder used as a credential returns 401/403, and the checker reports
"provider DOWN" / "0 messages" when the provider is perfectly fine.** A false
all-clear is worse than a loud failure, because it is trusted.

THE RULE
--------
A credential reference in tracked source must resolve to a real value in the
language it is written in. This checker is LANGUAGE-AWARE: it knows that
`${...}` means different things in Python, JS and shell.

It also flags HARDCODED live-looking credentials in tracked source - the same
class the pre-commit guard catches, but for the whole tree rather than only
the staged subset (the guard only sees what you are about to commit; a
credential can already be sitting in a tracked file from an earlier commit).

THE SHELL PARSER IS PART OF THE CHECK
-------------------------------------
A checker's reader is part of the check. The first version of this file
mis-read shell in three ways, and each one produced a FALSE POSITIVE:

  1. Shell `#` comments were not treated as prose, so the *documentation* of
     the bug ("a quoted heredoc writes ${VAR} literally") was flagged as a bug.
  2. A heredoc marker mentioned inside a comment created a bogus heredoc range
     that ran to EOF, poisoning every line after it.
  3. A heredoc marker nested inside a double-quoted string was treated as a
     statement-level quoted heredoc. It is not: `run "cat > f << 'EOF' ... EOF"`
     sends a COMMAND whose body is double-quoted, so bash expands `${...}`
     locally before transmitting it.

Case 3 is not theoretical - `orchestrix/start-war.sh` uses exactly that form,
and this checker used to call its (correct) credential substitution a bug. The
rule "fix the reader, or the check is reading your assumptions back to you"
applies to a checker just as much as to a cron parser.

Exit 0 = clean. Exit 1 = unresolved references or hardcoded credentials found.

Usage: python3 ops/credential-resolution-check.py
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The root the checker scans. Overridable so the regression test can point
# it at a THROWAWAY sandbox. The reason this override exists: a sibling test
# once wrote its fixture into the LIVE outbound-drafts folder - real email
# drafts to real external partners - and an interrupted run left it there.
# The fix for that class of bug is never "clean up better"; it is never
# write there at all.
CHECK_ROOT = os.environ.get("CREDENTIAL_CHECK_ROOT") or ROOT

# Names that must never be a literal placeholder or a hardcoded value.
CRED_NAME = re.compile(
    r"\$\{([A-Z_][A-Z_0-9]*(?:KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)[A-Z_0-9]*)\}"
)

# Live-looking credential literals. Mirrors .githooks/pre-commit plus the
# shapes that repo-specific keys use.
LITERAL_PATTERNS = [
    (r"am_us_[A-Za-z0-9]{30,}", "AgentMail API key"),
    (r"sk-ant-[A-Za-z0-9_\-]{20,}", "Anthropic API key"),
    (r"sk-proj-[A-Za-z0-9_\-]{20,}", "OpenAI API key"),
    (r"cfat_[A-Za-z0-9_\-]{20,}", "Cloudflare API token"),
    (r"sk_live_[A-Za-z0-9]{20,}", "sk_live_ secret key"),
    (r"ghp_[A-Za-z0-9]{30,}", "GitHub PAT"),
    (r"xox[baprs]-[A-Za-z0-9-]{20,}", "Slack token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"LTAI[0-9A-Za-z]{12,}", "Alibaba access key id"),
    (r"pcsk_[A-Za-z0-9]{30,}", "Pinecone API key"),
    (r"prtapi_[A-Za-z0-9]{20,}", "Shopify Admin token"),
    (r"hyrve_ak_[A-Za-z0-9_]{20,}", "Hyvare API key"),
    (r"nvapi-[A-Za-z0-9_\-]{20,}", "NVIDIA API key"),
    (r"blt_[A-Za-z0-9]{20,}", "Blotato API key"),
    (r"rl_sk_[A-Za-z0-9_\-]{20,}", "MaxClaw/OpenClaw relay token"),
    (r"pplx-[A-Za-z0-9_\-]{20,}", "Perplexity API key"),
    (r"sk-ws-[A-Za-z0-9._\-]{20,}", "Alibaba MAAS key"),
    (r"sk_[0-9a-f]{32}", "ElevenLabs API key"),
    (r"MTUw[A-Za-z0-9]{20,}\.[A-Za-z0-9_.\-]{20,}", "Discord bot token"),
    (r"EAAS[A-Za-z0-9]{40,}", "Meta Graph API token"),
    (r"pk_\d{9}_[A-Za-z0-9]{20,}", "ClickUp API token"),
    (r"sk-r[A-Za-z0-9]{30,}", "Kimi/Moonshot API key"),
    (r"tskey-[A-Za-z0-9\-_]{20,}", "Tailscale auth key"),
    (r"AIza[A-Za-z0-9_\-]{30,}", "Google API key"),
    (r"glpat-[A-Za-z0-9_\-]{20,}", "GitLab PAT"),
    (r"fh_[0-9a-f]{40,}", "FeedHive API key"),
    (r"sso-key\s+[A-Za-z0-9_]{16,}:[A-Za-z0-9_]{16,}", "GoDaddy sso-key credential"),
]

# One combined pattern for every literal shape. Scanning the file ONCE with
# this is what keeps the check fast enough to run over the whole tree: 25
# separate regex passes per line over ~2,000 tracked files takes minutes, and
# a checker nobody runs is a checker nobody trusts.
LITERAL_COMBINED = re.compile(
    "|".join("(?P<g%d>%s)" % (i, pat) for i, (pat, _) in enumerate(LITERAL_PATTERNS))
)

# A bare 32-hex or 64-hex string is only a credential if it is ASSIGNED to a
# credential-named variable. Cloudflare R2 access key ids and Higgsfield keys
# are raw hex with no prefix, so shape alone cannot catch them - but the
# assignment can. A pattern that fires on non-credentials is a checker people
# learn to ignore, so the shape must be narrow.
HEX_ASSIGNED = re.compile(
    r"^\s*(?:export\s+)?[A-Z_][A-Z_0-9]*(?:KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL|PAT)"
    r"[A-Z_0-9]*\s*[:=]\s*[\"']?([0-9a-f]{32}|[0-9a-f]{64})[\"']?\s*$"
)

# An opaque mixed-case token (no recognisable prefix) assigned to a
# credential-named variable. Some providers issue keys with no prefix at
# all, so shape alone cannot catch them - the ASSIGNMENT can. Kept narrow:
# the variable name must say "credential" and the value must be long and
# mixed-case, which ordinary identifiers never are.
# A base64 credential whose value ends in "=". Blotato's key is one.
# Writing "${BLOTATO_API_KEY}=" against a stored value that ALREADY ends
# in "=" produces "...==" and the provider rejects it. The scrubber that
# caused this pasted a placeholder over the key body and left the
# trailing "=" behind, so the class of bug is easy to reintroduce.
#
# A credential reference immediately followed by "=" is only correct if
# the stored value does NOT already carry the padding. We cannot know
# that at scan time, so this is reported as a MANGLED REFERENCE for a
# human to confirm - it is the shape of the bug, not a proven instance.
PADDED_REF = re.compile(
    r"\$\{(BLOTATO_API_KEY|AGENTMAIL_API_KEY|[A-Z_]*BLOTATO[A-Z_]*)\}="
)

OPAQUE_ASSIGNED = re.compile(
    r"^\s*(?:export\s+)?[A-Z_][A-Z_0-9]*(?:KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL|PAT)"
    r"[A-Z_0-9]*\s*[:=]\s*[\"']?([A-Za-z0-9_\-]{32,64})[\"']?\s*$"
)

# A bare KEY / SEC pair. The pattern above needs a variable name of at least
# four characters, so `KEY = "..."` and `SEC = "..."` did not match it - which
# is exactly the shape GoDaddy's sso-key pair takes. The checker reported
# CLEAN while a live GoDaddy API key and its secret sat in four tracked
# scripts, published to the public remote.
# A rule that only covers what it scans is decoration.
BARE_PAIR_ASSIGNED = re.compile(
    r"^\s*(?:export\s+)?(?:KEY|SEC)(?:RET)?[A-Z_0-9]*\s*[:=]\s*"
    r"[\"']?([A-Za-z0-9_\-]{20,64})[\"']?\s*$"
)

# Vendored third-party trees and directories that are history/docs, not code.
# History is skipped deliberately: rewriting old session logs destroys the
# audit trail and the rotation, not the scrub, is what makes them safe.
# Only genuinely third-party trees and build artifacts are skipped. The
# skipped set used to include memory/, builds/, research/ and
# studex-obsidian-vault/ - ALL of which are OURS, and all of which turned
# out to contain 33 distinct LIVE credential values across 74 tracked
# files. The checker said CLEAN because it never looked there.
#
# A directory of notes is still tracked source. If it is in the public
# remote, it is published.
SKIP_DIRS = re.compile(
    r"^(\.git/|\.matrix-|node_modules/|Decepticon/|OpenJarvis/|gstack/|headroom/|"
    r"OBLITERATUS/|Agent-Reach/|OpenClawHomeAssistant/|core/|odysseus/|"
    r"\.archive/)"
)

# Files that legitimately discuss the patterns (docs about the bug, the guard).
# Files that legitimately discuss the patterns (docs about the bug, the
# guard, the test's own fixtures).
#
# This used to allow EVERY .md file. That is the same blind spot as the
# skip list: 74 tracked markdown files carried live credential values and
# the checker waved them all through. A markdown file is not a safe place
# for a key - it renders on GitHub.
#
# The only .md files allowed here are the ones that are documentation
# ABOUT this checker, which is checked by content rather than by suffix.
ALLOW = re.compile(
    r"(\.example$|^templates?/|^ops/test-credential-resolution\.py$"
    r"|^ops/credential-resolution-check\.py$)",
    re.I,
)

# A NARROW, SELF-DECLARED exemption - narrower than ALLOW on purpose.
#
# Some tools are DOC-POINTER EMITTERS: their job is to write the text
# `${VAR}` INTO a markdown file, so the pointer reaches a human who then
# looks the value up in .env. In their source, `${VAR}` is OUTPUT, not a
# reference - Python not expanding it is the design, not a bug.
#
# ALLOW is too broad for this: it skips the file ENTIRELY, including the
# HARDCODED-literal scan. A file that is allowed to carry live credential
# literals because it merely talks about them is exactly the blind spot
# this checker exists to close. So the exemption here is scoped to the
# ${VAR} RESOLUTION rule only, and the file must declare it in a comment:
#
#     # credential-resolution: doc-pointer-emitter
#
# The HARDCODED scan still runs over such a file in full. The regression
# test proves both halves: a marked emitter with ${VAR} is GREEN, and a
# marked emitter holding a live key is still RED.
RESOLUTION_EXEMPT_MARKER = "credential-resolution: doc-pointer-emitter"

# Obvious dummies - a checker that fires on a test fixture teaches people to
# ignore it.
#
# TWO tiers, and the distinction matters. A dummy match must be judged
# against the WHOLE matched credential, not against a fragment of it: a
# substring rule will dismiss a real key that merely happens to contain a
# dummy-looking run of characters. (This was caught by the regression test's
# own negative control, which is the only reason it is worth having.)
DUMMY_EXACT = re.compile(
    r"(AKIAIOSFODNN7EXA|sk-ant-api03-rea\w*|sk-proj-abc123de\w*|"
    r"ghp_abcdefghij12\w*|1234567890abcd|0123456789abcdef|"
    r"sk_live_\w{0,8}|blt_\w{0,8}|am_us_\w{0,8})",
    re.I,
)
# Word-shaped markers: unambiguous wherever they appear in a key.
DUMMY_SUBSTRING = re.compile(
    r"(xxx+|YOUR_|_YOUR_|REDACTED|placeholder|dummy|fake|test[-_]?key|"
    r"sk_xxxxxxxxx|random-secure-string|your-[a-z-]+-key|"
    r"NEED_[A-Z_]+|^change[_-]?this)",
    re.I,
)


def is_dummy(matched_text):
    """True when the matched credential is an obvious placeholder.

    Judged on the WHOLE match. A substring rule dismisses real credentials
    that merely contain a dummy-looking run.
    """
    if DUMMY_EXACT.fullmatch(matched_text):
        return True
    return bool(DUMMY_SUBSTRING.search(matched_text))


# Only text files can contain a credential reference. Reading 590 MB of
# tracked binaries (a 47 MB MP4, PDFs, PNGs) as text to look for an API key
# is what made this checker take minutes instead of seconds.
TEXT_EXT = {
    ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".py", ".sh", ".bash", ".zsh",
    ".json", ".jsonc", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env",
    ".ipynb", ".md", ".txt", ".html", ".htm", ".css", ".scss", ".xml", ".sql",
    ".rb", ".go", ".rs", ".java", ".kt", ".php", ".pl", ".lua", ".r", ".dart",
    ".ps1", ".bat", ".cmd", ".vue", ".svelte", ".astro", ".graphql", ".proto",
    ".properties", ".mk", ".cmake", ".gradle", ".tf", ".tfvars", ".hcl",
    ".service", ".desktop", ".gyp", ".nix", ".elm", ".clj", ".ex", ".exs",
    ".csv", ".tsv", ".log", ".gitignore", ".gitattributes", ".editorconfig",
    ".s3cfg", ".npmrc", ".dockerignore", ".eslintrc", ".prettierrc",
}
# Files with no extension that are still text.
TEXT_NO_EXT = {
    "Dockerfile", "Makefile", "Procfile", "LICENSE", "README", "CHANGELOG",
    "Caddyfile", "Brewfile", "Justfile", "Gemfile", "Rakefile", "Gemfile.lock",
    ".env", ".env.example", ".gitignore", ".dockerignore", ".npmrc",
}


def is_text_candidate(rel):
    """Cheap extension test - no file is opened to decide this."""
    name = os.path.basename(rel)
    if name in TEXT_NO_EXT or name.startswith(".env"):
        return True
    if name.startswith(".") and not os.path.splitext(name)[1]:
        return True
    return os.path.splitext(rel)[1].lower() in TEXT_EXT


def tracked_files():
    out = subprocess.run(
        ["git", "ls-files", "-z"],
        capture_output=True, text=True, check=True, cwd=CHECK_ROOT,
    ).stdout.split("\0")
    return [f for f in out if f.strip()]


# ── Shell reader ────────────────────────────────────────────────────────────
# Shell quoting is a small state machine, and getting it right is the whole
# job. The contexts we care about:
#
#   bare          unquoted text            -> ${VAR} EXPANDS
#   dq            inside "..."             -> ${VAR} EXPANDS
#   sq            inside '...'             -> ${VAR} is LITERAL
#   heredoc       body of a QUOTED heredoc -> ${VAR} is LITERAL
#   heredoc_exp   body of an unquoted here -> ${VAR} EXPANDS
#   comment       # ... to end of line     -> prose
#
# A heredoc whose `<<` appears INSIDE a double-quoted string is not a
# statement-level heredoc at all - the whole thing is one argument, and bash
# expands `${...}` inside it before the command is even transmitted.
#
def shell_line_segments(text):
    """Map each line number to [(col_start, col_end, context), ...]."""
    lines = text.splitlines()
    segs = {i: [] for i in range(1, len(lines) + 1)}
    in_sq = False
    in_dq = False
    pending = []          # list of (delimiter, quoted?) awaiting a body
    i = 0
    while i < len(lines):
        line = lines[i]
        lineno = i + 1
        n = len(line)

        # Inside a heredoc body: the whole line is body until the terminator.
        if pending:
            delim, quoted = pending[0]
            ctx = "heredoc" if quoted else "heredoc_exp"
            if line.strip() == delim:
                pending.pop(0)
                segs[lineno].append((0, n, "heredoc_end"))
            else:
                segs[lineno].append((0, n, ctx))
            i += 1
            continue

        col = 0
        while col < n:
            c = line[col]

            if in_sq:
                start = col
                while col < n:
                    if line[col] == "\\" and col + 1 < n and line[col + 1] == "'":
                        col += 2
                        continue
                    if line[col] == "'":
                        col += 1
                        break
                    col += 1
                segs[lineno].append((start, col, "sq"))
                in_sq = False
                continue

            if in_dq:
                start = col
                while col < n:
                    if line[col] == "\\" and col + 1 < n:
                        col += 2
                        continue
                    if line[col] == '"':
                        col += 1
                        break
                    col += 1
                segs[lineno].append((start, col, "dq"))
                in_dq = False
                continue

            # Unquoted context.
            if c == "\\" and col + 1 < n:
                segs[lineno].append((col, col + 2, "bare"))
                col += 2
                continue
            if c == "'":
                in_sq = True
                col += 1
                continue
            if c == '"':
                in_dq = True
                col += 1
                continue
            if c == "#" and (col == 0 or line[col - 1] in " \t"):
                segs[lineno].append((col, n, "comment"))
                col = n
                continue
            if c == "<" and line.startswith("<<", col):
                m = re.match(r"<<-?\s*(?:'([^']*)'|\"([^\"]*)\"|([A-Za-z_][A-Za-z_0-9]*))", line[col:])
                if m:
                    delim = m.group(1) or m.group(2) or m.group(3)
                    quoted = bool(m.group(1) or m.group(2))
                    pending.append((delim, quoted))
                    end = col + m.end()
                    segs[lineno].append((col, end, "bare"))
                    col = end
                    continue
            segs[lineno].append((col, col + 1, "bare"))
            col += 1
        i += 1
    return segs


def shell_context_at(segs, line_no, col):
    """The shell context of the character at (line_no, col)."""
    for start, end, ctx in segs.get(line_no, ()):
        if start <= col < end:
            return ctx
    return "bare"


def in_template_literal(line, quote_char):
    """True if the ${...} occurrence on this line sits inside a backtick template."""
    for m in CRED_NAME.finditer(line):
        before = line[: m.start()]
        if before.count("`") % 2 == 1:
            return True
    return False


def prose_line_numbers(path, text):
    """
    Line numbers that are PROSE (comments, docstrings, markdown) rather than code.

    A docstring that *describes* the placeholder bug is not a bug. Without this,
    the checker fires on the very files that document the problem, and a checker
    that cries wolf is a checker people learn to ignore.
    """
    ext = os.path.splitext(path)[1]
    prose = set()
    if ext == ".py":
        try:
            import ast
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    body = getattr(node, "body", None)
                    if not body:
                        continue
                    first = body[0]
                    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) \
                            and isinstance(first.value.value, str):
                        s = first.value.value
                        start = first.value.lineno
                        end = getattr(first.value, "end_lineno", start) or start
                        for ln in range(start, end + 1):
                            prose.add(ln)
        except SyntaxError:
            pass
        for i, line in enumerate(text.splitlines(), 1):
            s = line.strip()
            if s.startswith("#"):
                prose.add(i)
    elif ext in (".sh", ".bash", ""):
        # Shell comments are handled by the state machine, which knows that a
        # `#` only starts a comment at the start of a word.
        segs = shell_line_segments(text)
        for ln, seglist in segs.items():
            if any(ctx == "comment" for _, _, ctx in seglist):
                prose.add(ln)
    elif ext in (".md", ".markdown"):
        # Markdown is DOCUMENTATION. A ${VAR} reference shown in prose or in
        # a fenced example is an EXPLANATION - it is how the runbook tells
        # the reader the correct form. It is not a credential that will be
        # sent to a provider.
        #
        # Before this branch existed, .md fell through to the JS/TS
        # comment stripper, so a markdown file documenting the mangled
        # shape was reported as a live reference. A checker that fires on
        # the very documents that explain the problem is a checker people
        # learn to ignore.
        #
        # NOTE: the HARDCODED-literal check is NOT allowed to rely on this
        # classification. An earlier version of this file carried a comment
        # asserting "the HARDCODED check is unaffected: it judges the
        # VALUE, not the context, so a live key inside a fenced block is
        # still caught". THAT COMMENT WAS FALSE, and a negative control
        # proved it: a synthetic blt_ key inside a ``` fence in a tracked
        # .md file was reported CLEAN, exit 0.
        #
        # The prose set is a CONTEXT hint. It is used to DOWNGRADE a
        # heuristic (a generic high-entropy/assigned value that only matters
        # in code) and to suppress the ${VAR} RESOLUTION check in
        # documentation. It must NEVER suppress a match of an exact,
        # provider-specific credential PATTERN - a live key is a live key
        # whether it sits in prose, in a fenced code block, in a table, in
        # YAML front matter, or in an inline code span.
        in_fence = False
        for i, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                prose.add(i)
                continue
            if in_fence:
                prose.add(i)
                continue
            # An inline code span showing a credential shape is a display,
            # not a use.
            if re.search(r"`[^`]*\$\{[^}]+\}[^`]*`", line):
                prose.add(i)
    else:
        # JS/TS: strip // and /* */ comment regions.
        in_block = False
        for i, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if in_block:
                prose.add(i)
                if "*/" in stripped:
                    in_block = False
                continue
            if stripped.startswith("/*"):
                prose.add(i)
                if "*/" not in stripped:
                    in_block = True
                continue
            if stripped.startswith("//") or stripped.startswith("*"):
                prose.add(i)
    return prose


def check():
    issues = []
    scanned = 0
    for rel in tracked_files():
        if SKIP_DIRS.search(rel) or ALLOW.search(rel):
            continue
        path = os.path.join(CHECK_ROOT, rel)
        if not os.path.isfile(path):
            continue
        if not is_text_candidate(rel):
            continue
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        # The prefilter only gates the ${VAR} RESOLUTION check - it is an
        # optimisation, and it is safe there because a credential reference
        # always names a credential-ish word.
        #
        # It must NOT gate the HARDCODED check. A file that holds a live key
        # does not have to mention API_KEY or TOKEN anywhere: the regression
        # test's own negative control caught exactly that, by writing a
        # hardcoded key into a file whose only other content was
        # `const key = '...'`. The old prefilter skipped the file and the
        # checker returned GREEN on a file containing a live credential.
        #
        # A checker that only looks where it expects to find the problem is
        # a checker that reports CLEAN on the problem.
        mentions_credential_word = (
            "API_KEY" in text or "TOKEN" in text or "SECRET" in text
            or "PASSWORD" in text or "CREDENTIAL" in text
        )
        # Narrow exemption: the ${VAR} RESOLUTION rule only. The HARDCODED
        # scan below still runs over this file in full, so a marked emitter
        # that carries a live key is still RED.
        resolution_exempt = RESOLUTION_EXEMPT_MARKER in text
        scanned += 1
        lines = text.splitlines()
        ext = os.path.splitext(rel)[1]
        is_shell = ext in (".sh", ".bash", "")
        segs = shell_line_segments(text) if is_shell else {}
        prose = prose_line_numbers(rel, text)

        for i, line in enumerate(lines, 1):
            is_prose = i in prose
            for m in (() if (is_prose or not mentions_credential_word
                             or resolution_exempt)
                      else CRED_NAME.finditer(line)):
                name = m.group(1)
                resolved = True
                why = ""
                if ext == ".py":
                    # Python never expands ${}. In an f-string it raises NameError.
                    resolved = False
                    why = "python does not expand ${} - this is a literal string"
                elif ext in (".js", ".ts", ".mjs", ".cjs", ".jsx", ".tsx"):
                    if not in_template_literal(line, "`"):
                        resolved = False
                        why = "JS only expands ${} inside a backtick template literal"
                elif is_shell:
                    ctx = shell_context_at(segs, i, m.start())
                    if ctx == "sq":
                        resolved = False
                        why = "inside a single-quoted string - ${} is not expanded"
                    elif ctx == "heredoc":
                        resolved = False
                        why = "inside a quoted heredoc (<< 'EOF') - ${} is not expanded"
                if not resolved:
                    issues.append(
                        f"  {rel}:{i}  UNRESOLVED ${{{name}}}  {why}"
                    )

            hm = None if is_prose else HEX_ASSIGNED.match(line)
            if hm and not is_dummy(hm.group(1)):
                issues.append(
                    f"  {rel}:{i}  HARDCODED raw hex credential  -> {hm.group(1)[:12]}..."
                )

            # A provider key with no recognisable prefix, assigned to a
            # credential-named variable. HEX_ASSIGNED only sees lowercase
            # hex; some issuers hand out mixed-case opaque tokens, and
            # those have no shape for the pattern list to match.
            om = None if is_prose else OPAQUE_ASSIGNED.match(line)
            if om and not is_dummy(om.group(1)):
                issues.append(
                    f"  {rel}:{i}  HARDCODED opaque credential  -> {om.group(1)[:12]}..."
                )

            # A bare KEY = / SEC = pair - GoDaddy's sso-key shape. The
            # variable name is too short for the pattern above to see it.
            bm = None if is_prose else BARE_PAIR_ASSIGNED.match(line)
            if bm and not is_dummy(bm.group(1)):
                issues.append(
                    f"  {rel}:{i}  HARDCODED bare KEY/SEC credential  -> "
                    f"{bm.group(1)[:12]}..."
                )

            # A credential reference with a trailing "=" glued to it. If
            # the stored value already ends in "=" (base64 padding) the
            # result is a doubled "=" and the provider rejects it.
            pm = None if is_prose else PADDED_REF.search(line)
            if pm:
                issues.append(
                    f"  {rel}:{i}  MANGLED credential reference  -> "
                    f"{{{pm.group(1)}}}="
                )

        # Literal credentials: ONE pass over the whole file. This runs on
        # every tracked file, not only on files that mention a credential
        # word, because a file holding a live key need not name it.
        for m in LITERAL_COMBINED.finditer(text):
            matched = m.group(0)
            if is_dummy(matched):
                continue
            label = "credential"
            for gi, (pat, lbl) in enumerate(LITERAL_PATTERNS):
                if m.group("g%d" % gi):
                    label = lbl
                    break
            lineno = text.count("\n", 0, m.start()) + 1
            # A provider-specific credential PATTERN is never suppressed by
            # the prose/fence classification. That classification is a
            # CONTEXT hint for the ${VAR} resolution check and for the
            # generic heuristics (assigned hex / assigned opaque value),
            # where "this is documentation" legitimately downgrades a
            # match. It is NOT a licence to ignore a literal that matches a
            # provider's exact key shape - a live key in a fenced code
            # block in a tracked .md file is a live key, and the remote is
            # PUBLIC.
            #
            # A negative control proved the previous behaviour was wrong:
            # a synthetic blt_ key inside a ``` fence was reported CLEAN.
            issues.append(
                f"  {rel}:{lineno}  HARDCODED {label}  -> {matched[:18]}..."
            )
    return scanned, issues


def main():
    scanned, issues = check()
    print("=" * 72)
    print("CREDENTIAL RESOLUTION CHECK (language-aware)")
    print("=" * 72)
    if issues:
        print(f"\n{len(issues)} issue(s) in tracked source:\n")
        for i in issues:
            print(i)
        print()
        print("A ${VAR} reference must be a form the host language actually")
        print("expands, or it must be resolved in code (os.environ / process.env")
        print("/ a .env loader). A hardcoded credential must not be in tracked")
        print("source at all - the remote is PUBLIC.")
        print()
        # 🔑 The runner reads this line to report the verdict. Without it the
        # runner falls back to the last prose line, which is a sentence about
        # credential syntax, not a verdict.
        print("VERDICT: %d issue(s) in tracked source" % len(issues))
        return 1
    if scanned == 0:
        print()
        print("VERDICT: BROKEN - 0 tracked files were scanned, so this scan is VACUOUS")
        print("The repository has nothing tracked (no commits?), so 'no credential")
        print("found' proves nothing at all. Create a baseline commit and re-run.")
        print("=" * 72)
        return 1
    print(f"  [ OK ] credential resolution   CLEAN   {scanned} credential-bearing tracked file(s) scanned")
    print("VERDICT: CLEAN - %d credential-bearing tracked file(s) scanned" % scanned)
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
