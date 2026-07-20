# StudEx Content Pipeline — Unified Dashboard
## Built by Amara | Status: Building

---

## 🎯 What We're Building

A unified **StudEx Content OS** — a single dashboard that connects ALL your tools, agents, and content flows in one place:

```
Tumelo + Agents ←→ Content Pipeline OS ←→ All Connected Tools
```

---

## 🔗 Your Current API Stack

| Service | Key | Status | Purpose |
|---|---|---|---|
| **Blotato** | ✅ Connected | 6 accounts | Publishing |
| **Freepik** | `MS840e4cdb0fb842cdac06973ced3bef0b` | ✅ Ready | Image generation |
| **Higgsfield** | 🔴 No key yet | Needs setup | Video/image AI creatives |
| **Meta/Facebook** | ✅ Tokens in TOOLS.md | Partial | Facebook + Instagram |
| **Shopify** | 🔴 No token | Needs setup | Order + product data |
| **AgentMail** | ✅ Connected | 4 inboxes | Email for agents |
| **VAPI** | 🔴 No key | Needs setup | Voice calls + meetings |
| **ClickClack** | 🔴 Not deployed | Needs VM | Internal agent chat |
| **CORE OS** | 🔴 Not deployed | Needs VM | Agent OS layer |
| **Agent-Reach** | ✅ Cloned | Not wired | 13-platform web access |
| **ffmpeg-wasm** | ✅ Cloned | Not wired | Video processing |
| **Ollama** | 🔴 No VM | Blocked | Local model inference |

---

## 🗣️ Voice System — VAPI Architecture

### Individual Agent Calls
```
Tumelo calls VAPI number
    ↓
VAPI routes to specific agent (Robusca / Naledi / Auto-Meat / Hermes)
    ↓
Agent answers with their persona + voice
    ↓
Call transcribed in real-time
    ↓
Saved to Obsidian vault at: /calls/YYYY-MM-DD/[agent-name].md
    ↓
Key decisions extracted → action items → ClickClack #general
```

### War Room Meeting (Multi-Agent Squad)
```
Tumelo calls VAPI War Room number
    ↓
VAPI Squad starts — Robusca as coordinator
    ↓
Robusca briefs: overnight activity, orders, content queue
    ↓
Tumelo can interrupt + direct specific agents
    ↓
Full transcript saved → /calls/YYYY-MM-DD/war-room-[timestamp].md
    ↓
Meeting summary → Posted to ClickClack #general + Obsidian
```

### VAPI Setup Steps
1. Go to https://vapi.ai → Sign up (free tier = 5 assistants)
2. Get API key from Dashboard
3. Get a phone number (VAPI provides one free)
4. Create assistants for: Robusca, Naledi, Auto-Meat, Hermes
5. Create a Squad called "War Room"
6. Give Amara the API key → I'll configure everything

---

## 🧠 RAG Architecture — Super Brain

### What is RAG?
**Retrieval-Augmented Generation** = when an AI answers, it first searches your knowledge base, then generates. Means Charlie, Robusca, Naledi all answer based on YOUR data — not generic knowledge.

### The Stack We're Building
```
StudEx Obsidian Vault (raw notes)
    ↓ + Robusca Brain (docs)
    ↓ + War Room Data (call transcripts)
    ↓ + Shopify Orders (structured data)
    ↓ + AgentMail (communications)
    ↓ + All past campaigns
    ↓
ChromaDB Vector Database (indexed embeddings)
    ↓
Query Engine per Agent (Ollama or cloud model)
    ↓
Each agent answers with YOUR context
```

### Best RAG Tools Evaluated

| Tool | Pros | Cons | Verdict |
|---|---|---|---|
| **ChromaDB** | Simple, local, fast | Limited scalability | ✅ Use for now |
| **LlamaIndex** | Powerful, flexible | More setup | ✅ Use with Chroma |
| **Qdrant** | Cloud-native, production | Extra infra | Save for later |
| **Pinecone** | Managed, reliable | Expensive, vendor lock | ❌ Avoid |
| **Weaviate** | Graph RAG | Heavy | ❌ Avoid for now |
| **Ollama + nomic-embed-text** | Free, local, private | Needs good hardware | ✅ Use on VM |

### Our RAG Pipeline
```
Obsidian Vault (markdown files)
    ↓
Ollama Embedding Model (nomic-embed-text)
    ↓
ChromaDB Collection: studex-brain
    ↓
Query: "what orders came in yesterday?"
    ↓
ChromaDB similarity search → relevant docs
    ↓
Context injected into agent's system prompt
    ↓
Agent answers with full context
```

---

## 📱 Our Own Blotato — StudEx Content OS

### Why Build Our Own?
- Blotato is a third-party middleman — if it goes down, your publishing stops
- No API = no permanent connection = tokens expire = you lose access
- Own platform = you control the connections permanently
- ALL your tools integrated: Freepik + Higgsfield + Meta + more

### Architecture
```
┌─────────────────────────────────────────────────────┐
│           StudEx Content OS (React Dashboard)           │
│  [Create] [Schedule] [Publish] [Analytics] [Pipeline]   │
└──────────────────┬──────────────────────────────────┘
                   │
     ┌─────────────┼─────────────┐
     ↓             ↓             ↓
┌─────────┐  ┌──────────┐  ┌──────────┐
│ Freepik │  │Higgsfield│  │  Meta    │
│  Image  │  │  Video   │  │ Facebook │
│  Gen    │  │  AI      │  │  + IG    │
└────┬────┘  └────┬─────┘  └────┬─────┘
     ↓             ↓             ↓
┌─────────────────────────────────────────┐
│          Content Pipeline (Node.js)          │
│  AI generates caption → Image/Video → Post  │
└──────────────────────┬──────────────────┘
                       ↓
         ┌─────────────┼─────────────┐
         ↓             ↓             ↓
    ┌─────────┐  ┌──────────┐  ┌──────────┐
    │ Blotato │  │ Meta API │  │ YouTube  │
    │(backup) │  │ (direct) │  │ (direct)│
    └─────────┘  └──────────┘  └──────────┘
```

### Dashboard Features
- **Create** — AI generates caption + hashtags for your product/brand
- **Visual** — Generate image/video with Freepik + Higgsfield
- **Schedule** — Queue for any connected platform
- **Publish** — Direct to Meta, YouTube, TikTok, Instagram
- **Analytics** — Pull engagement data back
- **Agent Chat** — Talk to Naledi while she builds content
- **Call Log** — Every War Room call + transcript saved here

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Dashboard** | React + Vite + Tailwind |
| **Backend API** | Node.js + Express |
| **Database** | SQLite (local) |
| **Agent Runtime** | OpenClaw (this instance) |
| **Voice** | VAPI |
| **RAG Vector DB** | ChromaDB + Ollama |
| **Memory** | Obsidian Vault (git-synced) |
| **Publishing** | Meta Graph API + Blotato MCP |
| **Image Gen** | Freepik API |
| **Video Gen** | Higgsfield API |
| **Search** | Agent-Reach (Twitter, Reddit, etc.) |
| **Video Process** | ffmpeg-wasm |

---

## 🚀 Deploy Plan

### Phase 1 — Today (Amara's control panel)
- [x] Deploy React dashboard to web
- [ ] Get VAPI key → configure voice agents
- [ ] Wire Blotato MCP into OpenClaw
- [ ] Test individual agent call with Robusca
- [ ] Test War Room squad call

### Phase 2 — This Week
- [ ] Deploy to Orgo VM (once new ID recovered)
- [ ] Install CORE OS on VM
- [ ] Deploy ClickClack for agent chat
- [ ] Set up ChromaDB + index Obsidian vault
- [ ] Wire Agent-Reach into Robusca + Charlie

### Phase 3 — Content Engine
- [ ] Freepik → auto-generate product images
- [ ] Higgsfield → auto-generate video creatives
- [ ] ffmpeg-wasm → trim + resize for each platform
- [ ] Meta Graph API → publish directly (no Blotato middleman)
- [ ] Full content pipeline dashboard

---

## 📂 Obsidian Vault Structure
```
studex-obsidian-vault/
├── 00-Core/           # Brand, mission, personas
├── 02-Agents/         # Robusca, Naledi, Auto-Meat, Hermes
├── 04-Content/        # Campaigns, templates, calendars
├── 05-Campaigns/      # Active campaigns
├── 07-Operations/      # SOPs, procedures
└── daily/             # Daily call logs, meeting notes
```

---

## 🔑 Getting GitHub Access

To give me (Amara) write access to your repos:

1. Go to: https://github.com/TumeloRamaphosa/SrudEx-Agents-Nest-Cloud-VM/settings/access
2. Click "Add people"
3. Search for: `TumeloRamaphosa` (or your GitHub username)
4. For the repo you want me to work in → add me as **Collaborator**

Or — give me a Personal Access Token (PAT) with `repo` scope:
- GitHub → Settings → Developer Settings → Personal Access Tokens → Generate new token
- Select: `repo` full scope
- Share the token with me

Which repo should I push the Content Pipeline OS to?
