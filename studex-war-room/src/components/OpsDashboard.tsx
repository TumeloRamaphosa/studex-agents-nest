import { socialStatus } from '../data/agents';

interface Task {
  id: string;
  label: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'blocked' | 'ready' | 'in-progress' | 'done';
  agent: string;
}

const tasks: Task[] = [
  { id: 't1', label: 'Youth Day Posts — Facebook/IG/TikTok', priority: 'critical', status: 'blocked', agent: 'Naledi' },
  { id: 't2', label: 'Shopify Admin API Token', priority: 'critical', status: 'blocked', agent: 'Charlie' },
  { id: 't3', label: 'Refresh Meta User Token', priority: 'high', status: 'blocked', agent: 'Tumelo' },
  { id: 't4', label: 'AgentMail DKIM Verify', priority: 'high', status: 'ready', agent: 'Tumelo' },
  { id: 't5', label: 'Add Discord Bot to Server', priority: 'medium', status: 'blocked', agent: 'Hermes' },
  { id: 't6', label: 'Populate 03-Products in Vault', priority: 'medium', status: 'blocked', agent: 'Robusca' },
  { id: 't7', label: 'Godot OS Phase 1 War Room', priority: 'high', status: 'in-progress', agent: 'Hermes' },
  { id: 't8', label: 'SPF Record — send.stud.exchange', priority: 'high', status: 'ready', agent: 'Tumelo' },
];

const statusLabels: Record<string, string> = {
  blocked: '🔴',
  ready: '🟡',
  'in-progress': '🟢',
  done: '✅',
};

export default function OpsDashboard() {
  const blockedCount = tasks.filter(t => t.status === 'blocked').length;
  const inProgressCount = tasks.filter(t => t.status === 'in-progress').length;
  const readyCount = tasks.filter(t => t.status === 'ready').length;

  return (
    <footer className="ops-dashboard">
      <div className="ops-strip">
        {/* Orders */}
        <div className="ops-module">
          <div className="ops-module-label">📦 TODAY'S ORDERS</div>
          <div className="ops-module-value" style={{ color: '#ff4444' }}>R0.00</div>
          <div className="ops-module-sub">⚠️ Shopify blocked</div>
        </div>

        {/* Task queue */}
        <div className="ops-module">
          <div className="ops-module-label">📋 TASK QUEUE</div>
          <div className="ops-task-counts">
            <span className="count-badge blocked">{blockedCount} Blocked</span>
            <span className="count-badge in-progress">{inProgressCount} Active</span>
            <span className="count-badge ready">{readyCount} Ready</span>
          </div>
          <div className="ops-module-sub">Kanban: a5f1pjxakddy.space.minimax.io</div>
        </div>

        {/* Next task */}
        <div className="ops-module">
          <div className="ops-module-label">▶ NEXT PRIORITY</div>
          <div className="ops-next-task">
            {statusLabels[tasks[0].status]} {tasks[0].label}
          </div>
          <div className="ops-module-sub">Owner: {tasks[0].agent}</div>
        </div>

        {/* Divider */}
        <div className="ops-divider" />

        {/* Channel Status */}
        <div className="ops-module">
          <div className="ops-module-label">📡 CHANNELS</div>
          <div className="ops-channels">
            {socialStatus.map(ch => (
              <div key={ch.name} className="channel-status">
                <span
                  className="channel-dot"
                  style={{ backgroundColor: ch.color }}
                  title={ch.detail}
                />
                <span className="channel-name">{ch.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* System status */}
        <div className="ops-module">
          <div className="ops-module-label">🖥️ SYSTEM</div>
          <div className="ops-sys-items">
            <div className="sys-item">
              <span className="sys-dot active" />
              <span>OpenClaw</span>
            </div>
            <div className="sys-item">
              <span className="sys-dot active" />
              <span>Orgo VM</span>
            </div>
            <div className="sys-item">
              <span className="sys-dot active" />
              <span>GitHub</span>
            </div>
            <div className="sys-item">
              <span className="sys-dot blocked" />
              <span>Shopify</span>
            </div>
          </div>
        </div>

        <div className="ops-brand">
          <span>STUDEX OS v1.0</span>
          <span>// PHASE 1</span>
        </div>
      </div>
    </footer>
  );
}
