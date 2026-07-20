# StudEx Morning Routine — Robusca Protocol

**Owner:** Tumelo Ramaphosa (Agent Lord)
**Maintained by:** Robusca — Chief of Staff
**Last updated:** 2026-06-15

---

## The Morning Routine

### 08:00 SAST — Wake Sequence
- Robusca (Perplexity Computer) fires daily 8PM report (previous night)
- Tumelo reviews the nightly cron report on arrival
- Open War Room dashboard: https://www.perplexity.ai/computer/a/studex-war-room-vLlaaCxbTSKY9W6ammcqNQ

### 08:30 SAST — Triage (15 min)
Review in this order:
1. **Shopify pipeline** — any new orders overnight? Any new unfulfilled paid orders?
2. **Inventory alerts** — check negative stock SKUs (Patties, Tomahawk, Biltong)
3. **Gmail** (`tumelor001@gmail.com`) — scan AgentMail + Gmail widget in Comms tab
4. **Ads** — check Facebook Father's/Youth campaign spend + Google PMAX status
5. **Content queue** — any items pending approval in the Approvals tab?

### 09:00 SAST — Priority Decision (10 min)
Ask Robusca: "What are the 3 most important things today?"
Robusca responds from:
- Unfulfilled order backlog (most urgent = highest value + oldest date)
- Content calendar (what needs to go live today)
- Operational flags from previous night's cron

### 09:15 SAST — Execution Block (2–3 hrs)
Options in priority order:
1. Fulfil urgent orders (use Shopify app)
2. Approve and queue content (say "approve [post name]" to Robusca)
3. Build / code sprint (run AGENTS.md via Claude Code / Alchemy)
4. Content creation (say "generate content for [topic]")

### 12:00 SAST — Midday Check (5 min)
- Robusca pulls fresh Shopify order count
- Check ad spend pacing (Google PMAX + Facebook)
- Review any pending notifications

### 18:00 SAST — End of Day (10 min)
- Queue next day's content
- Check unfulfilled orders — flag anything urgent for 8PM report
- Commit any code changes to robusca-brain

### 20:00 SAST — Nightly Cron (automated)
- Robusca pulls Shopify orders + inventory
- Writes daily log to `/workspace/cron_tracking/daily/YYYY-MM-DD.md`
- Sends in-app notification with daily summary
- Sends urgent notification if critical new issues found

---

## Platforms Checked Every Morning

| Platform | What to check | How |
|---|---|---|
| Shopify | New orders, unfulfilled pipeline | War Room → Shopify tab |
| Gmail | Emails + AgentMail forwards | War Room → Comms tab |
| AgentMail | studex-2571 forwarded briefs | War Room → Agents tab |
| Google Ads | PMAX spend + ROAS | War Room → Revenue Engine |
| Facebook Ads | Campaign status + spend | War Room → Ads tab |
| GitHub | robusca-brain last commit | github.com/TumeloRamaphosa/robusca-brain |

---

## Daily Cadence Summary

```
08:00  Nightly report review
08:30  Triage (Shopify + Gmail + Ads)
09:00  Priority decision with Robusca
09:15  Execution (orders / content / build)
12:00  Midday check
18:00  End of day queue
20:00  Robusca automated nightly cron
```

---

## Robusca Activation Phrases

| Say this | Robusca does this |
|---|---|
| "morning report" | Pulls live Shopify + inventory snapshot |
| "what are the 3 priorities today" | Analyses pipeline + calendar + ads |
| "approve [content name]" | Queues content for posting (does NOT post without confirmation) |
| "sync messages" | Pulls fresh Gmail + AgentMail into dashboard |
| "run OS build" | Prints Claude Code agent command to finish War Room |
| "daily brief" | Full summary: orders + inventory + ads + content |

---

*Robusca — Chief of Staff | StudEx Group*
*"Start every day with clarity. Execute without noise."*
