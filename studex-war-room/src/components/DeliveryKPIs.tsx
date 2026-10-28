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

interface ShopifyOrder {
  id: number;
  name: string;
  email: string;
  created_at: string;
  total_price: string;
  financial_status: string;
  fulfillment_status: string | null;
  line_items: { title: string; quantity: number; price: string }[];
  shipping_address: { address1: string; city: string; province: string } | null;
  source: 'shopify';
}

const statusConfig: Record<string, { label: string; color: string; icon: string }> = {
  pending:     { label: 'PENDING',     color: '#7a8099', icon: '⏳' },
  processing:  { label: 'PROCESSING', color: '#ffaa44', icon: '⚙️' },
  dispatched:  { label: 'DISPATCHED', color: '#4a9eff', icon: '🚚' },
  delivered:   { label: 'DELIVERED',  color: '#4aff88', icon: '✅' },
  cancelled:   { label: 'CANCELLED',  color: '#ff4444', icon: '❌' },
};

const sourceIcons: Record<string, string> = {
  shopify:    '🛒',
  whatsapp:   '💬',
  instagram:  '📸',
};

const FINANCIAL_TO_STATUS: Record<string, DeliveryOrder['status']> = {
  paid:         'processing',
  pending:      'pending',
  refunded:     'cancelled',
  voided:       'cancelled',
};

const FULFILLMENT_TO_STATUS: Record<string, DeliveryOrder['status']> = {
  partial:     'dispatched',
  fulfilled:   'delivered',
};

function mapShopifyOrder(order: ShopifyOrder): DeliveryOrder {
  let status: DeliveryOrder['status'] = FINANCIAL_TO_STATUS[order.financial_status] ?? 'pending';
  if (order.fulfillment_status && FULFILLMENT_TO_STATUS[order.fulfillment_status]) {
    status = FULFILLMENT_TO_STATUS[order.fulfillment_status];
  }
  const products = order.line_items.map(li => `${li.quantity}x ${li.title}`).join(' + ');
  const addr = order.shipping_address;
  const address = addr ? `${addr.city}, ${addr.province}` : '—';
  const eta = status === 'pending' || status === 'processing'
    ? new Date(Date.now() + 2 * 86400000).toLocaleDateString('en-ZA', { day: '2-digit', month: 'short' })
    : status === 'dispatched'
    ? new Date(Date.now() + 1 * 86400000).toLocaleDateString('en-ZA', { day: '2-digit', month: 'short' })
    : '—';

  return {
    id: order.name.replace('#', 'ORD-'),
    customer: order.email?.split('@')[0] ?? 'Guest',
    product: products || 'Order',
    value: Math.round(parseFloat(order.total_price) || 0),
    status,
    date: new Date(order.created_at).toLocaleDateString('en-ZA', { day: '2-digit', month: 'short', year: 'numeric' }),
    eta,
    address,
    source: 'shopify',
  };
}

const MOCK_ORDERS: DeliveryOrder[] = [
  { id: 'ORD-001', customer: 'Thabo M.', product: 'Wagyu Ribeye 500g + Biltong 250g', value: 780, status: 'dispatched', date: '2026-08-15', eta: '2026-08-18', address: 'Sandton, JHB', source: 'instagram' },
  { id: 'ORD-002', customer: 'Lerato K.', product: 'Karoo Lamb Chops 1kg', value: 420, status: 'processing', date: '2026-08-16', eta: '2026-08-19', address: 'Rosebank, JHB', source: 'whatsapp' },
  { id: 'ORD-003', customer: 'Johan S.', product: 'Premium Beef Sampler Box', value: 1250, status: 'pending', date: '2026-08-17', eta: '2026-08-20', address: 'Pretoria East', source: 'shopify' },
  { id: 'ORD-004', customer: 'Priya N.', product: 'Biltong + Droëwors Combo', value: 340, status: 'delivered', date: '2026-08-14', eta: '2026-08-15', address: 'Four Ways, JHB', source: 'instagram' },
  { id: 'ORD-005', customer: 'David R.', product: 'Wagyu Burger Patties 8pc', value: 560, status: 'cancelled', date: '2026-08-13', eta: '—', address: 'Midrand', source: 'whatsapp' },
  { id: 'ORD-006', customer: 'Sophie L.', product: 'Dry-Aged T-Bone 1.2kg', value: 890, status: 'dispatched', date: '2026-08-16', eta: '2026-08-18', address: 'Umhlanga, KZN', source: 'shopify' },
  { id: 'ORD-007', customer: 'Mike B.', product: 'Biltong Sampler — 3 pack', value: 299, status: 'pending', date: '2026-08-17', eta: '2026-08-21', address: 'Centurion, PTA', source: 'instagram' },
];

function getSASTDate(): string {
  const now = new Date();
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const saTime = new Date(utc + 2 * 60 * 60 * 1000);
  return saTime.toLocaleDateString('en-ZA', { day: '2-digit', month: 'short', year: 'numeric' });
}

async function fetchShopifyOrders(): Promise<DeliveryOrder[]> {
  // The Shopify Admin token is NEVER read in the browser - Vite would inline it
  // into the bundle. Orders come from a same-origin proxy route that holds the
  // token (same shape as the lead proxy).
  const proxy = import.meta.env.VITE_SHOPIFY_PROXY_URL as string | undefined;
  if (!proxy) throw new Error('Shopify proxy not configured (VITE_SHOPIFY_PROXY_URL)');

  const url = `${proxy.replace(/\/+$/, '')}/orders?status=any&limit=50`;
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (!res.ok) throw new Error(`Shopify API ${res.status}`);
  const data = await res.json();
  return (data.orders || []).map(mapShopifyOrder);
}

export default function DeliveryKPIs() {
  const [orders, setOrders] = useState<DeliveryOrder[]>(MOCK_ORDERS);
  const [shopifyStatus, setShopifyStatus] = useState<'loading' | 'live' | 'mock' | 'error'>('loading');
  const [today] = useState(getSASTDate());
  const [lastRefresh, setLastRefresh] = useState<string>(today);

  useEffect(() => {
    if (!import.meta.env.VITE_SHOPIFY_PROXY_URL) {
      setShopifyStatus('mock');
      return;
    }

    fetchShopifyOrders()
      .then(shopifyOrders => {
        const merged = [...shopifyOrders];
        setOrders(shopifyOrders.length > 0 ? shopifyOrders : MOCK_ORDERS);
        setShopifyStatus(shopifyOrders.length > 0 ? 'live' : 'mock');
        setLastRefresh(new Date().toLocaleTimeString('en-ZA', { hour: '2-digit', minute: '2-digit' }));
      })
      .catch(() => {
        setShopifyStatus('error');
      });
  }, []);

  const activeOrders   = orders.filter(o => o.status !== 'delivered' && o.status !== 'cancelled');
  const totalValue     = orders.reduce((s, o) => s + o.value, 0);
  const deliveredCount = orders.filter(o => o.status === 'delivered').length;
  const avgOrderValue  = Math.round(totalValue / orders.filter(o => o.status !== 'cancelled').length);
  const cancelRate     = Math.round((orders.filter(o => o.status === 'cancelled').length / orders.length) * 100);
  const shopifyCount   = orders.filter(o => o.source === 'shopify').length;

  const shopifyBadge = {
    loading: { label: 'CONNECTING...', color: '#7a8099' },
    live:    { label: '🟢 LIVE',     color: '#4aff88' },
    mock:    { label: '⚠️ MOCK DATA', color: '#ffaa44' },
    error:   { label: '❌ API ERROR', color: '#ff4444' },
  }[shopifyStatus];

  return (
    <div className="delivery-kpis">
      <div className="dkpi-header">
        <div className="dkpi-title">📦 DELIVERY &amp; ORDER KPIs</div>
        <div className="dkpi-date">{today} {lastRefresh && <span className="dkpi-refresh">↻ {lastRefresh}</span>}</div>
      </div>

      {/* Shopify status banner */}
      <div className="shopify-status-banner" style={{ borderColor: shopifyBadge.color, color: shopifyBadge.color }}>
        SHOPIFY ORDERS: {shopifyBadge.label} · {shopifyCount}/{orders.length} orders from Shopify
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
          <div className="dkpi-val" style={{ color: '#4aff88' }}>{deliveredCount}</div>
          <div className="dkpi-lbl">DELIVERED</div>
          <div className="dkpi-sub">completed</div>
        </div>
        <div className="dkpi-card">
          <div className="dkpi-val" style={{ color: '#d4a017' }}>R{avgOrderValue}</div>
          <div className="dkpi-lbl">AVG ORDER</div>
          <div className="dkpi-sub">value</div>
        </div>
        <div className="dkpi-card">
          <div className="dkpi-val" style={{ color: cancelRate > 10 ? '#ff4444' : '#ff6eb4' }}>{cancelRate}%</div>
          <div className="dkpi-lbl">CANCEL RATE</div>
          <div className="dkpi-sub">review needed</div>
        </div>
        <div className="dkpi-card">
          <div className="dkpi-val" style={{ color: shopifyBadge.color }}>{shopifyCount}</div>
          <div className="dkpi-lbl">SHOPIFY</div>
          <div className="dkpi-sub">orders</div>
        </div>
      </div>

      {/* Order Table */}
      <div className="order-table-wrap">
        <div className="order-table-header">LIVE ORDER TRACKER</div>
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
