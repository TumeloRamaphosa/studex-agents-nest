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
    lastSeen: '2026-07-21 21:00 SAST',
    avatar: '👑',
    specialties: ['Daily Standups', 'CEO Reports', 'Cron Scheduling', 'DNS Config', 'Agent Coordination', 'China Coffee Trade'],
    currentTasks: [
      '🔥 URGENT: Apply for CIIE booth at ciie.org — deadline Aug 31 2026',
      '🔥 URGENT: Send Luckin Coffee outreach — CIIE booth + Rwanda A1/A2 sample offer',
      '🔥 URGENT: Send Tim Hortons China outreach — heritage angle + CIIE',
      'PROWTC Dubai: Follow up with Svetlana — Q4 China corridor depends on it',
      'n8n on DigitalOcean VPS — ~$6/month temporary Orgo replacement',
      'Make.com for Naledi — visual Blotato workflows (easier than n8n)',
    ],
    recentActivity: 'Build Hour Jul 21 2026: War Room China pipeline updated with CIIE booth, Luckin Coffee, Tim Hortons China, PROWTC Dubai, Shanghai importers. China zero-tariff effective Jul 20 2026 (YESTERDAY). Rwanda is white space — Luckin locked to Brazil deal through 2029. CIIE Aug 31 deadline is THE key B2B touchpoint.',
  },
  {
    id: 'charlie',
    name: 'Charlie',
    role: 'Orchestrator',
    type: 'orchestrator',
    color: '#4a9eff',
    status: 'idle',
    statusReason: 'Shopify API token not provided',
    lastSeen: '2026-07-02 19:00 SAST',
    avatar: '🎛️',
    specialties: ['Perplexity Computer', 'Agent Routing', 'Order Processing', 'Supabase DB'],
    currentTasks: [
      'Shopify agent: needs SHOPIFY_ACCESS_TOKEN to activate',
      'Route orders to Shopify — blocked',
      'Coordinate Naledi content pipeline',
      'Monitor Finance sub-agent',
    ],
    recentActivity: 'Jul 2 2026: all sub-agents idle. Shopify token needed to activate order routing. Naledi content pipeline needs Blotato connected. Voicebox queued for customer service automation.',
  },
  {
    id: 'naledi',
    name: 'Naledi',
    role: 'CMO / Content Lead',
    type: 'cmo',
    color: '#ff6eb4',
    status: 'idle',
    lastSeen: '2026-07-21 19:00 SAST',
    avatar: '🎬',
    specialties: ['Content Strategy', 'Youth Day Campaign', 'FeedHive Scheduling', 'TikTok (@freekpik)', 'Instagram (@higgsfikd)', 'Blotato Automation'],
    currentTasks: [
      'ACTION NEEDED: blotato.com → reconnect Facebook Page + Instagram (Meta OAuth)',
      'Set up Make.com visual workflows for Blotato auto-posting (easier than n8n)',
      'Content plan: China Coffee / CIIE outreach campaign + Rwanda provenance story',
      'World of Coffee Dubai 2027 content angle',
    ],
    recentActivity: 'Jul 21 2026: Meta token re-auth needed in Blotato dashboard. Make.com recommended as easier alternative for visual workflows. China Coffee LP deployed at studexwildlife.com/china-coffee — share in all outreach. Naledi unblocked once FB re-auth completes.',
  },
  {
    id: 'hermes',
    name: 'Hermes',
    role: 'DevOps / CTO',
    type: 'devops',
    color: '#00e5cc',
    status: 'active',
    lastSeen: '2026-07-21 21:00 SAST',
    avatar: '⚡',
    specialties: ['Orgo VM', 'OpenClaw Gateway', 'GitHub Sync', 'Discord Bot', 'Three.js War Room'],
    currentTasks: [
      'War Room China Coffee upgrade — DEPLOYED Jul 21 ✅',
      'Deploy Discord bot to server',
      'n8n on DigitalOcean VPS — setup script ready, needs DO API key',
      'Orgo VM rebuild — pending',
    ],
    recentActivity: 'Build Hour Jul 21: War Room updated with CIIE booth, Luckin, Tim Hortons, PROWTC, Shanghai importer deals. All agents tab wired. War Room deployed at new URL. Orgo VM rebuild pending.',
  },
];

export const socialStatus = [
  { name: 'Shopify', status: 'blocked', detail: 'No API token — Charlie idle', color: '#ff4444' },
  { name: 'Facebook', status: 'blocked', detail: 'Token expired Jun 22 — reconnect in Blotato', color: '#ff4444' },
  { name: 'Instagram', status: 'blocked', detail: 'Token expired Jun 22 — reconnect in Blotato', color: '#ff4444' },
  { name: 'TikTok', status: 'idle', detail: '@freekpik — token ok, no active campaign', color: '#ffaa44' },
  { name: 'Discord', status: 'active', detail: 'MiniMax Claw bot — fully operational', color: '#4aff88' },
  { name: 'AgentMail', status: 'active', detail: 'API ready — DNS DKIM verify pending', color: '#4aff88' },
  { name: 'WhatsApp', status: 'blocked', detail: 'Voicebox cloning in progress — Tumelo voice', color: '#ffaa44' },
  { name: 'Blotato', status: 'idle', detail: 'API key set — 0 accounts connected', color: '#ffaa44' },
];
