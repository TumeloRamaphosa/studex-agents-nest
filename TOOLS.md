# TOOLS.md - Local Notes

## API Keys & Credentials

> Stored securely — never expose in logs or code

### Cloudflare
- **Account:** Tumelor001@gmail.com
- **Dashboard:** https://dash.cloudflare.com
- **API Token:** ❌ MISSING — needs to be created at: Cloudflare Dashboard → My Profile → API Tokens → Create Token
- **SSO Setup:** https://developers.cloudflare.com/fundamentals/manage-members/dashboard-sso/
- **Note:** `am_us_c900a...` key in original message was mislabeled — it's an AgentMail key, NOT Cloudflare

### Blotato
- **API Key:** `blt_y5mVD6oMJrgFb8UsfWN3T4GSYN2ZvCeGsVWWwdaf8Og=`
- **Base URL:** `https://backend.blotato.com/v2`
- **Auth header:** `blotato-api-key` (NOT Authorization Bearer)
- **Accounts endpoint:** `GET /users/me/accounts`
- **Post endpoint:** `POST /posts`
- **Status:** API confirmed working — 0 accounts connected, need to connect FB/IG inside Blotato dashboard

### Freepik
- **API Key:** `MS840e4cdb0fb842cdac06973ced3bef0b`
- **API Base:** `https://api.freepik.com/v1/`
- **Free tier:** 100 credits/month
- **Creds file:** `/workspace/robusca-brain/skills/studex-freepik-connector/FREEP IK_KEY.txt`

### AgentMail
- **API Key:** `am_us_24fcb06c6b1babba88c56d49b1a83fc33f1b8acf153acf3ef905136f335e7502`
- **API Base:** `https://api.agentmail.to/v0/`
- **Dashboard:** https://app.agentmail.to
- **Domain:** send.studexmeat.com (status: INVALID — DNS MISSING)
- **Domain:** stud.exchange (status: PENDING — DNS MISSING)

### Model Providers
| Service | API Key |
|---------|---------|
| Cursor | `rl_sk_0Sbp8XwG01JsLZeNSryRx7d_urMUxYtANNI-0OiRzls` |
| GitHub Copilot | `rl_sk_0Uz1k7CegkXlN4w77ON8ZpiC_uc2DBpUBKLpWi6SGdM` |
| Hermes | `rl_sk_VWTyPSoPW7zNz-CUjdfJZX44rYK6K7zCRHOLQeUj63I` |
| Anti Gravity | `rl_sk_0Uz1k7CegkXlN4w77ON8ZpiC_uc2DBpUBKLpWi6SGdM` |
| Claude | `rl_sk_0Uz1k7CegkXlN4w77ON8ZpiC_uc2DBpUBKLpWi6SGdM` |
| OpenClaw | `rl_sk_0Uz1k7CegkXlN4w77ON8ZpiC_uc2DBpUBKLpWi6SGdM` |
| Codex | `rl_sk_0Uz1k7CegkXlN4w77ON8ZpiC_uc2DBpUBKLpWi6SGdM` |
| Dyatona | `dtn_0ad29d3bdfb7b55f5f97985d2a6c1691e9cff1d8b6a745c76ae4620565887029` |

### Perplexity
- **API Key:** `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`
- **Status:** Active ✅

### Daytona
- **API Key:** `dtn_0ad29d3bdfb7b55f5f97985d2a6c1691e9cff1d8b6a745c76ae4620565887029`
- **Status:** API key added — capabilities unknown, needs investigation
- **Docs:** dyatona.ai (site not reachable — may be private/ invite-only)

### Tencent/Other
- **Tencent API (suspected):** `6cf598bbd026437ebd0b1b46b4c25ca9.VJazMWhK3RqkddYiVIUm9Ii3`

### Meta / Facebook
- **Facebook User Token:** `EAASNg25ZBOoUBRZCknSEm77CUwX7jJ7LJnZADwjZBtz0l1Dyv8FAZCvZCXbhagjkNMIhqZCL43fXMirzh6BGLGyNXttsHgOZBZAsVeC4i2cb1hHZCQFVZBQyLeeDxCDADZAp09hvV99Dgelrckxfvym6dKNIuRwpd7w3fghObZC0CeP9nbABGV7ZAWksZBn1ZCmcuiIAnKoR1OlZB0nG0s6IRMvULsiDv7XgE5f8ba5voCMnwZBb09cs8mn2yhMAxMTWovjDV64N6Kn7CFyZBJPW0YWW0O9N6qbBatPQFwYC3nDLtFu7LiCYg1Hc84v9Vwu1VqYQ3nm2Guw2wIsLkAl`
- **Facebook Page Token:** `EAASNg25ZBOoUBR8dT2diYUmUzfZAspz8r5aneEYoB8fZBBXFkyrFe459n1cZCXczTO4B994nS9F8QRLot1P0ocSsZCgjJpxZAQBwZCzp0vR9SbgSGKKKx7hqyBBBwsWfQTaZAZCWCtKH5GHxZCnOKQ81IKcAoWT9zzazLDK7w8JxmCHyvKyCE1DdfUwpk4N7x08Pfip4PW2WZBrBBEZCZBwKP4Fy4WjS5sKUIZBU1TJuge6zhAWAZDZD`
- **Facebook User ID:** `957514263586059` (Tumelo Ramaphosa)
- **Facebook Page:** `108934711902801` (StudEx Meat) — 2,544 fans — FULL ACCESS: ADVERTISE, CREATE_CONTENT, MESSAGING, MODERATE, MANAGE — POSTING ACTIVE ✅
- **WhatsApp Business Account:** `599570915061463` (StudEx Meat)
- **WhatsApp Business Account:** `749827870391669` (Studex Meat)
- **Meta App:** `1281495540841093` (Studex Content Analyser)

## Social / Platform Tokens
| Platform | Token |
|---------|-------|
| Discord Bot (MiniMax Claw) | `MTUwODk4NTc2MzEwMTAyMDI5MQ.GELgi6.whThc2OAVFjTiQF1xtfaBgaqOlv1-FgrBMivZY` |
| FeedHive | `fh_74b458c0bcd9317dd6019b1cae0c2ec608657fe3def408f4` |

---

## Orgo VM — StudEx Meat Auto Meat

| Field | Value |
|:---|:---|
| VM ID | `946b3156-cab9-4187-a94b-056dfab35105` |
| Connection URL | `https://www.orgo.ai/desktops/b454450e` |
| VNC Password | `f949611f6b891bbe` |
| SSH Access | `ssh root@67.213.119.157 -p <PORT>` (check Orgo dashboard) |
| Orgo API Key | `sk_live_a101a846ce4584ebe8bf81eda212f1ead12d9c0e6fa11ef2` |
| API Base | `https://www.orgo.ai/api/computers/{id}/bash` |
| Status | ✅ Running — accessed 2026-06-22 |
| RAM | 8GB / CPU 2 cores / 30GB disk |
| OS | Ubuntu — root access confirmed |
| Git Repo | `/root/robusca/robusca-brain/` (up to date ✅) |
| Desktop Shortcuts | warroom.desktop, chrome.desktop, terminal.desktop |
| Ports Running | 6080 (VNC), 5999 (Xvnc), 8080 (desktop-api) |

**How to execute commands on VM:**
```bash
curl -X POST "https://www.orgo.ai/api/computers/946b3156-cab9-4187-a94b-056dfab35105/bash" \
  -H "Authorization: Bearer sk_live_a101a846ce4584ebe8bf81eda212f1ead12d9c0e6fa11ef2" \
  -H "Content-Type: application/json" \
  -d '{"command":"ls /root"}'
```

---

## SSH Hosts

- **Orgo.ai VM (StudEx Meat Auto Meat):** `67.213.119.157` — Ubuntu, 2CPU/8GB RAM

---

## Platform Accounts

- **Cloudflare:** Tumelor001@gmail.com
- **AgentMail:** https://app.agentmail.to
- **FeedHive:** https://app.feedhive.com (free plan — needs setup)
- **GitHub:** github.com/TumeloRamaphosa
  - **PAT:** `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` (fine-grained, repo access)

---

## Agent Email Addresses

| Address | Agent | Status |
|---------|-------|--------|
| charlie@agent.studexmeat.com | Charlie orchestrator | 🔄 Setup pending |
| naledi@agent.studexmeat.com | Naledi CMO | 🔄 Setup pending |
| ceo@agent.studexmeat.com | Robusca (me) | 🔄 Setup pending |

---

## Preferred TTS Voice
- **Voice ID:** Nova (warm, slightly British)
- **Speaker:** Default

---

## Environment

- **Workspace:** /workspace/repos/studex-agents-nest (GitHub sync target)
- **VM:** Orgo.ai Ubuntu VM (2CPU/8GB)
- **OpenClaw Gateway:** Running on this MaxClaw instance

## New Keys Added Tonight
### ElevenLabs
- **API Key:** [REDACTED — stored in env as ELEVENLABS_API_KEY]
- Key: sk_93f872929e312224f4012da0709e8e18dfe53fdd0ae790b5
- Set in: /workspace/.env as ELEVENLABS_API_KEY

### NotebookLM
- Key link: https://makersuite.google.com/app/apikeys
- Status: NEEDS_KEY
