import { useState } from 'react';
import { Agent } from '../data/agents';
import { GraphNode } from '../data/graphData';

interface Props {
  agents: Agent[];
  onAgentClick: (agent: Agent) => void;
  selectedAgentId: string | null;
  onNodeClick?: (node: GraphNode) => void;
}

export default function AgentPanel({ agents, onAgentClick, selectedAgentId }: Props) {
  const [collapsed, setCollapsed] = useState(false);

  const statusIcon = (agent: Agent) => {
    if (agent.status === 'active') return <span className="agent-status-dot active" />;
    if (agent.status === 'blocked') return <span className="agent-status-dot blocked" />;
    return <span className="agent-status-dot idle" />;
  };

  return (
    <aside className={`agent-panel ${collapsed ? 'collapsed' : ''}`}>
      <div className="panel-header">
        <div className="panel-title">
          <span className="panel-icon">🤖</span>
          <span>AGENT NPCs</span>
        </div>
        <button className="collapse-btn" onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? '◀' : '▶'}
        </button>
      </div>

      {!collapsed && (
        <>
          <div className="panel-subheader">STUDEX OS TEAM</div>
          <div className="agent-list">
            {agents.map(agent => (
              <div
                key={agent.id}
                className={`agent-card ${selectedAgentId === agent.id ? 'selected' : ''}`}
                onClick={() => onAgentClick(agent)}
                style={{ '--agent-color': agent.color } as React.CSSProperties}
              >
                <div className="agent-card-header">
                  <div className="agent-avatar">{agent.avatar}</div>
                  <div className="agent-info">
                    <div className="agent-name">{agent.name}</div>
                    <div className="agent-role">{agent.role}</div>
                  </div>
                  {statusIcon(agent)}
                </div>

                <div className="agent-specialties">
                  {agent.specialties.slice(0, 3).map(s => (
                    <span key={s} className="specialty-tag">{s}</span>
                  ))}
                </div>

                {agent.statusReason && (
                  <div className="agent-blocker">
                    <span className="blocker-icon">🚧</span>
                    <span>{agent.statusReason}</span>
                  </div>
                )}

                {selectedAgentId === agent.id && (
                  <div className="agent-details">
                    <div className="detail-section">
                      <div className="detail-label">CURRENT TASKS</div>
                      {agent.currentTasks.map(task => (
                        <div key={task} className="detail-task">
                          <span className="task-dot">›</span>
                          <span>{task}</span>
                        </div>
                      ))}
                    </div>
                    <div className="detail-section">
                      <div className="detail-label">RECENT ACTIVITY</div>
                      <p className="detail-activity">{agent.recentActivity}</p>
                    </div>
                    <div className="detail-section">
                      <div className="detail-label">LAST SEEN</div>
                      <p className="detail-time">{agent.lastSeen}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="panel-footer">
            <div className="footer-stat">
              <span className="stat-num" style={{ color: '#44cc77' }}>1</span>
              <span className="stat-label">Active</span>
            </div>
            <div className="footer-stat">
              <span className="stat-num" style={{ color: '#ff4444' }}>2</span>
              <span className="stat-label">Blocked</span>
            </div>
            <div className="footer-stat">
              <span className="stat-num" style={{ color: '#ffaa44' }}>1</span>
              <span className="stat-label">Idle</span>
            </div>
          </div>
        </>
      )}
    </aside>
  );
}
