#!/usr/bin/env python3
"""Last unknowns before fixing the content-agent catalog."""
import re, os, subprocess, json

print("=== 1. retail page: product card names + their prices (coffee + biltong) ===")
src = open("/workspace/studex-biltong/index.html").read()
# locate sections around coffee prices and biltong cards
for kw in ["Washed", "Honey", "Aerobic", "Natural", "Coffee — ", "Luxury Wagyu Biltong",
           "Fire &amp; Feast", "StudBot Rise", "Traditional Ox Tail"]:
    for m in re.finditer(r".{0,120}" + re.escape(kw) + r".{0,160}", src):
        t = re.sub(r"\s+", " ", m.group(0)).strip()
        if "R" in t:
            print(f"  [{kw}] {t[:230]}")
            break

print()
print("=== 2. who reads products/catalog.json ? ===")
for root, dirs, files in os.walk("/workspace"):
    dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", "dist", ".next", "build")]
    for f in files:
        if f.endswith((".js", ".ts", ".tsx", ".json", ".py", ".md")):
            p = os.path.join(root, f)
            if p.endswith("catalog.json"):
                continue
            try:
                t = open(p, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            if "catalog.json" in t or "products/catalog" in t:
                print("  ", p.replace("/workspace/", ""))

print()
print("=== 3. Facebook tokens in the env files ===")
for f in ("/root/.env", "/workspace/studex-content-automation/.env"):
    if not os.path.exists(f):
        continue
    for line in open(f):
        line = line.strip()
        if line.startswith("FB_") and "=" in line:
            k, v = line.split("=", 1)
            print(f"  {f} {k} = {v[:24]}...{v[-6:]} (len {len(v)})")

print()
print("=== 4. test each Facebook token against the Graph API ===")
PAGE_ID = "108934711902801"
tokens = {}
for f in ("/root/.env", "/workspace/studex-content-automation/.env"):
    if os.path.exists(f):
        for line in open(f):
            line = line.strip()
            if line.startswith("FB_PAGE_TOKEN") and "=" in line:
                tokens[f + " FB_PAGE_TOKEN"] = line.split("=", 1)[1].strip().strip('"').strip("'")
tokens["META_USER_TOKEN (env)"] = (
    os.environ.get("META_USER_TOKEN", ""))
for label, tok in tokens.items():
    r = subprocess.run(["curl", "-s", "--max-time", "25",
                        f"https://graph.facebook.com/v18.0/{PAGE_ID}?fields=id,name&access_token={tok}"],
                       capture_output=True, text=True, timeout=40)
    print(f"  {label:42} {r.stdout[:170].replace(chr(10),' ')}")
