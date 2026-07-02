// ─── Delivery Kanban Types ─────────────────────────────────────────────────

export type Priority = 'HIGH' | 'MED' | 'LOW';
export type Category = 'ORDERS' | 'CONTENT' | 'DNS' | 'SHOPIFY' | 'AGENTMAIL' | 'DISCORD' | 'OPS' | 'DELIVERY';

// ─── New Delivery Column IDs ────────────────────────────────────────────────

export type DeliveryColumnId =
  | 'order-intake'
  | 'packing'
  | 'dispatched'
  | 'delivered'
  | 'done'
  | 'cancelled';

// ─── Delivery Company ───────────────────────────────────────────────────────

export type DeliveryCompany = 'dinkoko' | 'mycourier';

export const DELIVERY_COMPANY_LABELS: Record<DeliveryCompany, string> = {
  dinkoko: '🐂 Dinkoko',
  mycourier: '📦 My Courier',
};

export const DELIVERY_COMPANY_COLORS: Record<DeliveryCompany, string> = {
  dinkoko: '#8B1A1A',
  mycourier: '#1e4d8c',
};

// ─── Memory Log ─────────────────────────────────────────────────────────────

export type MemoryEntry = {
  id: string;
  timestamp: string; // ISO
  actor: string;     // e.g. "🤖 Charlie", "👤 Tumelo"
  action: string;
};

// ─── Card ────────────────────────────────────────────────────────────────────

export interface Card {
  // --- existing fields (all preserved, now optional where needed) ---
  id: string;
  title: string;
  description: string;
  priority: Priority;
  dueDate: string;
  assignedAgent: string;
  category: Category;
  columnId: string; // DeliveryColumnId
  createdAt: string;

  // --- new delivery fields (all optional for backward compat) ---
  deliveryCompany?: DeliveryCompany | null;
  driverName?: string;
  driverPhone?: string;
  eta?: string;           // ISO timestamp
  customerAddress?: string;
  orderItems?: string[];
  whatsappGroupThread?: string;
  memoryLog?: MemoryEntry[];
  lastUpdatedBy?: string;
  lastUpdatedAt?: string;
}

// ─── Column ──────────────────────────────────────────────────────────────────

export interface Column {
  id: DeliveryColumnId;
  title: string;
  color: string;
  emoji: string;
}

export const COLUMNS: Column[] = [
  { id: 'order-intake',  title: 'NEW ORDER',    emoji: '📥', color: '#92400e' },
  { id: 'packing',      title: 'PACKING',      emoji: '📦', color: '#6d28d9' },
  { id: 'dispatched',   title: 'DISPATCHED',   emoji: '🚚', color: '#1e4d8c' },
  { id: 'delivered',    title: 'DELIVERED',    emoji: '🏁', color: '#14532d' },
  { id: 'done',         title: 'COMPLETE',     emoji: '✅', color: '#374151' },
  { id: 'cancelled',    title: 'CANCELLED',    emoji: '🔴', color: '#7f1d1d' },
];

// ─── Column helpers ──────────────────────────────────────────────────────────

export const COLUMN_MAP = Object.fromEntries(COLUMNS.map(c => [c.id, c]));

export const COLUMN_ORDER: DeliveryColumnId[] = [
  'order-intake', 'packing', 'dispatched', 'delivered', 'done', 'cancelled',
];

// Valid forward transitions (any → cancelled always allowed)
export const VALID_TRANSITIONS: Record<DeliveryColumnId, DeliveryColumnId[]> = {
  'order-intake':  ['packing',     'cancelled'],
  'packing':       ['dispatched',  'cancelled'],
  'dispatched':    ['delivered',   'cancelled'],
  'delivered':     ['done',        'cancelled'],
  'done':          ['cancelled'],
  'cancelled':     [],
};

export function isValidTransition(from: DeliveryColumnId, to: DeliveryColumnId): boolean {
  if (to === 'cancelled') return true;
  return VALID_TRANSITIONS[from]?.includes(to) ?? false;
}

// ─── Priority ────────────────────────────────────────────────────────────────

export const PRIORITY_COLORS: Record<Priority, string> = {
  HIGH: '#ef4444',
  MED:  '#f59e0b',
  LOW:  '#22c55e',
};

// ─── Teams ───────────────────────────────────────────────────────────────────

export const CATEGORIES: Category[] = [
  'ORDERS', 'CONTENT', 'DNS', 'SHOPIFY', 'AGENTMAIL', 'DISCORD', 'OPS', 'DELIVERY',
];

export const AGENTS = ['Robusca (CEO)', 'Naledi (CMO)', 'Charlie', 'Delivery Agent'];

// ─── Default cards ────────────────────────────────────────────────────────────

function makeLog(actor: string, action: string, hoursAgo: number): import('./types').MemoryEntry {
  const t = new Date(Date.now() - hoursAgo * 3600_000).toISOString();
  return { id: `log-${Math.random().toString(36).slice(2)}`, timestamp: t, actor, action };
}

export const DEFAULT_CARDS: Card[] = [
  {
    id: 'c1',
    title: '#STX-0041 — Mahlakoane Family',
    description: 'Mixed bone-in steaks + wors. Suburban JHB delivery.',
    priority: 'HIGH',
    dueDate: '',
    assignedAgent: 'Charlie',
    category: 'DELIVERY',
    columnId: 'order-intake',
    createdAt: new Date(Date.now() - 2 * 3600_000).toISOString(),
    deliveryCompany: 'dinkoko',
    driverName: 'Derrick Selepe',
    driverPhone: '+27 67 681 3076',
    eta: new Date(Date.now() + 3 * 3600_000).toISOString(),
    customerAddress: '14 Birch Ave, Senderwood, Bedfordview, Johannesburg, 2007',
    orderItems: ['2x Bone-in T-Bone (500g)', '1x Beef Wors (1kg)', '1x Marinated Chilli Bites (400g)'],
    whatsappGroupThread: 'Dinkoko Derrick — StudEx Deliveries',
    memoryLog: [
      makeLog('🤖 Charlie',        'Order received from Shopify. Assigned to Dinkoko.',         2.0),
      makeLog('🤖 Charlie',        'WhatsApp sent to Derrick (Dinkoko). Awaiting pickup slot.',  1.7),
      makeLog('👤 Tumelo',         'Customer requested delivery before 13:00.',                  0.5),
    ],
    lastUpdatedBy: '👤 Tumelo',
    lastUpdatedAt: new Date(Date.now() - 0.5 * 3600_000).toISOString(),
  },
  {
    id: 'c2',
    title: '#STX-0042 — Mokoena Braai Pack',
    description: 'Bulk braai pack for weekend event. Needs extra ice.',
    priority: 'MED',
    dueDate: '',
    assignedAgent: 'Charlie',
    category: 'DELIVERY',
    columnId: 'packing',
    createdAt: new Date(Date.now() - 4 * 3600_000).toISOString(),
    deliveryCompany: 'mycourier',
    driverName: 'Willy',
    driverPhone: '+27 61 362 3448',
    eta: new Date(Date.now() + 1.5 * 3600_000).toISOString(),
    customerAddress: '88 Oak Street, Norwood, Johannesburg, 2192',
    orderItems: ['5kg Braai Pack (mixed cuts)', '2x 2L Ice', '1x BBQ Sauce (500ml)'],
    whatsappGroupThread: '',
    memoryLog: [
      makeLog('🤖 Charlie',        'Order confirmed. Routing to My Courier (JHB metro).',        4.0),
      makeLog('🤖 Charlie',        'Packing list sent to warehouse team.',                        3.5),
      makeLog('👤 Tumelo',         'Added extra ice — customer braaiing 40 ppl.',                 3.0),
    ],
    lastUpdatedBy: '👤 Tumelo',
    lastUpdatedAt: new Date(Date.now() - 3 * 3600_000).toISOString(),
  },
  {
    id: 'c3',
    title: '#STX-0039 — Van der Merwe Bulk Order',
    description: 'Corporate catering — 12 trays mixed grill.',
    priority: 'HIGH',
    dueDate: '',
    assignedAgent: 'Delivery Agent',
    category: 'DELIVERY',
    columnId: 'dispatched',
    createdAt: new Date(Date.now() - 6 * 3600_000).toISOString(),
    deliveryCompany: 'dinkoko',
    driverName: 'Derrick Selepe',
    driverPhone: '+27 67 681 3076',
    eta: new Date(Date.now() + 0.4 * 3600_000).toISOString(),
    customerAddress: 'Blue Valley Golf Estate, R82, Centurion, 0157',
    orderItems: [
      '4x Beef Chuck Tray', '4x Lamb Shoulder Tray', '4x Boerewors Tray',
      '12x Chakalaka Portions', '12x Pap Portions',
    ],
    whatsappGroupThread: 'Dinkoko Derrick — StudEx Deliveries',
    memoryLog: [
      makeLog('🤖 Charlie',        'Bulk order flagged — priority routing to Dinkoko.',          6.0),
      makeLog('🤖 Charlie',        'Client confirmed delivery address at golf estate gate.',      5.5),
      makeLog('🤖 Charlie',        'Driver Derrick dispatched. ETA: 11:10 SAST.',               3.0),
      makeLog('👤 Tumelo',         'Client wants unloading help — confirmed.',                    2.0),
      makeLog('🤖 Charlie',        'Driver on route. ETA updated via Maps.',                     1.0),
    ],
    lastUpdatedBy: '🤖 Charlie',
    lastUpdatedAt: new Date(Date.now() - 1 * 3600_000).toISOString(),
  },
  {
    id: 'c4',
    title: '#STX-0038 — Ntuli Weekend Order',
    description: 'Standard weekend meat pack. Customer prepaid.',
    priority: 'LOW',
    dueDate: '',
    assignedAgent: 'Charlie',
    category: 'DELIVERY',
    columnId: 'delivered',
    createdAt: new Date(Date.now() - 8 * 3600_000).toISOString(),
    deliveryCompany: 'mycourier',
    driverName: 'Willy',
    driverPhone: '+27 61 362 3448',
    eta: new Date(Date.now() - 2 * 3600_000).toISOString(),
    customerAddress: '32 Kritzinger St, Springs, Gauteng, 1559',
    orderItems: ['1x Premium Beef Pack (3kg)', '1x Chicken Wings (2kg)'],
    whatsappGroupThread: '',
    memoryLog: [
      makeLog('🤖 Charlie',        'Order received.',                                            8.0),
      makeLog('🤖 Charlie',        'My Courier assigned (Springs metro route).',                7.5),
      makeLog('🤖 Charlie',        'Picked up by Willy.',                                        5.0),
      makeLog('🤖 Charlie',        'Delivered. Client sent WhatsApp thumbs-up ✅.',               2.0),
    ],
    lastUpdatedBy: '🤖 Charlie',
    lastUpdatedAt: new Date(Date.now() - 2 * 3600_000).toISOString(),
  },
  {
    id: 'c5',
    title: '#STX-0037 — Reddy Family Restock',
    description: 'Monthly restock. Repeat customer — 10% loyalty applied.',
    priority: 'MED',
    dueDate: '',
    assignedAgent: 'Charlie',
    category: 'DELIVERY',
    columnId: 'done',
    createdAt: new Date(Date.now() - 26 * 3600_000).toISOString(),
    deliveryCompany: 'dinkoko',
    driverName: 'Derrick Selepe',
    driverPhone: '+27 67 681 3076',
    eta: new Date(Date.now() - 22 * 3600_000).toISOString(),
    customerAddress: '7 Willowbrook, Buccleuch, Sandton, 2090',
    orderItems: ['2x Lamb Chops (1kg)', '1x Beef Mince (2kg)', '1x Pork Belly (1kg)'],
    whatsappGroupThread: 'Dinkoko Derrick — StudEx Deliveries',
    memoryLog: [
      makeLog('🤖 Charlie',        'Monthly restock order received. Loyalty discount applied.',  26.0),
      makeLog('🤖 Charlie',        'Delivered. Client happy — left 5-star review on website.',   22.0),
      makeLog('🤖 Charlie',        'Card moved to Done.',                                         1.0),
    ],
    lastUpdatedBy: '🤖 Charlie',
    lastUpdatedAt: new Date(Date.now() - 1 * 3600_000).toISOString(),
  },
];
