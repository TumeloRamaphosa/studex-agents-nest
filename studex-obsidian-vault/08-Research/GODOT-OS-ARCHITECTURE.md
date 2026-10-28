# 🎮 Godot OS — StudEx Meat Operating System Architecture

**Status:** PLANNING DRAFT  
**Date:** 2026-06-26  
**Author:** Robusca CEO AI  
**Engine:** Godot 4.x | **Language:** GDScript + Godot HTTP / WebView  

---

## 1. Vision

StudEx OS is a **game-engine-powered business command center** that transforms the abstract operations of StudEx Meat into a living, navigable 3D world. Every agent is a character. Every vault file is a location. Every order is an event. The CEO (Tumelo) enters the world, walks through the factory floor, and manages the entire business by interacting with it.

This is not a dashboard. This is a **place.**

---

## 2. Why Godot (Not Unity/Unreal)

| Criteria | Godot 4 | Unity | Unreal 5 |
|----------|---------|-------|---------|
| Cost | Free, open source | Free tier | Free, 5% royalty |
| Learning curve | Moderate (GDScript is Python-like) | Steeper (C#) | Steepest (C++) |
| Exports to Web/HTML5 | ✅ Yes (wasm + webgl) | ✅ Yes (but heavy) | ✅ Yes (but very heavy) |
| Linux server headless | ✅ Yes | ⚠️ Possible | ⚠️ Possible |
| Built-in 3D physics | ✅ Yes | ✅ Yes | ✅ Yes |
| Community for AI agents | Growing fast | Large | Large |
| Ships to web from VM | ✅ WebGL export | ⚠️ Heavy | ❌ Very heavy |

**Decision: Godot 4.x** — best balance of web export, cost, accessibility, and rapid development.

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  STUDEx OS (GODOT 4)                  │
│                 Running on Orgo VM                     │
├──────────┬──────────┬──────────┬─────────────────────┤
│  FACTORY │  CONTENT  │  WAR     │  AGENT              │
│  FLOOR   │  STUDIO  │  ROOM    │  NEXUS              │
│          │          │          │                     │
│ Orders   │ Naledi's │ 3D Graph │ Charlie, Hermes,   │
│流程面板   │ Queue    │ Sphere   │ Naledi as NPCs      │
└────┬─────┴────┬─────┴────┬────┴────────┬──────────┘
     │          │          │              │
     ▼          ▼          ▼              ▼
┌─────────────────────────────────────────────────────┐
│              DATA / API LAYER (OpenClaw)              │
├──────────┬──────────┬──────────┬─────────────────────┤
│ Shopify  │ AgentMail│ Discord  │ Obsidian Vault      │
│ Orders   │ Emails   │ Messages │ Markdown files      │
└──────────┴──────────┴──────────┴─────────────────────┘
```

---

## 4. Core Systems

### 4.1 The Factory Floor (Main Hub)
- 3D rendered industrial space — dark factory aesthetic
- Live order ticker (pulls from Shopify API)
- Production queue showing fulfilled vs pending orders
- Ambient factory sounds, glowing amber/coal lighting
- Entry point / spawn location for the player

### 4.2 Content Studio (Naledi's Domain)
- Video editing bay aesthetic
- Content calendar as a physical kanban board in 3D
- Queued posts as "tapes" waiting to be "aired"
- Naledi NPC character that you can talk to (ElevenLabs TTS)
- YouTube/TikTok/Facebook integration status panels

### 4.3 War Room (Operations Center)
- 3D knowledge graph sphere in the center — the Obsidian brain
- Agents represented as orbiting nodes
- Conversations as light trails between nodes
- Click any node → opens that file/chat in a panel
- Markdown files as interactive holographic panels

### 4.4 Agent Nexus (Team)
- Each agent is a 3D character with:
  - Custom avatar (3D model)
  - Voice (ElevenLabs TTS)
  - Personality prompt
  - Task queue visible as quest log
- Walk up to an agent → speak to them → they report
- Charlie (Orchestrator) — central hub manager
- Naledi (CMO) — content lead
- Hermes (DevOps) — infrastructure specialist

### 4.5 Communication Hub (Unified Inbox)
- WhatsApp, Discord, Slack, AgentMail as "communication channels"
- Each channel is a physical screen/post in the space
- Messages appear as incoming transmissions
- Send messages by walking to the channel terminal

---

## 5. Technical Implementation

### 5.1 Godot Project Structure
```
studex-os/
├── scenes/
│   ├── factory_floor.tscn       # Main hub
│   ├── war_room.tscn            # Knowledge graph room
│   ├── content_studio.tscn      # Naledi's area
│   ├── agent_nexus.tscn         # Agent NPC area
│   └── comms_hub.tscn           # Unified comms
├── scripts/
│   ├── openclaw_connector.gd    # API to OpenClaw/VM
│   ├── vault_loader.gd          # Reads Obsidian markdown
│   ├── shopify_connector.gd     # Live order data
│   ├── tts_driver.gd            # ElevenLabs integration
│   ├── ai_brain.gd              # Claude/haiku reasoning
│   └── agent_npc.gd             # NPC behavior
├── assets/
│   ├── models/                  # 3D character models
│   ├── textures/                # Factory/industrial textures
│   └── audio/                   # SFX + ambient
└── export_presets.cfg           # Web export settings
```

### 5.2 Data Pipeline (OpenClaw → Godot)
```
OpenClaw Gateway (this system)
    ↓ webhook / API
Orgo VM (war-room:5000)
    ↓ JSON API
Godot OS
    ↓ HTTP requests
OpenClaw API endpoints
    ↓
Vault files, agent memory, orders
```

### 5.3 ElevenLabs Voice Integration
- Each agent NPC has a `voice_id` from ElevenLabs
- Player walks to NPC → presses interact
- NPC "thinks" (calls OpenClaw reasoning) → generates response
- Response sent to ElevenLabs → TTS audio plays
- Audio spatialized in 3D (Godot AudioServer)

### 5.4 Knowledge Graph Sphere
- Three.js graph embedded in Godot as a WebView node
- Reads from `/workspace/studex-obsidian-vault/` on the VM
- Parses markdown → extracts connections → renders 3D nodes
- Studex Products as nodes (currently empty — needs population)
- Agents, conversations, decisions as connected edges

### 5.5 Local GPU + Tailscale LLM Mesh
- If MacBook/Windows have GPUs (NVIDIA CUDA or Apple Silicon):
  - Run ollama on local machines: `ollama serve`
  - Tailscale VPN: connect VM to local network
  - Godot OS → Tailscale IP → local ollama inference
  - Zero cloud cost for local model inference
- Backup: Use OpenClaw's existing model providers

### 5.6 Linear Integration (Task Manager)
- Linear API: issues as tasks in Godot
- Each task = "quest" in the game world
- Quest log UI in Godot (Overlay)
- Complete tasks → XP/achievement in OS
- Naledi's content requests → Linear tickets → her queue

---

## 6. Build Phases

### Phase 1 — MVP (Weeks 1-2): The War Room Web App
**What:** React + Three.js web app (no Godot yet)  
**Where:** war-room:5000 on VM  
**Features:**
- 3D knowledge graph sphere (reads vault)
- Agent cards with status
- Markdown panel (Obsidian-style editing)
- Live order count from Shopify
- Dark factory aesthetic

**Owner:** Hermes (DevOps) + main Robusca

### Phase 2 — Desktop App (Weeks 3-4): Electron Shell
**What:** Electron + Phase 1 web app  
**Where:** VM desktop shortcut  
**Features:**
- Fullscreen command center
- System tray for notifications
- Auto-start on VM boot
- Local file access

### Phase 3 — Godot World (Months 2-3): Full 3D Environment
**What:** Godot 4.x game engine  
**Where:** Exported as web app on VM  
**Features:**
- Factory floor hub
- Agent NPCs with ElevenLabs voices
- War room with knowledge graph
- Content studio
- Communication hub

### Phase 4 — Local GPU Mesh (Month 3+)
**What:** Tailscale + Ollama on MacBook/Windows  
**Where:** Local inference, VM controller  
**Features:**
- Free local LLM inference
- GPU-accelerated agent reasoning
- Private, no cloud dependency

---

## 7. Action Items (This Week)

| # | Owner | Task | Status |
|---|-------|------|--------|
| 1 | Tumelo | Get MacBook/Windows GPU specs | Pending |
| 2 | Tumelo | Install Tailscale on VM + machines | Pending |
| 3 | Tumelo | Install Godot 4.x, try the tutorial | Pending |
| 4 | Robusca | Populate 03-Products in vault | Pending |
| 5 | Robusca | Set up ElevenLabs account + voice IDs | Pending |
| 6 | Hermes | Phase 1 web app (Three.js War Room) | Next sprint |
| 7 | Naledi | Plan content for Godot OS demo | Pending |

---

## 8. Dependencies

- **OpenClaw** (this system) — already running ✅
- **Orgo VM** — running, port 5000 ✅
- **Obsidian Vault** — needs products + agent docs
- **Shopify API** — needs token
- **ElevenLabs** — needs account + voice IDs
- **Tailscale** — needs install on VM + machines
- **Godot 4.x** — needs installation (Tumelo)
- **Linear** — needs API key for integration

---

## 9. 3D Characters (Agent NPCs)

| Agent | Avatar Style | Voice | Role in World |
|-------|-------------|-------|---------------|
| Charlie | Corporate android, blue accent | Professional, warm | Factory floor manager |
| Naledi | Creative, colorful, energetic | SA accent, bold | Content studio lead |
| Hermes | Tech-focused, minimal, precise | Calm, technical | Server room / IT |
| Robusca (you) | CEO avatar — Tumelo's representation | Matches Tumelo's voice | Command center |

---

## 10. Success Metrics

- Tumelo can walk into the War Room and see a live order appear as a 3D event
- Charlie NPC can answer "what did we post yesterday?" in voice
- Naledi's content queue shows as a physical kanban in 3D
- Godot OS loads in <3 seconds on the VM
- ElevenLabs voice responses in <5 seconds

---

_Next step: Tumelo installs Godot 4.x and does the 3D platformer tutorial (30 min). Then we start Phase 1._
