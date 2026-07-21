import { useState } from 'react';

// Deal pipeline stage
interface CoffeeDeal {
  id: string;
  buyer: string;
  contact: string;
  origin: string;
  grade: string;
  volumeKg: number;
  pricePerKg: number;
  revenue: number;
  stage: 'lead' | 'negotiating' | 'contract' | 'shipped' | 'paid';
  country: string;
  lastContact: string;
  notes: string;
  probability: number;
}

const deals: CoffeeDeal[] = [
  {
    id: 'd0',
    buyer: '🔴 CIIE Shanghai Booth',
    contact: 'ciie.org — apply before Aug 31',
    origin: 'Rwanda',
    grade: 'A1/A2 Washed + Natural',
    volumeKg: 5000,
    pricePerKg: 9.00,
    revenue: 45000,
    stage: 'lead',
    country: 'China',
    lastContact: '2026-07-21',
    notes: '🔥 DEADLINE AUG 31: CIIE Shanghai is the ONLY direct B2B touchpoint with Luckin Coffee + Tim Hortons China buyers. 450+ exhibitors, 17,000+ visitors. Luckin has 33,596 stores — locked into Brazil deal, but Rwanda specialty line could break through. Rwanda A1/A2 commands 40–60% premium over commodity index.',
    probability: 70,
  },
  {
    id: 'd1',
    buyer: 'Luckin Coffee China',
    contact: 'buyer@luckincoffee.com — CIIE or direct outreach',
    origin: 'Rwanda',
    grade: 'A1 Washed (jasmine/stone fruit)',
    volumeKg: 10000,
    pricePerKg: 8.80,
    revenue: 88000,
    stage: 'lead',
    country: 'China',
    lastContact: '2026-07-21',
    notes: '🇨🇳 Luckin Coffee: 33,596 stores (Q1 2026), largest chain in China. Locked into Brazil deal (240,000 tons / $1.4B deal through 2029). Rwanda = NOT in current supply mix. Approach via CIIE booth — specialty/seasonal line only, NOT commodity. FOB $4.60–5.50/kg entry. PROWTC Rainforest Alliance + PROWTC cert = box ticked.',
    probability: 40,
  },
  {
    id: 'd2',
    buyer: 'Tim Hortons China',
    contact: 'procurement.cn@timhortons.com — CIIE or LinkedIn',
    origin: 'Rwanda',
    grade: 'A2 Natural (blueberry/chocolate)',
    volumeKg: 5000,
    pricePerKg: 8.20,
    revenue: 41000,
    stage: 'lead',
    country: 'China',
    lastContact: '2026-07-21',
    notes: 'Tim Hortons China: Canada heritage + Chinese market taste. Different buyer profile from Luckin. Rwanda A2 natural (blueberry/chocolate) aligns with premium blended coffee positioning. CIIE booth is key. PROWTC/RA certified = hotel chain requirement satisfied.',
    probability: 35,
  },
  {
    id: 'd3',
    buyer: 'PROWTC Dubai',
    contact: 'Svetlana @ PROWTC',
    origin: 'Rwanda',
    grade: 'A1 / A2 Washed',
    volumeKg: 2000,
    pricePerKg: 8.50,
    revenue: 17000,
    stage: 'negotiating',
    country: 'UAE',
    lastContact: '2026-07-02',
    notes: 'PROWTC positioned as Dubai re-export hub to China. China zero-tariff (effective Jul 20 2026 — JUST OPENED) makes Dubai→China corridor STRONGER than ever. Svetlana closing pricing by Jul 4. PROWTC + Rainforest Alliance certified.',
    probability: 80,
  },
  {
    id: 'd4',
    buyer: 'Shanghai Specialty Importers',
    contact: 'Via PROWTC referral — Jul 4 outreach',
    origin: 'Rwanda',
    grade: 'A1 Washed',
    volumeKg: 5000,
    pricePerKg: 9.20,
    revenue: 46000,
    stage: 'lead',
    country: 'China',
    lastContact: '2026-07-02',
    notes: '🇨🇳 CHINA ZERO TARIFF: Effective July 20 2026 (YESTERDAY) — 0% tariff on ALL 53 African countries coffee. Shanghai = 38% of China\'s total coffee import volume. Rwanda A1 commands 40–60% premium. Luckin locked to Brazil — white space for Rwanda.',
    probability: 50,
  },
  {
    id: 'd5',
    buyer: 'Chinese HORECA Chains',
    contact: 'Research needed — World of Coffee Dubai 2027',
    origin: 'Rwanda',
    grade: 'A1/A2 + Rainforest Alliance',
    volumeKg: 8000,
    pricePerKg: 7.80,
    revenue: 62400,
    stage: 'lead',
    country: 'China',
    lastContact: '2026-07-02',
    notes: 'Hotels/restaurants/cafés demand traceability and Rainforest Alliance cert. Q1 supply contracts needed. Chinese demand grew +21%/year since 2010. PROWTC + RA certified = box ticked.',
    probability: 35,
  },
  {
    id: 'd6',
    buyer: 'Dubai Re-Export to China',
    contact: 'Svetlana @ PROWTC',
    origin: 'Rwanda',
    grade: 'A2/B Washed',
    volumeKg: 10000,
    pricePerKg: 7.50,
    revenue: 75000,
    stage: 'negotiating',
    country: 'UAE',
    lastContact: '2026-07-02',
    notes: '🔥 Dubai as China gateway. Zero-tariff China (Jul 20 2026) + Dubai hub = African coffee competitive vs Latin America for first time ever. Container loads (10MT+) preferred. PROWTC re-export positioning.',
    probability: 65,
  },
  {
    id: 'd7',
    buyer: 'European Specialty Roasters',
    contact: 'TBD — need outreach list',
    origin: 'Rwanda',
    grade: 'A1/A2 + Rainforest Alliance',
    volumeKg: 3000,
    pricePerKg: 11.00,
    revenue: 33000,
    stage: 'lead',
    country: 'Europe',
    lastContact: '2026-06-28',
    notes: 'EU buyers need Rainforest Alliance or Fairtrade cert. Carbon footprint docs required. Cert costs $2,000–5,000/year. Target: Germany, Netherlands, Sweden specialty roasters.',
    probability: 20,
  },
];

const stageOrder = ['lead', 'negotiating', 'contract', 'shipped', 'paid'] as const;
const stageLabels: Record<string, string> = {
  lead: '🔎 LEAD',
  negotiating: '⚙️ NEGOTIATING',
  contract: '📝 CONTRACT',
  shipped: '🚢 SHIPPED',
  paid: '💰 PAID',
};
const stageColors: Record<string, string> = {
  lead: '#7a8099',
  negotiating: '#ffaa44',
  contract: '#4a9eff',
  shipped: '#00e5cc',
  paid: '#4aff88',
};

const countryFlags: Record<string, string> = {
  UAE: '🇦🇪',
  China: '🇨🇳',
  Europe: '🇪🇺',
};

export default function CoffeePipeline() {
  const [selectedDeal, setSelectedDeal] = useState<CoffeeDeal | null>(null);
  const [filterStage, setFilterStage] = useState<string>('all');

  const filteredDeals = filterStage === 'all' ? deals : deals.filter(d => d.stage === filterStage);
  const totalRevenue = deals.reduce((sum, d) => sum + d.revenue * (d.probability / 100), 0);
  const weightedRevenue = deals.reduce((sum, d) => sum + d.revenue * (d.probability / 100), 0);
  const guaranteedRevenue = deals.filter(d => d.stage === 'paid' || d.stage === 'shipped').reduce((sum, d) => sum + d.revenue, 0);

  return (
    <div className="coffee-pipeline">
      {/* Header KPIs */}
      <div className="coffee-kpis">
        <div className="ckpi-card">
          <div className="ckpi-label">WEIGHTED PIPELINE</div>
          <div className="ckpi-value" style={{ color: '#d4a017' }}>${(totalRevenue).toLocaleString()}</div>
          <div className="ckpi-sub">at probability-weighted</div>
        </div>
        <div className="ckpi-card">
          <div className="ckpi-label">GUARANTEED</div>
          <div className="ckpi-value" style={{ color: '#4aff88' }}>${guaranteedRevenue.toLocaleString()}</div>
          <div className="ckpi-sub">shipped + paid only</div>
        </div>
        <div className="ckpi-card">
          <div className="ckpi-label">GROSS POTENTIAL</div>
          <div className="ckpi-value" style={{ color: '#4a9eff' }}>${deals.reduce((s, d) => s + d.revenue, 0).toLocaleString()}</div>
          <div className="ckpi-sub">{deals.length} active deals</div>
        </div>
        <div className="ckpi-card">
          <div className="ckpi-label">TOP GRADE</div>
          <div className="ckpi-value" style={{ color: '#ff6eb4' }}>A1/A2</div>
          <div className="ckpi-sub">Rwanda Washed — premium tier</div>
        </div>
      </div>

      {/* Market Intel Banner */}
      <div className="intel-banner">
        <span className="intel-flag">🇨🇳</span>
        <div className="intel-text">
          <strong>MARKET INTEL:</strong> China is now Rwanda's #1 export destination. Rwanda A1/A2 commands a <strong>40–60% premium</strong> over commodity index.
          Specialty grade pricing: US$ 7.80–11.00/kg. PROWTC Dubai deal closing TODAY.
        </div>
      </div>

      {/* Stage filter */}
      <div className="stage-filter">
        <button
          className={`sf-btn ${filterStage === 'all' ? 'active' : ''}`}
          onClick={() => setFilterStage('all')}
        >ALL</button>
        {stageOrder.map(s => (
          <button
            key={s}
            className={`sf-btn ${filterStage === s ? 'active' : ''}`}
            onClick={() => setFilterStage(s)}
            style={{ borderColor: filterStage === s ? stageColors[s] : undefined }}
          >
            {stageLabels[s]}
          </button>
        ))}
      </div>

      {/* Pipeline board */}
      <div className="pipeline-board">
        {stageOrder.map(stage => (
          <div key={stage} className="pipeline-column" style={{ borderTopColor: stageColors[stage] }}>
            <div className="pipeline-col-header" style={{ color: stageColors[stage] }}>
              {stageLabels[stage]}
              <span className="col-count">{deals.filter(d => d.stage === stage).length}</span>
            </div>
            <div className="col-deals">
              {deals
                .filter(d => d.stage === stage && (filterStage === 'all' || d.stage === filterStage))
                .map(deal => (
                  <div
                    key={deal.id}
                    className={`deal-card ${selectedDeal?.id === deal.id ? 'selected' : ''}`}
                    onClick={() => setSelectedDeal(selectedDeal?.id === deal.id ? null : deal)}
                    style={{ borderLeftColor: stageColors[deal.stage] }}
                  >
                    <div className="deal-flag">{countryFlags[deal.country] || '🌍'}</div>
                    <div className="deal-buyer">{deal.buyer}</div>
                    <div className="deal-origin">{deal.origin} · {deal.grade}</div>
                    <div className="deal-vol">{deal.volumeKg.toLocaleString()} kg</div>
                    <div className="deal-rev">${deal.revenue.toLocaleString()}</div>
                    <div className="deal-prob">
                      <div className="prob-bar-bg">
                        <div className="prob-bar-fill" style={{ width: `${deal.probability}%`, background: stageColors[deal.stage] }} />
                      </div>
                      <span>{deal.probability}%</span>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>

      {/* Deal detail panel */}
      {selectedDeal && (
        <div className="deal-detail-panel">
          <div className="ddp-header">
            <span className="ddp-flag">{countryFlags[selectedDeal.country]}</span>
            <div>
              <div className="ddp-buyer">{selectedDeal.buyer}</div>
              <div className="ddp-contact">{selectedDeal.contact}</div>
            </div>
            <button className="ddp-close" onClick={() => setSelectedDeal(null)}>✕</button>
          </div>
          <div className="ddp-grid">
            <div className="ddp-field"><span>Origin</span><strong>{selectedDeal.origin}</strong></div>
            <div className="ddp-field"><span>Grade</span><strong>{selectedDeal.grade}</strong></div>
            <div className="ddp-field"><span>Volume</span><strong>{selectedDeal.volumeKg.toLocaleString()} kg</strong></div>
            <div className="ddp-field"><span>Price/kg</span><strong>${selectedDeal.pricePerKg.toFixed(2)}</strong></div>
            <div className="ddp-field"><span>Revenue</span><strong style={{ color: '#d4a017' }}>${selectedDeal.revenue.toLocaleString()}</strong></div>
            <div className="ddp-field"><span>Probability</span><strong>{selectedDeal.probability}%</strong></div>
            <div className="ddp-field"><span>Last Contact</span><strong>{selectedDeal.lastContact}</strong></div>
            <div className="ddp-field"><span>Stage</span><strong style={{ color: stageColors[selectedDeal.stage] }}>{stageLabels[selectedDeal.stage]}</strong></div>
          </div>
          <div className="ddp-notes">
            <div className="ddp-notes-label">📝 NOTES</div>
            <div className="ddp-notes-text">{selectedDeal.notes}</div>
          </div>
          <div className="ddp-actions">
            <button className="ddp-action primary">📧 Log Contact</button>
            <button className="ddp-action">📋 Create Task</button>
          </div>
        </div>
      )}
    </div>
  );
}
