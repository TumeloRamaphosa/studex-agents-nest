# StudEx Social Media Influencer Pipeline
## Powered by Blotato + FeedHive + Freepik + Higgsfield.ai — Coordinated by Naledi VM

---

## 🔄 Pipeline Overview

```
Naledi (Strategy & Calendar)
    ↓ content brief
War Room (Approve Queue)
    ↓ approved
Content Pipeline Agent (Naledi VM)
    ├── Freepik      → visual assets (images, templates, vectors)
    ├── Higgsfield   → AI image/video creatives
    ├── Blotato      → AI content generation + scheduling + cross-posting
    └── FeedHive     → analytics + performance tracking
```

---

## 🎯 The Influencer Flywheel

Naledi operates a **content flywheel** — each piece of content generates data, data improves the next piece:

1. **Plan** — Naledi sets the weekly content calendar (product launches, promos, lifestyle, education)
2. **Create** — Brief goes to Blotato (text), Freepik (visuals), Higgsfield (AI creatives)
3. **Approve** — War Room queue → Tumelo approves or adjusts
4. **Publish** — Blotato posts natively to Facebook, Instagram, TikTok, LinkedIn, Threads, X, etc.
5. **Track** — FeedHive pulls performance metrics per platform
6. **Learn** — Naledi reviews analytics, refines next week's content

---

## 🛠️ Tool Roles

### Blotato — Content Engine
- **Role**: AI writing, repurposing, scheduling, cross-posting
- **API**: REST + MCP (Model Context Protocol) — can be triggered by OpenClaw directly
- **Key superpowers**:
  - Genius AI Writer (fine-tuned on 1M+ viral posts)
  - Auto-repurpose: 1 blog/YouTube → 9 platform posts
  - Viral templates: 100+ proven formats
  - Native Facebook/Instagram posting (bypasses token expiry)
- **Naledi drives**: sends content briefs → Blotato → gets scheduled posts

### FeedHive — Analytics & Listening
- **Role**: Cross-platform analytics, content calendar, team collaboration, performance AI
- **Key superpowers**:
  - Auto-scheduler with optimal time detection
  - Hashtag intelligence
  - Competitor tracking
  - Content performance inbox
- **Status**: Needs API key from app.feedhive.com
- **Naledi drives**: reads FeedHive analytics → adjusts content strategy

### Freepik — Visual Asset Library
- **Role**: Stock images, design templates, vectors, mockups
- **API**: Freepik API (freepik.com/api) — image search and download
- **Key superpowers**:
  - Food/meat industry visuals
  - Promotional templates
  - Quote cards, infographics
- **Naledi drives**: generates visual briefs → downloads assets → Blotato

### Higgsfield.ai — AI Creatives
- **Role**: AI-generated images and video for ads and social content
- **Already integrated**: content-pipeline agent on Naledi VM polls War Room + dispatches to Higgsfield
- **Key superpowers**:
  - AI image generation (product showcases, lifestyle shots)
  - AI video generation (ads, reels, TikToks)
  - Background removal, image editing
- **Naledi drives**: brief → Higgsfield → assets uploaded to Blotato

---

## 📅 Naledi's Weekly Content Calendar

| Day | Focus | Platforms | Content Type |
|-----|-------|----------|-------------|
| Monday | Weekly promo | FB, IG, TikTok | Product spotlight + offer |
| Tuesday | Education | LinkedIn, X | How-to, meat tips, behind-the-scenes |
| Wednesday | Lifestyle | TikTok, IG Reels | ASMR cooking, farm-to-table vibe |
| Thursday | Engagement | All | Poll, Q&A, user-generated content |
| Friday | Weekend promo | FB, IG, X | Recipe suggestion + CTA |
| Saturday | Community | Threads, Reddit | Engagement post, trending话题 |
| Sunday | Planning | Internal | Review week, prep next week |

---

## 🧠 Naledi VM Agent Architecture

```
/root/nest/agents/content-pipeline/
├── index.js          — polls War Room approvals → dispatches to Blotato/Higgsfield
├── blotato.js        — Blotato API wrapper (create post, schedule, get analytics)
├── feedhive.js       — FeedHive API wrapper (fetch analytics, update calendar)
├── freepik.js        — Freepik API wrapper (search + download assets)
├── queue.js          — job queue: pending → processing → done → archived
└── memory/
    └── content-log.md — rolling log of published content + performance

/root/nest/studex-naledi-content/
└── index.md          — Naledi's brand voice, content guidelines, influencer style guide
```

---

## 🔌 API Keys Needed

| Tool | Status | Where to Get |
|------|--------|-------------|
| Blotato | 🔓 Tumelo signing up | blotato.com/pricing |
| FeedHive | ❌ Missing | app.feedhive.com → Settings → API |
| Freepik | ❌ Missing | freepik.com → API (free tier: 100 credits/mo) |
| Higgsfield | ❌ Missing | Higgsfield.app → API key |

---

## 📌 Actions Required

### Tumelo
- [ ] Sign up at **blotato.com** ($29/mo, 7-day free trial) → get API key
- [ ] Sign up at **freepik.com/api** (free tier) → get API key
- [ ] Get FeedHive API key from app.feedhive.com
- [ ] Confirm Higgsfield API key status

### Naledi VM (automated)
- [ ] Install Blotato MCP or use REST API
- [ ] Wire content-pipeline → blotato.js → Blotato API
- [ ] Wire content-pipeline → feedhive.js → FeedHive API
- [ ] Wire content-pipeline → freepik.js → Freepik API
- [ ] Connect FeedHive analytics → Naledi's content review

---

## 🚀 Quick Start Order

1. **Today**: Tumelo signs up for Blotato (priority — fixes Facebook posting NOW)
2. **This week**: Connect Blotato MCP → OpenClaw → I can trigger posts directly
3. **This week**: Naledi VM wires up → content pipeline agent
4. **Week 2**: FeedHive analytics flowing → Naledi reviews performance
5. **Week 3**: Freepik + Higgsfield → AI visual assets in every post

---

*v3 — Built 2026-06-27 — Tumelo + Robusca + Naledi VM*
