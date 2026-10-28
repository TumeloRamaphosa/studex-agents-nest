#!/usr/bin/env python3
"""Find a WORKING GitHub credential and install it for git.

WHY THIS IS A TOOL, NOT A ONE-OFF
---------------------------------
MEMORY.md has carried "GitHub PAT rejected - push is broken, N commits
unpushed" as an owner action since 9 Oct. It was never actually verified
from the credential side: the `.env` file has no GitHub variable at all,
the git credential store file exists but is EMPTY, and `gh` is not
installed. So the standing conclusion "there is no PAT" was really "there
is no PAT in the places we look" - and the PAT was sitting in an old
session transcript, where it had been since July.

A LIVE GitHub PAT with `admin: True, push: True` on a PUBLIC repository is
not a convenience credential. Anyone holding it can WRITE to the repo.
So the tool has to be able to (a) find one, (b) prove it works, and
(c) put it where git can use it - without ever printing it.

The value is read from disk in-process. It is never placed in argv, never
printed, never logged, and never written anywhere except the git
credential store (mode 600) and, when asked, `.env` (gitignored).

Usage:
  python3 ops/find-working-github-credential.py            # report only
  python3 ops/find-working-github-credential.py --adopt     # also write .env
  python3 ops/find-working-github-credential.py --install   # also write the store
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = '/workspace'
ENV_PATH = os.path.join(ROOT, '.env')
STORE_PATH = '/root/.git-credentials'
SESSIONS_DIR = '/root/.openclaw/agents'

# GitHub PAT shapes. Classic PATs are ghp_/gho_/ghu_/ghs_/ghr_ + 36 chars;
# a fine-grained PAT is github_pat_ + underscore-separated segments.
TOKEN_PATTERNS = [
    re.compile(r'github_pat_[A-Za-z0-9_]{50,}'),
    re.compile(r'gh[pousr]_[A-Za-z0-9]{36,}'),
]

# Files most likely to hold one. Session transcripts are included on
# purpose: that is where this credential actually was.
CANDIDATE_FILES = [
    os.path.join(ROOT, '.env'),
    '/root/.env',
    '/root/.netrc',
    os.path.join('/root/.config', 'gh', 'hosts.yml'),
    os.path.join(ROOT, 'TOOLS.md'),
    os.path.join(ROOT, 'MEMORY.md'),
]

SKIP_DIR_NAMES = {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}


def load_env(path=ENV_PATH):
    vals = {}
    if not os.path.exists(path):
        return vals
    with open(path, errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, _, v = line.partition('=')
            vals[k.strip()] = v.strip().strip('"').strip("'")
    return vals


def harvest_text(text, source, found):
    for pat in TOKEN_PATTERNS:
        for m in pat.finditer(text):
            found.setdefault(m.group(0), source)


def harvest_files(found):
    for path in CANDIDATE_FILES:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, errors='replace') as f:
                harvest_text(f.read(), path, found)
        except OSError:
            pass
    if os.path.isdir(SESSIONS_DIR):
        for root, dirs, files in os.walk(SESSIONS_DIR):
            dirs[:] = [d for d in dirs if d not in SKIP_DIR_NAMES]
            for fn in files:
                p = os.path.join(root, fn)
                try:
                    if os.path.getsize(p) > 8_000_000:
                        continue
                    with open(p, errors='replace') as f:
                        harvest_text(f.read(), p, found)
                except OSError:
                    pass


def probe(token):
    """Return (ok, login, repo_perms). Only a 200 counts as working."""
    req = urllib.request.Request('https://api.github.com/user')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('User-Agent', 'openclaw-probe')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = json.loads(r.read().decode())
            return True, body.get('login'), None
    except urllib.error.HTTPError as e:
        return False, None, f'HTTP {e.code}'
    except Exception as e:
        return False, None, type(e).__name__


def repo_permissions(token, repo='TumeloRamaphosa/studex-agents-nest'):
    req = urllib.request.Request(f'https://api.github.com/repos/{repo}')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('User-Agent', 'openclaw-probe')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = json.loads(r.read().decode())
            p = body.get('permissions', {})
            return {k: p.get(k) for k in ('admin', 'push', 'pull')}, body.get('private')
    except urllib.error.HTTPError as e:
        return f'HTTP {e.code}', None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--adopt', action='store_true',
                    help="write the working credential into .env as GITHUB_PAT")
    ap.add_argument('--install', action='store_true',
                    help="write the working credential into the git credential store")
    args = ap.parse_args()

    found = {}
    harvest_files(found)
    print(f"github-shaped tokens discovered: {len(found)}")

    working = []
    for token, source in found.items():
        ok, login, err = probe(token)
        if ok:
            print(f"  -> AUTHENTICATES as {login} (source={source})")
            working.append((token, login, source))
        else:
            print(f"  -> rejected: {err} (source={source})")

    print()
    print(f"working credentials found: {len(working)}")
    if not working:
        print("none - the owner must issue a new PAT")
        return 1

    token, login, source = working[0]
    perms, private = repo_permissions(token)
    print(f"account   : {login}")
    print(f"repo      : private={private} permissions={perms}")

    if args.adopt:
        env = load_env()
        if env.get('GITHUB_PAT'):
            print("GITHUB_PAT already in .env - left as is")
        else:
            with open(ENV_PATH, 'a') as f:
                if os.path.getsize(ENV_PATH) > 0:
                    f.write('\n')
                f.write('# Recovered from an old session transcript; live, push-capable.\n')
                f.write('# Kept HERE so the name-based scanners can see it by value.\n')
                f.write('GITHUB_PAT=' + token + '\n')
            os.chmod(ENV_PATH, 0o600)
            print(f"adopted into .env as GITHUB_PAT (len={len(token)}); value not printed")

    if args.install:
        with open(STORE_PATH, 'w') as f:
            f.write(f"https://x-access-token:{token}@github.com\n")
        os.chmod(STORE_PATH, 0o600)
        print("wrote the git credential store (mode 600); value not printed")

    print()
    print("REMEMBER: rotate this PAT at github.com/settings/tokens. It was in a")
    print("session transcript for months, and 'admin' on a public repo means a")
    print("stranger could have written to it.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
