# 📋 Orchestrix — Studex Agent Communication Hub
**Status:** 🔄 Building
**Last Updated:** 2026-06-28

---

## What is Orchestrix?

The Robusca voice & chat communication layer. Every conversation Tumelo has with any agent gets:
- 🎙️ Voice captured (via Voicebox)
- 💭 Robusca reasons and responds
- 💾 Auto-saved to Obsidian vault
- 🔗 Graphed in the Studex knowledge graph

---

## Architecture

```
Tumelo Laptop (Voicebox MCP :17493)
         ↓ voice / text
Matrix Homeserver (Orgo VM :8008)
         ↓
Robusca Voice Bot (Python/matrix-nio)
    ↓ reasons
OpenClaw (Robusca chief of staff)
    ↓
Obsidian Vault (/root/robusca/robusca-brain/memory/conversations/)
         ↓
Studex Knowledge Graph (graph.md)
```

---

## Agent Roster — Matrix Accounts

| Agent | Matrix ID | Role |
|-------|-----------|------|
| Robusca | @robusca:studex.local | Chief of Staff / Bot |
| Charlie | @charlie:studex.local | Orchestrator Agent |
| Naledi | @naledi:studex.local | CMO Agent |
| Hermes | @hermes:studex.local | CTO Agent |
| Tumelo | @tumelo:studex.local | Owner / Human |

---

## Matrix Rooms

| Room | Purpose |
|------|---------|
| `StudexCommandCenter` | Main ops room — Tumelo + all agents |
| `RobuscaReports` | Robusca's daily briefings to Tumelo |
| `ContentQueue` | Naledi's content pipeline |
| `CoffeeDesk` | Studex Wildlife deal tracking |

---

## Voice Pipeline

### Outbound (Robusca → Tumelo)
1. Robusca generates text response
2. Voicebox MCP `tts_generate` called via HTTP
3. Audio returned as base64
4. Sent as `m.audio` message to Matrix room
5. Tumelo hears it in Element/voice player

### Inbound (Tumelo → Robusca)
1. Tumelo records voice in Voicebox
2. Voicebox transcribes via `whisper_stt`
3. Text sent to Matrix room as `m.text`
4. Robusca bot picks it up, reasons, responds
5. Full exchange logged to Obsidian

---

## Obsidian Logging

Every message logged to:
`memory/conversations/YYYY-MM-DD.md`

```markdown
## [2026-06-28 17:45 UTC] tumelo (voice)

Hey Robusca, give me a status update on the PROWTC deal

## [2026-06-28 17:45 UTC] Robusca (response)

The PROWTC Dubai deal is at pricing stage. Email draft is ready at 
/workspace/drafts/email-svetlana-prowtc.md — awaiting your approval 
to send via AgentMail. What's your decision?
```

---

## Knowledge Graph Sync

After every conversation:
- Key entities (names, companies, deals, numbers) extracted
- Written to `memory/conversations/entities.json`
- Studex graph view at `memory/graph.md`

---

## Installation

```bash
# On Orgo VM
curl -sL https://workspace/orchestrix/setup-orchestrix.sh | bash
python3 /root/orchestrix/bot/robusca_voice_bot.py
```

---

## Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `MATRIX_HOMESERVER` | `http://127.0.0.1:8008` | Local VM |
| `MATRIX_USER` | `robusca` | Bot account |
| `MATRIX_PASSWORD` | `(set in .env)` | Bot password |
| `MATRIX_ACCESS_TOKEN` | `(set in .env)` | Alt auth |
| `MATRIX_ROOM` | `StudexCommandCenter` | Main room |
| `VOICEBOX_URL` | `http://127.0.0.1:17493/mcp` | Voicebox local |
| `OBSIDIAN_VAULT` | `/root/robusca/robusca-brain` | Vault path |