#!/usr/bin/env python3
"""EOD 2026-10-26 — final bounded fetch: the Blotato post list (key = 'items') with
platform + publish date, so the EOD log states exactly what went live today.
"""
import json, os, urllib.request

ROOT = "/workspace"


def env(key):
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8", errors="replace"):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def http(url, headers):
    req = urllib.request.Request(url, headers=headers)
    r = urllib.request.urlopen(req, timeout=25)
    return r.read().decode("utf-8", "replace")


bt = env("BLOTATO_API_KEY")
raw = json.loads(http("https://backend.blotato.com/v2/posts", {"blotato-api-key": bt}))
items = raw.get("items", [])
out = []
for it in items:
    out.append({
        "id": it.get("id"),
        "account": (it.get("account") or {}).get("id"),
        "platform": (it.get("account") or {}).get("provider"),
        "published_at": it.get("published_at"),
        "status": it.get("status"),
        "text": (it.get("text") or "")[:120],
        "media": len(it.get("media") or []),
    })
out.sort(key=lambda x: str(x["published_at"]))
json.dump({"count": len(out), "posts": out},
          open(os.path.join(ROOT, "memory/2026-10-26-eod-posts.json"), "w"), indent=2)
print("posts:", len(out))
for p in out:
    print(f"  {p['id']}  {p['platform']}  {p['published_at']}  media={p['media']}  {p['text'][:70]}")
