#!/usr/bin/env python3
"""Write docker-compose.yml to VM and start Rocket.Chat"""
import urllib.request, urllib.error, json, time

VM = "https://www.orgo.ai/api/computers/946b3156-cab9-4187-a94b-056dfab35105/bash"
H = {"Authorization": "Bearer sk_live_a101a846ce4584ebe8bf81eda212f1ead12d9c0e6fa11ef2", "Content-Type": "application/json"}

def run(cmd):
    req = urllib.request.Request(VM, data=json.dumps({"command": cmd}).encode(), headers=H, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read().decode()
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        return f"ERR: {e}"

compose = r"""version: "3.8"
networks:
  studex-net:
    driver: bridge
volumes:
  mongo-data:
    driver: local
services:
  mongo:
    image: mongo:6.0
    container_name: rocketchat_mongo
    restart: unless-stopped
    networks:
      - studex-net
    volumes:
      - mongo-data:/data/db
    mem_limit: 1g
    cpus: 0.5
  rocketchat:
    image: rocketchat/rocket.chat:7
    container_name: rocketchat_server
    restart: unless-stopped
    depends_on:
      mongo:
        condition: service_healthy
    networks:
      - studex-net
    volumes:
      - uploads:/app/uploads
    environment:
      MONGO_URL: mongodb://mongo:27017/rocketchat
      ROOT_URL: http://67.213.119.157:3000
      PORT: "3000"
      BIND_IP: 0.0.0.0
      ADMIN_USERNAME: admin
      ADMIN_EMAIL: admin@studexmeat.com
      ADMIN_PASS: StudexMeat2026
      NODE_ENV: production
    mem_limit: 2g
    cpus: 1.0
    ports:
      - "0.0.0.0:3000:3000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/info"]
      interval: 30s
      timeout: 10s
      retries: 10
      start_period: 120s
  caddy:
    image: caddy:2-alpine
    container_name: rocketchat_caddy
    restart: unless-stopped
    networks:
      - studex-net
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy-data:/data
      - caddy-config:/config
    ports:
      - "0.0.0.0:80:80"
      - "0.0.0.0:443:443"
    environment:
      DOMAIN: warroom.studexmeat.com
      ADMIN_EMAIL: ceo@studexmeat.com
    mem_limit: 256m
    cpus: 0.25
volumes:
  uploads:
    driver: local
  caddy-data:
    driver: local
  caddy-config:
    driver: local
"""

# Write the compose file using Python on the VM
write_script = f"""python3 -c \"
import os
os.makedirs('/root/studex-os/war-room', exist_ok=True)
with open('/root/studex-os/war-room/docker-compose.yml', 'w') as f:
    f.write({repr(compose)})
print('WRITTEN')
\""""

print("📤 Writing docker-compose.yml to VM...")
r = run(write_script)
print("Result:", r[:200])

# Check Docker
print("\n🐳 Docker status...")
print(run("docker ps 2>&1 | head -5"))

# Start containers
print("\n🚀 Starting Rocket.Chat...")
print(run(
    "cd /root/studex-os/war-room && "
    "nohup docker compose up -d > /tmp/rc.log 2>&1 & "
    "sleep 5 && docker ps 2>&1 | head -5 && "
    "echo STARTED_OK"
))

print("\n⏳ Waiting 90s for startup...")
time.sleep(90)

print("\n📋 Final status:")
print(run("docker ps --format '{{.Names}}\\t{{.Status}}' 2>&1"))
print("\n🌐 http://67.213.119.157:3000")
print("Admin login: admin@studexmeat.com / StudexMeat2026")
