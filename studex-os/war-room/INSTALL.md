# War Room Installation Guide — Rocket.Chat on Orgo VM
**Studex Meat OS — War Room Messaging Platform**

---

## Prerequisites

- Orgo.ai VM: `67.213.119.157` (Ubuntu, 2 vCPU, 8GB RAM)
- Orgo API Key: `sk_live_a101a846ce4584ebe8bf81eda212f1ead12d9c0e6fa11ef2`
- Orgo VM ID: `946b3156-cab9-4187-a94b-056dfab35105`
- SSH port: check Orgo dashboard at `https://www.orgo.ai/desktops/b454450e`

---

## Step 1 — SSH into VM and Check Environment

```bash
# Run on your local machine to get the SSH port from Orgo dashboard
curl -s "https://www.orgo.ai/api/computers/946b3156-cab9-4187-a94b-056dfab35105" \
  -H "Authorization: Bearer sk_live_a101a846ce4584ebe8bf81eda212f1ead12d9c0e6fa11ef2"

# SSH in (replace PORT with value from Orgo dashboard)
ssh root@67.213.119.157 -p PORT

# Inside VM: check resources
free -h && df -h / && nproc
# Expected: ~8GB RAM, 2 CPUs, 30GB disk
```

---

## Step 2 — Install Docker & Docker Compose (if not present)

```bash
# SSH into VM first, then run:
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker
docker --version        # Should be 24.x+
docker compose version  # Should be 2.x+

# Add Docker group (so you don't need sudo for docker commands)
usermod -aG docker root
```

---

## Step 3 — Clone / Update Studex OS Repo

```bash
# On VM:
cd /root
git clone https://github.com/TumeloRamaphosa/studex-os.git || \
  (cd /root/studex-os && git pull origin main)

cd /root/studex-os/war-room
ls -la
# Expected: INSTALL.md, docker-compose.yml, BRANDING.md, bot-integration.md
```

---

## Step 4 — Configure Environment Variables

Create a `.env` file in `/root/studex-os/war-room/`:

```bash
cat > /root/studex-os/war-room/.env << 'EOF'
# =============================================
# Rocket.Chat — Studex Meat OS War Room
# =============================================

# MongoDB (embedded in Rocket.Chat image — minimal config)
MONGO_URI=mongodb://mongo:27017/rocketchat

# Rocket.Chat Admin
ADMIN_USERNAME=tummebox
ADMIN_EMAIL=ceo@agent.studexmeat.com
ADMIN_PASS=CHANGE_ME_SECURE_PASSWORD_123!

# Rocket.Chat URL (replace with your domain or IP)
ROOT_URL=http://67.213.119.157:3000
PORT=3000

# SMTP (for email notifications — use Mailgun/SES or AgentMail)
# Get credentials from AgentMail dashboard: https://app.agentmail.to
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@mg.studexmeat.com
SMTP_PASSWORD=YOUR_SMTP_PASSWORD_HERE
SMTP_FROM=studex-war-room@studexmeat.com

# Caddy (auto-SSL via Let's Encrypt — set domain below)
DOMAIN=warroom.studexmeat.com
ADMIN_EMAIL_SSL=ceo@studexmeat.com

# File Storage (local for now; can switch to MinIO/S3 later)
UPLOAD_STORAGE_TYPE=GridFS

# Deploy with Caddy reverse proxy for SSL
DEPLOY_PLATFORM=caddy
EOF
```

> ⚠️ **Change `ADMIN_PASS`** to a strong password before running `docker compose up -d`.

---

## Step 5 — Pull and Start Rocket.Chat + MongoDB

```bash
cd /root/studex-os/war-room

# Pull images (run on VM)
docker compose pull

# Start in detached mode
docker compose up -d

# Watch logs until Rocket.Chat is ready (~2–3 minutes on first start)
docker compose logs -f rocketchat

# Press Ctrl+C once you see:
#   "Server startup complete. Port:3000"
```

**Expected resource usage:**
- MongoDB: ~500MB–1GB RAM
- Rocket.Chat: ~500MB–1.5GB RAM
- Total: ~1–2.5GB RAM (well within 8GB)

---

## Step 6 — Initial Admin Setup (Web Wizard)

1. Open browser: `http://67.213.119.157:3000`
2. Admin account page appears automatically on first run
3. Fill in:
   - **Full Name:** Meat B@ye
   - **Username:** tummebox
   - **Email:** `ceo@agent.studexmeat.com`
   - **Password:** (your strong password)
4. Click **"Create Account"**
5. Agree to terms → **"Stay logged in"**

---

## Step 7 — Admin Panel: Apply Kanan Band Branding

Navigate to: `http://67.213.119.157:3000/admin/settings`

### 7.1 General Settings
- **Site Name:** Studex Meat War Room
- **Site URL:** `http://67.213.119.157:3000`
- **Tagline:** "Premium Halal Meat — South Africa"

### 7.2 Logo Upload
Go to `http://67.213.119.157:3000/admin/settings/Layout#Assets`
- Upload **Studex Meat logo** (transparent PNG, 256×256 recommended)
- Upload **favicon** (red/gold Studex icon)

### 7.3 Live CSS Customization
Go to `http://67.213.119.157:3000/admin/settings/Layout#CustomCSS`

Paste the full CSS from `BRANDING.md` → Section: "Admin Panel CSS Injection" (live CSS editor).

Click **"Save Changes"** — theme applies instantly.

---

## Step 8 — Create War Room Channels

Navigate to: `http://67.213.119.157:3000/admin/rooms`

Create each room with the settings below:

| Room Name | Type | Description | Auto-join |
|---|---|---|---|
| `war-room` | Public Channel | Main ops hub — all agents + Tumelo | All |
| `orders` | Private Channel | Charlie → Shopify order alerts | charlie, robusca, tummebox |
| `delivery` | Private Channel | Delivery Agent → delivery status updates | delivery-agent, robusca, tummebox |
| `marketing` | Private Channel | Naledi → content published alerts | naledi, robusca, tummebox |
| `ceo` | Private Channel | Robusca → daily CEO briefings | robusca, tummebox |
| `alerts` | Private Channel | Critical escalations only | All |

### Alternative: Create via Rocket.Chat CLI

SSH into VM and run:

```bash
docker exec -it rocketchat_mongo mongo

# Inside mongo shell:
use rocketchat
db.rocketchat_room.insertMany([
  { name: "war-room", t: "c", default: true, msgs: 0, ts: new Date(), customFields: {} },
  { name: "orders", t: "p", default: false, msgs: 0, ts: new Date(), customFields: {} },
  { name: "delivery", t: "p", default: false, msgs: 0, ts: new Date(), customFields: {} },
  { name: "marketing", t: "p", default: false, msgs: 0, ts: new Date(), customFields: {} },
  { name: "ceo", t: "p", default: false, msgs: 0, ts: new Date(), customFields: {} },
  { name: "alerts", t: "p", default: false, msgs: 0, ts: new Date(), customFields: {} }
])
exit
```

Then invite members via UI: Room → 🔧 Settings → **Add Members**

---

## Step 9 — Create Bot Accounts

Go to: `http://67.213.119.157:3000/admin/users`

Create each bot account (set **"Join default channels"** = OFF for bots):

| Username | Display Name | Email | Password |
|---|---|---|---|
| `charlie` | Charlie Orchestrator | charlie@agent.studexmeat.com | `CHANGEME_charlie_bot_pass` |
| `naledi` | Naledi CMO | naledi@agent.studexmeat.com | `CHANGEME_naledi_bot_pass` |
| `delivery-agent` | Delivery Agent | delivery@agent.studexmeat.com | `CHANGEME_delivery_bot_pass` |
| `robusca` | Robusca AI | robusca@agent.studexmeat.com | `CHANGEME_robusca_bot_pass` |

For each bot account:
1. Create user → **"Bot"** role toggle
2. Copy the **Personal Access Token** from: User → **Profile** → **Tokens**
3. Store tokens securely in VM env or `/root/.env`:
```bash
# Add to /root/studex-os/war-room/.env
ROCKETCHAT_CHARLIE_TOKEN=your_token_here
ROCKETCHAT_NALEDI_TOKEN=your_token_here
ROCKETCHAT_DELIVERY_TOKEN=your_token_here
ROCKETCHAT_ROBUSCA_TOKEN=your_token_here
ROCKETCHAT_BOT_URL=http://localhost:3000
```

---

## Step 10 — Connect OpenClaw via Webhook

Go to: `http://67.213.119.157:3000/admin/integrations`

### Option A: Incoming Webhook (for agents → Rocket.Chat)
1. Create **Incoming Webhook**
2. Channel: `#war-room`
3. Bot name: `Robusca`
4. Copy the **Webhook URL**: `http://67.213.119.157:3000/hooks/TOKEN/TOKEN`
5. Add to OpenClaw config as a notification endpoint

### Option B: Bot User (for OpenClaw → Rocket.Chat)
Use Rocket.Chat's REST API with a bot user token:

```bash
# Test the API from VM
curl -H "X-Auth-Token: YOUR_BOT_TOKEN" \
     -H "X-User-Id: YOUR_BOT_USER_ID" \
     http://localhost:3000/api/v1/me
# Should return: {"status":"success","data":{...}}
```

### Option C: Full Bot SDK (Node.js)
See `bot-integration.md` for complete bot integration code.

---

## Step 11 — Configure Notifications

Go to: `http://67.213.119.157:3000/admin/settings/Notifications`

### Global Notification Rules
- **Desktop notifications:** All messages (War Room), Mentions only (other channels)
- **Mobile push:** All direct messages, @mentions in all channels
- **Sound:** On for all, volume 80%

### Per-Channel Rules (Tumelo sets these for himself)
In `#orders`: Desktop notification = All messages
In `#delivery`: Desktop notification = All messages
In `#marketing`: Desktop notification = Mentions only
In `#ceo`: Desktop notification = All messages + push
In `#alerts`: Desktop notification = All messages + push

### Auto-ping: When Charlie posts in #orders → Robusca gets @mention
Charlie bot should send messages formatted as:
```
@robusca New order alert! See #orders for details.
```
This ensures Robusca gets a push notification.

---

## Step 12 — Restrict Registration (No Public Signups)

Go to: `http://67.213.119.157:3000/admin/settings/General`

```
Allow new user registration from outside: DISABLED ✅
Allow user self-registration: DISABLED ✅
Require name for registration: ENABLED ✅
```

Only Tumelo (admin) can create accounts manually.

---

## Step 13 — Mobile App Setup (iOS/Android)

### iOS
1. Download **Rocket.Chat** from App Store
2. Server URL: `http://67.213.119.157:3000` (or domain)
3. Login with:
   - **Tumelo:** `tummebox` / `your_password`
   - **Robusca:** `robusca` / `robusca_bot_pass`
   - etc.

### Android
1. Download **Rocket.Chat** from Google Play
2. Same login process as iOS

### MDM / Bulk Enrolment
For more than 5 users, generate invitation links:
- Admin → Users → **"Send invitation email"** → paste email addresses

> ⚠️ If using self-signed SSL on the VM, you may need to:
> - On iOS: Settings → About → Certificate Trust Settings → Enable full trust for `67.213.119.157`
> - Or set up a proper domain with Let's Encrypt (Step 14)

---

## Step 14 — Set Up SSL / Domain (Recommended)

### Option A: Caddy (Recommended — auto-Let's Encrypt)
Update `docker-compose.yml` to include Caddy, then:

```bash
# Update .env with your domain
DOMAIN=warroom.studexmeat.com

# Restart with Caddy
cd /root/studex-os/war-room
docker compose -f docker-compose.yml -f docker-compose.ssl.yml up -d
```

Caddy automatically provisions and renews Let's Encrypt certificates.

### Option B: Manual Let's Encrypt (nginx)
```bash
# Install certbot
snap install --classic certbot
certbot --nginx -d warroom.studexmeat.com

# This generates certs, then configure nginx manually
```

### DNS Setup for Domain
```
Type: A    Name: warroom    Value: 67.213.119.157    TTL: 3600
Type: TXT  Name: warroom    Value: "v=spf1 include:mailgun.org ~all"
```

---

## Step 15 — Firewall Configuration

On the VM, configure UFW:

```bash
# On VM (SSH in first):
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp      comment 'SSH (Orgo console)'
ufw allow 80/tcp      comment 'HTTP'
ufw allow 443/tcp     comment 'HTTPS'
ufw allow 3000/tcp    comment 'Rocket.Chat (temporary, remove after proxy setup)'
ufw enable
ufw status verbose
```

After Caddy/nginx proxy is set up, **remove port 3000** from the firewall — all traffic should go through 443:

```bash
ufw delete allow 3000/tcp
```

---

## Step 16 — Verify Installation

```bash
# SSH into VM and run:
docker compose -f /root/studex-os/war-room/docker-compose.yml ps
# All services should show "Up"

curl -s http://localhost:3000/api/v1/info | jq .version
# Should return Rocket.Chat version

# Check logs for errors
docker compose -f /root/studex-os/war-room/docker-compose.yml logs --tail=50
```

---

## Step 17 — Connect Charlie (Shopify Webhook → Rocket.Chat)

Charlie bot (running on MaxClaw at port 3001) can POST to Rocket.Chat:

```javascript
// In Charlie's webhook handler (Shopify → Rocket.Chat)
const ROCKET_CHAT_TOKEN = process.env.ROCKETCHAT_CHARLIE_TOKEN;
const ROCKET_CHAT_USER_ID = process.env.ROCKETCHAT_CHARLIE_USER_ID;

async function postToWarRoom(order) {
  const channel = order.fulfillment_status === 'urgent' ? '#alerts' : '#orders';
  await fetch(`http://67.213.119.157:3000/api/v1/chat.postMessage`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Auth-Token': ROCKET_CHAT_TOKEN,
      'X-User-Id': ROCKET_CHAT_USER_ID,
    },
    body: JSON.stringify({
      channel: channel,
      text: `📦 *New Shopify Order*\n\nOrder #${order.id}\nCustomer: ${order.customer.first_name} ${order.customer.last_name}\nTotal: R${order.total_price}\nStatus: ${order.fulfillment_status}\n\n@robusca @tummebox`,
      alias: 'Charlie',
      emoji: ':robot_face:',
    }),
  });
}
```

Full bot code examples: see `bot-integration.md`

---

## Step 18 — Daily Briefings (Robusca → #ceo)

Robusca can post a daily briefing via cron (set in OpenClaw):

```javascript
// Robusca daily briefing cron — 08:00 SAST (06:00 UTC)
cron.schedule('0 6 * * *', async () => {
  const briefing = await generateDailyBriefing();
  
  await fetch(`http://67.213.119.157:3000/api/v1/chat.postMessage`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Auth-Token': process.env.ROCKETCHAT_ROBUSCA_TOKEN,
      'X-User-Id': process.env.ROCKETCHAT_ROBUSCA_USER_ID,
    },
    body: JSON.stringify({
      channel: '#ceo',
      text: briefing,
      alias: 'Robusca',
      emoji: ':sun_with_face:',
    }),
  });
});
```

---

## Troubleshooting

### Rocket.Chat won't start
```bash
docker compose logs rocketchat | tail -30
docker compose restart rocketchat
```

### MongoDB is the bottleneck
```bash
docker compose restart mongo
# Wait 30 seconds, then restart rocketchat
docker compose restart rocketchat
```

### Can't access from browser
```bash
# Check firewall on VM
ufw status
# Check Rocket.Chat is listening on all interfaces
docker exec rocketchat_net cat /app/rocketchat/etc Rocket.Chat Rocket.Chat.json | grep -i bind
# Should show 0.0.0.0, not 127.0.0.1
```

### Bot API returns 401 Unauthorized
- Verify token hasn't expired (Rocket.Chat tokens can expire)
- Regenerate token: Admin → Users → Bot User → Regenerate Token

### Mobile app can't connect
- Check SSL certificate (if using self-signed, add cert to device)
- Best fix: Set up Caddy with Let's Encrypt (Step 14)
- Alternative: Allow HTTP in Rocket.Chat admin: `Admin → Settings → General → Force SSL = Off`

---

## Backup Strategy

```bash
# On VM — daily backup of MongoDB
cat >> /root/crontab << 'EOF'
# Studex Meat OS — Rocket.Chat backup (daily at 03:00 SAST)
0 3 * * * docker exec rocketchat_mongo mongodump --archive=/dump/backup_$(date +\%Y\%m\%d).archive --gzip && cp /var/lib/docker/volumes/war-room_mongo_data/_data/backup_$(date +\%Y\%m\%d).archive /root/backups/
EOF
crontab /root/crontab
mkdir -p /root/backups
```

---

## Uninstallation

```bash
# To completely remove:
cd /root/studex-os/war-room
docker compose down -v   # ⚠️ -v DELETES all data including messages
docker rmi $(docker images | grep rocket)
# Then remove from git if desired:
# cd /root/studex-os && git rm -rf war-room && git commit -m "remove war-room"
```
