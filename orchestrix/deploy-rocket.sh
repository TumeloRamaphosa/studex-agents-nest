#!/usr/bin/env python3
"""
Deploy Rocket.Chat to the Orgo VM
Usage: python3 deploy-rocket.py
"""
import urllib.request
import urllib.error
import json
import base64
import time
import os

VM_API = "https://www.orgo.ai/api/computers/946b3156-cab9-4187-a94b-056dfab35105/bash"
HEADERS = {
    "Authorization": "Bearer sk_live_a101a846ce4584ebe8bf81eda212f1ead12d9c0e6fa11ef2",
    "Content-Type": "application/json"
}

def run(cmd):
    """Run a command on the VM and return output"""
    payload = json.dumps({"command": cmd}).encode()
    req = urllib.request.Request(VM_API, data=payload, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read().decode()
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        return f"ERR: {e}"

def write_file_remote(path, content):
    """Write a file to VM using Python on the other side"""
    encoded = base64.b64encode(content.encode()).decode()
    # Use python3 on remote to decode and write
    cmd = f"python3 -c \"import base64;open('{path}','wb').write(base64.b64decode('{encoded}'))\""
    return run(cmd)

def read_local(path):
    with open(path, 'r') as f:
        return f.read()

# Files to upload
war_room = "/workspace/studex-os/war-room"
files = {
    "/root/studex-os/war-room/docker-compose.yml": f"{war_room}/docker-compose.yml",
    "/root/studex-os/war-room/docker-compose.ssl.yml": f"{war_room}/docker-compose.ssl.yml",
    "/root/studex-os/war-room/Caddyfile": f"{war_room}/Caddyfile",
}

print("🚀 Deploying Rocket.Chat to VM...")

# Step 1: Create directory
print("📁 Creating directories...")
print(run("mkdir -p /root/studex-os/war-room && echo OK"))

# Step 2: Upload files
for remote_path, local_path in files.items():
    print(f"📤 Uploading {os.path.basename(remote_path)}...")
    content = read_local(local_path)
    result = write_file_remote(remote_path, content)
    if "Error" in result or "error" in result:
        print(f"  ⚠️  {result[:100]}")
    else:
        print(f"  ✅ Uploaded")

# Step 3: Check Docker
print("\n🐳 Checking Docker...")
print(run("docker --version && echo OK"))

# Step 4: Start Rocket.Chat
print("\n🚀 Starting Rocket.Chat (this takes 2-3 mins)...")
print(run("cd /root/studex-os/war-room && docker compose up -d && echo STARTED"))

# Step 5: Wait and check
print("\n⏳ Waiting 60 seconds for Rocket.Chat to start...")
time.sleep(60)

print("\n📋 Container status:")
print(run("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}"))

print("\n🌐 Rocket.Chat should be at: http://67.213.119.157:3000")
print("📋 Setup admin account at first launch")
