# CTO Department — Tech Stack & Development Playbook
_StudEx | March 2026_

---

## 🏗️ BMAD Methodology — How We Build

**BMAD = Build More Architect Dreams**
Open source | MIT License | 40,000+ GitHub stars
Repo: https://github.com/bmad-code-org/BMAD-METHOD

### What it is
BMAD is an AI-driven agile framework with 12+ specialized AI agents that collaborate to build software from idea to deployment. Instead of one AI doing everything, you have a team of agents:

| Agent | Role |
|-------|------|
| **PM (Product Manager)** | Requirements, prioritization, user stories |
| **Architect** | System design, tech decisions, ERD |
| **Developer** | Code, PRs, implementation |
| **UX Designer** | Wireframes, user flows, UI decisions |
| **Scrum Master** | Sprint planning, blockers, retrospectives |
| **Test Architect (TEA)** | Risk-based testing strategy |
| **+ 6 more** | Domain specialists |

### BMAD Workflow for CTO
```
1. Brief → PM agent creates PRD (Product Requirements Doc)
2. Architect designs system architecture + ERD
3. Dev tasks broken into sprint tickets
4. Developer agents implement with code review
5. Test Architect writes & runs test strategy
6. Deploy
```

### Install BMAD (non-interactive, CTO can set up):
```
npx bmad-method install --directory /project --modules bmm --tools claude-code --yes
```

---

## 🔍 CodeRabbit — Code Review

**What it does:**
- AI-powered PR code review (catches bugs humans miss)
- Integrates with GitHub at PR stage
- Generates unit tests, docstrings, architectural diagrams
- 40+ linters + security scanners built in
- Zero data retention post-review (SOC2 Type II)

**For our workflow:**
- Every PR on our GitHub repos gets auto-reviewed
- CodeRabbit reviews BEFORE human CTO reviews
- Catches issues early, especially in automation code

**Does it work with Ollama local models?**
No — CodeRabbit uses its own cloud AI. But for a LOCAL code review alternative, use **ollama + qwen2.5-coder** via a custom review script I can build.

---

## 💻 Ollama for Heavy Coding Tasks

Once Tailscale is connected (MacBook at 100.102.205.9):

**Best Ollama coding models (install these):**
```
ollama pull qwen2.5-coder:32b     # Best overall coding model
ollama pull deepseek-coder-v2     # Strong at complex tasks  
ollama pull codestral:22b         # Excellent for JS/Python
```

**How routing will work:**
- Light tasks (captions, content, quick answers) → My current model (fast, cheap)
- Heavy tasks (full app builds, complex architecture) → Route to Ollama via Tailscale
- This saves API costs and uses your local GPU power

**Fix needed first:**
Set `OLLAMA_HOST=0.0.0.0` on MacBook so Ollama listens on Tailscale interface.

---

## 📦 Skills for CTO Department

### 1. Perplexity Research (for Research Chief)
**What it does:** Real-time web search via Perplexity API. Gets live data with citations for research tasks.
**Needs:** Perplexity API key from https://perplexity.ai/settings/api
**Official MCP:** https://github.com/perplexityai/modelcontextprotocol
**Note:** This is a Claude Code skill. For OpenClaw, add Perplexity as an MCP tool server.

### 2. GitHub Integration
**What it does:** Full GitHub operations — create repos, manage PRs, review code, create issues, branches
**Official GitHub MCP:** https://github.com/github/github-mcp-server
**Needs:** GitHub Personal Access Token (classic, with repo scope)

### 3. Coding Agent Orchestrator
**What it does:** Orchestrates multiple coding subagents working in parallel — one handles frontend, one backend, one tests. Massively speeds up development.
**Use case:** Spawn 3 coding agents on a new feature simultaneously

### 4. OrderCLI / Food Delivery Skill
**IMPORTANT CLARIFICATION:** The ordercli skill is for ORDERING FOOD from Foodora (a European delivery app). It is NOT for building a delivery app.

**For building a Delivery/Uber-like app — here's the real plan:**

---

## 🚗 Delivery App — Build Plan (CTO Project)

### Stack Recommendation
| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React Native (Expo) | iOS + Android from one codebase |
| Backend | Supabase | Real-time order tracking, auth, DB |
| Maps | Google Maps API | Route + driver tracking |
| Payments | Yoco (SA) or Stripe | Local SA payment processing |
| Notifications | OneSignal | Push notifications (free tier) |
| Hosting | Vercel (web) + Expo (mobile) | Already using Vercel |

### Core Features (MVP)
- Customer: Browse, order, track in real time
- Driver: Accept orders, GPS tracking, earnings
- Admin: Orders dashboard, driver management, analytics

### For Store Order Tracking Specifically
Shopify Webhooks → N8n → Supabase → Real-time dashboard
No full app needed for tracking — just a Supabase table + simple React dashboard.

---

## 🏭 Automated App Warehouse — Client App Factory

**The concept:** Client fills Google Form → auto-builds their app

### Architecture
```
Google Form (client intake)
     ↓
N8n webhook trigger
     ↓
Classify request → match to template
     ↓
Spawn BMAD agents (PM + Architect + Dev)
     ↓
GitHub repo created from template
     ↓
Lovable.dev or Bolt.new for rapid prototyping
     ↓
CodeRabbit reviews code
     ↓
Deploy to Vercel/client domain
     ↓
Notify client on WhatsApp/Email
```

### Pre-built Template Library (to create)
| App Type | Template | Time to Deploy |
|----------|----------|----------------|
| Restaurant / takeaway | React + Supabase | 2 hours |
| Booking / appointments | Next.js + Cal.com | 2 hours |
| E-commerce store | Shopify / Next.js | 3 hours |
| Delivery tracking | React Native + Maps | 4 hours |
| Business dashboard | Next.js + Supabase | 2 hours |
| Landing page | Next.js + Vercel | 30 min |
| Portfolio | Astro + Vercel | 30 min |
| Community app | Next.js + Supabase Auth | 3 hours |

### Top App Requests (2026 Trends)
Based on market research:
1. **AI chatbot assistants** for businesses (WhatsApp bots, customer service)
2. **Delivery apps** (food, groceries, laundry)
3. **Booking apps** (salons, doctors, services)
4. **Loyalty/rewards apps** for local businesses
5. **Real estate listing apps**
6. **Event ticketing platforms**
7. **Freelancer marketplaces**
8. **Health tracking apps**

### Google Form Fields (Client Intake)
- Business name + industry
- App type (select from template list)
- Platforms needed (Web / iOS / Android / All)
- Key features (checkbox list)
- Budget range
- Timeline
- Design preference (upload logo/brand colors)
- Contact details

---

## 🗄️ Supabase vs Airtable vs Affine — When to Use What

| Tool | Best For | NOT for |
|------|----------|---------|
| **Affine** | Visual mind maps, planning sessions, whiteboard brainstorming | Production data |
| **Airtable** | Content calendar, simple tracking, non-technical team visibility | Large data, real-time |
| **Supabase** | Production database, real-time data, auth, APIs, app backends | Simple spreadsheet views |

### Our Recommended Setup
```
PLANNING LAYER:    Affine    → Whiteboard, mind maps, project planning
TRACKING LAYER:   Airtable  → Content calendar, campaigns, tasks
DATA LAYER:       Supabase  → Production data, orders, metrics, store data
```

**Supabase advantages over Airtable for scale:**
- Real-time subscriptions (order tracking updates live)
- PostgreSQL (proper relational DB with joins, queries)
- Built-in auth (user login system)
- Edge functions (serverless API endpoints)
- Storage (file uploads)
- Free tier: 2 projects, 500MB DB, 5GB storage
- 100x faster queries at scale
- Can power actual production apps

---

## ☁️ Google Drive vs Google Cloud Storage

**Your current setup:** Google Drive folders (personal/shared Drive)
- Drive: https://drive.google.com/drive/folders/1J_BnooZi-y3PN0eMyyLnD6MglVLEoC1j (content)
- Drive: https://drive.google.com/drive/folders/1ECixCejowMK--5ru8JMoP4PMY2BMigl5 (Naledi assets)

**Google Drive** = file sharing/storage for humans (like Dropbox)
**Google Cloud Storage** = programmatic file storage for apps (like AWS S3)

For Naledi content pipeline, **Drive is fine** for now. When we move to production automation, we'd switch to Google Cloud Storage or Supabase Storage for the generated images.
