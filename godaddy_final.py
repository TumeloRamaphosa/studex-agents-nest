#!/usr/bin/env python3
"""Final clean GoDaddy DNS setup — adds send subdomain records for both domains."""
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
            if not body:
                return {"status": "ok", "body": ""}, r.status
            return json.loads(body), r.status
    except urllib.error.HTTPError as e:
        body = e.read()
        if not body:
            return {"error": f"HTTP {e.code}"}, e.code
        return json.loads(body), e.code

def get_records(domain, rec_type):
    res, code = gd("GET", f"/domains/{domain}/records/{rec_type}")
    return res if code == 200 else []

def patch_records(domain, records):
    """PATCH with full replacement of each type."""
    by_type = {}
    for r in records:
        t = r["type"]
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(r)
    results = {}
    for rec_type, recs in by_type.items():
        res, code = gd("PATCH", f"/domains/{domain}/records", recs)
        results[rec_type] = ("OK", code) if code == 200 else (str(res), code)
    return results

def add_send_records(domain):
    print(f"\n{'='*40}")
    print(f"Setting up send.{domain}")
    print('='*40)
    
    # Get current A, MX records to avoid duplicates
    current_a = get_records(domain, "A")
    current_mx = get_records(domain, "MX")
    current_txt = get_records(domain, "TXT")
    
    # Check if send records already exist
    send_a = [r for r in current_a if r["name"] == "send"]
    send_mx = [r for r in current_mx if r["name"] == "send"]
    send_txt = [r for r in current_txt if r["name"] == "send"]
    
    print(f"  Existing send A: {send_a}")
    print(f"  Existing send MX: {send_mx}")
    print(f"  Existing send TXT: {send_txt}")
    
    # Build new records to add (avoiding duplicates)
    new_a = [] if send_a else [{"type": "A", "name": "send", "ttl": 600, "data": "23.227.38.32"}]
    new_mx = [] if send_mx else [{"type": "MX", "name": "send", "ttl": 3600, "priority": 10, "data": "mx.sendgrid.net"}]
    
    results = {}
    if new_a:
        res, code = gd("PATCH", f"/domains/{domain}/records", new_a)
        msg = "✅ Added" if code == 200 else f"❌ {res.get('message', res) if isinstance(res,dict) else res}"
        results["A"] = (msg, code)
    else:
        results["A"] = ("ℹ️ Already exists", 200)
    
    if new_mx:
        res, code = gd("PATCH", f"/domains/{domain}/records", new_mx)
        msg = "✅ Added" if code == 200 else f"❌ {res.get('message', res) if isinstance(res,dict) else res}"
        results["MX"] = (msg, code)
    else:
        results["MX"] = ("ℹ️ Already exists", 200)
    
    # For TXT (SPF): only add if not exists - use full replacement strategy
    new_txt = {"type": "TXT", "name": "send", "ttl": 3600, "data": "v=spf1 include:amazonses.com -all"}
    if not send_txt:
        # Get all current TXT and add send SPF, avoiding exact duplicates
        all_txt = current_txt[:]
        seen = {(r["name"], r.get("data","")) for r in all_txt}
        if ("send", new_txt["data"]) not in seen:
            all_txt.append(new_txt)
        res, code = gd("PATCH", f"/domains/{domain}/records", all_txt)
        msg = "✅ SPF Added" if code == 200 else f"❌ {res.get('message', res) if isinstance(res,dict) else res}"
        results["TXT"] = (msg, code)
    else:
        results["TXT"] = ("ℹ️ Already exists", 200)
    
    for k, (msg, code) in results.items():
        print(f"  {k}: {msg} ({code})")
    return results

# Run for both domains
add_send_records("studexmeat.com")
add_send_records("stud.exchange")

print("\n\n=== SUMMARY ===")
print("DNS changes propagate in 5 min to 48 hours.")
print("Next step: Get DKIM value from app.agentmail.to → Domains → add DKIM record")
print("DKIM record to add:")
print("  Name: agentmail._domainkey.send")
print("  Type: TXT")
print("  Value: (get from AgentMail dashboard — 'Add DKIM Record' button)")
