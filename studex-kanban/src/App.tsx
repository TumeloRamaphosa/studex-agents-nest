import { useState, useCallback, useRef, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import type { DropResult } from '@hello-pangea/dnd';
import type { Card, MemoryEntry, DeliveryColumnId } from './types';
import {
  COLUMNS, isValidTransition,
  DELIVERY_COMPANY_LABELS, DELIVERY_COMPANY_COLORS,
  AGENTS,
} from './types';
import { useBoardStore, makeMemoryEntry } from './store';

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatEta(iso: string): { label: string; color: string; dot: string } {
  const now = Date.now();
  const eta = new Date(iso).getTime();
  const diffMs = eta - now;
  const diffMin = Math.round(diffMs / 60_000);
  const timeStr = new Date(iso).toLocaleTimeString('en-ZA', {
    hour: '2-digit', minute: '2-digit', timeZone: 'Africa/Johannesburg',
  });
  if (diffMs < 0) {
    return { label: `${timeStr} SAST — OVERDUE`, color: '#ef4444', dot: '🔴' };
  }
  if (diffMin <= 60) {
    return { label: `${timeStr} SAST`, color: '#ef4444', dot: '🔴' };
  }
  if (diffMin <= 120) {
    return { label: `${timeStr} SAST`, color: '#f59e0b', dot: '🟡' };
  }
  return { label: `${timeStr} SAST`, color: '#22c55e', dot: '🟢' };
}

function formatTimestamp(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString('en-ZA', {
    hour: '2-digit', minute: '2-digit',
    timeZone: 'Africa/Johannesburg',
  });
}

function actorColor(actor: string): string {
  if (actor.startsWith('🤖')) return '#a78bfa';
  if (actor.startsWith('👤')) return '#34d399';
  return '#9ca3af';
}

function actorInitial(actor: string): string {
  const parts = actor.replace('🤖', '').replace('👤', '').trim().split(' ');
  return parts[0]?.[0] ?? '?';
}

// ─── Toast ───────────────────────────────────────────────────────────────────

function Toast({ message, onDone }: { message: string; onDone: () => void }) {
  useEffect(() => {
    const t = setTimeout(onDone, 3000);
    return () => clearTimeout(t);
  }, [onDone]);
  return (
    <div style={{
      position: 'fixed', bottom: '24px', left: '50%', transform: 'translateX(-50%)',
      background: '#7f1d1d', border: '1px solid #ef4444', borderRadius: '8px',
      color: '#fca5a5', padding: '10px 20px', fontSize: '13px', fontFamily: 'monospace',
      fontWeight: 700, zIndex: 9999, boxShadow: '0 4px 20px rgba(239,68,68,0.4)',
      letterSpacing: '0.5px', whiteSpace: 'nowrap',
    }}>
      🚫 {message}
    </div>
  );
}

// ─── ETA Badge ───────────────────────────────────────────────────────────────

function EtaBadge({ eta }: { eta?: string }) {
  if (!eta) return null;
  const { label, color, dot } = formatEta(eta);
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: '4px',
      fontSize: '10px', fontWeight: 700, color, fontFamily: 'monospace',
      background: `${color}18`, border: `1px solid ${color}44`,
      borderRadius: '4px', padding: '2px 7px', letterSpacing: '0.3px',
    }}>
      {dot} ETA: {label}
    </span>
  );
}

// ─── Memory Log ──────────────────────────────────────────────────────────────

function MemoryLog({ entries }: { entries?: MemoryEntry[] }) {
  const [expanded, setExpanded] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const visible = entries && entries.length > 0;
  if (!visible) return null;
  const shown = expanded ? entries : entries.slice(0, 3);
  const hasMore = entries.length > 3;

  useEffect(() => {
    if (expanded && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [expanded]);

  return (
    <div style={{
      marginTop: '8px', borderTop: '1px solid #2a1a1a', paddingTop: '6px',
    }}>
      <button
        onClick={() => setExpanded(x => !x)}
        style={{
          background: 'none', border: 'none', cursor: 'pointer', width: '100%',
          textAlign: 'left', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '0', marginBottom: expanded ? '5px' : '0',
        }}
      >
        <span style={{ fontSize: '9px', fontWeight: 700, color: '#6b4c4c', fontFamily: 'monospace', letterSpacing: '1px' }}>
          🧠 MEMORY LOG {entries.length > 0 && <span style={{ color: '#8B1A1A' }}>({entries.length})</span>}
        </span>
        <span style={{ fontSize: '9px', color: '#6b4c4c', fontFamily: 'monospace' }}>
          {expanded ? '▲ collapse' : '▼ expand'}
        </span>
      </button>

      <div
        ref={containerRef}
        style={{
          maxHeight: expanded ? '160px' : '80px',
          overflow: 'hidden',
          transition: 'max-height 0.25s ease',
          display: 'flex', flexDirection: 'column', gap: '3px',
        }}
      >
        {shown.map((e, i) => (
          <div key={e.id} style={{ display: 'flex', gap: '5px', alignItems: 'flex-start' }}>
            {i === 0 && !expanded && (
              <span style={{ fontSize: '8px', color: '#8B1A1A', fontWeight: 800, fontFamily: 'monospace', lineHeight: '1.4', minWidth: '28px' }}>NEW</span>
            )}
            {i !== 0 || expanded ? (
              <span style={{ fontSize: '8px', color: '#4a3030', fontFamily: 'monospace', lineHeight: '1.4', minWidth: '28px' }}>
                {formatTimestamp(e.timestamp)}
              </span>
            ) : null}
            <span style={{ fontSize: '9px', fontWeight: 700, color: actorColor(e.actor), fontFamily: 'monospace', lineHeight: '1.4', whiteSpace: 'nowrap', minWidth: '52px' }}>
              {actorInitial(e.actor)}
            </span>
            <span style={{ fontSize: '9px', color: '#7a5555', lineHeight: '1.4', fontFamily: 'monospace' }}>
              {e.action}
            </span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {hasMore && !expanded && (
        <button
          onClick={() => setExpanded(true)}
          style={{
            background: 'none', border: 'none', cursor: 'pointer',
            fontSize: '9px', color: '#8B1A1A', fontFamily: 'monospace', fontWeight: 700,
            padding: '2px 0', marginTop: '2px',
          }}
        >
          + {entries.length - 3} more entries...
        </button>
      )}
    </div>
  );
}

// ─── Delivery Company Badge ──────────────────────────────────────────────────

function CompanyBadge({ company }: { company?: string | null }) {
  if (!company) return null;
  const color = DELIVERY_COMPANY_COLORS[company as keyof typeof DELIVERY_COMPANY_COLORS] ?? '#374151';
  const label = DELIVERY_COMPANY_LABELS[company as keyof typeof DELIVERY_COMPANY_LABELS] ?? company;
  return (
    <span style={{
      background: color, color: '#fff', fontSize: '9px', fontWeight: 700,
      padding: '1px 6px', borderRadius: '3px', fontFamily: 'monospace', letterSpacing: '0.3px',
    }}>
      {label}
    </span>
  );
}

// ─── Team Access Indicator ───────────────────────────────────────────────────

function TeamIndicator({ actor, timestamp }: { actor?: string; timestamp?: string }) {
  if (!actor) return null;
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '4px',
      fontSize: '9px', color: actorColor(actor), fontFamily: 'monospace',
      marginTop: '4px',
    }}>
      <span style={{
        width: '14px', height: '14px', borderRadius: '50%', background: `${actorColor(actor)}22`,
        border: `1px solid ${actorColor(actor)}55`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '7px', fontWeight: 800, color: actorColor(actor),
      }}>
        {actorInitial(actor)}
      </span>
      <span style={{ color: '#5a3e3e' }}>{actor}</span>
      {timestamp && (
        <span style={{ color: '#3d2828', marginLeft: '2px' }}>
          · {formatTimestamp(timestamp)}
        </span>
      )}
    </div>
  );
}

// ─── Kanban Card ─────────────────────────────────────────────────────────────

function KanbanCard({ card, index, onEdit, onDelete }: {
  card: Card;
  index: number;
  onEdit: (card: Card) => void;
  onDelete: (id: string) => void;
}) {
  const isCancelled = card.columnId === 'cancelled';

  return (
    <Draggable draggableId={card.id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          style={{
            ...provided.draggableProps.style,
            background: snapshot.isDragging
              ? '#2d1a1a'
              : isCancelled ? '#1a0f0f' : '#1c1c1c',
            border: `1px solid ${snapshot.isDragging ? '#8B1A1A' : isCancelled ? '#3d1515' : '#2a1a1a'}`,
            borderLeft: `3px solid ${isCancelled ? '#ef4444' : '#8B1A1A'}`,
            borderRadius: '6px',
            padding: '10px 12px',
            marginBottom: '8px',
            opacity: snapshot.isDragging ? 0.95 : isCancelled ? 0.6 : 1,
            boxShadow: snapshot.isDragging
              ? '0 0 20px rgba(139,26,26,0.5), 0 8px 24px rgba(0,0,0,0.8)'
              : '0 2px 8px rgba(0,0,0,0.4)',
            transition: 'box-shadow 0.15s, opacity 0.15s',
            cursor: snapshot.isDragging ? 'grabbing' : 'grab',
          }}
        >
          {/* ETA + Company row */}
          {(card.eta || card.deliveryCompany) && (
            <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap', marginBottom: '6px', alignItems: 'center' }}>
              <EtaBadge eta={card.eta} />
              <CompanyBadge company={card.deliveryCompany} />
            </div>
          )}

          {/* Title */}
          <div style={{ fontSize: '12px', fontWeight: 600, color: isCancelled ? '#6b4c4c' : '#f9fafb', lineHeight: 1.3, marginBottom: '4px' }}>
            {card.title}
          </div>

          {/* Description */}
          {card.description && (
            <p style={{ fontSize: '10px', color: isCancelled ? '#3d2828' : '#7a5555', margin: '0 0 6px 0', lineHeight: 1.4 }}>
              {card.description}
            </p>
          )}

          {/* Order items */}
          {card.orderItems && card.orderItems.length > 0 && (
            <div style={{ marginBottom: '6px' }}>
              <div style={{ fontSize: '8px', fontWeight: 700, color: '#5a3e3e', fontFamily: 'monospace', letterSpacing: '1px', marginBottom: '2px' }}>
                ORDER ITEMS
              </div>
              {card.orderItems.slice(0, 2).map((item, i) => (
                <div key={i} style={{ fontSize: '9px', color: '#7a5555', fontFamily: 'monospace' }}>
                  · {item}
                </div>
              ))}
              {card.orderItems.length > 2 && (
                <div style={{ fontSize: '9px', color: '#8B1A1A', fontFamily: 'monospace' }}>
                  +{card.orderItems.length - 2} more...
                </div>
              )}
            </div>
          )}

          {/* Address */}
          {card.customerAddress && (
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '4px', marginBottom: '6px' }}>
              <span style={{ fontSize: '9px', color: '#5a3e3e', flexShrink: 0 }}>📍</span>
              <span style={{ fontSize: '9px', color: '#6b4c4c', lineHeight: 1.4 }}>{card.customerAddress}</span>
            </div>
          )}

          {/* Driver */}
          {(card.driverName || card.driverPhone) && (
            <div style={{ display: 'flex', gap: '6px', alignItems: 'center', marginBottom: '6px', flexWrap: 'wrap' }}>
              {card.driverName && (
                <span style={{ fontSize: '9px', color: '#8B6914', fontFamily: 'monospace' }}>
                  👤 {card.driverName}
                </span>
              )}
              {card.driverPhone && (
                <a
                  href={`tel:${card.driverPhone}`}
                  onClick={e => e.stopPropagation()}
                  style={{ fontSize: '9px', color: '#6d28d9', fontFamily: 'monospace', textDecoration: 'none' }}
                >
                  📞 {card.driverPhone}
                </a>
              )}
            </div>
          )}

          {/* Memory log */}
          <MemoryLog entries={card.memoryLog} />

          {/* Footer */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px', paddingTop: '6px', borderTop: '1px solid #1a0a0a' }}>
            <TeamIndicator actor={card.lastUpdatedBy} timestamp={card.lastUpdatedAt} />
            <div style={{ display: 'flex', gap: '4px' }}>
              <button
                onClick={() => onEdit(card)}
                style={iconBtn('#2a1a1a', '#7a5555')}
                title="Edit"
              >
                <EditIcon />
              </button>
              <button
                onClick={() => onDelete(card.id)}
                style={iconBtn('#3d1010', '#ef4444')}
                title="Delete"
              >
                <TrashIcon />
              </button>
            </div>
          </div>
        </div>
      )}
    </Draggable>
  );
}

function iconBtn(bg: string, color: string): React.CSSProperties {
  return {
    background: bg, border: 'none', color, borderRadius: '4px',
    padding: '3px 4px', cursor: 'pointer', display: 'flex', alignItems: 'center',
  };
}

// ─── Card Modal ───────────────────────────────────────────────────────────────

interface CardModalProps {
  card?: Card;
  defaultColumnId?: DeliveryColumnId;
  onSave: (data: Omit<Card, 'id' | 'createdAt'>) => void;
  onClose: () => void;
}

function CardModal({ card, defaultColumnId = 'order-intake', onSave, onClose }: CardModalProps) {
  const [title, setTitle]               = useState(card?.title ?? '');
  const [description, setDescription]  = useState(card?.description ?? '');
  const [priority, setPriority]         = useState(card?.priority ?? 'MED');
  const [deliveryCompany, setDeliveryCompany] = useState<Card['deliveryCompany']>(card?.deliveryCompany ?? null);
  const [driverName, setDriverName]     = useState(card?.driverName ?? '');
  const [driverPhone, setDriverPhone]   = useState(card?.driverPhone ?? '');
  const [eta, setEta]                   = useState(card?.eta ? card.eta.slice(0, 16) : '');
  const [customerAddress, setCustomerAddress] = useState(card?.customerAddress ?? '');
  const [orderItemsRaw, setOrderItemsRaw] = useState(card?.orderItems?.join('\n') ?? '');
  const [assignedAgent, setAssignedAgent] = useState(card?.assignedAgent ?? AGENTS[0]);
  const [lastUpdatedBy, setLastUpdatedBy] = useState(card?.lastUpdatedBy ?? AGENTS[0]);
  const [columnId, setColumnId]         = useState<DeliveryColumnId>(card?.columnId as DeliveryColumnId ?? defaultColumnId);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    const orderItems = orderItemsRaw
      .split('\n')
      .map(s => s.trim())
      .filter(Boolean);
    const etaIso = eta ? new Date(eta).toISOString() : undefined;
    const existingLog = card?.memoryLog ?? [];
    const newEntry = makeMemoryEntry(lastUpdatedBy, card ? 'Card updated.' : 'Card created.');
    onSave({
      title: title.trim(),
      description: description.trim(),
      priority,
      dueDate: '',
      assignedAgent,
      category: 'DELIVERY',
      columnId,
      deliveryCompany: deliveryCompany || null,
      driverName,
      driverPhone,
      eta: etaIso,
      customerAddress,
      orderItems,
      whatsappGroupThread: '',
      memoryLog: [newEntry, ...existingLog].slice(0, 50),
      lastUpdatedBy,
      lastUpdatedAt: new Date().toISOString(),
    });
  }

  return (
    <div style={overlayStyle} onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div style={modalStyle}>
        <div style={modalHeaderStyle}>
          <span style={{ color: '#f9fafb', fontSize: '13px', fontWeight: 700, fontFamily: 'monospace', letterSpacing: '0.5px' }}>
            {card ? '✏️ EDIT DELIVERY' : '➕ NEW DELIVERY'}
          </span>
          <button onClick={onClose} style={{ ...iconBtn('transparent', '#6b7280'), padding: '4px' }}>
            <XIcon />
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '80vh', overflowY: 'auto', paddingRight: '4px' }}>

          {/* Title */}
          <label style={labelStyle}>
            ORDER TITLE *
            <input value={title} onChange={e => setTitle(e.target.value)} required
              placeholder="#STX-XXXX — Customer Name"
              style={inputStyle} />
          </label>

          {/* Description */}
          <label style={labelStyle}>
            NOTES
            <textarea value={description} onChange={e => setDescription(e.target.value)} rows={2}
              placeholder="Delivery notes, special requests..."
              style={{ ...inputStyle, resize: 'vertical' }} />
          </label>

          {/* Grid row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <label style={labelStyle}>
              DELIVERY COMPANY
              <select value={deliveryCompany ?? ''} onChange={e => setDeliveryCompany((e.target.value || null) as Card['deliveryCompany'])} style={inputStyle}>
                <option value="">— none —</option>
                <option value="dinkoko">🐂 Dinkoko (Derrick)</option>
                <option value="mycourier">📦 My Courier (Willy)</option>
              </select>
            </label>
            <label style={labelStyle}>
              PRIORITY
              <select value={priority} onChange={e => setPriority(e.target.value as Card['priority'])} style={inputStyle}>
                <option value="HIGH">🔴 HIGH</option>
                <option value="MED">🟡 MED</option>
                <option value="LOW">🟢 LOW</option>
              </select>
            </label>
            <label style={labelStyle}>
              DRIVER NAME
              <input value={driverName} onChange={e => setDriverName(e.target.value)}
                placeholder="Derrick Selepe" style={inputStyle} />
            </label>
            <label style={labelStyle}>
              DRIVER PHONE
              <input value={driverPhone} onChange={e => setDriverPhone(e.target.value)}
                placeholder="+27 67 681 3076" style={inputStyle} />
            </label>
          </div>

          {/* ETA */}
          <label style={labelStyle}>
            ETA (delivery time)
            <input type="datetime-local" value={eta} onChange={e => setEta(e.target.value)}
              style={inputStyle} />
          </label>

          {/* Customer address */}
          <label style={labelStyle}>
            CUSTOMER ADDRESS
            <input value={customerAddress} onChange={e => setCustomerAddress(e.target.value)}
              placeholder="Full delivery address" style={inputStyle} />
          </label>

          {/* Order items */}
          <label style={labelStyle}>
            ORDER ITEMS (one per line)
            <textarea value={orderItemsRaw} onChange={e => setOrderItemsRaw(e.target.value)}
              rows={4} placeholder={"2x T-Bone Steak (500g)\n1x Beef Wors (1kg)"}
              style={{ ...inputStyle, resize: 'vertical' }} />
          </label>

          {/* Assignee / updater */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <label style={labelStyle}>
              ASSIGNED AGENT
              <select value={assignedAgent} onChange={e => setAssignedAgent(e.target.value)} style={inputStyle}>
                {AGENTS.map(a => <option key={a} value={a}>{a}</option>)}
              </select>
            </label>
            <label style={labelStyle}>
              UPDATED BY
              <select value={lastUpdatedBy} onChange={e => setLastUpdatedBy(e.target.value)} style={inputStyle}>
                {AGENTS.map(a => <option key={a} value={a}>{a}</option>)}
              </select>
            </label>
          </div>

          {/* Column */}
          <label style={labelStyle}>
            STAGE
            <select value={columnId} onChange={e => setColumnId(e.target.value as DeliveryColumnId)} style={inputStyle}>
              {COLUMNS.map(c => <option key={c.id} value={c.id}>{c.emoji} {c.title}</option>)}
            </select>
          </label>

          <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
            <button type="submit" style={{ ...submitBtn, flex: 1 }}>
              {card ? '💾 SAVE CHANGES' : '➕ CREATE DELIVERY'}
            </button>
            <button type="button" onClick={onClose} style={{ ...cancelBtn, flex: 1 }}>
              CANCEL
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Styles ──────────────────────────────────────────────────────────────────

const overlayStyle: React.CSSProperties = {
  position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)',
  backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center',
  justifyContent: 'center', zIndex: 1000, padding: '16px',
};

const modalStyle: React.CSSProperties = {
  background: '#131010',
  border: '1px solid #3d1515',
  borderRadius: '10px',
  padding: '20px',
  width: '100%',
  maxWidth: '580px',
  boxShadow: '0 20px 60px rgba(139,26,26,0.2)',
};

const modalHeaderStyle: React.CSSProperties = {
  display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px',
};

const labelStyle: React.CSSProperties = {
  display: 'flex', flexDirection: 'column', gap: '4px',
  fontSize: '9px', fontWeight: 700, color: '#7a5555', letterSpacing: '1px', fontFamily: 'monospace',
};

const inputStyle: React.CSSProperties = {
  background: '#0a0a0a', border: '1px solid #2a1a1a', borderRadius: '5px',
  color: '#f9fafb', padding: '8px 10px', fontSize: '12px', fontFamily: 'inherit', outline: 'none',
};

const submitBtn: React.CSSProperties = {
  background: '#7f1d1d', border: '1px solid #8B1A1A', borderRadius: '5px',
  color: '#fca5a5', padding: '10px 16px', fontSize: '11px', fontWeight: 700,
  cursor: 'pointer', fontFamily: 'monospace', letterSpacing: '0.5px',
};

const cancelBtn: React.CSSProperties = {
  background: 'transparent', border: '1px solid #2a1a1a', borderRadius: '5px',
  color: '#6b7280', padding: '10px 16px', fontSize: '11px', fontWeight: 700,
  cursor: 'pointer', fontFamily: 'monospace', letterSpacing: '0.5px',
};

// ─── Icons ───────────────────────────────────────────────────────────────────

function PlusIcon() {
  return <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>;
}
function TrashIcon() {
  return <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>;
}
function EditIcon() {
  return <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>;
}
function XIcon() {
  return <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>;
}
function TruckIcon() {
  return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#8B1A1A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>;
}

// ─── Main App ────────────────────────────────────────────────────────────────


// ─── Main App (patch — append to App.tsx) ────────────────────────────────────

export default function App() {
  const { cards, addCard, updateCard, deleteCard, moveCard, isLoaded } = useBoardStore();
  const [showModal, setShowModal]     = useState(false);
  const [editingCard, setEditingCard] = useState<Card | null>(null);
  const [defaultCol, setDefaultCol]   = useState<DeliveryColumnId>('order-intake');
  const [toast, setToast]             = useState<string | null>(null);

  const openAdd  = (colId: DeliveryColumnId = 'order-intake') => { setEditingCard(null); setDefaultCol(colId); setShowModal(true); };
  const openEdit = (card: Card) => { setEditingCard(card); setShowModal(true); };

  const handleSave = (data: Omit<Card, 'id' | 'createdAt'>) => {
    if (editingCard) {
      updateCard(editingCard.id, data);
    } else {
      addCard({ ...data, columnId: defaultCol });
    }
    setShowModal(false);
    setEditingCard(null);
  };

  const handleDragEnd = useCallback((result: DropResult) => {
    const { source, destination, draggableId } = result;
    if (!destination) return;
    if (source.droppableId === destination.droppableId && source.index === destination.index) return;
    const from = source.droppableId as DeliveryColumnId;
    const to   = destination.droppableId as DeliveryColumnId;
    if (!isValidTransition(from, to)) {
      setToast(`Invalid transition: ${COLUMNS.find(c => c.id === from)?.emoji ?? from} → ${COLUMNS.find(c => c.id === to)?.emoji ?? to} not allowed`);
      return;
    }
    moveCard(draggableId, to);
  }, [moveCard]);

  const total     = cards.length;
  const highCount = cards.filter(c => c.priority === 'HIGH').length;
  const delivered  = cards.filter(c => c.columnId === 'delivered').length;
  const cancelled  = cards.filter(c => c.columnId === 'cancelled').length;

  if (!isLoaded) {
    return (
      <div style={{ background: '#0a0a0a', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <span style={{ color: '#6b4c4c', fontFamily: 'monospace', fontSize: '14px' }}>LOADING DELIVERY BOARD...</span>
      </div>
    );
  }

  return (
    <div style={{ background: 'linear-gradient(135deg, #0a0a0a 0%, #1a0a0a 100%)', minHeight: '100vh', color: '#f9fafb', fontFamily: "'Inter', -apple-system, sans-serif" }}>

      {/* ── Header ── */}
      <div style={{
        background: 'linear-gradient(90deg, #0d0808 0%, #1a0808 100%)',
        borderBottom: '1px solid #2a1010',
        padding: '12px 24px',
        position: 'sticky', top: 0, zIndex: 100,
        backdropFilter: 'blur(8px)',
      }}>
        <div style={{ maxWidth: '1600px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>

          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <TruckIcon />
            <div>
              <div style={{ fontSize: '17px', fontWeight: 900, color: '#f9fafb', letterSpacing: '-0.5px', lineHeight: 1 }}>
                STUDEx MEAT <span style={{ color: '#8B1A1A' }}>DELIVERY</span> BOARD
              </div>
              <div style={{ fontSize: '9px', color: '#6b4c4c', fontFamily: 'monospace', letterSpacing: '2px', marginTop: '2px' }}>
                KANBAN · SAST · {new Date().toLocaleDateString('en-ZA', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' })}
              </div>
            </div>
          </div>

          {/* Stats */}
          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
            {([
              { label: 'TOTAL',     value: total,     color: '#9ca3af' },
              { label: 'HIGH',      value: highCount, color: '#fca5a5' },
              { label: 'DELIVERED', value: delivered, color: '#86efac' },
              { label: 'CANCELLED', value: cancelled, color: '#6b4c4c' },
            ] as { label: string; value: number; color: string }[]).map(s => (
              <div key={s.label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '22px', fontWeight: 900, color: s.color, fontFamily: 'monospace', lineHeight: 1 }}>{s.value}</div>
                <div style={{ fontSize: '8px', color: '#6b4c4c', fontFamily: 'monospace', letterSpacing: '1px', marginTop: '3px' }}>{s.label}</div>
              </div>
            ))}
          </div>

          {/* Controls */}
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button
              onClick={() => openAdd()}
              style={{ background: '#7f1d1d', border: '1px solid #8B1A1A', borderRadius: '5px', color: '#fca5a5', padding: '8px 14px', fontSize: '11px', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px', fontFamily: 'monospace', letterSpacing: '0.5px' }}
            >
              <PlusIcon /> NEW DELIVERY
            </button>
          </div>
        </div>
      </div>

      {/* ── Delivery Partners Strip ── */}
      <div style={{ background: '#0a0606', borderBottom: '1px solid #2a1010', padding: '8px 24px' }}>
        <div style={{ maxWidth: '1600px', margin: '0 auto', display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
          {[
            { name: '🐂 Dinkoko', contact: 'Derrick Selepe', phone: '+27 67 681 3076', color: '#8B1A1A' },
            { name: '📦 My Courier', contact: 'Willy', phone: '+27 61 362 3448', color: '#1e4d8c' },
          ].map(p => (
            <div key={p.name} style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#0f0a0a', border: `1px solid ${p.color}44`, borderRadius: '6px', padding: '5px 12px' }}>
              <span style={{ fontSize: '12px' }}>{p.name}</span>
              <span style={{ fontSize: '10px', color: '#6b4c4c' }}>—</span>
              <span style={{ fontSize: '10px', color: '#9ca3af', fontFamily: 'monospace' }}>{p.contact}</span>
              <span style={{ fontSize: '10px', color: '#6b4c4c', fontFamily: 'monospace' }}>{p.phone}</span>
            </div>
          ))}
          <span style={{ fontSize: '9px', color: '#3d2020', fontFamily: 'monospace', letterSpacing: '1px' }}>
            DRAG CARDS TO ADVANCE STAGE · ANY → 🔴 CANCELLED
          </span>
        </div>
      </div>

      {/* ── Kanban Board ── */}
      <div style={{ maxWidth: '1600px', margin: '0 auto', padding: '20px 16px' }}>
        <DragDropContext onDragEnd={handleDragEnd}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(6, minmax(210px, 1fr))',
            gap: '12px',
            alignItems: 'start',
          }}>
            {COLUMNS.map(col => {
              const colCards = cards.filter(c => c.columnId === col.id);
              return (
                <div
                  key={col.id}
                  style={{
                    background: '#0f0a0a',
                    border: `1px solid #2a1010`,
                    borderTop: `3px solid ${col.color}`,
                    borderRadius: '8px 8px 0 0',
                    display: 'flex',
                    flexDirection: 'column',
                    minHeight: '500px',
                  }}
                >
                  {/* Column header */}
                  <div style={{
                    padding: '10px 12px 8px',
                    borderBottom: `2px solid ${col.color}22`,
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
                      <span style={{ fontSize: '15px' }}>{col.emoji}</span>
                      <span style={{ fontSize: '10px', fontWeight: 800, color: '#f9fafb', fontFamily: 'monospace', letterSpacing: '0.8px' }}>{col.title}</span>
                      <span style={{
                        background: col.color, color: '#fff', fontSize: '9px', fontWeight: 800,
                        padding: '1px 7px', borderRadius: '10px', fontFamily: 'monospace',
                      }}>{colCards.length}</span>
                    </div>
                    <button
                      onClick={() => openAdd(col.id)}
                      style={{ background: 'transparent', border: 'none', color: '#6b4c4c', cursor: 'pointer', display: 'flex', padding: '2px', borderRadius: '3px', transition: 'color 0.15s' }}
                      title={`Add to ${col.title}`}
                      onMouseEnter={e => { (e.currentTarget as HTMLElement).style.color = '#f9fafb'; }}
                      onMouseLeave={e => { (e.currentTarget as HTMLElement).style.color = '#6b4c4c'; }}
                    >
                      <PlusIcon />
                    </button>
                  </div>

                  {/* Drop zone */}
                  <Droppable droppableId={col.id}>
                    {(provided, snapshot) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.droppableProps}
                        style={{
                          flex: 1,
                          padding: '10px',
                          minHeight: '200px',
                          background: snapshot.isDraggingOver ? '#1a0808' : 'transparent',
                          transition: 'background 0.15s',
                        }}
                      >
                        {colCards.length === 0 && !snapshot.isDraggingOver && (
                          <div style={{
                            textAlign: 'center', padding: '28px 8px', color: '#3d2020',
                            fontSize: '10px', fontFamily: 'monospace', letterSpacing: '1px',
                            border: '1px dashed #2a1010', borderRadius: '4px', marginTop: '4px',
                          }}>
                            DROP HERE
                          </div>
                        )}
                        {colCards.map((card, idx) => (
                          <KanbanCard
                            key={card.id}
                            card={card}
                            index={idx}
                            onEdit={openEdit}
                            onDelete={deleteCard}
                          />
                        ))}
                        {provided.placeholder}
                      </div>
                    )}
                  </Droppable>
                </div>
              );
            })}
          </div>
        </DragDropContext>
      </div>

      {/* ── Footer ── */}
      <div style={{ textAlign: 'center', padding: '16px', fontSize: '9px', color: '#3d2020', fontFamily: 'monospace', letterSpacing: '1px' }}>
        STUDEx MEAT DELIVERY BOARD · LOCAL STORAGE · AUTO-SAVED · SAST {new Date().toLocaleTimeString('en-ZA', { timeZone: 'Africa/Johannesburg' })}
      </div>

      {/* Modal */}
      {showModal && (
        <CardModal
          card={editingCard ?? undefined}
          defaultColumnId={defaultCol}
          onSave={handleSave}
          onClose={() => { setShowModal(false); setEditingCard(null); }}
        />
      )}

      {/* Toast */}
      {toast && <Toast message={toast} onDone={() => setToast(null)} />}
    </div>
  );
}
