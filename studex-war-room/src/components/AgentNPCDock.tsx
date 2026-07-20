import { useState } from 'react';
import { Agent, agents } from '../data/agents';

const agentStatusColors: Record<string, string> = {
  active: '#4aff88',
  idle: '#ffaa44',
  blocked: '#ff4444',
};

export default function AgentNPCDock() {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="agent-npc-dock">
      <div className="dock-header">
        <span>🤖 AGENT ROSTER</span>
        <div className="dock-counts">
          <span className="dc active">{agents.filter(a => a.status === 'active').length} ACT</span>
          <span className="dc idle">{agents.filter(a => a.status === 'idle').length} IDLE</span>
          <span className="dc blocked">{agents.filter(a => a.status === 'blocked').length} BLOCKED</span>
        </div>
      </div>
      <div className="dock-agents">
        {agents.map(agent => (
          <div key={agent.id} className="npc-card">
            <div className="npc-top">
              <div className="npc-avatar">{agent.avatar}</div>
              <div className="npc-info">
                <div className="npc-name">{agent.name}</div>
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
    </div>
  );
}
