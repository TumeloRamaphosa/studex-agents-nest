import { useState } from 'react';

interface ChecklistItem {
  id: string;
  task: string;
  done: boolean;
  due: string;
  owner: 'Tumelo' | 'Robusca' | 'Both';
  link?: string;
  notes: string;
}

function getSASTDate(): string {
  const now = new Date();
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const saTime = new Date(utc + 2 * 60 * 60 * 1000);
  return saTime.toLocaleDateString('en-ZA', { day: '2-digit', month: 'short', year: 'numeric' });
}

function getCIIECountdown(): { days: number; label: string } {
  const now = new Date();
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const saTime = new Date(utc + 2 * 60 * 60 * 1000);
  const ciie = new Date('2026-11-05T00:00:00+02:00');
  const diff = ciie.getTime() - saTime.getTime();
  const days = Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
  return { days, label: `CIIE 2026 — D-${days}` };
}

const initialChecklist: ChecklistItem[] = [
  {
    id: 'c1',
    task: 'Register as official CIIE buyer on ciie.org',
    done: false,
    due: '2026-09-19',
    owner: 'Tumelo',
    link: 'https://www.ciie.org',
    notes: 'Buyer registration opens early Sep. Need company docs + import license.',
  },
  {
    id: 'c2',
    task: 'Submit booth application for location to be confirmed / Food & Agriculture zone',
    done: false,
    due: '2026-09-22',
    owner: 'Tumelo',
    link: 'https://www.ciie.org/zbz.html',
    notes: 'location to be confirmed is Food & Ag. Apply as Rwanda coffee exporter. Mention PROWTC + full origin documentation: phytosanitary certificates, COA, fumigation records.',
  },
  {
    id: 'c3',
    task: 'Pay CIIE presence fees (R28,000–R65,000 depending on size)',
    done: false,
    due: '2026-09-30',
    owner: 'Tumelo',
    notes: 'Standard booth ~R45,000. Premium positioning +R20,000. Budget approval needed.',
  },
  {
    id: 'c4',
    task: 'Arrange Rwanda coffee sample packs (250g x 50 bags per grade)',
    done: false,
    due: '2026-10-01',
    owner: 'Robusca',
    notes: 'A1 Washed, A2 Natural, A2 Washed — 3 grades. Phytosanitary certificates and COA attached to each lot.',
  },
  {
    id: 'c5',
    task: 'Book flights: JNB → PVG Nov 3-11 (8 nights)',
    done: false,
    due: '2026-10-05',
    owner: 'Tumelo',
    notes: 'Nov 3 arrival, Nov 4 setup, Nov 5-10 expo, Nov 11 departure. Book via Travelstart or direct.',
  },
  {
    id: 'c6',
    task: 'Book hotel near National Exhibition Center (NECC), Qingpu district',
    done: false,
    due: '2026-10-05',
    owner: 'Tumelo',
    notes: 'NECC is in Qingpu — book hotel within 2km. Nov 3-11 covers setup + expo days.',
  },
  {
    id: 'c7',
    task: 'Apply for China business visa (M visa for commercial)',
    done: false,
    due: '2026-09-25',
    owner: 'Tumelo',
    notes: 'SA passport. Application takes 5-7 working days. Use VFS Global or China Visa Centre.',
  },
  {
    id: 'c8',
    task: 'Prepare Rwanda Certificate of Origin + phytosanitary certificate',
    done: false,
    due: '2026-10-15',
    owner: 'Robusca',
    notes: 'Rwanda Revenue Authority issues COO. Phytosanitary from Rwanda Agriculture Board.',
  },
  {
    id: 'c9',
    task: 'Design + print CIIE exhibition materials (banners, biz cards, flyers)',
    done: false,
    due: '2026-10-10',
    owner: 'Robusca',
    notes: 'Pull template from /workspace/studex-coffee/promo/. Print via order in SA before departure.',
  },
  {
    id: 'c10',
    task: 'Pre-schedule CIIE buyer meetings via official portal',
    done: false,
    due: '2026-10-15',
    owner: 'Robusca',
    link: 'https://www.ciie.org',
    notes: 'Buyers can pre-book meeting slots from Oct 1. Target: Luckin, Tim Hortons, BonCafe, Coffee Planet.',
  },
  {
    id: 'c11',
    task: 'Confirm freight forwarder for sample shipment to Shanghai warehouse',
    done: false,
    due: '2026-10-10',
    owner: 'Robusca',
    notes: 'Use DHL Express or SA post for sample boxes. Mark as "commercial sample, no commercial value".',
  },
  {
    id: 'c12',
    task: 'Study CIIE buyer registration list — pre-identify coffee buyers',
    done: false,
    due: '2026-09-30',
    owner: 'Robusca',
    notes: 'CIIE publishes registered buyers by sector. Pull food/beverage buyer list. Focus on China + UAE + Europe.',
  },
  {
    id: 'c13',
    task: 'Confirm export funding / forex arrangements for booth + travel',
    done: false,
    due: '2026-10-01',
    owner: 'Tumelo',
    notes: 'Estimate R80,000 total cost. Check FNB / Absa forex facilities for CNY travel allowance.',
  },
];

export default function CIIEBoothApplication() {
  const [checklist, setChecklist] = useState<ChecklistItem[]>(initialChecklist);
  const [activeFilter, setActiveFilter] = useState<'all' | 'pending' | 'done'>('all');
  const today = getSASTDate();
  const ciie = getCIIECountdown();

  const toggle = (id: string) => {
    setChecklist(prev => prev.map(c => c.id === id ? { ...c, done: !c.done } : c));
  };

  const doneCount = checklist.filter(c => c.done).length;
  const pendingCount = checklist.filter(c => !c.done).length;
  const pct = Math.round((doneCount / checklist.length) * 100);

  const filtered = checklist.filter(c => {
    if (activeFilter === 'done') return c.done;
    if (activeFilter === 'pending') return !c.done;
    return true;
  });

  return (
    <div className="ciie-booth-panel">
      {/* Header */}
      <div className="ciie-header">
        <div className="ciie-title-row">
          <div>
            <div className="ciie-title">🏛️ CIIE 2026 BOOTH APPLICATION TRACKER</div>
            <div className="ciie-subtitle">{today} · Shanghai, Nov 5–10 · Studex Meat Coffee</div>
          </div>
          <div className="ciie-countdown">
            <div className="ciie-days">{ciie.days}</div>
            <div className="ciie-days-label">days to CIIE</div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="booth-progress-row">
          <div className="booth-progress-bar">
            <div className="booth-progress-fill" style={{ width: `${pct}%` }} />
          </div>
          <div className="booth-progress-label">{doneCount}/{checklist.length} tasks done ({pct}%)</div>
        </div>

        <div className="ciie-kpi-strip">
          <div className="ciie-kpi">
            <span className="ciie-kpi-val" style={{ color: '#ef4444' }}>{pendingCount}</span>
            <span className="ciie-kpi-lbl">PENDING</span>
          </div>
          <div className="ciie-kpi">
            <span className="ciie-kpi-val" style={{ color: '#22c55e' }}>{doneCount}</span>
            <span className="ciie-kpi-lbl">DONE</span>
          </div>
          <div className="ciie-kpi">
            <span className="ciie-kpi-val" style={{ color: '#d4a017' }}>R80k</span>
            <span className="ciie-kpi-lbl">EST. COST</span>
          </div>
          <div className="ciie-kpi">
            <span className="ciie-kpi-val" style={{ color: '#4a9eff' }}>Nov 3</span>
            <span className="ciie-kpi-lbl">ARRIVE SHANGHAI</span>
          </div>
          <div className="ciie-kpi">
            <span className="ciie-kpi-val" style={{ color: '#4a9eff' }}>Nov 4</span>
            <span className="ciie-kpi-lbl">SETUP DAY</span>
          </div>
          <div className="ciie-kpi">
            <span className="ciie-kpi-val" style={{ color: '#4a9eff' }}>ciie.org</span>
            <span className="ciie-kpi-lbl">REGISTER NOW</span>
          </div>
        </div>
      </div>

      <div className="ciie-body">
        {/* Filters */}
        <div className="booth-filters">
          {[['all', `All (${checklist.length})`], ['pending', `Pending (${pendingCount})`], ['done', `Done (${doneCount})`]].map(([val, label]) => (
            <button
              key={val}
              className={`ciie-filter-btn ${activeFilter === val ? 'active' : ''}`}
              onClick={() => setActiveFilter(val as 'all' | 'pending' | 'done')}
            >
              {label}
            </button>
          ))}
          <a
            href="https://www.ciie.org"
            target="_blank"
            rel="noopener noreferrer"
            className="ciie-reg-btn"
          >
            🌐 ciie.org — Apply for Booth
          </a>
        </div>

        {/* Checklist */}
        <div className="booth-checklist">
          {filtered.map((item, idx) => {
            const isOverdue = !item.done && item.due < today.split(' ')[0];
            return (
              <div key={item.id} className={`booth-item ${item.done ? 'done' : ''} ${isOverdue ? 'overdue' : ''}`}>
                <div className="booth-check-col">
                  <button
                    className={`booth-check-btn ${item.done ? 'checked' : ''}`}
                    onClick={() => toggle(item.id)}
                  >
                    {item.done ? '✅' : '⬜'}
                  </button>
                </div>
                <div className="booth-info-col">
                  <div className="booth-task">{item.task}</div>
                  <div className="booth-meta">
                    <span className={`booth-owner owner-${item.owner.toLowerCase()}`}>{item.owner}</span>
                    <span className="booth-due" style={{ color: isOverdue ? '#ef4444' : '#7a8099' }}>
                      {isOverdue ? '⚠️ ' : ''}Due: {item.due}
                    </span>
                    {item.link && (
                      <a href={item.link} target="_blank" rel="noopener noreferrer" className="booth-link">
                        🔗 Open
                      </a>
                    )}
                  </div>
                  {item.notes && <div className="booth-notes">{item.notes}</div>}
                </div>
              </div>
            );
          })}
        </div>

        {/* Bottom CTA */}
        <div className="booth-cta-row">
          <div className="booth-cta-box">
            <div className="booth-cta-title">🎯 Mission: Get Rwanda Coffee in Front of 200+ China Buyers</div>
            <div className="booth-cta-sub">CIIE 2025 hosted 3,496 exporters from 129 countries. 85% of attendees were buyers. This is where the deals start.</div>
          </div>
        </div>
      </div>
    </div>
  );
}
