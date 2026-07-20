import { useState, useEffect } from 'react';

interface DeliveryOrder {
  id: string;
  customer: string;
  product: string;
  value: number;
  status: 'pending' | 'processing' | 'dispatched' | 'delivered' | 'cancelled';
  date: string;
  eta: string;
  address: string;
  source: 'shopify' | 'whatsapp' | 'instagram';
}

const mockOrders: DeliveryOrder[] = [
  { id: 'ORD-001', customer: 'Thabo M.', product: 'Wagyu Ribeye 500g + Biltong 250g', value: 780, status: 'dispatched', date: '2026-06-28', eta: '2026-06-29', address: 'Sandton, JHB', source: 'instagram' },
  { id: 'ORD-002', customer: 'Lerato K.', product: 'Karoo Lamb Chops 1kg', value: 420, status: 'processing', date: '2026-06-28', eta: '2026-06-30', address: 'Rosebank, JHB', source: 'whatsapp' },
  { id: 'ORD-003', customer: 'Johan S.', product: 'Premium Beef Sampler Box', value: 1250, status: 'pending', date: '2026-06-28', eta: '2026-07-01', address: 'Pretoria East', source: 'shopify' },
  { id: 'ORD-004', customer: 'Priya N.', product: 'Biltong + Droëwors Combo', value: 340, status: 'delivered', date: '2026-06-26', eta: '2026-06-27', address: 'Four Ways, JHB', source: 'instagram' },
  { id: 'ORD-005', customer: 'David R.', product: 'Wagyu Burger Patties 8pc', value: 560, status: 'cancelled', date: '2026-06-27', eta: '—', address: 'Midrand', source: 'whatsapp' },
];

const statusConfig: Record<string, { label: string; color: string; icon: string }> = {
  pending: { label: 'PENDING', color: '#7a8099', icon: '⏳' },
  processing: { label: 'PROCESSING', color: '#ffaa44', icon: '⚙️' },
  dispatched: { label: 'DISPATCHED', color: '#4a9eff', icon: '🚚' },
  delivered: { label: 'DELIVERED', color: '#4aff88', icon: '✅' },
  cancelled: { label: 'CANCELLED', color: '#ff4444', icon: '❌' },
};

const sourceIcons: Record<string, string> = {
  shopify: '🛒',
  whatsapp: '💬',
  instagram: '📸',
};

function getSASTDate(): string {
  const now = new Date();
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const saTime = new Date(utc + 2 * 60 * 60 * 1000);
  return saTime.toLocaleDateString('en-ZA', { day: '2-digit', month: 'short', year: 'numeric' });
}

export default function DeliveryKPIs() {
  const [orders] = useState<DeliveryOrder[]>(mockOrders);
  const [today] = useState(getSASTDate());

  const activeOrders = orders.filter(o => o.status !== 'delivered' && o.status !== 'cancelled');
  const totalValue = orders.reduce((s, o) => s + o.value, 0);
  const deliveredToday = orders.filter(o => o.status === 'delivered').length;
  const avgOrderValue = Math.round(totalValue / orders.filter(o => o.status !== 'cancelled').length);
  const cancellationRate = Math.round((orders.filter(o => o.status === 'cancelled').length / orders.length) * 100);

  return (
    <div className="delivery-kpis">
      <div className="dkpi-header">
        <div className="dkpi-title">📦 DELIVERY & ORDER KPIs</div>
        <div className="dkpi-date">{today}</div>
      </div>

      {/* KPI Cards */}
      <div className="dkpi-grid">
        <div className="dkpi-card">
          <div className="dkpi-val" style={{ color: '#4a9eff' }}>{activeOrders.length}</div>
          <div className="dkpi-lbl">ACTIVE ORDERS</div>
          <div className="dkpi-sub">in pipeline</div>
        </div>
        <div className="dkpi-card">
          <div className="dkpi-val" style={{ color: '#d4a017' }}>R{totalValue.toLocaleString()}</div>
          <div className="dkpi-lbl">TOTAL VALUE</div>
          <div className="dkpi-sub">all orders</div>
        </div>
        <div className="dkpi-card">
          <div className="dkpi-val" style={{ color: '#4aff88' }}>{deliveredToday}</div>
          <div className="dkpi-lbl">DELIVERED</div>
          <div className="dkpi-sub">completed</div>
        </div>
        <div className="dkpi-card">
          <div className="dkpi-val" style={{ color: '#d4a017' }}>R{avgOrderValue}</div>
          <div className="dkpi-lbl">AVG ORDER</div>
          <div className="dkpi-sub">value</div>
        </div>
        <div className="dkpi-card">
          <div className="dkpi-val" style={{ color: '#ff6eb4' }}>{cancellationRate}%</div>
          <div className="dkpi-lbl">CANCEL RATE</div>
          <div className="dkpi-sub">review needed</div>
        </div>
        <div className="dkpi-card">
          <div className="dkpi-val" style={{ color: '#ffaa44' }}>0</div>
          <div className="dkpi-lbl">SHOPIFY</div>
          <div className="dkpi-sub" style={{ color: '#ff4444' }}>⚠ API blocked</div>
        </div>
      </div>

      {/* Order Table */}
      <div className="order-table-wrap">
        <div className="order-table-header">ORDER TRACKER</div>
        <table className="order-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>CUSTOMER</th>
              <th>PRODUCT</th>
              <th>SOURCE</th>
              <th>VALUE</th>
              <th>STATUS</th>
              <th>ETA</th>
            </tr>
          </thead>
          <tbody>
            {orders.map(o => {
              const cfg = statusConfig[o.status];
              return (
                <tr key={o.id} className={o.status === 'cancelled' ? 'row-cancelled' : ''}>
                  <td className="td-id">{o.id}</td>
                  <td>{o.customer}</td>
                  <td className="td-product">{o.product}</td>
                  <td>{sourceIcons[o.source]} {o.source}</td>
                  <td className="td-value">R{o.value}</td>
                  <td>
                    <span className="order-status-badge" style={{ color: cfg.color, borderColor: cfg.color }}>
                      {cfg.icon} {cfg.label}
                    </span>
                  </td>
                  <td className="td-eta">{o.eta}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Source breakdown */}
      <div className="source-breakdown">
        <div className="sb-label">ORDER SOURCES</div>
        <div className="sb-items">
          {(['shopify', 'whatsapp', 'instagram'] as const).map(src => {
            const count = orders.filter(o => o.source === src).length;
            const pct = Math.round((count / orders.length) * 100);
            return (
              <div key={src} className="sb-item">
                <span className="sb-icon">{sourceIcons[src]}</span>
                <span className="sb-src">{src}</span>
                <div className="sb-bar-bg"><div className="sb-bar-fill" style={{ width: `${pct}%` }} /></div>
                <span className="sb-pct">{count} ({pct}%)</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
