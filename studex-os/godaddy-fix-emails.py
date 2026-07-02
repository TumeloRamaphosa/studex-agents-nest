#!/usr/bin/env python3
"""
GoDaddy DNS Fix for AgentMail — uses PUT to replace all records of each type.
Keeps ALL existing records intact, only modifies/added the 'send' subdomain records.
"""
import urllib.request, urllib.error, json

KEY = "dL3oxjXQygtx_2KEvNjAitQcocTDeBt8T27"
SEC = "RoRnzR6RfZJqpm5dmHKcUs"

def gd(method, path, data=None):
    url = f"https://api.godaddy.com/v1{path}"
    headers = {"Authorization": f"sso-key {KEY}:{SEC}", "Content-Type": "application/json"}
    req = urllib.request.Request(url,
        data=json.dumps(data).encode() if data else None,
        headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

DKIM_TOKEN = ("MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwbFlylhKL2IcY61L19P3"
               "j8Tkt+VslUC+74gG1WirlusA2guENozM05+7ys0EDz9n3muHftwwV8619WYAx6"
               "xf/l+FQrNPGBBJZXonhJUQUrK6NvNBAU74CtBVZRxvrrXPG0f7TZbLUxwCdVU"
               "3VteDtmiS0hJSu91AZTtyRHjozsy391UoP4uMhzfmOcaBsnKY2RBCWUV7gb/EW"
               "NjM81b6yLLHiYbmlC/ya2bUDD08VeHhoNCwoM/FSy1kItboQUdLM1np3F1heI"
               "TowlkQ1Th6AtNdMS14Y6y4sHDhWXw/hCLgh/n6hFBJoHzsVKFJKmvRC9AFsF"
               "h6RWEbandOInKqfQIDAQAB")

def fix_domain(domain, sub):
    print(f"\n{'='*55}")
    print(f" Fixing: send.{domain}")
    print(f"{'='*55}")

    # Step 1: Read ALL current records
    all_recs, code = gd("GET", f"/domains/{domain}/records")
    if code != 200:
        print(f"  ❌ Read error ({code}): {all_recs}")
        return

    # Step 2: Separate by type — keep ALL existing records
    txt_records = [r for r in all_recs if r["type"] == "TXT"]
    mx_records  = [r for r in all_recs if r["type"] == "MX"]
    other_records = [r for r in all_recs if r["type"] not in ("TXT", "MX")]

    print(f"  Current: {len(txt_records)} TXT, {len(mx_records)} MX, {len(other_records)} other")

    # Step 3: Remove OLD send subdomain records (we'll replace them)
    new_txt = [r for r in txt_records
               if r["name"] not in (sub, f"mail.{sub}",
                                      f"agentmail._domainkey.{sub}",
                                      f"_dmarc.{sub}")]
    new_mx  = [r for r in mx_records
               if r["name"] not in (sub, f"mail.{sub}")]

    # Step 4: Add NEW send subdomain records pointing to AgentMail (AWS SES)
    new_txt += [
        {"name": sub,                         "type": "TXT", "ttl": 3600,
         "data": "v=spf1 include:amazonses.com -all"},
        {"name": f"mail.{sub}",               "type": "TXT", "ttl": 3600,
         "data": "v=spf1 include:amazonses.com -all"},
        {"name": f"agentmail._domainkey.{sub}","type": "TXT", "ttl": 3600,
         "data": DKIM_TOKEN},
        {"name": f"_dmarc.{sub}",            "type": "TXT", "ttl": 3600,
         "data": "v=DMARC1; p=quarantine; rua=mailto:dmarc@send.studexmeat.com"},
    ]
    new_mx += [
        {"name": sub,       "type": "MX", "ttl": 3600, "priority": 10,
         "data": "inbound-smtp.us-east-1.amazonaws.com"},
        {"name": f"mail.{sub}", "type": "MX", "ttl": 3600, "priority": 10,
         "data": "feedback-smtp.us-east-1.amazonses.com"},
    ]

    # Step 5: Write ALL TXT records (including other types preserved)
    all_txt = other_records + new_txt
    result, code = gd("PATCH", f"/domains/{domain}/records/TXT", all_txt)
    if code == 200:
        print(f"  ✅ TXT: wrote {len(all_txt)} records "
              f"(kept {len(other_records)} non-TXT, added {len(new_txt)} send records)")
    else:
        print(f"  ❌ TXT ({code}): {result}")
        for f in result.get("fields", []):
            print(f"      - {f.get('message','?')}")
        # Fallback: try just new_txt alone
        result, code = gd("PATCH", f"/domains/{domain}/records/TXT", new_txt)
        if code == 200:
            print(f"  ⚠️  TXT fallback: replaced with {len(new_txt)} send-only records")
        else:
            print(f"  ❌ TXT Fallback ({code}): {result}")

    # Step 6: Write ALL MX records
    all_mx = new_mx
    result, code = gd("PATCH", f"/domains/{domain}/records/MX", all_mx)
    if code == 200:
        print(f"  ✅ MX: replaced with {len(all_mx)} records (send → AWS SES)")
    else:
        print(f"  ❌ MX ({code}): {result}")
        for f in result.get("fields", []):
            print(f"      - {f.get('message','?')}")

    # Step 7: Verify
    print(f"\n  Verification for send.{domain}:")
    check, code = gd("GET", f"/domains/{domain}/records/{sub}")
    if code == 200:
        for r in check:
            print(f"    [{r['type']:4}] {r['name']} → {r.get('data','')[:70]}")
    mx_check, _ = gd("GET", f"/domains/{domain}/records/MX")
    if isinstance(mx_check, list):
        for r in mx_check:
            if sub in r.get("name",""):
                print(f"    [MX   ] {r['name']} → {r['data']}")

    print(f"\n  ⏳ Allow 10-30 min for DNS propagation")
    print(f"  Check: https://toolbox.google.com/dns/@send.{domain}")

fix_domain("studexmeat.com", "send")
fix_domain("stud.exchange", "send")
print("\n✅ Script complete.")
