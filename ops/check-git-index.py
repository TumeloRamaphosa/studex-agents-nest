#!/usr/bin/env python3
"""Check that the repo's git INDEX is intact and consistent with HEAD.

WHY THIS EXISTS
---------------
On 2026-10-27 the index at /workspace/.git/index was replaced by a **valid
but EMPTY** index (65 bytes, 0 entries) while HEAD tracked 15,922 files.

`git status` then reported all 15,922 files as **staged for deletion** - and
every single one of them still existed on disk. One `git commit` away from
wiping the repository's entire tracking.

It happened TWICE, and no checker reported it, because:
  * the working tree was never touched, so every content check still passed;
  * the damage was done by `ops/test-git-pre-push-guard.py`, which ran
    `git read-tree --empty` against the real index with no
    `GIT_INDEX_FILE` override - and that test is in `ops/run-tests.sh`, so
    **every canonical suite run emptied the index**.

KEY THE WORKTREE IS THE TRUTH; THE INDEX IS A CACHE OF IT - and a cache can
be corrupt while the thing it caches is perfectly fine. A checker that only
reads file CONTENTS cannot see this class of damage at all, because the
files are all still there. It has to look at git's own state.

WHAT IT CHECKS
--------------
  1. The index exists and is non-empty.
  2. The number of tracked files in the index matches HEAD's tree.
  3. The index does not report a mass deletion.
  4. The index contains NO gitlink (mode 160000) entries.

  If the index is empty while HEAD tracks thousands of files, this reports
  the damage and gives the exact repair (`git reset --mixed HEAD`, which
  rebuilds the index from HEAD and touches no file in the working tree).

WHY 4 EXISTS
-------------
A gitlink is git's record of "this path is ANOTHER repository". It is not
a file, so every content-based checker reads a clone of this repo and
finds an EMPTY DIRECTORY where the content should be, with no error
anywhere.

On 2026-10-29 a leftover scratch directory from
`ops/test-empty-repo-false-green.py` sat in the repo root. It held its own
`.git` directories, and `.gitignore` only ignored `.tmp-*.sh`/`.tmp-*.py` -
FILES, not DIRECTORIES. The next `git add .` (the Build Hour job runs one)
would have staged both nested repos as gitlinks and shipped them to a
PUBLIC remote. The index was perfectly consistent with HEAD, every other
checker was green, and the damage was one command away.

A guard that only checks what the damage LOOKS LIKE cannot catch damage
that changes what a clone CONTAINS. So this one reads git's own record of
the index, entry by entry, including the mode.
"""
import os
import pathlib
import subprocess
import sys

# The repo under inspection. Overridable so the checker can be driven against
# a SCRATCH repo - which is the only way to prove it can actually FAIL. A
# checker that can only ever be pointed at the one healthy repo it was
# written for is decoration, not a control.
REPO = pathlib.Path(os.environ.get("GIT_INDEX_CHECK_REPO", "/workspace"))
GIT_DIR = REPO / ".git"
INDEX = GIT_DIR / "index"


def _run(*args):
    try:
        r = subprocess.run(["git"] + list(args), cwd=str(REPO),
                           capture_output=True, text=True, timeout=300)
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()
    except Exception as e:  # noqa: BLE001
        return 1, "", type(e).__name__


def _count_nul(*args):
    """Count git's NUL-separated records.

    KEY DO NOT COUNT WITH .split() ON GIT'S DEFAULT OUTPUT. Git QUOTES paths
    that contain spaces or non-ASCII characters ("path with space"), so
    splitting on whitespace counts ONE path as THREE and inflates the total.
    The first version of this checker reported 16,035 tracked files for a
    repo that tracks 15,922 - a wrong number in the very output meant to
    establish trust. `-z` disables quoting and makes each record exact.
    """
    try:
        r = subprocess.run(["git"] + list(args) + ["-z"], cwd=str(REPO),
                           capture_output=True, timeout=300)
        if r.returncode != 0:
            return -1
        return len([x for x in r.stdout.split(b"\0") if x])
    except Exception:  # noqa: BLE001
        return -1


def _staged_deletions():
    """Count staged deletions, using NUL-separated records."""
    try:
        r = subprocess.run(["git", "diff", "--cached", "--name-status", "-z"],
                           cwd=str(REPO), capture_output=True, timeout=300)
        if r.returncode != 0:
            return 0
        fields = [x for x in r.stdout.split(b"\0") if x]
        n = 0
        i = 0
        while i < len(fields):
            f = fields[i].decode("utf-8", "replace")
            if f.startswith("D"):
                n += 1
                i += 2          # status + path
            else:
                i += 1
                if f[:1] in ("R", "C"):
                    i += 1      # rename/copy has an extra path
        return n
    except Exception:  # noqa: BLE001
        return 0


def _gitlinks():
    """Return the paths staged as gitlinks (mode 160000).

    `git ls-files -s` prints one record per index entry:
        <mode> <sha> <stage>\t<path>
    A gitlink is mode 160000 - a path that is ANOTHER repository, not a
    file. It is invisible to every content-based checker: a clone of this
    repo would contain an EMPTY directory at that path, with no error
    anywhere to say so.
    """
    try:
        r = subprocess.run(["git", "ls-files", "-s"], cwd=str(REPO),
                           capture_output=True, text=True, timeout=300)
        if r.returncode != 0:
            return []
        links = []
        for line in r.stdout.splitlines():
            if not line.strip():
                continue
            meta, _, path = line.partition("\t")
            parts = meta.split()
            if parts and parts[0] == "160000":
                links.append(path if path else meta)
        return links
    except Exception:  # noqa: BLE001
        return []


def main():
    findings = []

    if not INDEX.exists():
        findings.append("there is no index at %s - git will rebuild an EMPTY "
                        "one and every tracked file will look deleted" % INDEX)
    else:
        size = INDEX.stat().st_size
        tracked = _count_nul("ls-files")
        head_count = _count_nul("ls-tree", "-r", "HEAD", "--name-only")

        print("index file            : %s (%d bytes)" % (INDEX, size))
        print("files in the index    : %s" % tracked)
        print("files tracked by HEAD : %s" % (head_count if head_count >= 0
                                              else "NONE (HEAD has no commits)"))

        if head_count <= 0:
            findings.append(
                "the repository has NO COMMITS - the working tree is not under "
                "version control. Every check that reads the history (this "
                "one, the pre-push guard, the tracked-credential scan) is "
                "VACUOUS: there is nothing to inspect, so 'clean' would be "
                "proving nothing. Create a baseline commit.")
        elif tracked == 0 and head_count > 0:
            findings.append(
                "THE INDEX IS EMPTY but HEAD tracks %d files - git status is "
                "reporting every one of them as staged for deletion, and they "
                "all still exist on disk. One commit away from wiping the "
                "repository's tracking." % head_count)
        elif head_count > 0 and tracked != head_count:
            findings.append(
                "the index tracks %d files but HEAD tracks %d - the index and "
                "HEAD disagree" % (tracked, head_count))

        # A mass staged deletion is the symptom, whatever the cause.
        dels = _staged_deletions()
        if dels > 100:
            findings.append(
                "%d files are staged for DELETION - if those files exist on "
                "disk, the index is corrupt, not the worktree" % dels)

        # A gitlink in the index is a path that is ANOTHER repository. It
        # is not a file, so a clone of this repo would contain an EMPTY
        # DIRECTORY there - and no content-based checker could ever see
        # it. One `git add .` is all it takes to create one.
        links = _gitlinks()
        if links:
            findings.append(
                "%d path(s) are staged as GITLINKS (mode 160000) - each is "
                "another REPOSITORY, not a file: %s. A clone of this repo "
                "would carry an EMPTY DIRECTORY at each of those paths, and "
                "no content-based checker can see it. Remove them from the "
                "index and ignore the source." % (len(links),
                                                   ", ".join(links[:10])))

    if findings:
        print()
        print("VERDICT: BROKEN - the git index is not consistent with HEAD")
        for f in findings:
            print("  - %s" % f)
        print()
        print("Repair (rebuilds the index from HEAD, touches NO file in the")
        print("working tree -- do NOT use --hard):")
        print("    cd /workspace && git reset --mixed HEAD")
        return 1

    print()
    print("VERDICT: CLEAN - the index is intact and consistent with HEAD.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
