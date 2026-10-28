#!/usr/bin/env python3
"""Repair studex-os/n8n-workflows/NALEDI-Content-Pipeline.json.

The file has been invalid JSON since it was first committed (2026-07-25), so
n8n could never import it. The defect is in the "messages" parameter, whose
value is a JSON array embedded as a STRING inside the outer JSON - two
layers, and the author mixed them:

  layer 0 - the file itself (JSON)
  layer 1 - the string value; n8n's "defineBelow" message array parses this,
            so layer 1 must be valid JSON on its own

The file wrote layer-1's escapes at layer-0 depth, so layer 1's content
string closed early and layer 0 broke too. Rather than hand-editing escapes
(the mistake that broke a file earlier tonight), this script rebuilds the
value from a properly specified layer-1 text with json.dumps, so both
layers are correct BY CONSTRUCTION.

Validation gate - nothing is written unless ALL of these hold:
  1. the repaired file parses as JSON (layer 0)
  2. the messages value parses as JSON on its own (layer 1)
  3. layer 1's content carries the prompt text and the example schema
  4. exactly ONE line of the file changes
  5. every OTHER value in the file is unchanged
"""
import json
import pathlib
import sys

PATH = pathlib.Path("studex-os/n8n-workflows/NALEDI-Content-Pipeline.json")

# The intended layer-1 TEXT. In the Python source below, "\\n" is a literal
# backslash+n (layer 1's own JSON escape for a newline) and '\\"' is a
# literal backslash+quote (layer 1's escape for a quote inside the content
# string). json.dumps does the layer-0 escaping.
LAYER1_TEXT = (
    '[{"role":"user","content":'
    '"Write a social media caption for this StudEx Meat content:'
    '\\n\\nPlatform: {{ $json.platform }}'
    '\\nContent Type: {{ $json.content_type }}'
    '\\nProduct/Topic: {{ $json.topic }}'
    '\\nTheme: {{ $json.theme }}'
    '\\nCall to Action: {{ $json.cta }}'
    '\\n\\nFormat your response ONLY as valid JSON like this:'
    '\\n{\\"caption\\": \\"your caption text here\\", '
    '\\"hashtags\\": \\"#tag1 #tag2 #tag3\\"}"}]'
)

VALUE_MARK = '"value": "'


def parseable_variant(raw: str) -> str:
    """Return the file with its stray bare quote escaped, so it parses.

    The author intended that quote as an escaped quote; the escape was
    simply lost. Recovering a parseable view lets the repair be made
    against a PARSED OBJECT rather than against quote offsets.
    """
    text = raw
    for _ in range(8):
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError as e:
            # Escape the last bare quote before the error position.
            seg = text[:e.pos]
            idx = -1
            for i in range(len(seg) - 1, -1, -1):
                if seg[i] == '"' and (i == 0 or seg[i - 1] != "\\"):
                    idx = i
                    break
            if idx < 0:
                raise SystemExit(f"NO REPAIR CANDIDATE: {e}")
            text = text[:idx] + '\\"' + text[idx + 1:]
    raise SystemExit("COULD NOT RECOVER A PARSEABLE VARIANT")


def find_messages_param(obj):
    """Find every parameter named "messages", wherever it is nested.

    The payload appears under bodyParameters as well as parameters, and a
    lookup that only checked one of them silently compared a FIXED value
    against the BROKEN one - which read as "another value changed".
    """
    found = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("name") == "messages" and "value" in node:
                found.append(node)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(obj)
    return found


def sentinelise(obj):
    """Copy of obj with every messages value masked, for comparison."""
    clone = json.loads(json.dumps(obj))
    for p in find_messages_param(clone):
        p["value"] = "<SENTINEL>"
    return clone


def main() -> int:
    raw = PATH.read_text(encoding="utf-8")
    original_lines = raw.split("\n")

    before = json.loads(parseable_variant(raw))

    # Gate 1+2: both layers must parse.
    try:
        layer1 = json.loads(LAYER1_TEXT)
    except Exception as e:  # noqa: BLE001
        print(f"LAYER 1 INVALID: {e}", file=sys.stderr)
        return 1

    # Gate 3: content must carry the prompt and the example schema.
    content = layer1[0]["content"]
    for needle in ("Write a social media caption", "{{ $json.platform }}",
                   "Format your response ONLY as valid JSON", "hashtags",
                   "#tag1 #tag2 #tag3"):
        if needle not in content:
            print(f"CONTENT MISSING {needle!r}", file=sys.stderr)
            return 1

    # Rebuild the one line. The parameter object is
    #   { "name": "messages", "value": <literal> }
    # and everything from '"value": "' to the end of that line is replaced.
    target = None
    for i, line in enumerate(original_lines):
        if '"name": "messages"' in line:
            target = i
            break
    if target is None:
        print("MESSAGES LINE NOT FOUND", file=sys.stderr)
        return 1

    line = original_lines[target]
    head = line[:line.index(VALUE_MARK) + len(VALUE_MARK)]
    new_line = head + json.dumps(LAYER1_TEXT)[1:-1] + '" }'

    new_lines = list(original_lines)
    new_lines[target] = new_line

    # Gate 4: exactly one line changes.
    if len(new_lines) != len(original_lines):
        print("LINE COUNT CHANGED", file=sys.stderr)
        return 1
    changed = [i for i, (a, b) in enumerate(zip(original_lines, new_lines)) if a != b]
    if len(changed) != 1:
        print(f"EXPECTED 1 CHANGED LINE, GOT {changed}", file=sys.stderr)
        return 1

    new_raw = "\n".join(new_lines)

    # Gate 5: every other value unchanged.
    try:
        after = json.loads(new_raw)
    except Exception as e:  # noqa: BLE001
        print(f"RESULT INVALID: {e}", file=sys.stderr)
        return 1
    if sentinelise(before) != sentinelise(after):
        print("GATE 5 FAILED: another value in the file changed", file=sys.stderr)
        return 1

    # Final gates: layer 0 parses and layer 1 parses in the written file.
    final = json.loads(new_raw)
    for p in find_messages_param(final):
        try:
            json.loads(p["value"])
        except Exception as e:  # noqa: BLE001
            print(f"LAYER 1 INVALID IN FINAL FILE: {e}", file=sys.stderr)
            return 1

    PATH.write_text(new_raw, encoding="utf-8")
    print(f"repaired line {changed[0] + 1}")
    print("layer 0 parses: yes")
    print("layer 1 parses: yes")
    print("other values unchanged: yes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
