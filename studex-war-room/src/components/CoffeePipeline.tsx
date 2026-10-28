import { useState } from 'react';

// ── Types ──────────────────────────────────────────────────────────────────
interface Prospect {
  id: string;
  name: string;
  type: 'hotel' | 'cafe' | 'restaurant' | 'oc OFFICE';
  city: string;
  status: 'cold' | 'cupping' | 'sampling' | 'negotiating' | 'contracted' | 'retainer';
  contact: string;
  source: string;
  value: number; // monthly R
  lastContact: string;
  notes: string;
  cuppingDate?: string;
}

interface PipelineStage {
  id: Prospect['status'];
  label: string;
  color: string;
}

// ── Pipeline Config ───────────────────────────────────────────────────────────
const stages: PipelineStage[] = [
  { id: 'cold',       label: 'COLD OUTREACH',    color: '#7a8099' },
  { id: 'cupping',    label: 'CUPPING SESSION',  color: '#d4a017' },
  { id: 'sampling',   label: 'SAMPLING',         color: '#ff6eb4' },
  { id: 'negotiating',label: 'NEGOTIATING',      color: '#ff8800' },
  { id: 'contracted', label: 'CONTRACTED',        color: '#4a9eff' },
  { id: 'retainer',   label: 'RETAINER',         color: '#4aff88' },
];

// ── Mock Data ────────────────────────────────────────────────────────────────
const prospects: Prospect[] = [
  // COLD OUTREACH
  { id: 'P001', name: 'Radisson RED V&A',        type: 'hotel',        city: 'Cape Town', status: 'cold',         contact: 'F&B Manager',       source: 'LinkedIn',     value: 45000, lastContact: '2026-08-10', notes: 'Large conference ops — cold brew opportunity', },
  { id: 'P002', name: 'The Oyster Box',          type: 'hotel',        city: 'Durban',    status: 'cold',         contact: 'GM',                source: 'Referral',     value: 80000, lastContact: '2026-08-08', notes: 'Luxury — caviar + coffee pairing potential', },
  { id: 'P003', name: 'Father Coffee',           type: 'cafe',         city: 'Johannesburg', status: 'cold',    contact: 'Owner',             source: 'Instagram',    value: 12000, lastContact: '2026-08-05', notes: 'Specialty — single origin seekers', },
  { id: 'P004', name: 'Haute CRL Restaurant',    type: 'restaurant',   city: 'Cape Town', status: 'cold',         contact: 'Chef Patron',       source: 'Google Maps', value: 22000, lastContact: '2026-08-12', notes: 'Fine dining — wagyu + coffee dessert menu', },
  // CUPPING
  { id: 'P005', name: 'Glen Lounge JHB',         type: 'oc OFFICE',    city: 'Johannesburg', status: 'cupping', contact: 'Office Manager',   source: 'Email',        value: 18000, lastContact: '2026-08-14', notes: 'OCS potential — 80 staff, 3 floors', cuppingDate: '2026-08-18', },
  { id: 'P006', name: 'Mount Grace Country House',type:'hotel',        city: 'Magaliesburg',status: 'cupping',  contact: 'F&B Director',      source: 'Referral',     value: 35000, lastContact: '2026-08-13', notes: 'Weekend retreats — cold brew focus', cuppingDate: '2026-08-20', },
  { id: 'P007', name: 'Bean There CPT',          type: 'cafe',         city: 'Cape Town', status: 'cupping',     contact: 'Head Barista',      source: 'Trade show',   value: 9000,  lastContact: '2026-08-11', notes: 'Existing importer — may want backup supplier', cuppingDate: '2026-08-19', },
  // SAMPLING
  { id: 'P008', name: 'Indaba Hotel',             type: 'hotel',        city: 'Johannesburg', status: 'sampling', contact: 'Banqueting Mgr',   source: 'Cold call',    value: 55000, lastContact: '2026-08-12', notes: 'Weddings + conferences — high volume', },
  { id: 'P009', name: 'Krispy Kreme HO',         type: 'oc OFFICE',    city: 'Johannesburg', status: 'sampling', contact: 'Facilities Lead',  source: 'Warm intro',   value: 25000, lastContact: '2026-08-09', notes: 'Morning coffee service for 200 staff', },
  // NEGOTIATING
  { id: 'P010', name: 'Sandton Conference Centre',type: 'hotel',        city: 'Johannesburg', status: 'negotiating', contact: 'Catering Dir', source: 'LinkedIn',     value: 95000, lastContact: '2026-08-15', notes: '3-yr contract on table — exclusivity clause discussed', },
  { id: 'P011', name: 'The Bloc Hotel',           type: 'hotel',        city: 'Johannesburg', status: 'negotiating', contact: 'GM',          source: 'Referral',     value: 40000, lastContact: '2026-08-14', notes: 'Barista training included in proposal', },
  // CONTRACTED
  { id: 'P012', name: 'Park Hyatt JHB',          type: 'hotel',        city: 'Johannesburg', status: 'contracted', contact: 'F&B Mgr',        source: 'Existing',     value: 72000, lastContact: '2026-08-01', notes: '6-month contract — renewal Oct', },
  { id: 'P013', name: 'Vida e Caffè Bruma',       type: 'cafe',         city: 'Durban',      status: 'contracted', contact: 'Area Manager',    source: 'Referral',     value: 15000, lastContact: '2026-07-28', notes: '10 branches — rollout to 5 more in Q4', },
  // RETAINER
  { id: 'P014', name: 'Africa Cloud Offices',    type: 'oc OFFICE',    city: 'Johannesburg', status: 'retainer',  contact: 'CEO',              source: 'Warm lead',    value: 38000, lastContact: '2026-07-15', notes: '✅ RETAINER — 12-month barista retainer + monthly bean supply', },
  { id: 'P015', name: 'Protea Marriott JHB',      type: 'hotel',        city: 'Johannesburg', status: 'retainer',   contact: 'F&B Director',    source: 'Existing',     value: 61000, lastContact: '2026-07-20', notes: '✅ RETAINER — training included, quarterly menu refresh', },
];

// ── Rwanda Origin Data ──────────────────────────────────────────────────────
const rwandaOrigin = {
  grade: 'A1 / A2',
  region: 'Nyamasheke, Rusizi District, Western Province',
  cooperative: 'Ejo Heza — Dukunde Kawa',
  womenFarmers: '2,400 women',
  altitude: '1,800–2,200m ASL',
  process: 'Fully washed, raised-bed dried',
  certifications: ['Rainforest Alliance', 'UTZ', 'Fairtrade'],
  harvestSeason: 'April–June 2026',
  available: 'September 2026',
  pricePerKg: 'USD 4.20–5.80 (FOB Kigali)',
  moq: '500kg',
  sampleAvailable: 'Yes — 200g sample kits free for qualified prospects',
  usp: 'Zero-tariff to China (May 2026), women-owned cooperative, cup quality 84+ SCA',
};

// ── Helpers ──────────────────────────────────────────────────────────────────
function stageColor(status: Prospect['status']): string {
  return stages.find(s => s.id === status)?.color ?? '#7a8099';
}

function daysUntil(target: string): number {
  const now = new Date();
  const t = new Date(target);
  return Math.ceil((t.getTime() - now.getTime()) / 86400000);
}

function formatDate(ds: string): string {
  const d = new Date(ds);
  return d.toLocaleDateString('en-ZA', { day: '2-digit', month: 'short' });
}

// ── Component ────────────────────────────────────────────────────────────────
export default function CoffeePipeline() {
  const [filter, setFilter] = useState<Prospect['status'] | 'all'>('all');
  const [selectedProspect, setSelectedProspect] = useState<Prospect | null>(null);
  const [inquiryOpen, setInquiryOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', contact: '', type: 'hotel' as Prospect['type'], city: '', notes: '' });
  const [formSent, setFormSent] = useState(false);

  const filtered = filter === 'all' ? prospects : prospects.filter(p => p.status === filter);
  const totalPipeline = prospects.reduce((s, p) => s + p.value, 0);
  const activeMonthly = prospects.filter(p => !['cold'].includes(p.status)).reduce((s, p) => s + p.value, 0);
  const coldOutreach = prospects.filter(p => p.status === 'cold').length;
  const cuppingCount = prospects.filter(p => ['cupping', 'sampling'].includes(p.status)).length;
  const contractedARR = prospects.filter(p => ['contracted', 'retainer'].includes(p.status)).reduce((s, p) => s + p.value, 0);
  const daysToLaunch = daysUntil('2026-09-01');
  const launchProgress = Math.round(((30 - daysToLaunch) / 30) * 100);

  function handleInquirySubmit(e: React.FormEvent) {
    e.preventDefault();
    setFormSent(true);
    setTimeout(() => { setFormSent(false); setInquiryOpen(false); setFormData({ name: '', contact: '', type: 'hotel', city: '', notes: '' }); }, 2500);
  }

  return (
    <div className="coffee-pipeline">
      {/* ── Header ── */}
      <div className="cp-header">
        <div className="cp-title">
          <span style={{ fontSize: '20px' }}>☕</span>
          <span>STUDEX COFFEE — B2B PIPELINE</span>
          <span className="cp-countdown" style={{ background: daysToLaunch <= 14 ? '#ff4444' : daysToLaunch <= 30 ? '#d4a017' : '#4a9eff' }}>
            {daysToLaunch > 0 ? `${daysToLaunch} DAYS TO LAUNCH` : '🚀 LIVE'}
          </span>
        </div>
        <div className="cp-launch-bar">
          <div className="cp-launch-label">RWANDA A1/A2 LAUNCH PROGRESS</div>
          <div className="cp-launch-track">
            <div className="cp-launch-fill" style={{ width: `${launchProgress}%` }} />
          </div>
          <div className="cp-launch-pct">{launchProgress}%</div>
        </div>
      </div>

      {/* ── KPI Row ── */}
      <div className="cp-kpis">
        <div className="cp-kpi">
          <div className="cp-kpi-val" style={{ color: '#4a9eff' }}>R{totalPipeline.toLocaleString()}</div>
          <div className="cp-kpi-lbl">FULL PIPELINE</div>
          <div className="cp-kpi-sub">monthly potential</div>
        </div>
        <div className="cp-kpi">
          <div className="cp-kpi-val" style={{ color: '#4aff88' }}>R{activeMonthly.toLocaleString()}</div>
          <div className="cp-kpi-lbl">ACTIVE MONTHLY</div>
          <div className="cp-kpi-sub">cupping+</div>
        </div>
        <div className="cp-kpi">
          <div className="cp-kpi-val" style={{ color: '#d4a017' }}>R{contractedARR.toLocaleString()}</div>
          <div className="cp-kpi-lbl">CONTRACTED ARR</div>
          <div className="cp-kpi-sub">confirmed revenue</div>
        </div>
        <div className="cp-kpi">
          <div className="cp-kpi-val" style={{ color: '#ff6eb4' }}>{cuppingCount}</div>
          <div className="cp-kpi-lbl">CUPPING / SAMPLE</div>
          <div className="cp-kpi-sub">active sessions</div>
        </div>
        <div className="cp-kpi">
          <div className="cp-kpi-val" style={{ color: '#7a8099' }}>{coldOutreach}</div>
          <div className="cp-kpi-lbl">COLD OUTREACH</div>
          <div className="cp-kpi-sub">top-of-funnel</div>
        </div>
      </div>

      {/* ── Rwanda Origin Card ── */}
      <div className="cp-rwanda-card">
        <div className="cp-rwanda-header">
          <span className="cp-rwanda-flag">🇷🇼</span>
          <div>
            <div className="cp-rwanda-title">RWANDA A1 / A2 — NYAMASHEKE HARVEST 2026</div>
            <div className="cp-rwanda-sub">Ejo Heza Cooperative · 2,400 women farmers · 1,800–2,200m ASL</div>
          </div>
          <div className="cp-rwanda-badges">
            {rwandaOrigin.certifications.map(c => (
              <span key={c} className="cp-badge">{c}</span>
            ))}
          </div>
        </div>
        <div className="cp-rwanda-grid">
          <div className="cp-rwanda-stat"><span className="crs-label">MOQ</span><span className="crs-val">{rwandaOrigin.moq}</span></div>
          <div className="cp-rwanda-stat"><span className="crs-label">PRICE/ KG</span><span className="crs-val">{rwandaOrigin.pricePerKg}</span></div>
          <div className="cp-rwanda-stat"><span className="crs-label">HARVEST</span><span className="crs-val">{rwandaOrigin.harvestSeason}</span></div>
          <div className="cp-rwanda-stat"><span className="crs-label">AVAILABLE</span><span className="crs-val" style={{ color: '#4aff88' }}>{rwandaOrigin.available}</span></div>
          <div className="cp-rwanda-stat"><span className="crs-label">PROCESS</span><span className="crs-val">{rwandaOrigin.process}</span></div>
          <div className="cp-rwanda-stat"><span className="crs-label">SCA SCORE</span><span className="crs-val">84+</span></div>
          <div className="cp-rwanda-stat cp-rwanda-sample">
            <span className="crs-label">SAMPLES</span>
            <span className="crs-val" style={{ color: '#d4a017' }}>{rwandaOrigin.sampleAvailable}</span>
          </div>
        </div>
        <div className="cp-rwanda-usp">
          <span className="crs-label">MOAT</span>
          <span className="crs-val">{rwandaOrigin.usp}</span>
        </div>
      </div>

      {/* ── Pipeline Funnel ── */}
      <div className="cp-funnel">
        {stages.map(stage => {
          const count = prospects.filter(p => p.status === stage.id).length;
          const val = prospects.filter(p => p.status === stage.id).reduce((s, p) => s + p.value, 0);
          const pct = prospects.length > 0 ? Math.round((count / prospects.length) * 100) : 0;
          return (
            <div
              key={stage.id}
              className={`cp-funnel-stage ${filter === stage.id ? 'active' : ''}`}
              style={{ borderColor: stage.color, color: stage.color }}
              onClick={() => setFilter(filter === stage.id ? 'all' : stage.id)}
            >
              <div className="cfs-count">{count}</div>
              <div className="cfs-label">{stage.label}</div>
              <div className="cfs-val">R{val.toLocaleString()}/mo</div>
              <div className="cfs-bar"><div className="cfs-fill" style={{ width: `${pct}%`, backgroundColor: stage.color }} /></div>
            </div>
          );
        })}
      </div>

      {/* ── Prospect Table ── */}
      <div className="cp-table-wrap">
        <div className="cp-table-header">
          <span className="cp-table-title">PROSPECTS — {filtered.length}</span>
          <button className="cp-add-btn" onClick={() => setInquiryOpen(true)}>+ ADD PROSPECT</button>
        </div>
        <table className="cp-table">
          <thead>
            <tr>
              <th>NAME</th>
              <th>TYPE</th>
              <th>CITY</th>
              <th>STATUS</th>
              <th>CONTACT</th>
              <th>VALUE / MO</th>
              <th>LAST CONTACT</th>
              <th>NOTES</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(p => (
              <tr key={p.id} onClick={() => setSelectedProspect(p)} style={{ cursor: 'pointer' }} className="cp-row">
                <td className="cp-name">{p.name}</td>
                <td><span className="cp-type-badge">{p.type}</span></td>
                <td>{p.city}</td>
                <td>
                  <span className="cp-status-badge" style={{ color: stageColor(p.status), borderColor: stageColor(p.status) }}>
                    {p.status.toUpperCase()}
                  </span>
                </td>
                <td className="cp-contact">{p.contact}</td>
                <td className="cp-val">R{p.value.toLocaleString()}</td>
                <td className="cp-date">{formatDate(p.lastContact)}</td>
                <td className="cp-notes">{p.notes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ── Prospect Detail Modal ── */}
      {selectedProspect && (
        <div className="cp-modal-overlay" onClick={() => setSelectedProspect(null)}>
          <div className="cp-modal" onClick={e => e.stopPropagation()}>
            <div className="cp-modal-header" style={{ borderColor: stageColor(selectedProspect.status) }}>
              <div>
                <div className="cp-modal-name">{selectedProspect.name}</div>
                <div className="cp-modal-sub">{selectedProspect.type.toUpperCase()} · {selectedProspect.city}</div>
              </div>
              <button className="cp-modal-close" onClick={() => setSelectedProspect(null)}>✕</button>
            </div>
            <div className="cp-modal-body">
              <div className="cp-modal-grid">
                <div className="cpm-field"><span className="cpm-label">STATUS</span><span className="cpm-val" style={{ color: stageColor(selectedProspect.status) }}>{selectedProspect.status.toUpperCase()}</span></div>
                <div className="cpm-field"><span className="cpm-label">MONTHLY VALUE</span><span className="cpm-val">R{selectedProspect.value.toLocaleString()}</span></div>
                <div className="cpm-field"><span className="cpm-label">CONTACT</span><span className="cpm-val">{selectedProspect.contact}</span></div>
                <div className="cpm-field"><span className="cpm-label">SOURCE</span><span className="cpm-val">{selectedProspect.source}</span></div>
                <div className="cpm-field"><span className="cpm-label">LAST CONTACT</span><span className="cpm-val">{formatDate(selectedProspect.lastContact)}</span></div>
                {selectedProspect.cuppingDate && (
                  <div className="cpm-field"><span className="cpm-label">CUPPING DATE</span><span className="cpm-val" style={{ color: '#d4a017' }}>{formatDate(selectedProspect.cuppingDate)} ({daysUntil(selectedProspect.cuppingDate)}d)</span></div>
                )}
              </div>
              <div className="cpm-notes">
                <span className="cpm-label">NOTES</span>
                <div className="cpm-notes-text">{selectedProspect.notes}</div>
              </div>
              <div className="cpm-actions">
                <button className="cpm-btn primary">📧 SEND EMAIL</button>
                <button className="cpm-btn">📞 LOG CALL</button>
                <button className="cpm-btn">📅 SCHEDULE CUPPING</button>
                <button className="cpm-btn">✏️ EDIT</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Add Prospect Form ── */}
      {inquiryOpen && (
        <div className="cp-modal-overlay" onClick={() => setInquiryOpen(false)}>
          <div className="cp-modal" onClick={e => e.stopPropagation()}>
            <div className="cp-modal-header" style={{ borderColor: '#4a9eff' }}>
              <div>
                <div className="cp-modal-name">ADD NEW PROSPECT</div>
                <div className="cp-modal-sub">B2B Coffee Inquiry</div>
              </div>
              <button className="cp-modal-close" onClick={() => setInquiryOpen(false)}>✕</button>
            </div>
            {formSent ? (
              <div className="cp-form-success">✅ Prospect added to pipeline. Cupping session offer sent to {formData.contact}.</div>
            ) : (
              <form className="cp-form" onSubmit={handleInquirySubmit}>
                <div className="cp-form-row">
                  <label>ESTABLISHMENT NAME<input required value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} placeholder="e.g. Radisson RED V&A" /></label>
                  <label>TYPE<select value={formData.type} onChange={e => setFormData({ ...formData, type: e.target.value as Prospect['type'] })}>
                    <option value="hotel">🏨 Hotel</option>
                    <option value="cafe">☕ Café</option>
                    <option value="restaurant">🍽️ Restaurant</option>
                    <option value="oc OFFICE">🏢 OCS / Office</option>
                  </select></label>
                </div>
                <div className="cp-form-row">
                  <label>CONTACT NAME / TITLE<input required value={formData.contact} onChange={e => setFormData({ ...formData, contact: e.target.value })} placeholder="e.g. F&B Manager" /></label>
                  <label>CITY<input required value={formData.city} onChange={e => setFormData({ ...formData, city: e.target.value })} placeholder="e.g. Cape Town" /></label>
                </div>
                <label>NOTES<input value={formData.notes} onChange={e => setFormData({ ...formData, notes: e.target.value })} placeholder="Cold brew opportunity, 200 staff..." /></label>
                <div className="cp-form-actions">
                  <button type="submit" className="cpm-btn primary">➕ ADD TO PIPELINE</button>
                  <button type="button" className="cpm-btn" onClick={() => setInquiryOpen(false)}>CANCEL</button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
