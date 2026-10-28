# RocketChat Deploy Script — Orgo VM
**Created:** 2026-07-03

## Deploy RocketChat on Orgo VM

SSH into your Orgo VM and run:

```bash
# SSH into Orgo VM
ssh root@67.213.119.157 -p <PORT>

# Navigate to apps directory
cd /root

# Create RocketChat directory
mkdir -p rocket.chat && cd rocket.chat

# Download docker-compose.yml
curl -LO https://raw.githubusercontent.com/RocketChat/Rocket.Chat/develop/docker-compose.yml

# Edit environment vars
export ROOT_URL="https://chat.studexmeat.com"
export MONGO_URL="mongodb://mongo:27017/rocketchat"
export PORT=3000

# Start RocketChat
docker-compose up -d

# Check logs
docker-compose logs -f rocketchat
```

## Domain Setup (Cloudflare)
Add these DNS records:
- **A record:** `chat.studexmeat.com` → `67.213.119.157`
- **CNAME:** `chat` → your Orgo VM IP

## Nginx Reverse Proxy (on Orgo VM)
```nginx
# /etc/nginx/sites-available/chat.studexmeat.com
server {
    listen 80;
    server_name chat.studexmeat.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name chat.studexmeat.com;

    ssl_certificate /etc/letsencrypt/live/chat.studexmeat.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/chat.studexmeat.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Agent Setup in RocketChat
1. Create agent accounts: charlie, naledi, coffee-jarvis, rileyjarvis
2. Create channels: #ops, #coffee, #alerts, #content, #orders, #dev
3. Get API token:
```bash
curl -X POST https://chat.studexmeat.com/api/v1/login \
  -d "username=charlie&password=CHANGEME"
```
4. Add tokens to TOOLS.md

## Embed in OS
Once deployed, replace the placeholder with:
```html
<iframe 
  src="https://chat.studexmeat.com"
  style="width:100%;height:600px;border:none;">
</iframe>
```
