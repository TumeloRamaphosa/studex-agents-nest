#!/usr/bin/env python3
"""Where does the live Blotato key live on disk, and is it published?

Answers with NO credential value printed:
  1. which .env variable holds it
  2. which files on disk contain the literal (whole /workspace + /tmp,
     excluding the 179MB gateway log, which is handled separately)
  3. for each, is it TRACKED by git (i.e. would be published)
"""
import os
import pathlib
import subprocess

WS = pathlib.Path("/workspace")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".npm", ".cache", ".venv"}
MAX_BYTES = 20_000_000


def live_blotato_value():
    env = WS / ".env"
    if not env.exists():
        return None, None
    for line in env.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        if "BLOTATO" in k.upper() and v.startswith("blt_") and len(v) > 20:
            return k.strip(), v
    return None, None


def git_tracked(rel):
    r = subprocess.run(["git", "ls-files", "--error-unmatch", rel],
                       cwd=WS, capture_output=True, text=True)
    return r.returncode == 0


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            yield os.path.join(dirpath, name)


def main():
    name, val = live_blotato_value()
    if not val:
        print("no live blotato credential found in .env")
        return
    print(f"live credential  : {name}  (len={len(val)}, value not printed)")
    print()
    print("files on disk containing that literal:")
    for root in (str(WS), "/tmp"):
        for path in walk(root):
            try:
                st = os.stat(path)
                if st.st_size > MAX_BYTES:
                    continue
                data = pathlib.Path(path).read_bytes()
            except OSError:
                continue
            if val.encode() not in data:
                continue
            if path.startswith(str(WS)):
                rel = os.path.relpath(path, str(WS))
                tracked = git_tracked(rel)
                where = "TRACKED - WOULD BE PUBLISHED" if tracked else "untracked"
            else:
                rel = path
                tracked = False
                where = "outside the repo"
            n = data.count(val.encode())
            print(f"  {rel}  ({n} occurrence(s))  [{where}]")


if __name__ == "__main__":
    main()
