import { useEffect, useRef, useState } from 'react';

interface QuestMarker {
  id: string;
  label: string;
  type: 'order' | 'email' | 'task' | 'alert' | 'npc';
  x: number; // -1 to 1 (screen coords)
  y: number;
  pulse: boolean;
  completed: boolean;
  agent?: string;
}

interface AgentNPC {
  id: string;
  name: string;
  role: string;
  emoji: string;
  status: 'online' | 'idle' | 'offline';
  x: number; // position on a unit circle
  y: number;
  unread: number;
}

interface LiveFeedItem {
  id: string;
  type: 'order' | 'email' | 'whatsapp' | 'discord';
  message: string;
  time: string;
  icon: string;
  read: boolean;
}

const questMarkers: QuestMarker[] = [
  { id: 'q1', label: 'New Order #1047', type: 'order', x: 0.3, y: -0.2, pulse: true, completed: false },
  { id: 'q2', label: 'Email: Bulk Quote Request', type: 'email', x: -0.5, y: 0.1, pulse: true, completed: false },
  { id: 'q3', label: 'WhatsApp: Delivery Query', type: 'alert', x: 0.6, y: 0.3, pulse: false, completed: false },
  { id: 'q4', label: 'Review Youth Day Post', type: 'task', x: -0.2, y: 0.4, pulse: false, completed: false },
  { id: 'q5', label: 'Low Stock: Perle Biltong', type: 'alert', x: 0.1, y: -0.4, pulse: true, completed: false },
];

const agentNPCs: AgentNPC[] = [
  { id: 'charlie', name: 'Charlie', role: 'Orchestrator', emoji: '🤖', status: 'online', x: 0.8, y: -0.5, unread: 3 },
  { id: 'naledi', name: 'Naledi', role: 'CMO — Content', emoji: '📣', status: 'online', x: -0.9, y: -0.3, unread: 0 },
  { id: 'cashclaw', name: 'CashClaw', role: 'Revenue Agent', emoji: '🐺', status: 'idle', x: -0.7, y: 0.5, unread: 0 },
  { id: 'dench', name: 'Dench CRM', role: 'Sales Pipeline', emoji: '💼', status: 'offline', x: 0.9, y: 0.4, unread: 12 },
  { id: 'robusca', name: 'Robusca', role: 'CEO — You', emoji: '👑', status: 'online', x: 0.0, y: -0.8, unread: 1 },
];

const liveFeedInit: LiveFeedItem[] = [
  { id: 'f1', type: 'order', message: 'Order #1047 placed — R389, Cape Town', time: '2m ago', icon: '📦', read: false },
  { id: 'f2', type: 'email', message: 'Bulk quote request — 50x Biltong Gift Boxes', time: '14m ago', icon: '📧', read: false },
  { id: 'f3', type: 'discord', message: '#ops: Morning standup summary posted', time: '1h ago', icon: '💬', read: true },
  { id: 'f4', type: 'whatsapp', message: 'Customer: "When is my order arriving?"', time: '2h ago', icon: '📱', read: true },
];

export default function OpenWorldHUD() {
  const [markers] = useState<QuestMarker[]>(questMarkers);
  const [npcs] = useState<AgentNPC[]>(agentNPCs);
  const [feed, setFeed] = useState<LiveFeedItem[]>(liveFeedInit);
  const [selectedNPC, setSelectedNPC] = useState<AgentNPC | null>(null);
  const [hudMode, setHudMode] = useState<'full' | 'minimal' | 'stealth'>('full');
  const [minimapOpen, setMinimapOpen] = useState(true);
  const [notifCount] = useState(feed.filter(f => !f.read).length);
  const [time, setTime] = useState('');

  useEffect(() => {
    const update = () => {
      const now = new Date();
      const utc = now.getTime() + now.getTimezoneOffset() * 60000;
      const saTime = new Date(utc + 2 * 60 * 60 * 1000);
      setTime(saTime.toLocaleTimeString('en-ZA', { hour: '2-digit', minute: '2-digit', hour12: false }));
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  function markRead(id: string) {
    setFeed(prev => prev.map(f => f.id === id ? { ...f, read: true } : f));
  }

  function getStatusColor(status: AgentNPC['status']) {
    switch (status) {
      case 'online': return '#44cc77';
      case 'idle': return '#d4a017';
      case 'offline': return '#555';
    }
  }

  return (
    <div className="openworld-hud">
      {/* Mode Toggle */}
      <div className="hud-mode-bar">
        <div className="hud-title-tag">STUDEX OS — OPEN WORLD</div>
        <div className="hud-controls">
          <button className={`hud-ctrl-btn ${hudMode === 'full' ? 'active' : ''}`} onClick={() => setHudMode('full')}>FULL</button>
          <button className={`hud-ctrl-btn ${hudMode === 'minimal' ? 'active' : ''}`} onClick={() => setHudMode('minimal')}>MINI</button>
          <button className={`hud-ctrl-btn ${hudMode === 'stealth' ? 'active' : ''}`} onClick={() => setHudMode('stealth')}>STEALTH</button>
          <button className="hud-ctrl-btn" onClick={() => setMinimapOpen(p => !p)}>
            {minimapOpen ? '⬛ HIDE MAP' : '🗺️ SHOW MAP'}
          </button>
        </div>
        <div className="hud-time">
          <span className="hud-clock">{time}</span>
          <span className="hud-zone">SAST</span>
        </div>
      </div>

      {/* Top HUD Bar */}
      {hudMode !== 'stealth' && (
        <div className="hud-top-bar">
          {/* Notifications */}
          <div className="hud-panel notif-panel">
            <div className="hud-panel-header">
              <span>📡 LIVE FEED</span>
              <span className="hud-badge">{notifCount} NEW</span>
            </div>
            <div className="hud-feed">
              {feed.map(item => (
                <div key={item.id} className={`feed-item ${item.read ? '' : 'unread'}`} onClick={() => markRead(item.id)}>
                  <span className="feed-icon">{item.icon}</span>
                  <div className="feed-content">
                    <div className="feed-msg">{item.message}</div>
                    <div className="feed-time">{item.time}</div>
                  </div>
                  {!item.read && <span className="feed-dot" />}
                </div>
              ))}
            </div>
          </div>

          {/* Quest Log */}
          <div className="hud-panel quest-panel">
            <div className="hud-panel-header">
              <span>⚡ QUEST LOG</span>
              <span className="hud-badge">{markers.filter(m => !m.completed).length} ACTIVE</span>
            </div>
            <div className="quest-list">
              {markers.map(m => (
                <div key={m.id} className={`quest-item ${m.completed ? 'done' : ''}`}>
                  <span className="quest-check">{m.completed ? '✅' : m.pulse ? '🔵' : '⚪'}</span>
                  <span className="quest-label">{m.label}</span>
                  <span className={`quest-type-badge ${m.type}`}>{m.type}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Stats */}
          <div className="hud-panel stats-panel">
            <div className="hud-panel-header">📊 OPS STATS</div>
            <div className="stats-grid">
              <div className="stat-item">
                <div className="stat-num">R12,847</div>
                <div className="stat-label">Today's Revenue</div>
              </div>
              <div className="stat-item">
                <div className="stat-num">34</div>
                <div className="stat-label">Orders MTD</div>
              </div>
              <div className="stat-item">
                <div className="stat-num" style={{ color: '#ff6b6b' }}>LOW</div>
                <div className="stat-label">Perle Stock</div>
              </div>
              <div className="stat-item">
                <div className="stat-num">7</div>
                <div className="stat-label">Open Tasks</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Minimap */}
      {minimapOpen && (
        <div className="hud-minimap">
          <div className="hud-panel-header">🗺️ RADAR</div>
          <div className="minimap-container">
            {/* Center dot = StudEx Meat Hub */}
            <div className="minimap-center">
              <div className="minimap-hub">
                <span>🏪</span>
              </div>
              {/* NPC dots */}
              {npcs.map(npc => {
                const angle = Math.atan2(npc.y, npc.x);
                const dist = Math.sqrt(npc.x * npc.x + npc.y * npc.y);
                const px = Math.cos(angle) * dist * 80;
                const py = Math.sin(angle) * dist * 80;
                return (
                  <div
                    key={npc.id}
                    className="minimap-dot"
                    style={{
                      left: `calc(50% + ${px}px)`,
                      top: `calc(50% + ${py}px)`,
                      background: getStatusColor(npc.status),
                      boxShadow: `0 0 6px ${getStatusColor(npc.status)}`,
                    }}
                    title={`${npc.name} — ${npc.status}`}
                  >
                    <span className="minimap-label">{npc.emoji}</span>
                  </div>
                );
              })}
              {/* Quest markers */}
              {markers.filter(m => !m.completed).map(m => (
                <div
                  key={m.id}
                  className={`minimap-quest ${m.pulse ? 'pulse' : ''}`}
                  style={{
                    left: `calc(50% + ${m.x * 85}px)`,
                    top: `calc(50% + ${m.y * 85}px)`,
                  }}
                >
                  !
                </div>
              ))}
              <div className="minimap-ring ring1" />
              <div className="minimap-ring ring2" />
              <div className="minimap-ring ring3" />
            </div>
          </div>
        </div>
      )}

      {/* NPC Agent Dock */}
      {hudMode !== 'stealth' && (
        <div className="hud-npc-dock">
          {npcs.map(npc => (
            <div
              key={npc.id}
              className={`npc-card ${npc.status} ${selectedNPC?.id === npc.id ? 'selected' : ''}`}
              onClick={() => setSelectedNPC(selectedNPC?.id === npc.id ? null : npc)}
            >
              <div className="npc-avatar">{npc.emoji}</div>
              <div className="npc-info">
                <div className="npc-name">{npc.name}</div>
                <div className="npc-role">{npc.role}</div>
              </div>
              <div className="npc-status-dot" style={{ background: getStatusColor(npc.status) }} />
              {npc.unread > 0 && <div className="npc-badge">{npc.unread}</div>}
            </div>
          ))}
        </div>
      )}

      {/* Selected NPC Detail */}
      {selectedNPC && (
        <div className="npc-detail-panel">
          <div className="npc-detail-header">
            <span className="npc-detail-avatar">{selectedNPC.emoji}</span>
            <div>
              <div className="npc-detail-name">{selectedNPC.name}</div>
              <div className="npc-detail-role">{selectedNPC.role}</div>
            </div>
            <div className="npc-detail-status" style={{ color: getStatusColor(selectedNPC.status) }}>
              ● {selectedNPC.status.toUpperCase()}
            </div>
            <button className="npc-close" onClick={() => setSelectedNPC(null)}>✕</button>
          </div>
          <div className="npc-detail-body">
            <div className="npc-stat-row">
              <span>Unread messages</span>
              <span className="gold">{selectedNPC.unread}</span>
            </div>
            <div className="npc-stat-row">
              <span>Today's tasks</span>
              <span>3 completed</span>
            </div>
            <div className="npc-stat-row">
              <span>Last active</span>
              <span>2 min ago</span>
            </div>
            <div className="npc-actions">
              <button className="npc-action-btn primary">💬 Message</button>
              <button className="npc-action-btn">📋 View Tasks</button>
              <button className="npc-action-btn">📊 View Stats</button>
            </div>
          </div>
        </div>
      )}

      {/* Quest Markers (3D canvas overlay) */}
      <div className="hud-quest-markers">
        {markers.filter(m => !m.completed).map(m => (
          <div
            key={m.id}
            className={`quest-marker ${m.type} ${m.pulse ? 'pulse' : ''}`}
            style={{ left: `${50 + m.x * 45}%`, top: `${50 + m.y * 40}%` }}
          >
            <div className="marker-icon">
              {m.type === 'order' ? '📦' : m.type === 'email' ? '📧' : m.type === 'alert' ? '⚠️' : '📋'}
            </div>
            <div className="marker-label">{m.label}</div>
          </div>
        ))}
      </div>

      {/* Bottom Status */}
      <div className="hud-bottom-bar">
        <div className="hud-status-item">
          <span className="hud-dot green" />
          <span>Robusca Online</span>
        </div>
        <div className="hud-status-item">
          <span className="hud-dot amber" />
          <span>n8n: Ready</span>
        </div>
        <div className="hud-status-item">
          <span className="hud-dot red" />
          <span>DenchClaw: Setup Required</span>
        </div>
        <div className="hud-coords">
          <span>STUDEX OS v2.0</span>
          <span>·</span>
          <span>Orgo VM</span>
          <span>·</span>
          <span>SAST</span>
        </div>
      </div>
    </div>
  );
}
