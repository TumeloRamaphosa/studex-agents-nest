# Studex Outreach Engine

Built: 2026-09-09 | Robusca CEO | Build Hour

## What This Is

A command-line outreach tool for executing Studex's cold outreach campaigns — wedding caterers and CT cafés. Generates formatted WhatsApp messages, tracks send status, and logs all activity.

## Quick Start

```bash
cd /workspace/studex-war-room
npm run outreach today        # ← see today's outreach plan
npm run outreach list wedding  # ← list wedding caterers
npm run outreach message foodbarn first  # ← generate first message for Foodbarn
npm run outreach send foodbarn first     # ← mark as sent + log
npm run outreach report        # ← daily stats
```

## Workflow

1. **`npm run outreach today`** — shows who to contact today
2. **`npm run outreach message <id> first`** — generates the WhatsApp message (copy it)
3. Send via WhatsApp
4. **`npm run outreach send <id> first`** — logs the send
5. **`npm run outreach update <id> contact <phone>`** — set the contact number once you have it
6. **`npm run outreach report`** — track progress

## Contact IDs

### Wedding Caterers
- `foodbarn` — The Foodbarn Café & Deli
- `delicate-dance` — Delicate Dance Catering
- `inkvine` — Inkvine Catering

### CT Cafés
- `haarloo` — Haarloo Coffee (Gardens)
- `grove` — Grove Coffee (Wynberg)
- `kent-y` — Kent y Coffee (Sea Point)
- `giovanni` — Giovanni's Deliworld (Green Point)
- `bootlegger` — Bootlegger Coffee (Various CT)

## Message Types
- `first` — initial cold outreach
- `followup` — 3 days after no reply
- `closing` — final attempt

## Update Contact Number

Once you have a WhatsApp number for a contact:
```bash
npm run outreach update foodbarn contact "+27-XX-XXX-XXXX"
```

## Status Meanings
- `pending` — not yet contacted
- `sent` — first message sent, awaiting reply
- `overdue` — follow-up due
- `replied` — they responded 🎉
- `won` — converted to client
- `lost` — not interested / no response after closing
