import { useState, useEffect } from 'react';
import { Agent, agents as staticAgents } from '../data/agents';

const agentStatusColors: Record<string, string> = {
  active: '#4aff88',
  idle: '#ffaa44',
  blocked: '#ff4444',
};

function getSASTTime(): string {
  const now = new Date();
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const saTime = new Date(utc + 2 * 60 * 60 * 1000);
  return saTime.toLocaleTimeString('en-ZA', { hour: '2-digit', minute: '2-digit', hour12: false });
}

function getSASTDate(): string {
  const now = new Date();
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const saTime = new Date(utc + 2 * 60 * 60 * 1000);
  return saTime.toLocaleDateString('en-ZA', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' });
}

// Agents who are "live" if lastSeen is within 2 hours of current SAST
function computeLiveAgents(agentsList: Agent[]): Record<string, boolean> {
  const now = new Date();
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const saNow = new Date(utc + 2 * 60 * 60 * 1000);
  const windowMs = 2 * 60 * 60 * 1000;
  const live: Record<string, boolean> = {};
  agentsList.forEach(a => {
    try {
      const match = a.lastSeen.match(/(\d{4})-(\d{2})-(\d{2}) (\d{1,2}):(\d{2}) (.+)/);
      if (match) {
        const [_, year, month, day, hour, minute, ampm] = match;
        let h = parseInt(hour);
        if (ampm.includes('PM')) h = h === 12 ? 12 : h + 12;
        if (ampm.includes('AM') && h === 12) h = 0;
        const lastSeenDate = new Date(parseInt(year), parseInt(month) - 1, parseInt(day), h, parseInt(minute));
        live[a.id] = (saNow.getTime() - lastSeenDate.getTime()) < windowMs;
      } else {
        live[a.id] = a.status === 'active';
      }
    } catch {
      live[a.id] = a.status === 'active';
    }
  });
  return live;
}

function LivePulse({ active }: { active: boolean }) {
  if (!active) return null;
  return (
    <span style={{
      display: 'inline-block',
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: '#4aff88',
      marginLeft: '6px',
      animation: 'pulse 1.5s ease-in-out infinite',
      boxShadow: '0 0 6px #4aff88',
    }} title="Live now" />
  );
}

export default function AgentNPCDock() {
  const [expanded, setExpanded] = useState<string | null>(null);
  const [now, setNow] = useState(getSASTTime());
  const [today] = useState(getSASTDate());
  const [liveMap] = useState<Record<string, boolean>>(() => computeLiveAgents(staticAgents));

  useEffect(() => {
    const interval = setInterval(() => setNow(getSASTTime()), 30000);
    return () => clearInterval(interval);
  }, []);

  const isLive = (agentId: string): boolean => {
    if (agentId === 'robusca') return true; // This Build Hour session
    return liveMap[agentId] ?? false;
  };

  const liveCount = staticAgents.filter(a => isLive(a.id)).length;

  return (
    <div className="agent-npc-dock">
      <div className="dock-header">
        <span>🤖 AGENT ROSTER</span>
        <div className="dock-counts">
          <span className="dc active">{staticAgents.filter(a => a.status === 'active').length} ACT</span>
          <span className="dc idle">{staticAgents.filter(a => a.status === 'idle').length} IDLE</span>
          <span className="dc blocked">{staticAgents.filter(a => a.status === 'blocked').length} BLOCKED</span>
          <span className="dc" style={{ color: '#4aff88' }}>⬤ {liveCount} LIVE</span>
        </div>
      </div>
      <div className="dock-clock">{now} SAST · {today}</div>

      <div className="dock-agents">
        {staticAgents.map(agent => (
          <div key={agent.id} className="npc-card">
            <div className="npc-top">
              <div className="npc-avatar">
                {agent.avatar}
                {isLive(agent.id) && (
                  <span style={{
                    position: 'absolute',
                    top: '-2px',
                    right: '-2px',
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    backgroundColor: '#4aff88',
                    border: '2px solid #1a1a1a',
                    animation: 'pulse 1.5s ease-in-out infinite',
                    boxShadow: '0 0 6px #4aff88',
                  }} />
                )}
              </div>
              <div className="npc-info">
                <div className="npc-name">
                  {agent.name}
                  <LivePulse active={isLive(agent.id)} />
                </div>
                <div className="npc-role">{agent.role}</div>
              </div>
              <div className="npc-status-wrap">
                <span
                  className="npc-status-dot"
                  style={{ backgroundColor: agentStatusColors[agent.status] }}
                  title={agent.statusReason || agent.status}
                />
                <span className="npc-status-label">{agent.status.toUpperCase()}</span>
              </div>
              <button
                className="npc-expand-btn"
                onClick={() => setExpanded(expanded === agent.id ? null : agent.id)}
              >
                {expanded === agent.id ? '▲' : '▼'}
              </button>
            </div>

            {expanded === agent.id && (
              <div className="npc-expanded">
                <div className="npc-specialties">
                  <div className="npc-section-label">SPECIALTIES</div>
                  <div className="npc-tags">
                    {agent.specialties.map(s => (
                      <span key={s} className="npc-tag">{s}</span>
                    ))}
                  </div>
                </div>
                <div className="npc-current-tasks">
                  <div className="npc-section-label">CURRENT TASKS</div>
                  {agent.currentTasks.map((task, i) => (
                    <div key={i} className="npc-task-item">▸ {task}</div>
                  ))}
                </div>
                <div className="npc-activity">
                  <div className="npc-section-label">LAST ACTIVITY</div>
                  <div className="npc-activity-text">{agent.recentActivity}</div>
                </div>
                {agent.statusReason && (
                  <div className="npc-block-reason">⚠️ {agent.statusReason}</div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(0.85); }
        }
        .npc-avatar { position: relative; display: inline-block; }
      `}</style>
    </div>
  );
}
