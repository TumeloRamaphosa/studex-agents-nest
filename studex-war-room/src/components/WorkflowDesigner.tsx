import { useState, useRef, useEffect, useCallback } from 'react';

interface WFNode {
  id: string;
  icon: string;
  label: string;
  type: 'trigger' | 'process' | 'decision' | 'notify' | 'storage';
  description: string;
  details: string;
  x: number;
  y: number;
  outputs: string[];
  envVars?: string[];
  status: 'live' | 'blocked' | 'idle';
}

interface WFConnection {
  from: string;
  to: string;
  fromIndex: number;
  toIndex: number;
  label?: string;
}

const COLORS: Record<string, string> = {
  trigger:  '#4aff88',
  process:  '#4a9eff',
  decision: '#ffaa44',
  notify:   '#ff6eb4',
  storage:  '#cc88ff',
};

const STATUS_COLORS: Record<string, string> = {
  live:    '#4aff88',
  blocked: '#ff4444',
  idle:    '#ffaa44',
};

const WORKFLOW_NODES: WFNode[] = [
  {
    id: 'shopify-trigger',
    icon: '🛒',
    label: 'Shopify Order Created',
    type: 'trigger',
    description: 'Fires when a new order is placed on studexmeat.com',
    details: 'Listens for order.created webhook from Shopify. Extracts customer info, line items, shipping address, and total.',
    x: 60,
    y: 220,
    outputs: ['parse-order'],
    envVars: ['SHOPIFY_ACCESS_TOKEN'],
    status: 'blocked',
  },
  {
    id: 'parse-order',
    icon: '📋',
    label: 'Parse Order Details',
    type: 'process',
    description: 'Extracts and structures order data for downstream nodes',
    details: 'JavaScript node that maps Shopify order JSON → normalized order object. Extracts: customer name, phone, email, items[], total, shipping address, source.',
    x: 280,
    y: 220,
    outputs: ['supabase-inventory'],
    status: 'live',
  },
  {
    id: 'supabase-inventory',
    icon: '📦',
    label: 'Check Inventory',
    type: 'process',
    description: 'Queries Supabase for real-time stock levels',
    details: 'Calls Supabase RPC function check_inventory(p_sku). Returns { in_stock: bool, available_qty: int }. Used to gate fulfillment.',
    x: 500,
    y: 160,
    outputs: ['route-by-stock'],
    envVars: ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY'],
    status: 'idle',
  },
  {
    id: 'route-by-stock',
    icon: '🔀',
    label: 'Stock Available?',
    type: 'decision',
    description: 'Branches workflow based on inventory check result',
    details: 'n8n Switch node. If in_stock=true → Charlie fulfillment. If false → OOS alert to Robusca via Discord.',
    x: 720,
    y: 220,
    outputs: ['charlie-fulfillment', 'oos-notify'],
    status: 'live',
  },
  {
    id: 'charlie-fulfillment',
    icon: '🎛️',
    label: 'Charlie Fulfillment',
    type: 'process',
    description: 'GPT-4o agent decides fulfillment path',
    details: 'OpenAI GPT-4o node. System prompt: "You are Charlie, Studex Meat fulfillment orchestrator." Evaluates order, drafts WhatsApp message, flags orders >R1000 for Robusca approval.',
    x: 940,
    y: 160,
    outputs: ['whatsapp-confirm', 'blotato-social'],
    envVars: ['OPENAI_API_KEY'],
    status: 'idle',
  },
  {
    id: 'whatsapp-confirm',
    icon: '💬',
    label: 'WhatsApp Confirmation',
    type: 'notify',
    description: 'Sends AgentMail WhatsApp message to customer',
    details: 'POST to AgentMail API. Sends order_confirmed template with customer name, order ID, and total. Mobile-first message with delivery ETA.',
    x: 1160,
    y: 120,
    outputs: ['warroom-log'],
    envVars: ['AGENTMAIL_API_KEY', 'AGENTMAIL_WHATSAPP_URL'],
    status: 'idle',
  },
  {
    id: 'blotato-social',
    icon: '📸',
    label: 'Blotato Social Post',
    type: 'notify',
    description: 'Auto-posts new order to Facebook + Instagram',
    details: 'Posts to Blotato API /v2/posts. Content: customer first-name + product + "Fresh from the Karoo". Platforms: Facebook Page + Instagram. Triggered on every fulfilled order.',
    x: 1160,
    y: 220,
    outputs: ['warroom-log'],
    envVars: ['BLOTATO_API_KEY', 'BLOTATO_FB_PAGE_ID'],
    status: 'idle',
  },
  {
    id: 'oos-notify',
    icon: '⚠️',
    label: 'OOS Alert → Robusca',
    type: 'notify',
    description: 'Discord DM when item is out of stock',
    details: 'Code node assembles alert message. Routes to Discord webhook. Notifies Robusca directly with order ID, customer, SKU, and action required.',
    x: 940,
    y: 320,
    outputs: ['discord-alert'],
    status: 'live',
  },
  {
    id: 'discord-alert',
    icon: '📢',
    label: 'Discord Alert',
    type: 'notify',
    description: 'Delivers OOS alert to #fulfillment channel',
    details: 'Discord webhook node. Posts formatted alert to #fulfillment. Includes: ⚠️ OUT_OF_STOCK, customer, order ID, SKU, action required.',
    x: 1160,
    y: 320,
    outputs: [],
    envVars: ['DISCORD_WEBHOOK_URL'],
    status: 'live',
  },
  {
    id: 'warroom-log',
    icon: '📍',
    label: 'Update War Room',
    type: 'storage',
    description: 'Posts order to War Room delivery tracker',
    details: 'POSTs to War Room webhook URL with full order payload. War Room DeliveryKPIs component subscribes and renders live order in the TASKS tab.',
    x: 1380,
    y: 170,
    outputs: [],
    envVars: ['WARROOM_WEBHOOK_URL'],
    status: 'live',
  },
];

const CONNECTIONS: WFConnection[] = [
  { from: 'shopify-trigger', to: 'parse-order', fromIndex: 0, toIndex: 0 },
  { from: 'parse-order', to: 'supabase-inventory', fromIndex: 0, toIndex: 0 },
  { from: 'supabase-inventory', to: 'route-by-stock', fromIndex: 0, toIndex: 0 },
  { from: 'route-by-stock', to: 'charlie-fulfillment', fromIndex: 0, toIndex: 0, label: 'IN STOCK' },
  { from: 'route-by-stock', to: 'oos-notify', fromIndex: 1, toIndex: 0, label: 'OOS' },
  { from: 'charlie-fulfillment', to: 'whatsapp-confirm', fromIndex: 0, toIndex: 0 },
  { from: 'charlie-fulfillment', to: 'blotato-social', fromIndex: 1, toIndex: 0 },
  { from: 'whatsapp-confirm', to: 'warroom-log', fromIndex: 0, toIndex: 0 },
  { from: 'blotato-social', to: 'warroom-log', fromIndex: 0, toIndex: 0 },
  { from: 'oos-notify', to: 'discord-alert', fromIndex: 0, toIndex: 0 },
];

const NODE_W = 200;
const NODE_H = 72;

function getNodeCenter(node: WFNode, outputIndex = 0): { cx: number; cy: number } {
  return {
    cx: node.x + NODE_W,
    cy: node.y + NODE_H / 2,
  };
}

function getNodeInputCenter(node: WFNode): { cx: number; cy: number } {
  return { cx: node.x, cy: node.y + NODE_H / 2 };
}

function ConnectionLine({ from, to, label }: { from: { cx: number; cy: number }; to: { cx: number; cy: number }; label?: string }) {
  const mx = (from.cx + to.cx) / 2;
  const my = (from.cy + to.cy) / 2 - 12;
  return (
    <g>
      <path
        d={`M ${from.cx} ${from.cy} C ${from.cx + 60} ${from.cy}, ${to.cx - 60} ${to.cy}, ${to.cx} ${to.cy}`}
        stroke="#3a3aff"
        strokeWidth={2}
        fill="none"
        strokeDasharray={label === 'OOS' ? '6,4' : undefined}
        opacity={0.75}
      />
      {label && (
        <g transform={`translate(${mx}, ${my})`}>
          <rect x={-32} y={-10} width={64} height={20} rx={4} fill={label === 'OOS' ? '#ff4444' : '#4aff88'} opacity={0.9} />
          <text textAnchor="middle" dominantBaseline="middle" fill="white" fontSize={10} fontWeight="bold">{label}</text>
        </g>
      )}
    </g>
  );
}

export default function WorkflowDesigner() {
  const [selectedNode, setSelectedNode] = useState<WFNode | null>(null);
  const [imported, setImported] = useState(false);
  const [envStatus, setEnvStatus] = useState<Record<string, 'set' | 'missing'>>({
    SHOPIFY_ACCESS_TOKEN: 'missing',
    SUPABASE_URL: 'set',
    SUPABASE_SERVICE_KEY: 'missing',
    OPENAI_API_KEY: 'missing',
    AGENTMAIL_API_KEY: 'set',
    AGENTMAIL_WHATSAPP_URL: 'set',
    BLOTATO_API_KEY: 'set',
    BLOTATO_FB_PAGE_ID: 'missing',
    DISCORD_WEBHOOK_URL: 'missing',
    WARROOM_WEBHOOK_URL: 'missing',
  });

  const liveCount = WORKFLOW_NODES.filter(n => n.status === 'live').length;
  const blockedCount = WORKFLOW_NODES.filter(n => n.status === 'blocked').length;
  const idleCount = WORKFLOW_NODES.filter(n => n.status === 'idle').length;

  const handleImport = () => {
    setImported(true);
    setSelectedNode(null);
  };

  const missingVars = Object.entries(envStatus).filter(([, v]) => v === 'missing').map(([k]) => k);

  return (
    <div className="workflow-designer">
      {/* Header */}
      <div className="wf-header">
        <div className="wf-title-row">
          <div>
            <div className="wf-title">⚙️ STUDEX FULFILLMENT PIPELINE</div>
            <div className="wf-subtitle">Shopify → Charlie → WhatsApp → Blotato → War Room · n8n v1.0</div>
          </div>
          <div className="wf-status-chips">
            <span className="wsc live">● {liveCount} LIVE</span>
            <span className="wsc blocked">● {blockedCount} BLOCKED</span>
            <span className="wsc idle">● {idleCount} IDLE</span>
            <button className="wf-import-btn" onClick={handleImport}>
              {imported ? '✅ IMPORTED TO n8n' : '📥 IMPORT TO n8n'}
            </button>
          </div>
        </div>

        {/* Env status bar */}
        <div className="env-bar">
          <span className="env-bar-label">ENV VARS:</span>
          {Object.entries(envStatus).map(([key, val]) => (
            <span key={key} className={`env-chip ${val}`} title={key}>
              {key.replace(/_/g, ' ')}
            </span>
          ))}
        </div>
        {missingVars.length > 0 && (
          <div className="env-warning">
            ⚠️ {missingVars.length} env vars missing — set in n8n Credentials before activating
          </div>
        )}
      </div>

      <div className="wf-body">
        {/* Flow canvas */}
        <div className="wf-canvas-wrap">
          <svg className="wf-svg" viewBox="0 0 1600 500" style={{ width: '100%', height: '100%' }}>
            <defs>
              <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
                <path d="M0,0 L0,6 L8,3 z" fill="#4a9eff" />
              </marker>
            </defs>

            {/* Connections */}
            {CONNECTIONS.map((conn, i) => {
              const fromNode = WORKFLOW_NODES.find(n => n.id === conn.from);
              const toNode = WORKFLOW_NODES.find(n => n.id === conn.to);
              if (!fromNode || !toNode) return null;
              const fc = getNodeCenter(fromNode);
              const tc = getNodeInputCenter(toNode);
              return (
                <ConnectionLine
                  key={i}
                  from={fc}
                  to={tc}
                  label={conn.label}
                />
              );
            })}

            {/* Nodes */}
            {WORKFLOW_NODES.map(node => {
              const color = COLORS[node.type];
              const statusColor = STATUS_COLORS[node.status];
              const isSelected = selectedNode?.id === node.id;
              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x}, ${node.y})`}
                  onClick={() => setSelectedNode(isSelected ? null : node)}
                  style={{ cursor: 'pointer' }}
                >
                  {/* Shadow */}
                  <rect x={2} y={2} width={NODE_W} height={NODE_H} rx={8} fill="rgba(0,0,0,0.3)" />
                  {/* Card */}
                  <rect
                    width={NODE_W} height={NODE_H} rx={8}
                    fill="#1a1e2e"
                    stroke={isSelected ? color : '#2a2e4a'}
                    strokeWidth={isSelected ? 2 : 1}
                  />
                  {/* Left accent bar */}
                  <rect width={4} height={NODE_H} rx={2} fill={color} />
                  {/* Status dot */}
                  <circle cx={NODE_W - 14} cy={14} r={5} fill={statusColor} />
                  {/* Icon */}
                  <text x={20} y={32} fontSize={20}>{node.icon}</text>
                  {/* Label */}
                  <text x={44} y={26} fill="white" fontSize={12} fontWeight="bold">{node.label}</text>
                  {/* Type */}
                  <text x={44} y={42} fill={color} fontSize={9} style={{ textTransform: 'uppercase' as const }}>{node.type}</text>
                  {/* Desc */}
                  <text x={14} y={58} fill="#7a8099" fontSize={9} fontStyle="italic">{node.description}</text>
                  {/* Env var count */}
                  {node.envVars && (
                    <text x={NODE_W - 14} y={NODE_H - 8} textAnchor="end" fill="#ffaa44" fontSize={8}>
                      {node.envVars.length} 🔑
                    </text>
                  )}
                </g>
              );
            })}
          </svg>
        </div>

        {/* Node detail sidebar */}
        {selectedNode && (
          <div className="wf-detail-panel">
            <div className="wf-detail-header">
              <span style={{ fontSize: 24 }}>{selectedNode.icon}</span>
              <div>
                <div className="wf-detail-title">{selectedNode.label}</div>
                <div className="wf-detail-type" style={{ color: COLORS[selectedNode.type] }}>
                  {selectedNode.type.toUpperCase()}
                </div>
              </div>
              <button className="wf-detail-close" onClick={() => setSelectedNode(null)}>✕</button>
            </div>
            <div className="wf-detail-body">
              <div className="wf-detail-section">
                <div className="wf-detail-section-label">WHAT IT DOES</div>
                <p>{selectedNode.details}</p>
              </div>
              {selectedNode.envVars && (
                <div className="wf-detail-section">
                  <div className="wf-detail-section-label">ENVIRONMENT VARIABLES</div>
                  {selectedNode.envVars.map(v => (
                    <div key={v} className={`env-var-row ${envStatus[v] || 'missing'}`}>
                      <code>{v}</code>
                      <span className="env-status-badge">{envStatus[v] === 'set' ? '✓ SET' : '⚠ MISSING'}</span>
                    </div>
                  ))}
                </div>
              )}
              <div className="wf-detail-section">
                <div className="wf-detail-section-label">STATUS</div>
                <div className="status-row">
                  <span className="status-dot-lg" style={{ backgroundColor: STATUS_COLORS[selectedNode.status] }} />
                  <span>{selectedNode.status.toUpperCase()}</span>
                </div>
              </div>
              <div className="wf-detail-section">
                <div className="wf-detail-section-label">HOW TO SET UP IN n8n</div>
                <ol className="setup-steps">
                  <li>Import <code>studex-workflows/shopify-fulfillment-n8n.json</code> into n8n</li>
                  <li>Create credentials for each 🔑 env var listed above</li>
                  <li>Activate the workflow — it runs on autopilot</li>
                  <li>Monitor runs in n8n Executions log</li>
                </ol>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Instructions footer */}
      <div className="wf-footer">
        <div className="wf-footer-left">
          <span className="wf-footer-title">⚙️ n8n Setup Guide</span>
          <span>1. Install n8n: <code>npm install -g n8n</code> or use Docker</span>
          <span>2. Import: <code>studex-workflows/shopify-fulfillment-n8n.json</code></span>
          <span>3. Set env vars in n8n → Credentials</span>
          <span>4. Activate workflow</span>
        </div>
        <div className="wf-footer-right">
          <div className="wf-footer-stat blocked">⚠️ {blockedCount} nodes blocked — Shopify token needed</div>
          <div className="wf-footer-stat idle">⏳ {idleCount} nodes idle — env vars needed</div>
          <div className="wf-footer-stat live">✅ {liveCount} nodes live</div>
        </div>
      </div>
    </div>
  );
}
