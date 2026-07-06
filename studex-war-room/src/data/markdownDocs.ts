export interface MarkdownDoc {
  id: string;
  title: string;
  category: string;
  icon: string;
  lastUpdated: string;
  excerpt: string;
  fullContent: string;
}

export const markdownDocs: MarkdownDoc[] = [
  {
    id: 'daily-2026-06-26',
    title: 'Daily Log — 2026-06-26',
    category: 'Daily Standup',
    icon: '📅',
    lastUpdated: '2026-06-26 02:00 SAST',
    excerpt: 'GoDaddy DNS configured, Godot OS spec written, cron jobs set.',
    fullContent: `# 2026-06-26 — Morning/Midnight Session

**Time:** ~02:00 SAST (00:00 UTC)

---

## ✅ What Was Done

### Email DNS (GoDaddy API)
- \`send.studexmeat.com\` — FULLY CONFIGURED ✅
  - A: send.studexmeat.com → 23.227.38.32
  - MX: send.studexmeat.com → mx.sendgrid.net
  - TXT SPF: v=spf1 include:amazonses.com -all
- \`send.stud.exchange\` — PARTIAL ⚠️
  - A: ✅ added
  - MX: ✅ added
  - TXT SPF: ❌ Needs manual add in GoDaddy UI

### Cron Jobs Set
- **7am SAST** — Robusca sends Tumelo a morning brief (Mon-Fri)
- **10am SAST** — CEO Board Meeting, all agents present (Mon-Fri)

### Godot OS Architecture Spec Written
- Phase 1: Three.js War Room on VM ← YOU ARE HERE
- Phase 2: Electron desktop app
- Phase 3: Godot 4.x full 3D world
- Phase 4: Tailscale + Ollama GPU mesh

---

## 🚧 Pending Actions

1. GoDaddy UI: Add TXT SPF for send.stud.exchange
2. AgentMail DKIM verify
3. Create agent email addresses
4. **Meta token refresh** ← Unblocks Naledi
5. **Shopify Admin API token** ← Unblocks orders
6. Products folder in vault — NEEDS POPULATING
`,
  },
  {
    id: 'agent-roster',
    title: 'Agent Roster',
    category: 'Team Directory',
    icon: '👥',
    lastUpdated: '2026-07-06',
    excerpt: 'Full team: Robusca (COO), Naledi (CMO), Hermes (CTO), Charlie + 10 sub-agents.',
    fullContent: `# Agent Roster — Studex Meat AI Team

## Board of Directors
| Role | Agent | Model | Status |
|------|-------|-------|--------|
| CEO | Tumelo Ramaphosa | Human | Active |
| COO / Chief of Staff | **Robusca** | MiniMax orbit | ✅ Active |
| CMO | **Naledi** | Gemini 2.0 Flash | ⚠️ Blocked (Meta) |
| CTO | **Hermes** | o3-mini / GPT-4o | ✅ Active |
| CFO | Finance sub-agent | GPT-4o / Claude Sonnet | Active |

## Charlie OS Sub-Agents
| Agent | Function | Platform |
|-------|----------|----------|
| Charlie | Orchestrator | Perplexity Computer |
| Naledi | CMO / Content | Gemini 2.0 Flash |
| Amara | Instagram persona | Gemini |
| EDDIE | Paid ads | Gemini / Claude |
| RALF | Coordinator | Claude |
| GIUM | Analytics | Claude |
| Vera | Ops | Claude / GPT-4o-mini |
| Zane | Research | Claude Opus |
| Nova | Creative | Claude |

## Tool Access
- Shopify Admin API (studexmeat.myshopify.com)
- Supabase DB
- TCG (Courier Guy) API
- FeedHive, Postiz, Blotato
- Airtable (content + ops)
- Amazon SES (send.studexmeat.com)
- AgentMail (inbound)
`,
  },
  {
    id: 'brand-bible',
    title: 'Brand Bible',
    category: 'Brand Core',
    icon: '📖',
    lastUpdated: '2026-07-06',
    excerpt: '"Premium Halaal Meat. Proudly South African." Wagyu biltong, premium cuts, gifting.',
    fullContent: `# Brand Bible — Studex Meat

## Brand Identity
**Brand Name:** Studex Meat
**Tagline:** "Premium Halaal Meat. Proudly South African."
**Competitors:** Woolworths, The Meatblock, Craft Carnivores
**Differentiation:** Halaal-certified + premium + Black-owned + tech-enabled

## Visual Identity
- **Primary:** Deep charcoal (#1A1A1A) + Gold accent (#d4a017)
- **Secondary:** Rich terracotta / braai red
- **Typography:** Bold sans-serif headers, clean body
- **Imagery:** Cinematic food photography, SA landscapes, premium but authentic

## Products
| Category | Products | Price Range |
|----------|----------|-------------|
| Wagyu Biltong Gold | Sliced 500g / 1kg, whole | R280–R520 |
| Premium Cuts | Wagyu t-bone, ribeye, sirloin | R380–R850 |
| Droëwors | Classic, spicy | R120–R200 |
| Gift Boxes | Corporate, celebration | R450–R1,200 |
| Ankole Heritage Beef | Coming soon | TBA |

## Social Accounts
| Platform | Handle | Followers |
|----------|--------|-----------|
| Instagram | @studexmeat | 5.3K |
| TikTok | @freekpik | Growing |
| Facebook | @studexmeat | Page |
`,
  },
  {
    id: 'youth-day',
    title: 'Youth Day Campaign',
    category: 'Content Campaign',
    icon: '🔥',
    lastUpdated: '2026-07-06',
    excerpt: '"The Youth Shall Inherit the Flame." Content calendar for FB, IG, TikTok.',
    fullContent: `# Youth Day Content Plan — June 16, 2026

**Theme:** "The Youth Shall Inherit the Flame" — Honouring 1976, Building Tomorrow
**Campaign Tagline:** *"From the townships to your plate — premium meat, premium legacy."*
**CTA Link:** https://link.studexmeat.com
**Hashtags:** #YouthDay #June16 #StudexMeat #BuyBlack #TownshipEconomy #HalaalWagyu

---

## ⚠️ STATUS: Needs Meta token to execute

- Naledi ready to post
- All copy and assets prepared
- Waiting on Tumelo to refresh Meta token

---

## 🎙️ TikTok — Bold, SA entrepreneur voice

**Post 1:** "YOUNG & WATCHING 🌍 — 1976 they tried to silence us with bullets. 2026 we building empires with Wagyu. 🤯"

**Post 2:** Thread: "Why supporting Black business is STRATEGY not charity"

**Post 3:** Product demo — R2,000 Wagyu biltong slicing video

---

## 📸 Instagram — Cinematic, culturally rooted

**Post 1:** 7-slide carousel — Cinematic Wagyu + 1976 + Tumelo founder quote + CTA

**Post 2:** Story set — poll, BTS packing, UGC, countdown

---

## Execution
- [x] Copy approved
- [x] Assets created
- [ ] Scheduled via FeedHive — BLOCKED
- [ ] Boosted post — BLOCKED
`,
  },
  {
    id: 'blockers',
    title: 'Blockers & Priority Queue',
    category: 'Operations',
    icon: '🚧',
    lastUpdated: '2026-07-06',
    excerpt: '5 critical blockers. Shopify, Meta token, AgentMail DNS, WhatsApp, Discord.',
    fullContent: `# 🚧 Critical Blockers — Updated 2026-07-06

## Priority 1 — Revenue Unblocked
| Blocker | Owner | Status |
|---------|-------|--------|
| Shopify Admin API token | Tumelo | ❌ Pending |
| Hermes ready | ✅ Built |

## Priority 2 — Content Unblocked
| Blocker | Owner | Status |
|---------|-------|--------|
| Meta user token refresh | Tumelo | ❌ Expired |
| Youth Day posts | Naledi | 🏃 Ready |

## Priority 3 — Communications
| Blocker | Owner | Status |
|---------|-------|--------|
| AgentMail DNS | Cloudflare | ❌ INVALID |
| WhatsApp Phone Number ID | Meta | ❌ Pending |
| Discord bot invite | Tumelo | ❌ Not in server |

## Today's Completed (2026-07-06)
- ✅ Composio plugin installed (v0.0.12)
- ✅ Obsidian Brain wiki built into War Room
- ✅ YouTube content campaign drafted
`,
  },
  {
    id: 'global-markets',
    title: 'Global Markets Launch',
    category: 'Global Expansion',
    icon: '🌍',
    lastUpdated: '2026-07-06',
    excerpt: 'China coffee window Jul 20. Ankole tokenization. Blockchain conservation. Global beef export.',
    fullContent: `# 🌍 Global Markets — Studex Expansion Roadmap

**Vision:** From a South African meat business to a global heritage food platform.

---

## 🇨🇳 China Coffee Window — July 20

South Africa to China coffee export opportunity identified.
**studex-wildlife-coffee repo:** EMPTY — needs sourcing data
**Action needed:** Populate with Chinese buyer contacts, pricing, logistics

**Next steps:**
- Find coffee sourcing partners (Ethiopia, SA roasters)
- Identify import license requirements for China
- Set up Alibaba / WeChat trade contacts
- Draft LOI template for Chinese buyers

---

## 🏆 Ankole Tokenization — The Big Vision

**Ankole cattle = "the most valuable cow" = cow of kings**

Bloomberg valued one African buffalo at R11.1 million ($11M USD) in 2016.

The Studex Wildlife model:
1. Tokenize Ankole/buffalo on blockchain (ERC-721 whole / ERC-20 fractional)
2. Global investors buy fractions — own a piece of a rare African animal
3. IoT tracking + drone surveillance = proof of investment + anti-poaching
4. IBM + Cardano partnership for on-chain tracking

**2018 World Crypto Economic Forum:** Top 20 Startup #9 · Token Design #11 Overall
**Media:** Forbes "Blockchain Africa Rising"

---

## 🥩 Beef Export — Middle East + Europe

**Target markets:**
- UAE / Dubai — Halaal premium demand
- UK — South African diaspora + foodies
- Europe — Wagyu novelty market

**Requirements:**
- Export permits (DAFF SA)
- Halaal certification (international)
- Cold chain logistics
- Import permits per country

---

## 📋 Global Launch Phases

| Phase | Market | Product | Timeline |
|-------|--------|---------|----------|
| 1 | China | Coffee tokenization | Jul 20 window |
| 2 | UAE | Halaal Wagyu export | Q3 2026 |
| 3 | UK/EU | Premium biltong export | Q4 2026 |
| 4 | Global | Ankole tokenization | 2027 |

---

## 🤝 Partnership Targets
- Alibaba / JD.com (China)
- Carrefour, Tesco (EU)
- Waitrose, M&S (UK)
- Emirates Flight Catering (UAE)
- IBM Research Africa
- Cardano / Input Output Global
`,
  },
  {
    id: 'products',
    title: 'Product Catalog',
    category: 'Products',
    icon: '🥩',
    lastUpdated: '2026-07-06',
    excerpt: 'Full product list: Wagyu biltong, premium cuts, droëwors, gift boxes.',
    fullContent: `# 🥩 Studex Meat — Product Catalog

*Last updated: 2026-07-06 — ADD NEW PRODUCTS HERE*

---

## Wagyu Biltong Gold
**Our flagship product. Premium South African Wagyu biltong.**

| SKU | Product | Size | Price |
|-----|---------|------|-------|
| WBG-500 | Wagyu Biltong Gold | 500g | R280 |
| WBG-1KG | Wagyu Biltong Gold | 1kg | R520 |
| WBG-GIFT | Biltong Gift Box | 3kg | R1,400 |

**Certification:** MJC Halal Trust HT 4606
**Shelf life:** 6 months (ambient)

---

## Premium Cuts
**Wagyu beef — full marbling grades available**

| SKU | Cut | Weight | Price |
|-----|-----|--------|-------|
| WAG-TBONE-M | Wagyu T-Bone | ~1.2kg | R680 |
| WAG-RIB-M | Wagyu Ribeye | ~800g | R850 |
| WAG-SIR-M | Wagyu Sirloin | ~600g | R520 |
| WAG-SHORT | Beef Short Ribs | ~1kg | R380 |

---

## Droëwors
**Traditional South African dried sausage**

| SKU | Variant | Weight | Price |
|-----|---------|--------|-------|
| DW-CLS-500 | Classic | 500g | R120 |
| DW-SPC-500 | Spicy | 500g | R135 |
| DW-GIFT | Droëwors Gift Box | 1kg | R220 |

---

## Gift Boxes
**Corporate and celebration gift solutions**

| SKU | Box Type | Contents | Price |
|-----|----------|---------|-------|
| GB-CORP-S | Corporate Small | 1kg biltong + droëwors | R450 |
| GB-CORP-L | Corporate Large | 2kg mixed + gift note | R890 |
| GB-CELEB | Celebration | Premium cuts + biltong | R1,200 |

---

## Coming Soon
- **Ankole Heritage Beef** — Ultra-premium, limited stock
- **Monthly Subscription Box** — recurring revenue model
`,
  },
  {
    id: 'youtube-content',
    title: 'YouTube Content Plan',
    category: 'Content Campaign',
    icon: '📺',
    lastUpdated: '2026-07-06',
    excerpt: 'Content to promote the YouTube channel about what we built.',
    fullContent: `# 📺 YouTube Content Plan — "I Built This" Series

**Channel:** Studex Meat YouTube
**Goal:** Promote the War Room, agent team, and build story
**Angle:** "A South African meat company built an AI command center"

---

## 🎬 Video 1 — War Room Tour (PRIORITY)

**Title:** I Built an AI War Room for My Meat Business | Studex OS Demo
**Duration:** 5–8 minutes
**Script:** See below

### Hook (0:00–0:30)
"Most small businesses run on WhatsApp. We built a command center."

### The Story (0:30–2:00)
- Tumelo's background: 10 years, no bank account for 7
- Why automation was non-negotiable
- Meet the agent team: Charlie (COO), Naledi (CMO)

### The Demo (2:00–6:00)
- War Room tour: globe, KPIs, agent dock
- ContentHub walkthrough
- Intel panel
- Workflow editor

### The Vision (6:00–8:00)
- Global expansion: China coffee, Ankole tokenization
- What's launching today: global markets
- Call to action: subscribe, follow the journey

---

## 📝 Video Script — "I Built an AI War Room"

**[INTRO — Tumelo on camera]**
"Hi, I'm Tumelo Ramaphosa, founder of Studex Meat. We're a premium Halaal Wagyu and biltong business, 10 years old, based in South Africa. And this — this is what we built."

**[SCREEN: War Room full view]**
"This is the Studex War Room. Our AI command center. Every KPI, every agent, every piece of the business — in one place."

**[SCREEN: Agent dock]**
"These are our AI agents. Charlie runs operations. Naledi manages all our content and social. We have 10 sub-agents handling everything from analytics to creative."

**[SCREEN: ContentHub]**
"This is ContentHub — where Naledi plans, schedules, and publishes all our social content. She posted to TikTok, Instagram, and Facebook this morning without us lifting a finger."

**[SCREEN: Globe + nodes]**
"This is the most interesting part. This globe shows our entire operation as a connected network. Every node is a part of the business — products, agents, campaigns, GitHub repos — all visible in real time."

**[CAMERA: Tumelo]**
"Here's why we built this. For 7 of our 10 years, no South African bank would work with us. We were locked out of the system. So we stopped asking permission and started building our own."

**[SCREEN: INTEL panel]**
"This is our intelligence layer. Real-time data, token tracking, project status — everything the agents need to make decisions without waiting for us."

**[CAMERA: Tumelo]**
"Today we're launching globally. China is our first stop — a coffee export window opening July 20th. But this system we're showing you today — the War Room, the agents — that's the infrastructure that makes global scale possible."

**[SCREEN: Global map / closing shots]**
"Follow along. We're just getting started."

**[END CARD]**
"Studex Meat — Premium Halaal Meat. Proudly South African."
"Subscribe for Build In Public updates."

---

## 🧵 Supporting Twitter/X Thread

___THREAD_START___
🧵 We built a full AI command center for our meat business.

Studex Meat. 10 years. No bank account for 7 of those years.

Here's what we built 👇
___THREAD_END___

See full thread in social content docs.

---

## 📅 Content Calendar
| Video | Topic | Status |
|-------|-------|--------|
| 1 | War Room Tour | 🎬 Ready to film |
| 2 | How Naledi posts to 3 platforms automatically | 📝 Scripting |
| 3 | China Coffee — the Jul 20 window | 📝 Research |
| 4 | Ankole Tokenization explained simply | 📝 Research |
`,
  },
];
