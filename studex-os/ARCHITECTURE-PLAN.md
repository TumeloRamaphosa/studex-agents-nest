# STUDEX OS — Immersive Virtual World Architecture Plan
**Version 1.0 | July 3, 2026 | Status: PRE-BUILD VALIDATION**

---

## 🧠 The Vision (In Your Words)

> "A virtual world as our operating system — data centers and software factories where agents walk around as characters, report to the Obsidian knowledge graph, can be spoken to via voice or chat, where our VMs are locations we can fly to, with linear and notion integrated, rendered on a game engine."

This document: validates the vision, selects the right tech stack, maps what already exists, and defines a phased build plan.

---

## ✅ VALIDATION: Is This Achievable?

**Short answer: YES.** The individual pieces already exist and work. The challenge is integration, not invention.

**What you described is actually three layers working as one:**

| Layer | What It Does | Already Exists? |
|---|---|---|
| **Knowledge Graph / Brain** | Obsidian vault, CORE OS memory, all decisions/agents connected | ✅ `studex-obsidian-vault` + `core-os` |
| **3D Immersive World** | Data center rooms, walking agents, interactive dashboards, fly-to-VM navigation | 🔶 `studex-war-room` (R3F) — needs upgrade |
| **Agent Communication** | Voice (RileyJarvis), Chat (OpenClaw), Pixel Agents characters | 🔶 Pixel Agents needs setup, RileyJarvis needs Mac |
| **Integrations** | Linear, Notion, Tailscale SSH, Shopify | ❌ Need setup |
| **Game Engine Rendering** | For photorealistic 3D beyond R3F capability | ❓ See debate below |

---

## 🎮 GAME ENGINE vs WEB-NATIVE: The Critical Decision

### ❌ Do NOT Use Godot

Godot is a desktop game engine. For this use case it has serious problems:

- **Web export is complex** — requires WebAssembly, special build pipeline
- **No native React/web integration** — you'd be building two separate systems
- ** multiplayer over the web requires relay servers** — significant infrastructure
- **Hard to iterate** — every change requires re-export and re-deploy
- **Not designed for data/API-heavy UIs** — dashboards, charts, live KPIs are painful

### ✅ USE: React Three Fiber (R3F) — Web Native

**This is the correct choice.** Here's why:

| Criteria | Godot | React Three Fiber |
|---|---|---|
| Renders in browser | ✅ but complex | ✅ natively |
| Integrates with React dashboards | ❌ | ✅ perfectly |
| MCP / API connectivity | ❌ | ✅ natively |
| Deploy anywhere | ❌ | ✅ one command |
| Agent characters (3D avatars) | ✅ | ✅ (voxel/low-poly) |
| Knowledge graph panels | ❌ | ✅ |
| Voice API integration | ❌ | ✅ |
| Iteration speed | Slow | Fast |
| OpenClaw compatibility | ❌ | ✅ native |

**SEO-OS already proved this works** — it's a 3D office in React Three Fiber with 25 agent specialists working in parallel, with status LEDs, live task feeds, and 3D desk panels. That's exactly your vision, built today.

**When to consider Godot later:** If you want photorealistic graphics, VR support, or a downloadable desktop app with deep system access. Not for v1.

---

## 🏗️ ARCHITECTURE: Five Layers

```
┌─────────────────────────────────────────────────────┐
│                   STUDENT OS                         │
│           Immersive 3D World (R3F)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐    │
│  │Data Center│  │ War Room │  │ VM Corridors  │    │
│  │ (Meat)   │  │ (Studio) │  │ (Orgo VMs)   │    │
│  └──────────┘  └──────────┘  └──────────────┘    │
│  Agent Characters walk between rooms                 │
│  Knowledge Graph panels float in 3D space            │
├─────────────────────────────────────────────────────┤
│              AGENT LAYER                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐  │
│  │ Charlie │ │ Naledi  │ │ Hermes  │ │ Robusca│  │
│  │ (CEO)   │ │ (CMO)   │ │ (DevOps)│ │ (You) │  │
│  └─────────┘ └─────────┘ └─────────┘ └────────┘  │
│  Each agent = 3D avatar + Pixel Agents hooks        │
│  Connected to Obsidian vault (knowledge graph)      │
├─────────────────────────────────────────────────────┤
│              CORE OS LAYER                         │
│  Memory knowledge graph, 50+ MCP connectors         │
│  Linear | Notion | Shopify | Tailscale | GitHub    │
│  Proactive task automation                          │
├─────────────────────────────────────────────────────┤
│              VOICE LAYER                            │
│  RileyJarvis (OpenAI Realtime API)                 │
│  ElevenLabs voice synthesis                        │
│  Voice → agent → world action                      │
├─────────────────────────────────────────────────────┤
│              DATA LAYER                             │
│  Shopify orders, Meta ads, AgentMail, War Room     │
│  All live KPIs → 3D dashboard panels in world      │
└─────────────────────────────────────────────────────┘
```

---

## 📍 NAVIGATION: How "Flying to VMs" Works

Instead of actual flight (which requires game engine physics), use **portal/teleport navigation**:

```
You are HERE: [Main War Room — South Africa]
    │
    ├── Corridor → Orgo VM (Meat Auto) — 67.213.119.157
    │           └── Live: War Room dashboard, VM stats
    │
    ├── Corridor → RileyJarvis MacBook — Tailscale tailnet
    │           └── Live: Desktop camera, file access
    │
    ├── Corridor → Cursor/Devin — AI coding VMs
    │           └── Live: Code being written, terminal
    │
    ├── Corridor → Studex Website — Public VM
    │           └── Live: Traffic, orders, analytics
    │
    └── Corridor → Naledi Content Studio
                └── Live: Content queue, scheduled posts
```

Each corridor is a **Three.js portal** (glowing doorway) that transitions the camera into that VM's dashboard view. The VM itself is accessed via SSH/API — the 3D world is just the navigation layer.

**This is how SEO-OS already works** — different rooms, different agents, click to enter. We're just expanding it.

---

## 🔌 INTEGRATIONS MAP

| Service | How Connected | Status |
|---|---|---|
| **Obsidian Vault** | Filesystem reads via Node.js | ✅ Working |
| **CORE OS** | MCP server, `gateway-protocol` | 🔶 Clone needed |
| **Pixel Agents** | HTTP POST hooks to Fastify server | 🔶 Setup needed |
| **RileyJarvis** | OpenAI Realtime API + macOS permissions | 🔶 Mac needed |
| **Linear** | Linear API v2024.10.0 | ❌ No key |
| **Notion** | Notion API | ❌ No key |
| **Tailscale** | Tailscale API + SSH | 🔶 API key needed |
| **Shopify** | Admin API | ❌ No token |
| **AgentMail** | REST API | 🔶 DNS pending |
| **Meta/Facebook** | Graph API | ❌ Token expired |

---

## 🗺️ PHASED BUILD PLAN

### Phase 1: Foundation (This Week)
**Goal: Running 3D world with live data**

1. ✅ Deploy existing `studex-war-room` (already R3F + Three.js)
   - Already uses: `@react-three/fiber`, `drei`, `three`, `gojs`, `recharts`
   - Live at: `bl923ho8ctt3.space.minimax.io`
2. ✅ Upgrade War Room to underwater datacenter theme (green glow, ocean, server racks)
3. ✅ Connect live Shopify KPIs as floating 3D panels
4. ✅ Deploy `studex-os` full system to a new URL

**Deliverable: War Room shows live business data in 3D underwater world**

### Phase 2: Agent Characters (Week 2)
**Goal: Charlie, Naledi, Hermes visible and working in world**

1. Install Pixel Agents on Orgo VM (`npm install -g pixel-agents`)
2. Connect Pixel Agents hooks to Charlie + Naledi sub-agents
3. Add 3D avatar panels in War Room for each agent
4. Build "agent status dock" — shows who's active, what they're doing

**Deliverable: See agents working in real-time in the 3D world**

### Phase 3: Voice Layer (Week 3)
**Goal: Talk to any agent via voice**

1. Set up OpenAI Realtime API on MacBook (RileyJarvis)
2. OR: Build voice panel in War Room using Web Speech API + ElevenLabs
3. Connect voice → Charlie orchestrator → assigns tasks
4. Agent responses read aloud via ElevenLabs

**Deliverable: Voice conversation with any agent**

### Phase 4: Navigation + World Expansion (Week 4+)
**Goal: Fly between VMs, Linear/Notion in-world**

1. Build portal corridors between VMs (Tailscale SSH jump)
2. Add Linear and Notion as 3D panel rooms
3. Build the "VM corridor" — Orgo VM, MacBook, Cursor as navigable spaces
4. Add particle effects, animations, ambient motion

**Deliverable: Full navigable business world**

---

## ⚠️ RISKS AND HONEST ASSESSMENTS

| Risk | Likelihood | Mitigation |
|---|---|---|
| Pixel Agents + R3F character rendering conflict | Medium | Use R3F for world, Pixel Agents for desktop overlay (separate surfaces) |
| Voice latency kills immersion | High | Use push-to-talk, not continuous streaming |
| Tailscale SSH to MacBook unreliable | Medium | Use macOS Screen Sharing + VNC as fallback |
| Too many simultaneous live connections | Medium | Phase 4 before Phase 1 — build one room well first |
| Godot re-evaluation wasted time | Low | We're not using Godot — plan is validated against R3F |

---

## 🏆 THE STUDEX OS PHILOSOPHY

> "The best interface is no interface. You walk into your business and everything is exactly where you need it, doing what it does, and you can ask any part of it a question."

**Not a metaphor. An actual 3D world.**

---

## NEXT ACTION

> **Build Phase 1 first.** Upgrade the War Room to the underwater datacenter theme, connect live Shopify data, and deploy. Get the foundation solid. Everything else plugs in after.

**Owner:** Robusca (this agent)
**Review:** Before Phase 2, validate with Tumelo that Phase 1 delivers the right foundation.

---

*This document is the single source of truth for the Studex OS build. Updated at each phase boundary.*
