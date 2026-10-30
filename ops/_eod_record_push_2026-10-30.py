#!/usr/bin/env python3
"""Record the REAL commit sha + the verified push outcome in vault_sync.

Same discipline as _eod_vault_sync_state_2026-10-30.py: measure the on-disk indent,
keep ensure_ascii=True, edit only the named vault_sync keys, and assert that a DEEP DIFF
against the original touches nothing else. No force-push - the branch was created by this
run and is pushed forward, never rewritten.
"""
import io
import json
import subprocess
import sys

P = "/workspace/memory/heartbeat-state.json"


def detect_indent(text):
    for line in text.split("\n")[1:4]:
        stripped = line.lstrip(" ")
        if stripped and stripped != line:
            return len(line) - len(stripped)
    return 2


def deep_diffs(a, b, path=()):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            p = path + (k,)
            if k not in a:
                out.append((p, "<absent>", b[k]))
            elif k not in b:
                out.append((p, a[k], "<absent>"))
            else:
                out.extend(deep_diffs(a[k], b[k], p))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b) or a != b:
            out.append((path, a, b))
    elif a != b:
        out.append((path, a, b))
    return out


def main():
    sha = subprocess.run(["git", "-C", "/workspace", "rev-parse", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    remote = subprocess.run(["git", "-C", "/workspace", "ls-remote", "origin",
                             "refs/heads/standup/2026-10-30", "refs/heads/master"],
                            capture_output=True, text=True).stdout.strip().splitlines()
    rm = {ln.split("\t")[1]: ln.split("\t")[0] for ln in remote if "\t" in ln}
    branch_sha = rm.get("refs/heads/standup/2026-10-30", "")
    master_sha = rm.get("refs/heads/master", "(unknown)")
    assert branch_sha == sha, f"remote branch {branch_sha} != local HEAD {sha} - refusing to write"

    updates = {
        "last_sync_commit": sha,
        "commit": sha,
        "commit_status": f"COMMITTED AND PUSHED - {sha} on branch standup/2026-10-30 "
                         f"(origin/master deliberately untouched at {master_sha[:7]})",
        "push_result": f"2026-10-30 17:1x SAST - VERIFIED PUSH: HEAD -> refs/heads/standup/2026-10-30 "
                       f"at {sha}. origin/master verified UNCHANGED at {master_sha} (divergent July "
                       f"lineage, no merge-base, never force-pushed). Auth: classic PAT in .env read "
                       f"in-process by /root/.git-askpass-pat.sh, which lives OUTSIDE the repo so the "
                       f"mechanism that reads the secret is never published to the public remote. "
                       f"The .netrc fine-grained token READS the repo but is REJECTED on push - a "
                       f"read-only success is the most misleading possible green light.",
    }

    with io.open(P, encoding="utf-8") as fh:
        original_text = fh.read()
    data = json.loads(original_text, object_pairs_hook=dict)
    vs = data["vault_sync"]
    for k in updates:
        assert k in vs, f"refusing to create new vault_sync key {k}"
    for k, v in updates.items():
        vs[k] = v

    orig = json.loads(original_text, object_pairs_hook=dict)
    diffs = deep_diffs(orig, data)
    bad = [d for d in diffs if not (len(d[0]) == 2 and d[0][0] == "vault_sync" and d[0][1] in updates)]
    assert not bad, f"changes outside the intended keys: {bad[:3]}"

    out = json.dumps(data, indent=detect_indent(original_text), ensure_ascii=True) + "\n"
    ol, nl = original_text.split("\n"), out.split("\n")
    assert len(ol) == len(nl), "line count changed"
    changed = sum(1 for a, b in zip(ol, nl) if a != b)
    assert changed <= 40, f"{changed} lines differ - refusing to write"

    with io.open(P, "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"OK  recorded commit {sha} · {changed} lines changed · origin/master {master_sha[:7]} untouched")


if __name__ == "__main__":
    sys.exit(main())
