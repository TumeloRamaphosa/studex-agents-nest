# Notion Bridge — Rocket.Chat → Notion Sync

## What it does
When an agent posts in Rocket.Chat, this bridge captures it and:
1. Creates/updates a Notion page automatically
2. Posts Rocket.Chat notifications to Notion databases
3. Syncs agent stand-up summaries to Notion

## Architecture
```
Rocket.Chat Message
    ↓ (webhook)
Bridge Server (Node.js, port 3002 on VM)
    ↓
Notion API
    ↓
Pages/Databases updated
```

## Setup

### 1. Notion Integration
1. Go to notion.so/profile/integrations → Create "Rocket.Chat Bridge"
2. Share the target Notion workspace with the integration
3. Copy the Internal Integration Token

### 2. Set on VM
```bash
export NOTION_API_KEY="secret_xxx"
export NOTION_WORKSPACE_ID="workspace_id_xxx"
```

### 3. Environment vars (add to /root/.bashrc on VM)
```bash
export NOTION_API_KEY="secret_xxx"
export NOTION_WORKSPACE_ID="workspace_id_xxx"
export BRIDGE_PORT=3002
```

## What Gets Synced

| Rocket.Chat Event | Notion Action |
|---|---|
| New order in #orders | New page in "Orders" database |
| Delivery status change | Update order page status |
| Naledi posts in #marketing | New row in "Content Calendar" |
| Agent board meeting | New "Board Meeting" page in vault |
| Alert in #alerts | New page in "Alerts" database |

## Webhook URLs

Bridge listens at: `http://67.213.119.157:3002/`

Register in Rocket.Chat:
```
Admin → Webhooks → Add Custom Outgoing Webhook
URL: http://67.213.119.157:3002/rocketchat
Events: message_created, room_changed
```

## Notion Database IDs (to configure)
| Database | Notion DB ID |
|---|---|
| Orders | `NOTION_ORDERS_DB` |
| Products | `NOTION_PRODUCTS_DB` |
| Content Calendar | `NOTION_CONTENT_DB` |
| Delivery Partners | `NOTION_PARTNERS_DB` |
| Board Meetings | `NOTION_MEETINGS_DB` |

## Example Notion Page Creation (Node.js)
```javascript
const { Client } = require('@notionhq/client')
const notion = new Client({ auth: process.env.NOTION_API_KEY })

// Create order page in Notion
async function createOrderPage(order) {
  return await notion.pages.create({
    parent: { database_id: process.env.NOTION_ORDERS_DB },
    properties: {
      'Order ID': { title: [{ text: { content: order.id } }] },
      'Customer': { rich_text: [{ text: { content: order.customer } }] },
      'Total': { number: order.total },
      'Status': { select: { name: order.status } },
      'Created': { date: { start: order.created_at } },
    },
    children: [
      {
        object: 'block',
        type: 'bulleted_list_item',
        bulleted_list_item: {
          rich_text: [{ text: { content: `Items: ${order.items.join(', ')}` } }]
        }
      }
    ]
  })
}
```

## Agent Connection
Agents in Rocket.Chat can trigger Notion actions:
```
@notion create order [id] [customer] [amount]
@notion update status [order_id] [new_status]
@notion sync marketing [campaign_name]
@notion log meeting [date]
```

---
*Bridge code at: /workspace/studex-os/agents/bridges/notion-bridge.js*
