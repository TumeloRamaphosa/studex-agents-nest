#!/usr/bin/env python3
import os, re, json, urllib.request, urllib.error, glob

def http(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300].decode(errors="replace")
    except Exception as e:
        return None, str(e)

print("=== SHOPIFY ADMIN TOKEN hunt (workspace files) ===")
found = 0
for root, dirs, files in os.walk("/workspace"):
    dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", "dist", "build")]
    for f in files:
        p = os.path.join(root, f)
        if os.path.getsize(p) > 400000: continue
        try: txt = open(p, errors="replace").read()
        except: continue
        for m in re.finditer(r"(shpat_[A-Za-z0-9]{20,})", txt):
            print("TOKEN FOUND:", p, m.group(1)[:14] + "...")
            found += 1
            break
        if found: break
    if found: break
if not found: print("no shpat_ token found in workspace files")

print("\n=== BLOTATO accounts ===")
bt = os.environ.get("BLOTATO_API_KEY","")
st, body = http("https://backend.blotato.com/v2/users/me/accounts", {"blotato-api-key": bt})
print("->", st, body[:400])

print("\n=== storefront live check ===")
for u in ["https://studexmeat.com", "https://studexmeat.com/products.json?limit=3"]:
    st, body = http(u)
    print(u, "->", st, len(body or ""), (body or "")[:120].replace("\n"," "))

print("\n=== Discord ids in workspace (guild/channel) ===")
seen = set()
for p in ["/workspace/studex-war-room/src/markdownDocs.ts", "/workspace/memory/post-log.md"]:
    if os.path.exists(p):
        txt = open(p, errors="replace").read()
        for m in re.finditer(r"\b\d{17,20}\b", txt):
            if m.group(0) not in seen:
                seen.add(m.group(0)); print(p, m.group(0))
for p in glob.glob("/workspace/memory/*.md"):
    txt = open(p, errors="replace").read()
    for m in re.finditer(r"(?:channel|guild)[\"':= ]+(\d{17,20})", txt, re.I):
        if m.group(1) not in seen:
            seen.add(m.group(1)); print(p, m.group(1))
