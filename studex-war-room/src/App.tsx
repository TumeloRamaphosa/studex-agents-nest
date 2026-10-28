import { useState, useEffect } from 'react';
import { gsap } from 'gsap';
import NavigationHUD, { NavTab } from './components/NavigationHUD';
import WarRoomCanvas from './components/WarRoomCanvas';
import MarkdownPanel from './components/MarkdownPanel';
import NodeInfoPanel from './components/NodeInfoPanel';
import OpsDashboard from './components/OpsDashboard';
import IntelPanel from './components/IntelPanel';
import WorkflowPanel from './components/WorkflowPanel';
import WorkflowDesigner from './components/WorkflowDesigner';
import OpenWorldHUD from './components/OpenWorldHUD';
import AgentNPCDock from './components/AgentNPCDock';
import DeliveryKPIs from './components/DeliveryKPIs';
import CoffeePipeline from './components/CoffeePipeline';
import EmailWarmupDashboard from './components/EmailWarmupDashboard';
import BlotatoPipeline from './components/BlotatoPipeline';
import ContentHub from './components/ContentHub';
import ObsidianBrain from './components/ObsidianBrain';
import CommsPanel from './components/CommsPanel';
import CaviarPage from './components/CaviarPage';
import CIIEOutreachPanel from './components/CIIEOutreachPanel';
import CIIEBoothApplication from './components/CIIEBoothApplication';
import { GraphNode } from './data/graphData';

export default function App() {
  const [activeTab, setActiveTab] = useState<NavTab>('BRAIN');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [mdPanelOpen, setMdPanelOpen] = useState(false);

  // Taste-Skill entrance animation — staggered reveal on mount
  useEffect(() => {
    const tl = gsap.timeline({ defaults: { ease: 'power2.out' } });
    tl.from('.nav-hud',          { opacity: 0, y: -20, duration: 0.4 }, 0)
      .from('.sidebar-left',     { opacity: 0, x: -20, duration: 0.4 }, 0.15)
      .from('.app-main',         { opacity: 0, duration: 0.5 },          0.1)
      .from('.ops-dashboard',    { opacity: 0, y: 20, duration: 0.4 },   0.25);
  }, []);

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
              <button className="quick-link" onClick={() => setMdPanelOpen(true)}>DAILY LOG · JUL 30</button>
              <button className="quick-link" onClick={() => setMdPanelOpen(true)}>BRAND BIBLE</button>
              <button className="quick-link" onClick={() => setMdPanelOpen(true)}>CAMPAIGNS</button>
              <button className="quick-link blocked" onClick={() => setMdPanelOpen(true)}>CATALOGUE · INCOMPLETE</button>
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
          {activeTab === 'OUTREACH' && <CIIEOutreachPanel />}
          {activeTab === 'BOOTH' && <CIIEBoothApplication />}
          {activeTab === 'PIPELINE' && <BlotatoPipeline />}
          {activeTab === 'INTEL' && <IntelPanel />}
          {activeTab === 'WORKFLOW' && <WorkflowPanel />}
          {activeTab === 'WORKFLOWS' && <WorkflowDesigner />}
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
          {activeTab === 'WARMUP' && <EmailWarmupDashboard />}
          {activeTab === 'CAVIAR' && <CaviarPage />}
          {activeTab === 'COMMS' && <CommsPanel />}
        </div>

        <NodeInfoPanel selectedNode={selectedNode} onClose={() => setSelectedNode(null)} />
        <MarkdownPanel isOpen={mdPanelOpen} onToggle={() => setMdPanelOpen(false)} />
      </main>
    </div>
  );
}
