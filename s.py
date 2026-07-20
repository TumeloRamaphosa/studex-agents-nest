#!/usr/bin/env python3
import subprocess, os, sys

os.chdir("/root")
print("=== Installing Claude SEO ===")

# Clone
r = subprocess.run(["git","clone","--depth","1","https://github.com/AgriciDaniel/claude-seo.git"],
                   capture_output=True, text=True)
print("CLONE:", r.returncode, r.stdout.strip(), r.stderr.strip()[:200])

# Install
if os.path.exists("/root/claude-seo/install.sh"):
    r = subprocess.run(["bash","/root/claude-seo/install.sh"],
                       capture_output=True, text=True, cwd="/root/claude-seo")
    print("INSTALL RC:", r.returncode)
    print("OUT:", r.stdout[:1000])
    print("ERR:", r.stderr[:500])
else:
    print("No install.sh found, listing files:")
    for f in os.listdir("/root/claude-seo"):
        print(" ", f)

# Show what was installed
r = subprocess.run(["ls","/root/claude-seo/"],
                   capture_output=True, text=True)
print("FINAL FILES:", r.stdout)

# Check if claude-seo command is available
r = subprocess.run(["which","claude-seo"], capture_output=True, text=True)
print("CLAUDE-SEO PATH:", r.stdout.strip() or "not found")

# Check python packages installed
r = subprocess.run(["pip","list"], capture_output=True, text=True,
                  env={**os.environ, "PIP_FORMAT":"minimal"})
for pkg in ["playwright","weasyprint","trafilatura","htmldate","matplotlib"]:
    found = any(pkg in line for line in r.stdout.split("\n"))
    print(f"{pkg}: {'INSTALLED' if found else 'NOT FOUND'}")
