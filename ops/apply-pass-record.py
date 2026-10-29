#!/usr/bin/env python3
"""Apply one canonical-heartbeat pass record to memory/heartbeat-state.json.

KEY ORDER IS PRESERVED. The state file has been written by several writers
over time and its on-disk order is MIXED (not fully sorted), so a plain
sort_keys=True rewrite would reorder ~600 lines and bury a one-key change in
the noise. This loads the file (dict preserves insertion order), edits only
the target keys, and dumps with sort_keys=False.

A new pass key is APPENDED at the end of the top level, which is where every
previous pass_ key already sits. `last_heartbeat_pass` is updated IN PLACE, so
it keeps its existing position.

Asserts the write-back parses and that only the two intended keys changed.

Usage: python3 ops/apply-pass-record.py <pass_key> <pass_record.json> <last_heartbeat_pass>
"""
import collections
import json
import subprocess
import sys

P = "memory/heartbeat-state.json"


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    pass_key, record_path, last_hb = sys.argv[1], sys.argv[2], sys.argv[3]

    raw = open(P, encoding="utf8").read()
    before = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    record = json.loads(open(record_path, encoding="utf8").read(),
                         object_pairs_hook=collections.OrderedDict)

    if pass_key in before:
        print("ABORT: %s already exists - refusing to overwrite a pass record" % pass_key)
        return 1

    after = collections.OrderedDict(before)
    after["last_heartbeat_pass"] = last_hb
    after[pass_key] = record

    # Only the two intended keys may differ.
    changed = [k for k in set(before) | set(after)
               if before.get(k) != after.get(k)]
    expected = {pass_key, "last_heartbeat_pass"}
    if set(changed) != expected:
        print("ABORT: unexpected keys changed: %s" % sorted(set(changed) - expected))
        return 1

    text = json.dumps(after, indent=1, sort_keys=False)
    if raw.endswith("\n"):
        text += "\n"
    open(P, "w", encoding="utf8").write(text)

    reread = json.loads(open(P, encoding="utf8").read())
    assert reread == after, "write-back changed the DATA - aborting"
    print("OK: wrote %s, updated last_heartbeat_pass=%s, %d top-level keys"
          % (pass_key, last_hb, len(after)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
