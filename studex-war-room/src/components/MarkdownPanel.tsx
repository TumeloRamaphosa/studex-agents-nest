import { useState } from 'react';
import { markdownDocs, MarkdownDoc } from '../data/markdownDocs';

interface Props {
  isOpen: boolean;
  onToggle: () => void;
}

export default function MarkdownPanel({ isOpen, onToggle }: Props) {
  const [selectedDoc, setSelectedDoc] = useState<MarkdownDoc>(markdownDocs[0]);

  const [leftOpen, setLeftOpen] = useState(false);

  function renderSimpleMarkdown(text: string): string {
    return text
      .replace(/^### (.+)$/gm, '<h3>$1</h3>')
      .replace(/^## (.+)$/gm, '<h2>$1</h2>')
      .replace(/^# (.+)$/gm, '<h1>$1</h1>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/^- (.+)$/gm, '<li>$1</li>')
      .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
      .replace(/(<li>.*<\/li>(\n|$))+/g, match => `<ul>${match}</ul>`)
      .replace(/^---$/gm, '<hr/>')
      .replace(/\n\n/g, '<br/><br/>')
      .replace(/\n/g, '<br/>');
  }

  return (
    <>
      {/* Left doc list */}
      <div className={`doc-list-panel ${leftOpen ? 'open' : ''}`}>
        <div className="doc-list-header">
          <span>📄 DOCUMENTS</span>
          <button onClick={() => setLeftOpen(false)}>◀</button>
        </div>
        <div className="doc-list">
          {markdownDocs.map(doc => (
            <div
              key={doc.id}
              className={`doc-item ${selectedDoc.id === doc.id ? 'selected' : ''}`}
              onClick={() => { setSelectedDoc(doc); }}
            >
              <span className="doc-icon">{doc.icon}</span>
              <div className="doc-item-info">
                <div className="doc-title">{doc.title}</div>
                <div className="doc-category">{doc.category}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main slide-in panel */}
      <div className={`markdown-panel ${isOpen ? 'open' : ''}`}>
        <div className="md-panel-header">
          <button
            className="md-list-toggle"
            onClick={() => setLeftOpen(!leftOpen)}
            title="Documents"
          >
            ☰
          </button>
          <div className="md-panel-title">
            <span>{selectedDoc.icon}</span>
            <span>{selectedDoc.title}</span>
          </div>
          <div className="md-panel-meta">
            <span>{selectedDoc.category}</span>
            <span>{selectedDoc.lastUpdated}</span>
          </div>
          <button className="md-close-btn" onClick={onToggle}>✕</button>
        </div>
        <div className="md-panel-body">
          <div
            className="md-content"
            dangerouslySetInnerHTML={{ __html: renderSimpleMarkdown(selectedDoc.fullContent) }}
          />
        </div>
      </div>

      {/* Floating toggle button */}
      {!isOpen && (
        <button className="md-fab" onClick={onToggle} title="Open Vault Documents">
          📄
        </button>
      )}
    </>
  );
}
