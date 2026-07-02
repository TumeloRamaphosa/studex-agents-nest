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
    lastUpdated: '2026-06-17',
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
    lastUpdated: '2026-06-17',
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

## Products (NEEDS DOCUMENTING)
| Category | Products |
|----------|----------|
| Wagyu Biltong | Sliced, whole, gift packs |
| Premium Cuts | Wagyu t-bone, ribeye, sirloin |
| Droëwors | Classic, spicy |
| Gift Boxes | Corporate, celebration |
| Bundles | Monthly subscription box |

## Social Accounts
| Platform | Handle | Owner |
|----------|--------|-------|
| TikTok | @freekpik | Talking agent (voice) |
| Instagram | @higgsfikd | Visual brand agent |
| Facebook | @studexmeat | Naledi |
`,
  },
  {
    id: 'youth-day',
    title: 'Youth Day Campaign',
    category: 'Content Campaign',
    icon: '🔥',
    lastUpdated: '2026-06-17',
    excerpt: '⚠️ 9 DAYS LATE — "The Youth Shall Inherit the Flame." Posts for FB, IG, TikTok.',
    fullContent: `# Youth Day Content Plan — June 16, 2026

**Theme:** "The Youth Shall Inherit the Flame" — Honouring 1976, Building Tomorrow
**Campaign Tagline:** *"From the townships to your plate — premium meat, premium legacy."*
**CTA Link:** https://link.studexmeat.com
**Hashtags:** #YouthDay #June16 #StudexMeat #BuyBlack #TownshipEconomy #HalaalWagyu

---

## ⚠️ EXECUTION STATUS: BLOCKED

- Youth Day posts: **9 DAYS LATE**
- Blocker: **Meta user token expired Jun 22**
- Naledi ready to post, waiting for Tumelo to refresh token

---

## 🎙️ TikTok (@freekpik) — Voice/Talking Agent

Bold, direct, unapologetically SA, street-smart entrepreneur energy.

**Post 1:** "YOUNG & WATCHING 🌍 — 1976 they tried to silence us with bullets. 2026 we building empires with Wagyu. 🤯"

**Post 2:** Thread on "Why support Black business is STRATEGY not charity"

**Post 3:** Product demo — R2,000 Wagyu biltong slicing video

---

## 📸 Instagram (@higgsfikd) — Visual Brand Agent

Aesthetic, cinematic, proud, culturally rooted.

**Post 1:** 7-slide carousel — Cinematic Wagyu + 1976 imagery + Tumelo founder quote + CTA

**Post 2:** Story set — poll, BTS packing, UGC, countdown

---

## Execution Checklist
- [x] Naledi approves copy — ✅ Complete
- [x] Nova creates visual assets — ✅ Complete
- [ ] Amara schedules via FeedHive — ❌ BLOCKED
- [ ] EDDIE runs R50 boosted post — ❌ BLOCKED
- [ ] RALF logs to Airtable — ❌ BLOCKED
`,
  },
  {
    id: 'blockers',
    title: 'Blockers & Priority Queue',
    category: 'Operations',
    icon: '🚧',
    lastUpdated: '2026-06-26',
    excerpt: '5 critical blockers. Shopify, Meta token, AgentMail DNS, WhatsApp, Discord.',
    fullContent: `# 🚧 Critical Blockers — Updated 2026-06-26

## Priority 1 — Revenue Unblocked
| Blocker | Owner | Status |
|---------|-------|--------|
| Shopify Admin API token | Tumelo | ❌ Pending |
| Shopify agent ready | Hermes | ✅ Built |

## Priority 2 — Content Unblocked
| Blocker | Owner | Status |
|---------|-------|--------|
| Meta user token refresh | Tumelo | ❌ Expired Jun 22 |
| Youth Day posts (9 days late) | Naledi | 🏃 Ready |

## Priority 3 — Communications
| Blocker | Owner | Status |
|---------|-------|--------|
| AgentMail DKIM verify | Tumelo | ⚠️ Partial |
| send.stud.exchange SPF | Tumelo | ⚠️ Partial |
| WhatsApp Phone Number ID | Tumelo | ❌ Pending |
| Discord bot invite | Tumelo | ❌ Not in server |

## Priority 4 — Documentation
| Blocker | Owner | Status |
|---------|-------|--------|
| Products folder (03-Products) | Robusca | ❌ Empty |

## Today's Completed (2026-06-26)
- ✅ GoDaddy DNS configured
- ✅ Cron jobs set (7am + 10am SAST)
- ✅ Godot OS Phase 1 spec written
- 🏃 Godot OS Phase 1 War Room ← BUILDING NOW
`,
  },
];
