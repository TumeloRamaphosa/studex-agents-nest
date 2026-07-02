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
    lastSeen: '2026-07-02 20:00 SAST',
    avatar: '👑',
    specialties: ['Daily Standups', 'CEO Reports', 'Cron Scheduling', 'DNS Config', 'Agent Coordination', 'China Coffee Trade'],
    currentTasks: [
      'Build Hour: War Room China Coffee upgrade — DEPLOYED ✅',
      'Voicebox: clone Tumelo voice for WhatsApp customer service',
      'Contact Svetlana @ PROWTC — China zero-tariff pricing Jul 4',
      'Get Rwanda A1/A2 FOB quote before Chinese buyers lift prices',
      'World of Coffee Dubai 2027 — flag to Tumelo as must-attend',
    ],
    recentActivity: 'Build Hour Jul 2: upgraded War Room with China coffee research. China eliminated tariffs on African coffee Jul 1 2026 — historic opportunity. $42B China coffee market now open to Rwanda/African suppliers at 0% tariff.',
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
    status: 'blocked',
    statusReason: 'Meta user token expired Jun 22',
    lastSeen: '2026-07-02 19:00 SAST',
    avatar: '🎬',
    specialties: ['Content Strategy', 'Youth Day Campaign', 'FeedHive Scheduling', 'TikTok (@freekpik)', 'Instagram (@higgsfikd)', 'Blotato Automation'],
    currentTasks: [
      'Connect Blotato → Facebook Page + Instagram (OAuth login needed)',
      'Set up weekly auto-post queue for StudEx Meat',
      'Post Youth Day content — BLOCKED on Meta token',
      'World of Coffee Dubai 2027 content plan',
    ],
    recentActivity: 'Jul 2 2026: Blotato connected to studex-meat-subscription pipeline. Action needed: blotato.com → connect Facebook Page + Instagram via OAuth. Auto-post queue ready to activate.',
  },
  {
    id: 'hermes',
    name: 'Hermes',
    role: 'DevOps / CTO',
    type: 'devops',
    color: '#00e5cc',
    status: 'active',
    lastSeen: '2026-06-26 00:14 SAST',
    avatar: '⚡',
    specialties: ['Orgo VM', 'OpenClaw Gateway', 'GitHub Sync', 'Discord Bot', 'Three.js War Room'],
    currentTasks: [
      'Build Godot OS Phase 1 War Room ← IN PROGRESS',
      'Deploy Discord bot to server',
      'Audit VM for Polsia agent',
      'studexhermes-command repo sync',
    ],
    recentActivity: 'Building Godot OS Phase 1. Audited VM Jun 25: Polsia found (Jun 22). Shopify agent confirmed. GitHub sync up to date.',
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
