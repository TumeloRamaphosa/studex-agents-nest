#!/usr/bin/env python3
import os, re, json, glob, subprocess, time

print("=== openclaw config: discord ids ===")
try:
    cfg = json.load(open(os.path.expanduser("~/.openclaw/openclaw.json")))
    ch = cfg.get("channels", {})
    for k, v in ch.items():
        s = json.dumps(v)
        ids = re.findall(r"\d{17,20}", s)
        print(" ", k, "ids:", ids[:5], "keys:", list(v.keys())[:8])
except Exception as e:
    print("err", e)

print("\n=== content pipeline queue files ===")
for d in ["studex-content-pipeline", "studex-content-os", "studex-content-automation", "studex-content-factory", "content-factory", "content", "studex-social-pipeline"]:
    p = f"/workspace/{d}"
    if not os.path.isdir(p): continue
    files = []
    for root, dirs, fs in os.walk(p):
        dirs[:] = [x for x in dirs if x not in ("node_modules", ".git", "dist", "__pycache__")]
        for f in fs:
            fp = os.path.join(root, f)
            try: files.append((os.path.getmtime(fp), fp))
            except: pass
    files.sort(reverse=True)
    print(f"\n-- {d}: {len(files)} files; newest:")
    for m, fp in files[:6]:
        print("   ", time.strftime("%Y-%m-%d %H:%M", time.gmtime(m)), fp.replace("/workspace/",""))

print("\n=== memory/post-log.md tail ===")
try:
    print(open("/workspace/memory/post-log.md", errors="replace").read()[-1800:])
except Exception as e:
    print("err", e)
