#!/usr/bin/env python3
"""
Deploy Rocket.Chat to VM via Orgo API
Writes files by streaming them as a heredoc via Python
"""
import urllib.request, urllib.error, json, time

VM = "https://www.orgo.ai/api/computers/946b3156-cab9-4187-a94b-056dfab35105/bash"
HEADERS = {"Authorization": "Bearer sk_live_a101a846ce4584ebe8bf81eda212f1ead12d9c0e6fa11ef2", "Content-Type": "application/json"}

def cmd(c):
    req = urllib.request.Request(VM, data=json.dumps({"command": c}).encode(), headers=HEADERS, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode()

files = {
    "/root/studex-os/war-room/docker-compose.yml": open("/workspace/studex-os/war-room/docker-compose.yml").read(),
    "/root/studex-os/war-room/docker-compose.ssl.yml": open("/workspace/studex-os/war-room/docker-compose.ssl.yml").read(),
    "/root/studex-os/war-room/Caddyfile": open("/workspace/studex-os/war-room/Caddyfile").read(),
}

print("🚀 Deploying Rocket.Chat to VM...")
r = cmd("mkdir -p /root/studex-os/war-room && echo OK")
print("mkdir:", r[:100])

# Upload files using Python on VM with content passed as argument
for path, content in files.items():
    # Escape content for shell, use python to write
    escaped = content.replace("\\", "\\\\").replace("'", "'\"'\"'").replace("\n", "\\n").replace("$", "\\$").replace("`", "\\`")
    write_cmd = f"python3 -c \"open('{path}','w').write('\\\"'\\\"'\\\"{escaped}\\\"'\\\"'\\\"')\" 2>&1 || echo FAILED"
    r = cmd(f"echo '{escaped}' > {path} && echo OK")
    print(f"write {path}:", r[:100])

# Start Rocket.Chat
print("\n🚀 Starting docker compose...")
r = cmd("cd /root/studex-os/war-room && docker compose up -d 2>&1 && echo STARTED")
print(r[-300:] if len(r)>300 else r)

print("\n⏳ Waiting 90s for Rocket.Chat to start...")
time.sleep(90)

print("\n📋 Status:")
print(cmd("docker ps --format '{{.Names}}\t{{.Status}}' 2>&1"))
print("\n🌐 http://67.213.119.157:3000")
print("Admin: admin@studexmeat.com / StudexMeat2026")
