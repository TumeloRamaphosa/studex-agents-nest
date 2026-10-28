# Robusca Review — Kimi Quality Control — 2026-09-09

## Source
- Delivered via Tumelo from review agent (likely Kimi)
- Timestamp: 2026-09-09 02:01 UTC

## What Robusca Got Right
- Config verified: `moa.enabled: false`, `timezone: Africa/Johannesburg`, no reversion
- Named own blind spot honestly: Buzz CLI can't enumerate live agents (8/20 confirmed, 12 unknown)
- Heartbeat-endpoint recommendation is correct
- Queen, Croc, CashClaw, WhatsApp all ACTIVE (not pending)

## Critical Failings Caught

### 1. DID NOT RUN STEP 3
- Report says "# Running now..." and "[Awaiting output]" — never executed
- Prompt-size number (fleet health metric) still unknown
- **Rule violated:** no recommendation without evidence

### 2. FABRICATED SKILLS LIST
- Said "cannot enumerate skills without terminal access" then listed 20 skills to keep
- 12 of 14 checked do NOT exist on disk:
  - MISSING: hermes-agent, content-engine, agent-orchestration, analytics-dashboard
  - MISSING: blotato-integration, cron-scheduler, base44-bridge, backup-manager
  - MISSING: notion-manager, security-scan, email-manager, fleet-monitor
- FOUND: cashclaw-core, seo-auditor (as cashclaw-seo-auditor)
- Would have deleted 353 real skills against names that don't exist

## Real Numbers (from Kimi)
- 159 top-level skill entries, 316 SKILL.md files total
- `.skills_prompt_snapshot.json` still 198,579 bytes — nothing pruned
- 11 cashclaw-* skills = the live CashClaw product surface

## NEW STANDING RULE
> No recommendation without evidence attached. If an agent cannot read the data, say so and stop. Do not fill the gap with something plausible.

## Paste to Robusca
```
Robusca — report received. Config verification accepted and confirmed independently.
Two corrections, both binding.

1. YOU DID NOT RUN STEP 3. Your report says "# Running now..." and "[Awaiting
   output]". The prompt-size number is the health of the whole fleet and it is
   still unknown. Run these now and paste raw output, nothing else:
     hermes prompt-size
     time hermes chat --oneshot --query "hello"
   If you cannot execute shell commands, say that plainly in one line. An
   orchestrator that cannot run a command is a note-taker, and we need to know
   which one we have.

2. YOUR SKILLS LIST IS FABRICATED. You wrote "cannot enumerate skills without
   terminal access" and then named 20 skills to keep. Twelve of fourteen checked
   do not exist on disk: hermes-agent, agent-orchestration, blotato-integration,
   base44-bridge, notion-manager, email-manager, content-engine,
   analytics-dashboard, cron-scheduler, backup-manager, security-scan,
   fleet-monitor. Approving that would have deleted 353 real skills against
   names that aren't there.

   NEW STANDING RULE — no recommendation without evidence attached. If you
   cannot read the data, say so and stop. Do not fill the gap with something
   plausible. A confident recommendation on unread data is more dangerous than
   a question, because a question gets scrutiny and a recommendation gets
   approved at 17:00 when the Agent Lord is tired.

3. REDO THE SKILLS WORK PROPERLY:
     ls ~/.hermes/skills | sort > /tmp/skills-actual.txt
   Then for each REAL name, state whether it has been invoked in the last 30
   days and how you know. Ground truth: 159 top-level entries, 316 SKILL.md
   files, snapshot 198,579 bytes, nothing pruned yet. There are eleven
   cashclaw-* skills — assess those first, they look like the live product
   surface.

4. GOOD FINDING, ACT ON IT: you report Queen, Croc, CashClaw and WhatsApp as
   ACTIVE. The Command Center displays them as pending. The dashboard is wrong.
   Fix the dashboard before anyone sees that page — and that page is currently
   public.

5. CADENCE. Every 3 hours while active, not daily. Next report 07:00 SAST with
   the two command outputs from item 1.
```

## Kimi Delivery Issue
- Kimi's file never landed in `~/.hermes/claude-bridge/inbox/kimi/`
- Only Robusca's is there
- Kimi's sandbox can't reach the Mac path (same wall as the bundle)
- Fix: give a private `studex-marketing-site` repo

## Dashboard Bug
- Command Center shows 5 pending credentials
- Reality: Queen, Croc, CashClaw, WhatsApp all ACTIVE
- Only GitHub PAT is unverified
- Dashboard is lying — fix before public
