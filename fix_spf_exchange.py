#!/usr/bin/env python3
"""Fix SPF for stud.exchange — add AgentMail alongside existing Google SPF."""
import urllib.request, urllib.error, json

KEY = "dL3oxjXQygtx_2KEvNjAitQcocTDeBt8T27"
SEC = "RoRnzR6RfZJqpm5dmHKcUs"
auth = f"sso-key {KEY}:{SEC}"

def gd(method, path, data=None):
    url = f"https://api.godaddy.com/v1{path}"
    headers = {"Authorization": auth, "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                  headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read()
            return json.loads(body) if body else {}, r.status
    except urllib.error.HTTPError as e:
        body = e.read()
        return json.loads(body) if body else {"error": f"HTTP {e.code}"}, e.code

domain = "stud.exchange"
print(f"=== Fixing SPF for {domain} ===")

# Get ALL current TXT records
txt, code = gd("GET", f"/domains/{domain}/records/TXT")
print(f"Found {len(txt)} TXT records:")
for r in txt:
    print(f"  [{r['name']}] = {r.get('data','')}")

# Find the @ SPF record (Google) and update it to include both
updated = False
for r in txt:
    if r["name"] == "@" and "spf" in r.get("data","").lower():
        old_spf = r["data"]
        # Combine Google + Amazon SES (AgentMail)
        new_spf = "v=spf1 include:_spf.google.com include:amazonses.com ~all"
        r["data"] = new_spf
        print(f"\nOld SPF: {old_spf}")
        print(f"New SPF: {new_spf}")
        updated = True

if updated:
    res, code = gd("PATCH", f"/domains/{domain}/records", txt)
    print(f"\nPATCH result: {code}")
    if code == 200:
        print("✅ SUCCESS — Google + AgentMail SPF combined!")
        print("\nYour existing Google email stays active AND AgentMail emails now work.")
    else:
        print(f"Error: {res}")
else:
    print("No @ SPF record found — adding it...")
    txt.append({"type":"TXT","name":"@","ttl":3600,"data":"v=spf1 include:_spf.google.com include:amazonses.com ~all"})
    res, code = gd("PATCH", f"/domains/{domain}/records", txt)
    print(f"Result: {code} — {res}")
