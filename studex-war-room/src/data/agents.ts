export interface Agent {
  id: string;
  name: string;
  role: string;
  type: string;
  color: string;
  status: 'active' | 'idle' | 'blocked';
  statusReason?: string;
  lastSeen: string;
  avatar: string;
  specialties: string[];
  currentTasks: string[];
  recentActivity: string;
}

export const agents: Agent[] = [
  {
    id: 'robusca',
    name: 'Robusca',
    role: 'CEO / Chief of Staff',
    type: 'ceo-agent',
    color: '#d4a017',
    status: 'active',
    lastSeen: '2026-09-27 11:00 PM SAST',
    avatar: '👑',
    specialties: ['Daily Standups', 'CEO Reports', 'Cron Scheduling', 'DNS Config', 'Agent Coordination', 'China Coffee Trade', 'Build Hour'],
    currentTasks: [
      'Build Hour Sep 27 2026: War Room live status upgrade — session presence, CIIE banner, Meta reconnect alert',
      'Blotato MCP analytics test — 0 accounts connected, needs Meta OAuth re-auth in blotato.com dashboard',
      'CIIE Nov 5: catalog PDF + booth status — 9 days to deadline',
      'n8n VM webhook build — Shopify → Discord → WhatsApp order notifications (deferred)',
    ],
    recentActivity: 'Build Hour Sep 27 2026: War Room upgraded with live session presence in AgentNPCDock (green pulse for live agents). CIIE countdown banner added to NavigationHUD (Nov 5 = 9 days). BlotatoPipeline Meta reconnect alert made prominent. Research: SA e-commerce R159bn 2026, Blotato Analytics MCP live but 0 accounts connected.',
  },
  {
    id: 'charlie',
    name: 'Charlie',
    role: 'Orchestrator',
    type: 'orchestrator',
    color: '#4a9eff',
    status: 'active',
    lastSeen: '2026-09-27 10:30 PM SAST',
    avatar: '🎛️',
    specialties: ['Perplexity Research', 'Agent Routing', 'Order Processing', 'ClickUp', 'n8n Workflows'],
    currentTasks: [
      'P0: Deploy n8n on Orgo VM — Docker one-liner pending Orgo VM access fix',
      'P0: n8n workflow — AgentMail lead → ClickUp task → Discord ping for coffee pipeline',
      'P1: Shopify → Discord webhook for order notifications',
      'Lead routing: stud.exchange inbox → ClickUp → assign to Naledi < 1hr SLA',
    ],
    recentActivity: 'Sep 27 2026: Research complete. SA e-commerce at R159bn (2026), Blotato Analytics MCP live but no accounts connected. n8n deployment deferred to next session pending Orgo VM access confirmation. CIIE Nov 5 catalog priority confirmed.',
  },
  {
    id: 'naledi',
    name: 'Naledi',
    role: 'CMO / Content Lead',
    type: 'cmo',
    color: '#ff6eb4',
    status: 'blocked',
    statusReason: 'Meta tokens expired Jun 22 — FB + IG disconnected in Blotato. Re-auth required at blotato.com → Settings → Connected Accounts',
    lastSeen: '2026-09-27 09:00 PM SAST',
    avatar: '🎬',
    specialties: ['Content Strategy', 'Blotato Automation', 'FeedHive Scheduling', 'TikTok', 'Instagram', 'YouTube'],
    currentTasks: [
      'ACTION REQUIRED: blotato.com → Settings → Connected Accounts → Re-auth Facebook + Instagram via Meta OAuth',
      'CIIE content calendar: China Coffee origin story, CIIE booth promo, Rwanda provenance posts',
      'Wolf Pack subscription content: justify 3-4x premium pricing through brand story',
      'Corporate gift bundle landing page — 1-pager with AgentMail lead capture',
    ],
    recentActivity: 'Sep 27 2026: Meta tokens expired Jun 22 — FB + IG still disconnected. Content pipeline blocked until re-auth. Research: no SA competitor has a subscription tier like Wolf Pack — this is the moat. Subscription tier (R299-R999/mo) confirmed as top revenue opportunity. CIIE Nov 5 content plan drafted.',
  },
  {
    id: 'hermes',
    name: 'Hermes',
    role: 'DevOps / CTO',
    type: 'devops',
    color: '#00e5cc',
    status: 'active',
    lastSeen: '2026-09-27 11:00 PM SAST',
    avatar: '⚡',
    specialties: ['Orgo VM', 'OpenClaw Gateway', 'GitHub Sync', 'Docker', 'Discord Bot', 'War Room Canvas'],
    currentTasks: [
      'War Room Sep 27 upgrade: live agent presence + CIIE banner — DEPLOYED',
      'n8n Docker deploy on Orgo VM: docker run -d --name n8n -p 5678:5678 n8nio/n8n',
      'Verify Orgo VM API key — test connectivity to 67.213.119.157',
      'Voicebox on Orgo VM — customer service automation (deferred)',
    ],
    recentActivity: 'Build Hour Sep 27 2026: War Room live status upgrade deployed. AgentNPCDock now shows live session pulse (green dot for active agents). NavigationHUD shows CIIE countdown banner (Nov 5 = 9 days away). Orgo VM n8n deployment pending access verification.',
  },
];

export const socialStatus = [
  { name: 'Shopify', status: 'active', detail: 'Storefront API connected — live orders in War Room DeliveryKPIs', color: '#4aff88' },
  { name: 'Facebook', status: 'blocked', detail: 'Token expired Jun 22 — reconnect: blotato.com → Settings → Connected Accounts → Meta OAuth', color: '#ff4444' },
  { name: 'Instagram', status: 'blocked', detail: 'Token expired Jun 22 — reconnect: blotato.com → Settings → Connected Accounts → Meta OAuth', color: '#ff4444' },
  { name: 'TikTok', status: 'idle', detail: '@freekpik — token ok, no active campaign running', color: '#ffaa44' },
  { name: 'Discord', status: 'active', detail: 'MiniMax Claw bot MTUwODg... — fully operational', color: '#4aff88' },
  { name: 'AgentMail', status: 'active', detail: 'robusca.romanov@studex-group.com — operational, 3 inboxes confirmed', color: '#4aff88' },
  { name: 'WhatsApp', status: 'idle', detail: 'Business accounts 749827870391669 + 599570915061463 — connected via Meta Business', color: '#ffaa44' },
  { name: 'Blotato', status: 'idle', detail: 'API key confirmed — 0 accounts connected — URGENT: reconnect FB + IG in blotato.com', color: '#ffaa44' },
  { name: 'Takealot', status: 'idle', detail: 'Not connected — white space: premium biltong shelf has no dominant player', color: '#ffaa44' },
];
