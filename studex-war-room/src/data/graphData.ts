// Types defined in this file

export interface GraphNode {
  id: string;
  label: string;
  type: 'agent' | 'vault' | 'product' | 'task' | 'github' | 'campaign';
  x?: number;
  y?: number;
  z?: number;
  vx?: number;
  vy?: number;
  vz?: number;
  color: string;
  glowColor: string;
  size: number;
  info: string;
  sublabel?: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  label?: string;
  type: 'owns' | 'uses' | 'relates' | 'creates' | 'blocked';
  color: string;
}

export const initialNodes: GraphNode[] = [
  // CENTRAL HUB
  {
    id: 'studex-os',
    label: 'STUDEX OS',
    type: 'vault',
    color: '#d4a017',
    glowColor: '#ffcc00',
    size: 3.5,
    info: 'StudEx Meat Operating System — the command center for all operations. Currently in Phase 1: Web War Room.',
    sublabel: 'Central Hub',
  },
  // AGENTS
  {
    id: 'charlie',
    label: 'Charlie',
    type: 'agent',
    color: '#4a9eff',
    glowColor: '#80c0ff',
    size: 2.2,
    info: 'Orchestrator Agent — coordinates all sub-agents, manages Perplexity Computer, routes requests.',
    sublabel: 'Orchestrator',
  },
  {
    id: 'naledi',
    label: 'Naledi',
    type: 'agent',
    color: '#ff6eb4',
    glowColor: '#ffb0d0',
    size: 2.2,
    info: 'CMO Agent — manages all content creation, Youth Day campaign, social media scheduling via FeedHive.',
    sublabel: 'CMO',
  },
  {
    id: 'hermes',
    label: 'Hermes',
    type: 'agent',
    color: '#00e5cc',
    glowColor: '#60ffea',
    size: 2.2,
    info: 'DevOps Agent — manages the Orgo VM, OpenClaw, War Room deployment, infrastructure.',
    sublabel: 'DevOps',
  },
  {
    id: 'robusca',
    label: 'Robusca',
    type: 'agent',
    color: '#d4a017',
    glowColor: '#ffcc44',
    size: 2.8,
    info: 'COO / Chief of Staff — Tumelo\'s AI proxy, daily standups, CEO reports, cron scheduling.',
    sublabel: 'COO / CEO Agent',
  },
  // VAULT SECTIONS
  {
    id: 'vault-brand',
    label: 'Brand Bible',
    type: 'vault',
    color: '#b06020',
    glowColor: '#e08040',
    size: 1.8,
    info: 'Brand positioning: "Premium Halaal Meat. Proudly South African." Competitors: Woolies, Meatblock, Craft Carnivores. Tagline drives all copy.',
    sublabel: '00-Core',
  },
  {
    id: 'vault-products',
    label: 'Products',
    type: 'product',
    color: '#ff4444',
    glowColor: '#ff6666',
    size: 1.5,
    info: '⚠️ NEEDS DOCUMENTING — Products folder is empty. Categories exist in Brand Bible: Wagyu Biltong, Premium Cuts, Droëwors, Gift Boxes, Bundles.',
    sublabel: '03-Products',
  },
  {
    id: 'vault-operations',
    label: 'Operations',
    type: 'vault',
    color: '#6070a0',
    glowColor: '#8090c0',
    size: 1.8,
    info: 'Order processing, Shopify integration, TCG courier (Courier Guy API), Airtable ops tracking, Supabase DB.',
    sublabel: '02-Operations',
  },
  {
    id: 'vault-content',
    label: 'Content',
    type: 'vault',
    color: '#ff6eb4',
    glowColor: '#ffa0d0',
    size: 1.8,
    info: 'Youth Day campaign (⚠️ 9 days late), FeedHive scheduling, Postiz distribution, TikTok (@freekpik), Instagram (@higgsfikd), Facebook.',
    sublabel: '04-Content',
  },
  {
    id: 'vault-finance',
    label: 'Finance',
    type: 'vault',
    color: '#44cc77',
    glowColor: '#70ff99',
    size: 1.6,
    info: 'Revenue tracking, Shopify orders (blocked — no API), R0.00 today. Finance agent monitors via Claude Sonnet.',
    sublabel: '05-Finance',
  },
  {
    id: 'vault-campaigns',
    label: 'Campaigns',
    type: 'campaign',
    color: '#cc88ff',
    glowColor: '#dd99ff',
    size: 1.8,
    info: 'Active: Youth Day "The Youth Shall Inherit the Flame". Pending: Back to School. Planned: Heritage Day, Black Friday.',
    sublabel: '06-Campaigns',
  },
  // TASKS
  {
    id: 'task-youth-day',
    label: 'Youth Day Posts',
    type: 'task',
    color: '#ff8800',
    glowColor: '#ffaa44',
    size: 1.6,
    info: '⚠️ BLOCKED — Facebook post, Instagram carousel, TikTok reels. 9 days late. Blocker: expired Meta token (expired Jun 22).',
    sublabel: 'HIGH PRIORITY',
  },
  {
    id: 'task-shopify',
    label: 'Shopify API',
    type: 'task',
    color: '#ff8800',
    glowColor: '#ffaa44',
    size: 1.6,
    info: '⚠️ BLOCKED — Shopify admin agent built (/root/nest/agents/shopify-agent/) but needs SHOPIFY_ACCESS_TOKEN from Tumelo.',
    sublabel: 'CRITICAL',
  },
  {
    id: 'task-discord',
    label: 'Discord Bot',
    type: 'task',
    color: '#8855ff',
    glowColor: '#aa77ff',
    size: 1.4,
    info: '⚠️ BLOCKED — Discord bot not added to server. MiniMax Claw bot ready. Needs server invite from Tumelo.',
    sublabel: 'PENDING',
  },
  // GITHUB REPOS
  {
    id: 'github-brain',
    label: 'robusca-brain',
    type: 'github',
    color: '#3a3aff',
    glowColor: '#6060ff',
    size: 1.6,
    info: 'Main repo on Orgo VM at /root/robusca/robusca-brain/. Synced daily. Contains agent configs, vault, cron jobs.',
    sublabel: 'github.com/TumeloRamaphosa',
  },
  {
    id: 'github-hermes',
    label: 'studex-hermes',
    type: 'github',
    color: '#00ccaa',
    glowColor: '#40eed0',
    size: 1.4,
    info: 'studexhermes-command repo on VM. War Room dashboard, command execution, infrastructure scripts.',
    sublabel: 'github.com/TumeloRamaphosa',
  },
];

export const initialEdges: GraphEdge[] = [
  // OS → Agents
  { source: 'studex-os', target: 'charlie', label: 'orchestrates', type: 'owns', color: '#4a9eff' },
  { source: 'studex-os', target: 'naledi', label: 'directs', type: 'owns', color: '#ff6eb4' },
  { source: 'studex-os', target: 'hermes', label: 'deployed by', type: 'owns', color: '#00e5cc' },
  { source: 'studex-os', target: 'robusca', label: 'runs', type: 'owns', color: '#d4a017' },
  // Robusca → Vault sections
  { source: 'robusca', target: 'vault-brand', label: 'references', type: 'relates', color: '#d4a017' },
  { source: 'robusca', target: 'vault-operations', label: 'manages', type: 'owns', color: '#6070a0' },
  { source: 'robusca', target: 'vault-content', label: 'oversees', type: 'owns', color: '#6070a0' },
  { source: 'robusca', target: 'vault-finance', label: 'monitors', type: 'owns', color: '#6070a0' },
  { source: 'robusca', target: 'vault-campaigns', label: 'runs', type: 'owns', color: '#6070a0' },
  // Vault relationships
  { source: 'vault-products', target: 'vault-operations', label: 'fulfills', type: 'relates', color: '#b06020' },
  { source: 'vault-operations', target: 'task-shopify', label: 'needs', type: 'uses', color: '#ff8800' },
  { source: 'vault-content', target: 'task-youth-day', label: 'owns', type: 'owns', color: '#ff8800' },
  { source: 'naledi', target: 'vault-content', label: 'owns', type: 'owns', color: '#ff6eb4' },
  // Charlie relationships
  { source: 'charlie', target: 'github-brain', label: 'syncs', type: 'uses', color: '#4a9eff' },
  { source: 'charlie', target: 'task-shopify', label: 'needs', type: 'relates', color: '#4a9eff' },
  // Hermes relationships
  { source: 'hermes', target: 'github-hermes', label: 'maintains', type: 'owns', color: '#00e5cc' },
  { source: 'hermes', target: 'github-brain', label: 'audits', type: 'relates', color: '#00e5cc' },
  { source: 'hermes', target: 'task-discord', label: 'deploys', type: 'uses', color: '#00e5cc' },
  // Blocked tasks
  { source: 'task-youth-day', target: 'vault-content', label: 'part of', type: 'relates', color: '#ff8800' },
  { source: 'task-shopify', target: 'vault-operations', label: 'part of', type: 'relates', color: '#ff8800' },
  // GitHub relationships
  { source: 'github-brain', target: 'github-hermes', label: 'linked to', type: 'relates', color: '#3a3aff' },
  // Campaign
  { source: 'vault-campaigns', target: 'task-youth-day', label: 'includes', type: 'owns', color: '#cc88ff' },
];

// Convert edges to node references
export function buildGraphData() {
  const nodeMap = new Map<string, GraphNode>();
  initialNodes.forEach(n => nodeMap.set(n.id, n));
  return { nodes: initialNodes, edges: initialEdges, nodeMap };
}

// Simple force simulation
export function simulateForces(
  nodes: GraphNode[],
  edges: GraphEdge[],
  nodeMap: Map<string, GraphNode>,
  iterations = 200
) {
  const center = { x: 0, y: 0, z: 0 };
  
  for (let i = 0; i < iterations; i++) {
    const forces = new Map<string, { fx: number; fy: number; fz: number }>();
    nodes.forEach(n => forces.set(n.id, { fx: 0, fy: 0, fz: 0 }));

    // Repulsion between all nodes
    for (let a = 0; a < nodes.length; a++) {
      for (let b = a + 1; b < nodes.length; b++) {
        const na = nodes[a], nb = nodes[b];
        const dx = (nb.x ?? 0) - (na.x ?? 0);
        const dy = (nb.y ?? 0) - (na.y ?? 0);
        const dz = (nb.z ?? 0) - (na.z ?? 0);
        const dist = Math.sqrt(dx * dx + dy * dy + dz * dz) || 0.1;
        const repel = 8.0 / (dist * dist);
        const fx = (dx / dist) * repel;
        const fy = (dy / dist) * repel;
        const fz = (dz / dist) * repel;
        const fa = forces.get(na.id)!;
        const fb = forces.get(nb.id)!;
        fa.fx -= fx; fa.fy -= fy; fa.fz -= fz;
        fb.fx += fx; fb.fy += fy; fb.fz += fz;
      }
    }

    // Attraction along edges
    edges.forEach(e => {
      const src = nodeMap.get(e.source);
      const tgt = nodeMap.get(e.target);
      if (!src || !tgt) return;
      const dx = (tgt.x ?? 0) - (src.x ?? 0);
      const dy = (tgt.y ?? 0) - (src.y ?? 0);
      const dz = (tgt.z ?? 0) - (src.z ?? 0);
      const dist = Math.sqrt(dx * dx + dy * dy + dz * dz) || 0.1;
      const attract = 0.04;
      const fx = (dx / dist) * dist * attract;
      const fy = (dy / dist) * dist * attract;
      const fz = (dz / dist) * dist * attract;
      const fa = forces.get(src.id)!;
      const fb = forces.get(tgt.id)!;
      fa.fx += fx; fa.fy += fy; fa.fz += fz;
      fb.fx -= fx; fb.fy -= fy; fb.fz -= fz;
    });

    // Center gravity
    nodes.forEach(n => {
      const f = forces.get(n.id)!;
      f.fx -= (n.x ?? 0) * 0.01;
      f.fy -= (n.y ?? 0) * 0.01;
      f.fz -= (n.z ?? 0) * 0.01;
    });

    // Apply forces
    nodes.forEach(n => {
      const f = forces.get(n.id)!;
      n.x = (n.x ?? 0) + f.fx * 0.15;
      n.y = (n.y ?? 0) + f.fy * 0.15;
      n.z = (n.z ?? 0) + f.fz * 0.15;
    });
  }

  return nodes;
}
