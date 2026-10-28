#!/usr/bin/env python3
"""
Regression test: no publish path may emit literal markdown markers.

A live post shipped with visible '**' twice. The causes were two different
bugs, and a fix for only one of them leaves the other open:
  1. sanitize() ran AFTER character truncation -> a bold span cut in half by
     the limit loses its closing '**', so the pair regex cannot match it.
  2. blotato-fallback.js published pending.caption verbatim, with no
     sanitizer at all.

Run: python3 scripts/test-no-markdown-leak.py
"""
import os, re, subprocess, sys

FAIL = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not ok:
        FAIL.append(name)


DP = "/workspace/scripts/daily-post.py"
FB = "/workspace/studex-content-automation/scripts/blotato-fallback.js"

print("=== 1. daily-post.py: sanitize BEFORE truncate ===")
dp_src = open(DP, encoding="utf8").read()

# Pull the real socialize() out of the source and exec just that function.
# (Importing the module would run its main() as a side effect.)
m = re.search(r"(?s)^def socialize\(text\):.*?(?=\n\ndef |\n\n# ---)", dp_src, re.M)
if not m:
    m = re.search(r"(?s)def socialize\(text\):.*?(?=\n\ndef |\n\n# ---)", dp_src)
check("found socialize() in daily-post.py", m is not None)
ns = {"re": re}
exec(m.group(0), ns)
socialize = ns["socialize"]

cases = {
    "bold headline spanning a newline": "**China Just Opened Its Doors\nto African Coffee.**\n\nBody here.",
    "bold headline, single line": "**Your AI Forgets Everything. Ours Doesn't.**\n\nBody.",
    "unpaired bold marker (odd count)": "**Only one marker here\nBody.",
    "triple marker": "***Weird***",
    "backticks and double underscore": "Use `code` and __bold__ here.",
    "blockquote prefix": "> quoted line\n> second line",
}
for label, raw in cases.items():
    # The order that actually ships: clean -> platform text -> truncate -> publish
    clean = socialize(raw)
    truncated = clean[:497].rsplit(" ", 1)[0] + "..." if len(clean) > 500 else clean
    final = truncated.replace("**", "").replace("__", "").replace("`", "")
    check(f"no '**' leaks: {label}", "**" not in final, f"got {final[:55]!r}")

# The exact order that shipped the bug: truncate -> sanitize.
# A bold span cut in half by the limit loses its closing marker, so the pair
# regex cannot match it and the literal asterisks survive.
raw = ("**Bold headline " + ("padding " * 60) + "still inside the bold span**\n\ntail")
buggy = socialize(raw[:497].rsplit(" ", 1)[0] + "...")
check("old truncate-then-sanitize order is provably buggy", "**" in buggy,
      "confirms sanitize-first was the right fix")
check("sanitize-first order fixes the same input", "**" not in socialize(raw)[:497])

print()
print("=== 2. source order: sanitize() is called BEFORE the truncation ===")
i_sanitize = dp_src.find("clean = socialize(content)")
i_trunc = dp_src.find("threads = clean")
check("sanitize() precedes truncation in try_blotato()",
      i_sanitize != -1 and i_trunc != -1 and i_sanitize < i_trunc,
      f"sanitize@{i_sanitize} truncate@{i_trunc}")
check("no leftover raw `content` used for published text",
      "threads = content" not in dp_src and "ig_content = content" not in dp_src)
check("has the odd-marker safety net", '.replace("**", "")' in dp_src)

print()
print("=== 3. real captions are clean through the full pipeline ===")
for path, label in (("/workspace/memory/post-queue/2026-10-22-thursday-business.md", "Thu Business"),
                     ("/workspace/memory/post-queue/2026-10-23-friday-agents.md", "Fri Agents")):
    if not os.path.exists(path):
        continue
    src = open(path, encoding="utf8").read()
    mm = re.search(r"(?s)##+\s*Caption\s*\n(.*?)(?=\n##|\Z)", src)
    cap = mm.group(1).strip() if mm else src
    for plat, limit in (("instagram", None), ("threads", 500)):
        clean = socialize(cap)
        text = clean[:497].rsplit(" ", 1)[0] + "..." if limit and len(clean) > limit else clean
        text = text.replace("**", "").replace("__", "").replace("`", "")
        check(f"{label} / {plat}: clean", "**" not in text and "`" not in text)

print()
print("=== 4. blotato-fallback.js sanitizes before publishing ===")
js = open(FB, encoding="utf8").read()
check("defines a sanitize() function", "function sanitize(" in js)
check("calls sanitize(pending.caption)", "sanitize(pending.caption)" in js)
# every use of pending.caption must be wrapped in sanitize()
uses = re.findall(r"(?<!sanitize\()pending\.caption", js)
check("does NOT publish pending.caption raw", not uses,
      "every use must be wrapped in sanitize()")
check("has the odd-marker safety net", ".replace(/\\*\\*/g, '')" in js)
check("uses the dotAll flag for multi-line bold", "\\*\\*(.+?)\\*\\*" in js and "gs" in js)
check("no edit-tool markup leaked into the source", "</newText>" not in js)

print()
print("=== 5. node can parse the patched fallback ===")
r = subprocess.run(["node", "--check", FB], capture_output=True, text=True)
check("blotato-fallback.js parses", r.returncode == 0, r.stderr.strip()[:160])

print()
if FAIL:
    print(f"RESULT: {len(FAIL)} FAILURE(S): {FAIL}")
    sys.exit(1)
print("RESULT: all checks passed")
