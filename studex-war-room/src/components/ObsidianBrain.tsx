import { useState, useEffect, useRef } from 'react';
import { markdownDocs, MarkdownDoc } from '../data/markdownDocs';

const STORAGE_KEY = 'studex_brain_v2';

interface ChatMessage {
  id: string;
  role: 'user' | 'brain';
  text: string;
  time: string;
}

function getTime() {
  return new Date().toLocaleTimeString('en-ZA', { hour: '2-digit', minute: '2-digit', hour12: false });
}

function generateId() {
  return Math.random().toString(36).slice(2);
}

function getStoredDocs(): Record<string, string> {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); }
  catch (_) { return {}; }
}

function storeDoc(id: string, content: string) {
  const all = getStoredDocs();
  all[id] = content;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
}

function getDocContent(doc: MarkdownDoc): string {
  const stored = getStoredDocs();
  return stored[doc.id] ?? doc.fullContent;
}

function renderMarkdown(text: string): string {
  return text
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
    .replace(/(<li>.*<\/li>(\n|$))+/g, m => `<ul>${m}</ul>`)
    .replace(/^---$/gm, '<hr/>')
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>');
}

const KB: Record<string, string> = {
  products: 'Studex Meat products: Wagyu Biltong Gold (R280–R520), Premium Wagyu Cuts (T-bone R680, Ribeye R850, Sirloin R520), Droëwors (R120–R220), Corporate Gift Boxes (R450–R1,200). All Halaal-certified MJC Halal Trust HT 4606.',
  agents: 'The team: Robusca (COO), Naledi (CMO — blocked Meta), Charlie (orchestrator), Amara (IG), EDDIE (ads), RALF (coordination), GIUM (analytics), Vera (ops), Zane (research), Nova (creative).',
  blockers: 'Top blockers: 1) Shopify token — no orders. 2) Meta token expired — Naledi cant post. 3) AgentMail DNS invalid. 4) Discord bot not in server. 5) WhatsApp needs Phone Number ID.',
  brand: 'Studex Meat — "Premium Halaal Meat. Proudly South African." Charcoal #1A1A1A + Gold #d4a017. Differentiators: Halaal + premium + Black-owned + tech-enabled.',
  orders: 'Order visibility BLOCKED — Shopify Admin API token not yet provided. Once Tumelo adds it to config, Hermes will have live order access in the War Room.',
  coffee: 'China coffee export window: July 20. studex-wildlife-coffee repo is empty — needs sourcing data, Chinese buyer contacts, pricing, logistics. Tumelo action required.',
  content: 'Naledi runs content via FeedHive/Blotato. Blocked until Meta token refreshes. Youth Day campaign assets ready — just needs token to go live.',
  warroom: 'Studex OS command center: React + Three.js globe, agent NPC dock, ContentHub, workflow editor, Intel panel. Built on OpenClaw orchestration. Hosted on Orgo VM.',
  global: 'Global phases: 1) China coffee Jul 20. 2) UAE Halaal Wagyu export Q3. 3) UK/EU biltong Q4. 4) Ankole tokenization 2027. Partnership targets: Alibaba, Waitrose, Emirates Flight Catering.',
};

function brainAnswer(q: string): string {
  const lower = q.toLowerCase();
  for (const [k, v] of Object.entries(KB)) {
    if (lower.includes(k)) return v;
  }
  const hit = markdownDocs.find(d =>
    d.fullContent.toLowerCase().includes(lower.split(' ')[0]) ||
    d.title.toLowerCase().includes(lower.split(' ')[0])
  );
  if (hit) {
    const lines = hit.fullContent.split('\n').filter(l => l.trim() && (l.startsWith('##') || l.startsWith('#')));
    return `From "${hit.title}":\n\n${lines.slice(0, 3).join('\n')}\n\nOpen this document in the panel to read the full entry.`;
  }
  return `I searched the Brain but don't have a specific entry for "${q}". Try asking about: products, agents, blockers, brand, orders, coffee, content, war room, or global markets. Click ✏️ Edit to add this knowledge to the wiki.`;
}

export default function ObsidianBrain() {
  const [selectedId, setSelectedId] = useState<string>(markdownDocs[0]?.id ?? '');
  const [contents, setContents] = useState<Record<string, string>>(() => {
    const stored = getStoredDocs();
    const init: Record<string, string> = {};
    markdownDocs.forEach(d => { init[d.id] = stored[d.id] ?? d.fullContent; });
    return init;
  });
  const [editMode, setEditMode] = useState(false);
  const [editText, setEditText] = useState('');
  const [chatOpen, setChatOpen] = useState(true);
  const [msgs, setMsgs] = useState<ChatMessage[]>([
    { id: '1', role: 'brain', text: 'Welcome to the Studex Brain. I know all wiki docs, agent statuses, products, and business context. Ask me anything — products, agents, global expansion, current blockers.', time: getTime() }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [thinking, setThinking] = useState(false);
  const [cat, setCat] = useState('All');
  const [search, setSearch] = useState('');
  const chatEnd = useRef<HTMLDivElement>(null);

  const cats = ['All', ...Array.from(new Set(markdownDocs.map(d => d.category)))];
  const selDoc = markdownDocs.find(d => d.id === selectedId);
  const selContent = selDoc ? (contents[selectedId] ?? selDoc.fullContent) : '';

  useEffect(() => { chatEnd.current?.scrollIntoView({ behavior: 'smooth' }); }, [msgs]);

  function startEdit() {
    setEditText(selContent);
    setEditMode(true);
  }

  function saveEdit() {
    const updated = { ...contents, [selectedId]: editText };
    setContents(updated);
    storeDoc(selectedId, editText);
    setEditMode(false);
  }

  function send() {
    const t = chatInput.trim();
    if (!t) return;
    const umsg: ChatMessage = { id: generateId(), role: 'user', text: t, time: getTime() };
    setMsgs(m => [...m, umsg]);
    setChatInput('');
    setThinking(true);
    setTimeout(() => {
      setMsgs(m => [...m, { id: generateId(), role: 'brain', text: brainAnswer(t), time: getTime() }]);
      setThinking(false);
    }, 900 + Math.random() * 800);
  }

  const filtered = markdownDocs.filter(d => {
    const c = cat === 'All' || d.category === cat;
    const s = !search || d.title.toLowerCase().includes(search.toLowerCase()) || d.fullContent.toLowerCase().includes(search.toLowerCase());
    return c && s;
  });

  return (
    <div className="brain-root">
      {/* Sidebar */}
      <div className="brain-sidebar">
        <div className="brain-sidebar-header">
          <span className="brain-logo">🧠</span>
          <div>
            <div className="brain-title">OBSIDIAN BRAIN</div>
            <div className="brain-subtitle">Studex Wiki // LLM-Powered</div>
          </div>
        </div>
        <div className="brain-search">
          <input className="brain-search-input" placeholder="Search wiki..." value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="brain-cats">
          {cats.map(c => <button key={c} className={`brain-cat-btn ${cat === c ? 'active' : ''}`} onClick={() => setCat(c)}>{c}</button>)}
        </div>
        <div className="brain-doc-list">
          {filtered.map(doc => (
            <div key={doc.id} className={`brain-doc-item ${selectedId === doc.id ? 'selected' : ''}`} onClick={() => { setSelectedId(doc.id); setEditMode(false); }}>
              <span className="brain-doc-icon">{doc.icon}</span>
              <div className="brain-doc-info">
                <div className="brain-doc-name">{doc.title}</div>
                <div className="brain-doc-cat">{doc.category}</div>
              </div>
            </div>
          ))}
        </div>
        <div className="brain-sidebar-footer">
          <div className="brain-stat"><span className="brain-stat-num">{markdownDocs.length}</span><span className="brain-stat-lbl">docs</span></div>
          <div className="brain-stat"><span className="brain-stat-num">{msgs.length}</span><span className="brain-stat-lbl">queries</span></div>
        </div>
      </div>

      {/* Content */}
      <div className="brain-content">
        {selDoc && (
          <>
            <div className="brain-content-header">
              <div className="brain-content-title">
                <span className="brain-content-icon">{selDoc.icon}</span>
                <div>
                  <div className="brain-content-name">{selDoc.title}</div>
                  <div className="brain-content-meta">{selDoc.category} · {selDoc.lastUpdated}</div>
                </div>
              </div>
              <div className="brain-content-actions">
                {editMode ? (
                  <><button className="brain-btn brain-btn-save" onClick={saveEdit}>💾 Save</button><button className="brain-btn brain-btn-cancel" onClick={() => setEditMode(false)}>✕ Cancel</button></>
                ) : (
                  <><button className="brain-btn brain-btn-edit" onClick={startEdit}>✏️ Edit</button><button className="brain-btn brain-btn-ask" onClick={() => setChatOpen(v => !v)}>{chatOpen ? '🔒 Hide Brain' : '🧠 Ask the Brain'}</button></>
                )}
              </div>
            </div>
            <div className="brain-content-body">
              {editMode ? (
                <textarea className="brain-editor" value={editText} onChange={e => setEditText(e.target.value)} autoFocus spellCheck={false} />
              ) : (
                <div className="brain-rendered" dangerouslySetInnerHTML={{ __html: renderMarkdown(selContent) }} />
              )}
            </div>
            {!editMode && <div className="brain-content-footer"><span className="brain-footer-hint">✏️ Edit to add knowledge · 🧠 Ask the Brain about anything in the wiki</span></div>}
          </>
        )}
      </div>

      {/* Chat */}
      {chatOpen && (
        <div className="brain-chat">
          <div className="brain-chat-header">
            <span className="brain-chat-title">🧠 Ask the Brain</span>
            <button className="brain-chat-close" onClick={() => setChatOpen(false)}>✕</button>
          </div>
          <div className="brain-chat-messages">
            {msgs.map(msg => (
              <div key={msg.id} className={`brain-msg brain-msg-${msg.role}`}>
                <div className="brain-msg-role">{msg.role === 'brain' ? '🧠 Brain' : 'You'}</div>
                <div className="brain-msg-text">{msg.text}</div>
                <div className="brain-msg-time">{msg.time}</div>
              </div>
            ))}
            {thinking && <div className="brain-msg brain-msg-brain"><div className="brain-msg-role">🧠 Brain</div><div className="brain-msg-text brain-thinking"><span className="thinking-dots"><span>.</span><span>.</span><span>.</span></span> Searching wiki...</div></div>}
            <div ref={chatEnd} />
          </div>
          <div className="brain-chat-input-area">
            <div className="brain-quick-qs">
              <div className="brain-quick-qs-label">Quick:</div>
              {['What are the blockers?', 'Agent team summary', 'Global expansion plan?'].map(q => (
                <button key={q} className="brain-quick-q" onClick={() => setChatInput(q)}>{q}</button>
              ))}
            </div>
            <div className="brain-chat-input-row">
              <textarea className="brain-chat-input" placeholder="Ask the brain..." value={chatInput} onChange={e => setChatInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }}} rows={2} />
              <button className="brain-send-btn" onClick={send} disabled={!chatInput.trim()}>↑</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
