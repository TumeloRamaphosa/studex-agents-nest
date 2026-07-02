#!/usr/bin/env python3
"""
Robusca Brain Backup — pushes workspace brain files to GitHub
Repo: TumeloRamaphosa/robusca-brain (private)
Token sourced from /workspace/.github-config
"""
import json
import base64
import urllib.request
import urllib.error
import os
import glob
from datetime import datetime

# Load token from config
TOKEN = None
with open("/workspace/.github-config", "r") as f:
    for line in f:
        if line.startswith("GITHUB_TOKEN="):
            TOKEN = line.strip().split("=", 1)[1]
            break

OWNER = "TumeloRamaphosa"
REPO = "robusca-brain"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Content-Type": "application/json",
    "User-Agent": "Robusca-OpenClaw"
}

results = []

def gh_request(method, path, data=None):
    url = f"https://api.github.com{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

def ensure_repo():
    data = {
        "name": REPO,
        "description": "Robusca brain backup — memory, soul, identity, workspace files",
        "private": True,
        "auto_init": True
    }
    result, status = gh_request("POST", "/user/repos", data)
    if status == 201:
        print(f"✅ Repo created: {OWNER}/{REPO}")
    elif status == 422:
        print(f"ℹ️  Repo already exists: {OWNER}/{REPO}")
    else:
        print(f"⚠️  Repo create status {status}: {result}")
    return status in (201, 422)

def get_sha(path):
    result, status = gh_request("GET", f"/repos/{OWNER}/{REPO}/contents/{path}")
    if status == 200:
        return result.get("sha")
    return None

def push_file(local_path, remote_path):
    if not os.path.exists(local_path):
        print(f"⏩ Skip (not found): {local_path}")
        results.append(("SKIP", remote_path))
        return
    with open(local_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    encoded = base64.b64encode(content.encode()).decode()
    sha = get_sha(remote_path)
    data = {
        "message": f"backup: {remote_path}",
        "content": encoded,
        "branch": "main"
    }
    if sha:
        data["sha"] = sha
    result, status = gh_request("PUT", f"/repos/{OWNER}/{REPO}/contents/{remote_path}", data)
    if status in (200, 201):
        action = "created" if status == 201 else "updated"
        print(f"✅ {action.upper()}: {remote_path}")
        results.append(("OK", remote_path))
    else:
        msg = result.get('message', str(result))
        print(f"❌ FAIL {remote_path}: {status} — {msg}")
        results.append(("FAIL", remote_path, f"{status}: {msg}"))

# Build file list
static_files = [
    "/workspace/SOUL.md",
    "/workspace/IDENTITY.md",
    "/workspace/USER.md",
    "/workspace/AGENTS.md",
    "/workspace/HEARTBEAT.md",
    "/workspace/scripts/github-backup.py",
    "/workspace/skills/github-integration/SKILL.md",
]

memory_files = sorted(glob.glob("/workspace/memory/*.md"))
studex_files = sorted(glob.glob("/workspace/studex/*.md"))

all_files = static_files + memory_files + studex_files

print("🚀 Robusca Brain Backup — starting...\n")
if not ensure_repo():
    print("❌ Could not access/create repo. Aborting.")
    exit(1)

print()
for local in all_files:
    remote = local.replace("/workspace/", "")
    push_file(local, remote)

# Summary
ok = [r for r in results if r[0] == "OK"]
skipped = [r for r in results if r[0] == "SKIP"]
failed = [r for r in results if r[0] == "FAIL"]

print(f"\n📊 Summary: {len(ok)} pushed, {len(skipped)} skipped, {len(failed)} failed")

# Write status log
ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
status_lines = [f"# GitHub Backup Status\n\n", f"**Last run:** {ts}\n\n"]
status_lines.append(f"**Result:** {len(ok)} pushed · {len(skipped)} skipped · {len(failed)} failed\n\n")
status_lines.append("## Files Pushed\n")
for r in ok:
    status_lines.append(f"- ✅ {r[1]}\n")
if skipped:
    status_lines.append("\n## Skipped (not found)\n")
    for r in skipped:
        status_lines.append(f"- ⏩ {r[1]}\n")
if failed:
    status_lines.append("\n## Failed\n")
    for r in failed:
        status_lines.append(f"- ❌ {r[1]} — {r[2]}\n")

with open("/workspace/memory/github-backup-status.md", "w") as f:
    f.writelines(status_lines)

print("📝 Status log written to /workspace/memory/github-backup-status.md")
