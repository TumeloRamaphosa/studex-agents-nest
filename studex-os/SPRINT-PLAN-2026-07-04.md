# STUDEX — 2-Hour Sprint Plan
**Date:** July 4, 2026 | **Time:** 17:14 SAST | **Window:** Now → 19:14 SAST

---

## ✅ Already Done Before Sprint

- [x] Rwanda Coffee Proposal PDF — `/workspace/studex-os/proposals/rwanda-offer-PROWTC-2026-07.pdf`
- [x] Rwanda Coffee Proposal PDF uploaded to CDN
- [x] War Room underwater datacenter deployed — https://uru0on54sv4k.space.minimax.io
- [x] TenacitOS Mission Control deployed — http://67.213.119.157:3500
- [x] Claude SEO installed on VM
- [x] Ollama local AI running (qwen3:4b)
- [x] GitHub CLI installed on VM
- [x] All workspace files staged and committed locally

---

## 🟡 NEED TUMELO — Actions Required From You

### 1. GitHub Token — 2 min (CRITICAL)
```
Go to: https://github.com/settings/tokens/new
Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
Generate new token → ✅ repo scope only → Generate
Copy token → paste to me in chat
```
Once provided → I push all commits in 30 seconds.

### 2. Cloudflare DNS for send.studexmeat.com — 10 min
```
Add these DNS records at Cloudflare for send.studexmeat.com:

MX:    @ → mail.agentmail.to (priority 10)
TXT:   @ → v=spf1 include:agentmail.to ~all
TXT:   _dmarc → v=DMARC1; p=quarantine; rua=mailto:dmarc@studex-group.com
```
This enables emails from robusca@agent.studexmeat.com

### 3. Notion API Key — 5 min
```
Go to: https://www.notion.so/my-integrations
New integration → Name: "Robusca OS" → Submit
Copy the Internal Integration Token → paste to me
```
This connects Notion to our operating system.

### 4. NotebookLM Auth — 5 min
On your Mac terminal:
```bash
cd ~/notebooklm-skill && python3 -m notebooklm login
# browser opens → sign into Google → done
```
Tell me when done. Then I can query your notebook directly.

### 5. AgentMail — Which inbox has the email from the other agent?
```
Robusca inbox: oddgas768@agentmail.to
Naledi inbox: cooperativeinspiration780@agentmail.to
```
Tell me which inbox has the email and I'll read it.

---

## 🚀 What I Will Do During Sprint

### MIN 0-10: GitHub Push (once token provided)
- Auth gh CLI with token
- Push all workspace commits
- Set up GitHub remote properly

### MIN 10-30: Rocket.Chat Deployment
- Docker install running in background on VM (if Docker works)
- OR: Deploy Rocket.Chat via native install if Docker unavailable
- Rocket.Chat URL: http://67.213.119.157:3000

### MIN 30-50: NotebookLM Video Workflow
- Analyze video from URL
- Generate infographic image
- Build slide deck presentation
- Deploy both for sharing

### MIN 50-70: AgentMail Investigation
- Check all inboxes for new messages
- Read email from other agent
- Attempt to send proposal via AgentMail API

### MIN 70-90: Notion Integration
- Connect Notion API once token provided
- Set up operating system workspace in Notion
- Link to War Room and TenacitOS

### MIN 90-120: Workspace Organization + Sprint Summary
- Write sprint document
- Update all memory files
- Push everything to GitHub
- Create NEXT SPRINT plan

---

## 📊 Business Operating System — Architecture

```
Tumelo (You)
    ↓
┌─────────────────────────────────────────────────────┐
│              STUDENT OS (This System)               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │ War Room    │  │ TenacitOS    │  │ Notion   │  │
│  │ 3D datacenter│  │ Agent Office  │  │ Workspace│  │
│  └─────────────┘  └──────────────┘  └──────────┘  │
│                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │ Claude SEO  │  │ Rocket.Chat  │  │ GitHub   │  │
│  │ 25 agents   │  │ Team Chat    │  │ Code     │  │
│  └─────────────┘  └──────────────┘  └──────────┘  │
│                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │ Ollama      │  │ AgentMail    │  │ Notebook │  │
│  │ Local AI    │  │ Email/Chat   │  │ LM       │  │
│  └─────────────┘  └──────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────┘
    ↓
Orgo VM (67.213.119.157) — all services run here
```

---

## 🎯 Sprint Goals — What "Done" Looks Like

By 19:14 SAST:
- [ ] GitHub pushing — all workspace commits live
- [ ] Rocket.Chat deployed and accessible
- [ ] Proposal PDF sent via AgentMail
- [ ] Email from other agent read and actioned
- [ ] NotebookLM video → infographic + slide deck deployed
- [ ] Notion OS connected (if API key provided)
- [ ] Sprint summary written and pushed to GitHub

---

## ⚠️ Blockers

| Blocker | Owner | Status |
|---|---|---|
| GitHub token | Tumelo | ⏳ Waiting |
| Docker daemon | VM | 🔄 Installing |
| Cloudflare DNS | Tumelo | ⏳ Waiting |
| Notion API key | Tumelo | ⏳ Waiting |
| AgentMail inbox | Tumelo | ⏳ Waiting |
| NotebookLM auth | Tumelo (Mac) | ⏳ Waiting |

---

*This document is the sprint contract. Updated at start and end of sprint.*
