#!/usr/bin/env python3
"""
StudEx Meat — GoDaddy DNS Setup for AgentMail
Sets up send.studexmeat.com and send.stud.exchange for AgentMail email routing.
"""
import urllib.request, urllib.error, json, sys

KEY = "dL3oxjXQygtx_2KEvNjAitQcocTDeBt8T27"
SEC = "RoRnzR6RfZJqpm5dmHKcUs"
auth = f"sso-key {KEY}:{SEC}"

def gd(method, path, data=None):
    url = f"https://api.godaddy.com/v1{path}"
    headers = {"Authorization": auth, "Content-Type": "application/json"}
    req = urllib.request.Request(url,
                                  data=json.dumps(data).encode() if data else None,
                                  headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return json.loads(r.read()), r.status, None
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code, str(e)

def add_records(domain, records_by_type):
    """Add records using PATCH - replaces ALL records of each type."""
    for rec_type, records in records_by_type.items():
        result, code, err = gd("PATCH", f"/domains/{domain}/records", records)
        if code == 200:
            print(f"  ✅ {rec_type}: {len(records)} record(s) set")
        else:
            print(f"  ❌ {rec_type} error ({code}): {result.get('message', result)}")
            # Show field errors
            for f in result.get("fields", []):
                print(f"     - {f['path']}: {f['message']}")

# ---- STUDEXMEAT.COM ----
print("\n=== studexmeat.com ===")

# Get existing TXT records so we know what to preserve
existing_txt, code, _ = gd("GET", "/domains/studexmeat.com/records/TXT")
print(f"Existing TXT records found: {len(existing_txt)}")
for r in existing_txt:
    print(f"  [{r['name']}] = {r.get('data','')[:60]}")

# The issue: GoDaddy rejects PATCH if it sees duplicate name+type already.
# Workaround: include ALL existing records + new ones in one call.
# GoDaddy replaces ALL TXT records with what we send.
existing_txt.append({
    "name": "send",
    "type": "TXT",
    "ttl": 3600,
    "data": "v=spf1 include:amazonses.com -all"
})

result, code, _ = gd("PATCH", "/domains/studexmeat.com/records", existing_txt)
if code == 200:
    print("  ✅ send SPF added to studexmeat.com")
else:
    print(f"  ❌ {code}: {result}")
    # Try just the new record alone (will replace ALL TXT - risky)
    print("  Trying alternate approach...")
    result2, code2, _ = gd("PATCH", "/domains/studexmeat.com/records", [
        {"type": "TXT", "name": "send", "ttl": 3600, "data": "v=spf1 include:amazonses.com -all"}
    ])
    if code2 == 200:
        print("  ✅ send SPF added (alternate method)")
    else:
        print(f"  ❌ Alternate also failed: {code2} — {result2}")

# A record for send.studexmeat.com
result, code, _ = gd("PATCH", "/domains/studexmeat.com/records", [
    {"type": "A", "name": "send", "ttl": 600, "data": "23.227.38.32"}
])
print(f"  A send.studexmeat.com → {'✅ done' if code==200 else '❌ '+str(result)}")

# MX record for send.studexmeat.com
result, code, _ = gd("PATCH", "/domains/studexmeat.com/records", [
    {"type": "MX", "name": "send", "ttl": 3600, "priority": 10, "data": "mx.sendgrid.net"}
])
print(f"  MX send.studexmeat.com → {'✅ done' if code==200 else '❌ '+str(result)}")

# DKIM CNAME for agentmail._domainkey.send.studexmeat.com
# Note: Replace the DKIM value below with the actual DKIM value from AgentMail dashboard
result, code, _ = gd("PATCH", "/domains/studexmeat.com/records", [
    {"type": "CNAME", "name": "agentmail._domainkey.send", "ttl": 3600,
     "data": "agentmail._domainkey. sending domain will provide this value"}
])
print(f"  DKIM CNAME → {'✅ done (NOTE: update DKIM value!)' if code==200 else '❌ '+str(result)}")

# ---- STUD.EXCHANGE ----
print("\n=== stud.exchange ===")

existing_txt2, code, _ = gd("GET", "/domains/stud.exchange/records/TXT")
print(f"Existing TXT records: {len(existing_txt2)}")
for r in existing_txt2:
    print(f"  [{r['name']}] = {r.get('data','')[:60]}")

existing_txt2.append({
    "name": "send",
    "type": "TXT",
    "ttl": 3600,
    "data": "v=spf1 include:amazonses.com -all"
})

result, code, _ = gd("PATCH", "/domains/stud.exchange/records", existing_txt2)
print(f"  send SPF stud.exchange → {'✅ done' if code==200 else '❌ '+str(result)}")

result, code, _ = gd("PATCH", "/domains/stud.exchange/records", [
    {"type": "A", "name": "send", "ttl": 600, "data": "23.227.38.32"}
])
print(f"  A send.stud.exchange → {'✅ done' if code==200 else '❌ '+str(result)}")

result, code, _ = gd("PATCH", "/domains/stud.exchange/records", [
    {"type": "MX", "name": "send", "ttl": 3600, "priority": 10, "data": "mx.sendgrid.net"}
])
print(f"  MX send.stud.exchange → {'✅ done' if code==200 else '❌ '+str(result)}")

print("\n=== DNS propagation note ===")
print("DNS changes can take 5 min to 48 hours to propagate globally.")
print("Once done, verify at: https://toolbox.googleapps.com/apps/dig/#MX/send.studexmeat.com")
print("\nNext step: Get DKIM value from AgentMail dashboard and update the DKIM record.")
