---
name: in-place-redact-active-log
description: Redact live credential literals from an actively-appended log file without breaking the writer
---

# Redacting a live log in place

When a long-running process holds a log file open for append, you cannot
safely fix a credential leak in it by rewriting or replacing the file.

**Why:**
- `mv new old` / `rename()` swaps the **inode**. The process keeps its
  file descriptor pointing at the ORIGINAL inode, so it keeps writing to a
  file that is no longer reachable by its path. The visible log silently
  freezes while the real one grows unobserved. This is the worst outcome:
  it looks fixed and is not.
- `truncate -s 0` destroys the diagnostic trail and gains nothing when
  disk is not the problem.
- Editing with a text editor that rewrites the file has the same inode
  problem.

**The safe method:** open the file `r+b` and overwrite each match
**in place** with a mask of the **exact same byte length**. Byte offsets
never shift, the inode is never replaced, the writer's fd and append
position stay valid, and the secret is gone.

```python
with open(path, "r+b") as fh:
    for m in matches:
        fh.seek(m.start())
        fh.write((MASK + b"_" * len(m.group(0)))[:len(m.group(0))])
    fh.flush()
```

**Verify all four properties after:**
1. `stat().st_size` unchanged
2. `stat().st_ino` unchanged
3. the secret no longer matches
4. the file still parses (for JSONL: every sampled line `json.loads`)

Plus: the owning process is still healthy (HTTP 200) and the file is still
being written to.

**Take liveness from the provider, not from the file.** A credential
sitting in `.env` is not necessarily live — `am_us_057fa6...` is in `.env`
and returns HTTP 403. Masking by "is this string in .env" overstates the
exposure and redactions dead values for no reason. Probe
`GET /v0/inboxes` and mask only what answers 200.

**Do not mask a dead key to make a report look better.** The point is
removing a usable secret, not reducing a count.
