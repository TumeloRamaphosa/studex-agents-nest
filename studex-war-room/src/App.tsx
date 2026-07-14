import { useState } from 'react';
import NavigationHUD, { NavTab } from './components/NavigationHUD';
import WarRoomCanvas from './components/WarRoomCanvas';
import MarkdownPanel from './components/MarkdownPanel';
import NodeInfoPanel from './components/NodeInfoPanel';
import OpsDashboard from './components/OpsDashboard';
import IntelPanel from './components/IntelPanel';
import WorkflowPanel from './components/WorkflowPanel';
import OpenWorldHUD from './components/OpenWorldHUD';
import AgentNPCDock from './components/AgentNPCDock';
import DeliveryKPIs from './components/DeliveryKPIs';
import CoffeePipeline from './components/CoffeePipeline';
import BlotatoPipeline from './components/BlotatoPipeline';
import ContentHub from './components/ContentHub';
import ObsidianBrain from './components/ObsidianBrain';
import CommsPanel from './components/CommsPanel';
import { GraphNode } from './data/graphData';

export default function App() {
  const [activeTab, setActiveTab] = useState<NavTab>('BRAIN');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [mdPanelOpen, setMdPanelOpen] = useState(false);

  return (
    <div className="app-root">
      <NavigationHUD activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="app-main">
        <div className="sidebar-left">
          <div className="sidebar-section">
            <div className="sidebar-section-title">GRAPH LEGEND</div>
            <div className="legend-items">
              <div className="legend-item"><span className="legend-dot" style={{ background: '#4a9eff' }} />Agents</div>
              <div className="legend-item"><span className="legend-dot" style={{ background: '#d4a017' }} />StudEx OS Hub</div>
              <div className="legend-item"><span className="legend-dot" style={{ background: '#b06020' }} />Vault Sections</div>
              <div className="legend-item"><span className="legend-dot" style={{ background: '#ff4444' }} />Products</div>
              <div className="legend-item"><span className="legend-dot" style={{ background: '#ff8800' }} />Active Tasks</div>
              <div className="legend-item"><span className="legend-dot" style={{ background: '#3a3aff' }} />GitHub Repos</div>
              <div className="legend-item"><span className="legend-dot" style={{ background: '#cc88ff' }} />Campaigns</div>
            </div>
          </div>
          <div className="sidebar-section">
            <div className="sidebar-section-title">CONTROLS</div>
            <div className="controls-list">
              <div className="control-item">Drag to rotate sphere</div>
              <div className="control-item">Click node for details</div>
              <div className="control-item">Click agent card for activity</div>
            </div>
          </div>
          <div className="sidebar-section vault-quick">
            <div className="sidebar-section-title">QUICK ACCESS</div>
            <div className="quick-links">
              <button className="quick-link" onClick={() => setMdPanelOpen(true)}>Daily Log 2026-06-26</button>
              <button className="quick-link" onClick={() => setMdPanelOpen(true)}>Brand Bible</button>
              <button className="quick-link" onClick={() => setMdPanelOpen(true)}>Youth Day Campaign</button>
              <button className="quick-link blocked" onClick={() => setMdPanelOpen(true)}>Products (NEEDS DOCS)</button>
            </div>
          </div>
        </div>

        <div className="content-area">
          {activeTab === 'WAR ROOM' && (
            <div style={{ position: 'relative', width: '100%', height: '100%' }}>
              <WarRoomCanvas
                onNodeSelect={setSelectedNode}
                selectedNodeId={selectedNode?.id ?? null}
                hoveredNodeId={hoveredNodeId}
                onNodeHover={setHoveredNodeId}
              />
              <OpenWorldHUD />
            </div>
          )}
          {activeTab === 'BRAIN' && <ObsidianBrain />}
          {activeTab === 'COFFEE' && <CoffeePipeline />}
          {activeTab === 'PIPELINE' && <BlotatoPipeline />}
          {activeTab === 'INTEL' && <IntelPanel />}
          {activeTab === 'WORKFLOW' && <WorkflowPanel />}
          {activeTab === 'CONTENT' && <ContentHub />}
          {activeTab === 'AGENTS' && (
            <div style={{ display: 'flex', gap: '12px', width: '100%', height: '100%', overflow: 'hidden' }}>
              <div style={{ flex: 1, overflowY: 'auto' }}>
                <OpsDashboard />
              </div>
              <div style={{ width: '340px', overflowY: 'auto', flexShrink: 0 }}>
                <AgentNPCDock />
              </div>
            </div>
          )}
          {activeTab === 'TASKS' && <DeliveryKPIs />}
          {activeTab === 'COMMS' && <CommsPanel />}
        </div>

        <NodeInfoPanel selectedNode={selectedNode} onClose={() => setSelectedNode(null)} />
        <MarkdownPanel isOpen={mdPanelOpen} onToggle={() => setMdPanelOpen(false)} />
      </main>
    </div>
  );
}
