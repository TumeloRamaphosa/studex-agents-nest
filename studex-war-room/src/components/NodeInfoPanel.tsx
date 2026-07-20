import { GraphNode } from '../data/graphData';

interface Props {
  selectedNode: GraphNode | null;
  onClose: () => void;
}

const typeColors: Record<string, string> = {
  agent: '#4a9eff',
  vault: '#b06020',
  product: '#ff4444',
  task: '#ff8800',
  github: '#3a3aff',
  campaign: '#cc88ff',
};

const typeIcons: Record<string, string> = {
  agent: '🤖',
  vault: '📁',
  product: '🥩',
  task: '📋',
  github: '🔗',
  campaign: '🎯',
};

export default function NodeInfoPanel({ selectedNode, onClose }: Props) {
  if (!selectedNode) return null;
  const color = typeColors[selectedNode.type] || '#d4a017';
  const icon = typeIcons[selectedNode.type] || '📌';

  return (
    <div className="node-info-panel" style={{ '--node-color': color } as React.CSSProperties}>
      <div className="node-info-header">
        <div className="node-info-icon">{icon}</div>
        <div className="node-info-titles">
          <div className="node-info-label">{selectedNode.label}</div>
          <div className="node-info-type" style={{ color }}>{selectedNode.type.toUpperCase()}</div>
          {selectedNode.sublabel && (
            <div className="node-info-sub">{selectedNode.sublabel}</div>
          )}
        </div>
        <button className="node-close-btn" onClick={onClose}>✕</button>
      </div>
      <div className="node-info-body">
        <p className="node-info-desc">{selectedNode.info}</p>
        {selectedNode.info.includes('⚠️') && (
          <span className="info-tag warning">⚠️ ACTION REQUIRED</span>
        )}
      </div>
    </div>
  );
}
