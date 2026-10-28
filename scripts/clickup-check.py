#!/usr/bin/env python3
import json, urllib.request, urllib.error, os, re

def http(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300].decode(errors="replace")
    except Exception as e:
        return None, str(e)

env = {}
for line in open("/workspace/studex-war-room/.env", errors="replace"):
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.strip().split("=", 1)
        env[k] = v
tok = env.get("VITE_CLICKUP_TOKEN", "")
lists = {
 "COFFEE": env.get("VITE_CLICKUP_LIST_COFFEE",""),
 "CAVIAR": env.get("VITE_CLICKUP_LIST_CAVIAR",""),
 "BILTONG": env.get("VITE_CLICKUP_LIST_BILTONG",""),
}
for name, lid in lists.items():
    if not lid: continue
    st, body = http(f"https://api.clickup.com/api/v2/list/{lid}/task?include_closed=false&subtasks=true&include_markdown_description=true",
                    {"Authorization": tok})
    print(f"\n=== {name} ({lid}) -> {st}")
    if st == 200:
        d = json.loads(body)
        for t in d.get("tasks", [])[:15]:
            print("  -", t.get("name"), "|", t.get("status",{}).get("status"), "| due", t.get("due_date"))
    else:
        print(body[:200])
