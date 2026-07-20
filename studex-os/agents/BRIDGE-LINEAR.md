# Linear Bridge — Rocket.Chat → Linear Project Management

## What it does
When an agent or Tumelo types in Rocket.Chat, Linear issues are created automatically:
- Charlie creates issues for delivery problems
- Naledi creates tasks for content campaigns
- Robusca creates high-priority issues for business decisions
- Tumelo can say "create a task for Charlie to fix the kanban" in #ceo

## Architecture
```
Rocket.Chat Message
    ↓ (webhook)
Bridge Server (port 3002)
    ↓
Linear API (issues created/updated)
    ↓
Linear Project
```

## Setup

### 1. Linear API Key
1. Go to linear.app → Settings → API
2. Create a new API key (name: "Rocket.Chat Bridge")
3. Copy it

### 2. Linear Team ID
Find your team ID: `linear.app/settings/teams` — the team slug is in the URL

### 3. Set on VM
```bash
export LINEAR_API_KEY="lin_api_xxx"
export LINEAR_TEAM_ID="studex-meat-team"
```

## What Gets Synced

| Rocket.Chat Event | Linear Action |
|---|---|
| Charlie flags a delivery issue | Create "Delivery" issue, assign to self |
| Naledi publishes content | Create "Content Published" task |
| Tumelo types in #ceo | Create issue in "CEO Tasks" project |
| Delivery agent flags blocker | Create P1 issue, ping Tumelo |
| "New client: [name]" in any channel | Create onboarding task for Charlie |

## Example Linear Issue Creation (Node.js)
```javascript
const { LinearClient } = require('@linear/sdk')

const linear = new LinearClient({ apiKey: process.env.LINEAR_API_KEY })

async function createIssue({ title, description, teamId, priority }) {
  const issue = await linear.createIssue({
    teamId,
    title,
    description,
    priority: priority || 0, // 0=none, 1=urgent, 2=high, 3=normal, 4=low
    label: 'rocketchat-import'
  })
  return issue
}

// Example: Charlie creates a delivery issue
await createIssue({
  title: '[Order #1087] ETA exceeded by 30min',
  description: 'Customer: Tshepo Sebe\nDriver: Derrick Selepe\nDinkoko Pty',
  teamId: process.env.LINEAR_TEAM_ID,
  priority: 1
})
```

## Rocket.Chat Slash Commands
```
/linear create [title] — Create a Linear issue
/linear assign [issue-id] [team-member] — Assign issue
/linear status [issue-id] — Check issue status
/linear priority [issue-id] [p1-p4] — Set priority
/linear close [issue-id] — Mark done
```

## Agent Commands
```
Charlie: "linear task New order received from Shopify — processing"
Naledi: "linear task Content campaign: Instagram Q3 launch"
Robusca: "linear block Token missing — Shopify not connected"
```

## Teams & Projects
| Project | Purpose |
|---|---|
| `studex-ops` | Daily operations tasks |
| `studex-content` | Naledi's marketing campaigns |
| `studex-delivery` | Delivery pipeline issues |
| `studex-tech` | Tech debt, integrations, new features |

---
*Bridge code at: /workspace/studex-os/agents/bridges/linear-bridge.js*
