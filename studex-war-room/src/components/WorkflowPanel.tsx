import { useEffect, useRef, useState } from 'react';
import * as go from 'gojs';

type WfTab = 'BUILDER' | 'RUNS' | 'SETTINGS';

const nodeTypes = [
  { category: 'trigger', label: 'Telegram Trigger', color: '#ff6b35', icon: '✈️', desc: 'Updates: message' },
  { category: 'trigger', label: 'Schedule', color: '#ff6b35', icon: '⏰', desc: 'Cron trigger' },
  { category: 'trigger', label: 'Webhook', color: '#ff6b35', icon: '🪝', desc: 'HTTP endpoint' },
  { category: 'ai', label: 'AI Agent', color: '#4a9eff', icon: '🤖', desc: 'ToolsAgent' },
  { category: 'ai', label: 'Memory', color: '#4a9eff', icon: '🧠', desc: 'VectorStore' },
  { category: 'tool', label: 'Slack', color: '#cc88ff', icon: '💬', desc: 'post: message' },
  { category: 'tool', label: 'Email', color: '#cc88ff', icon: '📧', desc: 'send: email' },
  { category: 'tool', label: 'Sheets', color: '#44ffaa', icon: '📊', desc: 'read: orders' },
  { category: 'tool', label: 'Calendar', color: '#44ffaa', icon: '📅', desc: 'schedule event' },
  { category: 'tool', label: 'Research', color: '#44ffaa', icon: '🔍', desc: 'web: lookup' },
  { category: 'tool', label: 'Calculator', color: '#44ffaa', icon: '🔢', desc: 'compute' },
  { category: 'output', label: 'Respond', color: '#d4a017', icon: '💬', desc: 'sendMessage' },
];

const initialNodes = [
  { id: 'n1', label: 'Telegram Trigger', sublabel: 'Updates: message', type: 'trigger', x: 60, y: 220 },
  { id: 'n2', label: 'AI Agent', sublabel: 'ToolsAgent', type: 'ai', x: 320, y: 220 },
  { id: 'n3', label: 'Sheets', sublabel: 'read: orders', type: 'tool', x: 580, y: 100 },
  { id: 'n4', label: 'Slack', sublabel: 'post: summary', type: 'tool', x: 580, y: 220 },
  { id: 'n5', label: 'Research', sublabel: 'web: lookup', type: 'tool', x: 580, y: 340 },
  { id: 'n6', label: 'Respond', sublabel: 'sendMessage', type: 'output', x: 840, y: 220 },
];

function nodeColor(type: string) {
  switch (type) {
    case 'trigger': return '#ff6b35';
    case 'ai': return '#4a9eff';
    case 'tool': return '#cc88ff';
    case 'output': return '#d4a017';
    default: return '#7a8099';
  }
}

const recentRuns = [
  { id: 'run_8821', time: '2026-06-26 08:14', duration: '12s', tokens: '48.2K', status: 'success' },
  { id: 'run_8820', time: '2026-06-26 07:52', duration: '9s', tokens: '31.7K', status: 'success' },
  { id: 'run_8819', time: '2026-06-26 07:30', duration: '18s', tokens: '67.3K', status: 'error' },
  { id: 'run_8818', time: '2026-06-26 06:15', duration: '11s', tokens: '44.1K', status: 'success' },
  { id: 'run_8817', time: '2026-06-25 22:04', duration: '24s', tokens: '89.5K', status: 'success' },
];

export default function WorkflowPanel() {
  const diagramRef = useRef<go.Diagram | null>(null);
  const [activeTab, setActiveTab] = useState<WfTab>('BUILDER');
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [wfName, setWfName] = useState('Personal Assistant AI Agent 2.0');
  const [wfStatus, setWfStatus] = useState<'active' | 'inactive'>('inactive');
  const [initDone, setInitDone] = useState(false);

  useEffect(() => {
    if (activeTab !== 'BUILDER' || initDone) return;
    buildDiagram();
    setInitDone(true);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, initDone]);

  function buildDiagram() {
    const GO = go.GraphObject.make;

    const diagram = new go.Diagram('wf-canvas', {
      background: 'transparent',
      'grid.visible': true,
      'grid.gridCellSize': new go.Size(20, 20),
      'draggingTool.isGridSnapEnabled': true,
      'animationManager.isEnabled': true,
    });

    diagram.nodeTemplate = GO(go.Node, 'Auto', {
      locationSpot: go.Spot.Center,
      resizable: false,
      minSize: new go.Size(140, 68),
      cursor: 'pointer',
    },
      // Background shape
      GO(go.Shape, 'RoundedRectangle', {
        parameter1: 10,
        fill: GO(go.Brush, 'Linear', { 0: '#111827', 1: '#0d1422' }),
        stroke: '#d4a017',
        strokeWidth: 1,
      }),
      // Content panel
      GO(go.Panel, 'Vertical', { margin: 10 },
        GO(go.TextBlock, 'icon', {
          font: '16px sans-serif',
          textAlign: 'center', margin: new go.Margin(0, 0, 4, 0),
        }),
        GO(go.TextBlock, 'label', {
          font: 'bold 12px Inter, sans-serif',
          fill: '#e8e8f0', textAlign: 'center',
        }),
        GO(go.TextBlock, 'sublabel', {
          font: '10px Inter, sans-serif',
          fill: '#7a8099', textAlign: 'center',
        })
      ),
      // Input port
      GO(go.Shape, 'Rectangle', {
        width: 10, height: 10, fill: '#080c14', stroke: '#d4a017', strokeWidth: 1.5,
        alignment: go.Spot.Left, portId: 'IN', fromSpot: go.Spot.Left, toSpot: go.Spot.Right,
      }),
      // Output port
      GO(go.Shape, 'Rectangle', {
        width: 10, height: 10, fill: '#d4a017', stroke: '#080c14', strokeWidth: 1.5,
        alignment: go.Spot.Right, portId: 'OUT', fromSpot: go.Spot.Left, toSpot: go.Spot.Right,
      }),
    );

    // Link template
    diagram.linkTemplate = GO(go.Link, {
      routing: go.Link.Normal,
      curve: go.Link.None,
      layerName: 'Background',
    },
      GO(go.Shape, {
        stroke: 'rgba(212,160,23,0.4)',
        strokeWidth: 1.5,
      }),
      GO(go.Shape, {
        toArrow: 'Standard',
        fill: 'rgba(212,160,23,0.4)',
        stroke: 'transparent',
        scale: 0.8,
      }),
    );

    const model = new go.GraphLinksModel();
    diagram.model = model;

    // Add nodes
    initialNodes.forEach(n => {
      const color = nodeColor(n.type);
      const icon = nodeTypes.find(t => t.label === n.label)?.icon || '⬡';
      model.addNodeData({
        id: n.id, loc: `${n.x} ${n.y}`,
        label: n.label, sublabel: n.sublabel, icon,
        fill: color,
      });
    });

    // Add links
    const links = [
      { from: 'n1', fromPort: 'OUT', to: 'n2', toPort: 'IN' },
      { from: 'n2', fromPort: 'OUT', to: 'n3', toPort: 'IN' },
      { from: 'n2', fromPort: 'OUT', to: 'n4', toPort: 'IN' },
      { from: 'n2', fromPort: 'OUT', to: 'n5', toPort: 'IN' },
      { from: 'n4', fromPort: 'OUT', to: 'n6', toPort: 'IN' },
    ];
    links.forEach(l => model.addLinkData(l));

    diagram.addDiagramListener('ObjectSingleClicked', (e) => {
      const node = e.subject.part;
      if (node instanceof go.Node && node.data) {
        setSelectedNode(node.data.id as string);
      }
    });

    diagramRef.current = diagram;
  }

  function addNode(category: string) {
    const diagram = diagramRef.current;
    if (!diagram) return;
    const tmpl = nodeTypes.find(t => t.category === category);
    if (!tmpl) return;
    const newId = `n${Date.now()}`;
    diagram.model.addNodeData({
      id: newId, loc: `300 200`,
      label: tmpl.label, sublabel: tmpl.desc, icon: tmpl.icon,
      fill: tmpl.color,
    });
    setSelectedNode(newId);
  }

  return (
    <div className="workflow-panel">
      {/* Header */}
      <div className="wf-header">
        <div className="wf-title-area">
          <div className="wf-name-row">
            <span className="wf-icon">⚙️</span>
            <input
              className="wf-name-input"
              value={wfName}
              onChange={e => setWfName(e.target.value)}
            />
          </div>
          <div className="wf-meta">
            <span className="wf-badge">v2.0</span>
            <span className="wf-nodes">{initialNodes.length} nodes</span>
            <span className={`wf-status ${wfStatus}`}>
              <span className="status-dot" />
              {wfStatus === 'active' ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>
        <div className="wf-header-actions">
          <button className="wf-btn ghost">Share</button>
          <button className="wf-btn ghost">Saved</button>
          <button className="wf-btn primary">▶ Test workflow</button>
        </div>
      </div>

      {/* Sub Tabs */}
      <div className="wf-tabs">
        {(['BUILDER', 'RUNS', 'SETTINGS'] as WfTab[]).map(t => (
          <button key={t} className={`wf-tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
            {t}
          </button>
        ))}
      </div>

      {/* BUILDER */}
      {activeTab === 'BUILDER' && (
        <div className="wf-builder">
          {/* Left Palette */}
          <div className="wf-palette">
            {(['trigger', 'ai', 'tool', 'output'] as const).map(cat => (
              <div key={cat} className="palette-section">
                <div className="palette-title">{cat.toUpperCase()}</div>
                {nodeTypes.filter(n => n.category === cat).map(n => (
                  <button key={n.label} className="palette-node" onClick={() => addNode(n.category)}>
                    <span className="p-icon">{n.icon}</span>
                    <span className="p-label">{n.label}</span>
                  </button>
                ))}
              </div>
            ))}
          </div>

          {/* Canvas */}
          <div className="wf-canvas-wrap">
            <div id="wf-canvas" className="wf-canvas" />
            <div className="wf-canvas-hint">
              DRAG TO ORBIT · CLICK TO SELECT · DOUBLE-CLICK NODE TO DELETE
            </div>
          </div>

          {/* Properties */}
          <div className="wf-props">
            <div className="props-title">PROPERTIES</div>
            {selectedNode ? (
              <div className="props-form">
                <div className="prop-group">
                  <label>Node ID</label>
                  <div className="prop-value mono">{selectedNode}</div>
                </div>
                <div className="prop-group">
                  <label>Node Type</label>
                  <div className="prop-value">{initialNodes.find(n => n.id === selectedNode)?.label ?? '—'}</div>
                </div>
                <div className="prop-group">
                  <label>Model</label>
                  <select className="prop-select">
                    <option>claude-sonnet-4</option>
                    <option>gpt-4o</option>
                    <option>gemini-2.0-flash</option>
                  </select>
                </div>
                <div className="prop-group">
                  <label>Temperature</label>
                  <div className="range-row">
                    <input type="range" min="0" max="100" defaultValue={30} className="prop-range" />
                    <span className="range-val">0.3</span>
                  </div>
                </div>
                <div className="prop-group">
                  <label>Max Tokens</label>
                  <input type="number" defaultValue={4096} className="prop-input" />
                </div>
                <button className="prop-save">Save Changes</button>
              </div>
            ) : (
              <div className="props-empty">
                Select a node to<br />edit its properties
              </div>
            )}
          </div>
        </div>
      )}

      {/* RUNS */}
      {activeTab === 'RUNS' && (
        <div className="wf-runs">
          <table className="intel-table">
            <thead>
              <tr>
                <th>Run ID</th><th>Started</th><th>Duration</th><th>Tokens</th><th>Status</th><th></th>
              </tr>
            </thead>
            <tbody>
              {recentRuns.map(r => (
                <tr key={r.id}>
                  <td className="mono">{r.id}</td>
                  <td>{r.time}</td>
                  <td className="mono">{r.duration}</td>
                  <td className="mono">{r.tokens}</td>
                  <td><span className={`status-badge ${r.status}`}>{r.status}</span></td>
                  <td><button className="wf-btn ghost small">View</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* SETTINGS */}
      {activeTab === 'SETTINGS' && (
        <div className="wf-settings">
          <div className="settings-section">
            <div className="settings-title">WORKFLOW SETTINGS</div>
            <div className="prop-group">
              <label>Workflow Name</label>
              <input className="prop-input full" value={wfName} onChange={e => setWfName(e.target.value)} />
            </div>
            <div className="prop-group">
              <label>Status</label>
              <select className="prop-select full" value={wfStatus} onChange={e => setWfStatus(e.target.value as 'active' | 'inactive')}>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
            <div className="prop-group">
              <label>Trigger Type</label>
              <div className="trigger-type-card selected">
                <span>✈️</span>
                <div>
                  <div className="tt-name">Telegram Bot</div>
                  <div className="tt-desc">Listens for message updates</div>
                </div>
              </div>
            </div>
            <button className="prop-save">Save Settings</button>
          </div>
        </div>
      )}
    </div>
  );
}
