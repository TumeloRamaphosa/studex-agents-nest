#!/usr/bin/env python3
"""Restore the ORIGINAL key order of memory/heartbeat-state.json.

The file was written by several different writers over time: some dumped with
sort_keys=True, some did not, so the on-disk order is MIXED (top level mostly
alphabetical, some nested objects not).

A plain json.dump(..., sort_keys=True) rewrite therefore reorders the whole
file and buries a one-key change in ~600 changed lines. This rebuilds the
original order instead:
  * a key that HEAD already had  -> keeps HEAD's position (and HEAD's nested
    order, recursively)
  * a key added since HEAD        -> keeps its current position, appended
    after the inherited ones

The VALUES are never touched. The script asserts the rebuilt file parses to
exactly the same data it read, then writes it back with the original
indent=1 / no-sort formatting.

Usage: python3 ops/restore-state-key-order.py
"""
import json
import subprocess
import sys

P = "memory/heartbeat-state.json"


def reorder(cur, head):
    if isinstance(cur, dict):
        if isinstance(head, dict):
            out = {}
            for k in head:                      # inherited keys, HEAD's order
                if k in cur:
                    out[k] = reorder(cur[k], head[k])
            for k in cur:                       # keys added since HEAD
                if k not in out:
                    out[k] = cur[k]
            return out
        return cur
    if isinstance(cur, list):
        # A LIST of records: the element order never changed, only the key
        # order INSIDE each element. Match elements by position, and by
        # messageId when both sides carry one, so an appended record does not
        # shift the mapping.
        if not isinstance(head, list):
            return cur
        head_by_id = {e["messageId"]: e for e in head
                      if isinstance(e, dict) and "messageId" in e}
        out = []
        used = set()
        for i, e in enumerate(cur):
            h = None
            if isinstance(e, dict) and "messageId" in e:
                h = head_by_id.get(e["messageId"])
            if h is None and i < len(head):
                cand = head[i]
                if isinstance(cand, dict) and isinstance(e, dict) and \
                        ("messageId" in cand) == ("messageId" in e):
                    h = cand
            if h is not None and id(h) in used:
                h = None
            if h is not None:
                used.add(id(h))
                out.append(reorder(e, h))
            else:
                out.append(e)
        return out
    return cur


def main():
    raw = open(P, encoding="utf8").read()
    cur = json.loads(raw)
    head = json.loads(subprocess.run(
        ["git", "show", "HEAD:" + P], capture_output=True, text=True, check=True).stdout)

    rebuilt = reorder(cur, head)
    assert rebuilt == cur, "reorder changed the DATA - aborting"

    text = json.dumps(rebuilt, indent=1, sort_keys=False)
    if raw.endswith("\n"):
        text += "\n"
    open(P, "w", encoding="utf8").write(text)

    after = json.loads(open(P, encoding="utf8").read())
    assert after == cur, "write-back changed the DATA - aborting"
    print("OK: original key order restored, data identical, %d top-level keys" % len(after))
    return 0


if __name__ == "__main__":
    sys.exit(main())
