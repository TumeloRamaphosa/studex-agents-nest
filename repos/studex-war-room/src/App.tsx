import { useState } from 'react'

// ─── Types ───────────────────────────────────────────────────────────────────
type AgentStatus = 'online' | 'idle' | 'busy' | 'offline'
type OrderStatus = 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled'

interface Agent {
  id: string
  name: string
  role: string
  email: string
  status: AgentStatus
  lastActive: string
  tasks: number
  avatar: string
}

interface Order {
  id: string
  customer: string
  product: string
  amount: number
  status: OrderStatus
  date: string
  tracking?: string
}

interface CoffeeLead {
  company: string
  contact: string
  type: 'hotel' | 'office' | 'export' | '意向'
  stage: 'cold' | 'warm' | 'hot' | 'contract'
  notes: string
  lastContact: string
}

// ─── Data ────────────────────────────────────────────────────────────────────
const agents: Agent[] = [
  { id: 'charlie', name: 'Charlie', role: 'COO Orchestrator', email: 'charlie@agent.studexmeat.com', status: 'online', lastActive: '2 min ago', tasks: 4, avatar: '🎯' },
  { id: 'naledi', name: 'Naledi', role: 'CMO — Content & Social', email: 'naledi@agent.studexmeat.com', status: 'busy', lastActive: 'just now', tasks: 7, avatar: '📣' },
  { id: 'robusca', name: 'Robusca', role: 'CEO — Vision & Strategy', email: 'ceo@agent.studexmeat.com', status: 'online', lastActive: 'just now', tasks: 12, avatar: '👑' },
]

const orders: Order[] = [
  { id: '#1047', customer: 'Istanbul Restaurant', product: 'Vacuum-packed beef (5kg)', amount: 4200, status: 'shipped', date: '2026-07-14', tracking: 'DPSAF001' },
  { id: '#1048', customer: 'Marble Beef Co.', product: 'Dry-aged T-bone (10kg)', amount: 6800, status: 'processing', date: '2026-07-15' },
  { id: '#1049', customer: 'Chef Nkosi', product: 'Beef short ribs (bulk)', amount: 3100, status: 'pending', date: '2026-07-16' },
  { id: '#1050', customer: 'Steakhouse JV', product: 'Mixed cuts trial box', amount: 2200, status: 'delivered', date: '2026-07-12' },
  { id: '#1051', customer: 'LeboWholesale', product: 'Frozen beef patties (200 units)', amount: 5600, status: 'shipped', date: '2026-07-13', tracking: 'DPSAF002' },
]

const coffeeLeads: CoffeeLead[] = [
  { company: 'Luckin Coffee', contact: 'Buyer — China ops', type: 'export', stage: 'hot', notes: 'Interested in Rwanda A1/A2. Awaiting FOB pricing.', lastContact: '2026-07-15' },
  { company: 'Tsogo Sun Hotels', contact: 'Procurement dept', type: 'hotel', stage: 'warm', notes: 'Sent intro email. No response yet.', lastContact: '2026-07-10' },
  { company: 'Tim Hortons China', contact: 'Via trade intermediary', type: 'export', stage: 'warm', notes: 'Intermediary confirmed Chinese-palate floral profile interest.', lastContact: '2026-07-12' },
  { company: 'City Lodge Group', contact: 'F&B Manager', type: 'hotel', stage: 'cold', notes: 'Will contact after CIIE registration.', lastContact: '2026-07-08' },
  { company: 'CIIE 2026 Booth', contact: 'Registration pending', type: '意向', stage: 'warm', notes: 'DEADLINE AUG 31. Must register before then.', lastContact: '2026-07-16' },
  { company: 'Southern Sun', contact: 'Group chef', type: 'hotel', stage: 'cold', notes: 'Target after hotel reference account established.', lastContact: '2026-07-01' },
]

// ─── Components ─────────────────────────────────────────────────────────────
const STATUS_COLORS: Record<AgentStatus, string> = {
  online: 'bg-green-500',
  idle: 'bg-yellow-500',
  busy: 'bg-orange-500',
  offline: 'bg-gray-500',
}

const STATUS_TEXT: Record<AgentStatus, string> = {
  online: 'Online',
  idle: 'Idle',
  busy: 'Busy',
  offline: 'Offline',
}

const ORDER_STAGE_COLORS: Record<OrderStatus, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  processing: 'bg-blue-100 text-blue-800',
  shipped: 'bg-purple-100 text-purple-800',
  delivered: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
}

const PIPELINE_COLORS: Record<string, string> = {
  cold: 'bg-gray-100 text-gray-600',
  warm: 'bg-blue-100 text-blue-700',
  hot: 'bg-orange-100 text-orange-700',
  contract: 'bg-green-100 text-green-800',
}

function AgentDock() {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-gray-900">🤖 Agent NPC Dock</h2>
        <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
          {agents.filter(a => a.status === 'online').length} active
        </span>
      </div>
      <div className="space-y-3">
        {agents.map(agent => (
          <div key={agent.id} className="bg-white border border-gray-200 rounded-xl p-4 flex items-center gap-4 shadow-sm hover:shadow-md transition-shadow">
            <div className="text-3xl">{agent.avatar}</div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-900">{agent.name}</span>
                <span className={`w-2 h-2 rounded-full ${STATUS_COLORS[agent.status]} inline-block`} />
                <span className="text-xs text-gray-500">{STATUS_TEXT[agent.status]}</span>
              </div>
              <div className="text-xs text-gray-500 mt-0.5">{agent.role}</div>
              <div className="text-xs text-gray-400 mt-0.5 truncate">{agent.email}</div>
            </div>
            <div className="text-right flex-shrink-0">
              <div className="text-xs font-medium text-gray-700">{agent.tasks} tasks</div>
              <div className="text-xs text-gray-400 mt-0.5">{agent.lastActive}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4 bg-blue-50 border border-blue-200 rounded-xl p-3">
        <div className="text-xs text-blue-700 font-medium mb-1">📌 AgentMail Status</div>
        <div className="text-xs text-blue-600 space-y-0.5">
          <div>• charlie@agent.studexmeat.com — <span className="text-yellow-600">Setup pending</span></div>
          <div>• naledi@agent.studexmeat.com — <span className="text-yellow-600">Setup pending</span></div>
          <div>• ceo@agent.studexmeat.com — <span className="text-yellow-600">Setup pending</span></div>
          <div className="text-xs mt-1 text-blue-500">→ Fix: AgentMail DNS missing — send.studexmeat.com INVALID</div>
        </div>
      </div>
    </div>
  )
}

function DeliveryKPIs() {
  const total = orders.length
  const delivered = orders.filter(o => o.status === 'delivered').length
  const shipped = orders.filter(o => o.status === 'shipped').length
  const revenue = orders.reduce((sum, o) => sum + o.amount, 0)
  const avgOrder = revenue / total

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold text-gray-900">📦 Delivery KPIs</h2>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
          <div className="text-2xl font-bold text-gray-900">{total}</div>
          <div className="text-xs text-gray-500 mt-1">Total Orders</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
          <div className="text-2xl font-bold text-green-600">{delivered}</div>
          <div className="text-xs text-gray-500 mt-1">Delivered</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
          <div className="text-2xl font-bold text-purple-600">{shipped}</div>
          <div className="text-xs text-gray-500 mt-1">In Transit</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
          <div className="text-2xl font-bold text-gray-900">R{avgOrder.toLocaleString('en-ZA', { maximumFractionDigits: 0 })}</div>
          <div className="text-xs text-gray-500 mt-1">Avg Order (ZAR)</div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
        <div className="text-sm font-semibold text-gray-700 mb-3">Recent Orders</div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-gray-400 border-b border-gray-100">
                <th className="text-left pb-2 font-medium">Order</th>
                <th className="text-left pb-2 font-medium">Customer</th>
                <th className="text-left pb-2 font-medium hidden md:table-cell">Product</th>
                <th className="text-right pb-2 font-medium">Amount</th>
                <th className="text-left pb-2 font-medium">Status</th>
                <th className="text-left pb-2 font-medium hidden sm:table-cell">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {orders.map(order => (
                <tr key={order.id} className="hover:bg-gray-50">
                  <td className="py-2 font-mono font-medium text-gray-800">{order.id}</td>
                  <td className="py-2 text-gray-700">{order.customer}</td>
                  <td className="py-2 text-gray-500 hidden md:table-cell">{order.product}</td>
                  <td className="py-2 text-right font-medium text-gray-800">R{order.amount.toLocaleString('en-ZA')}</td>
                  <td className="py-2">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${ORDER_STAGE_COLORS[order.status]}`}>
                      {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                    </span>
                  </td>
                  <td className="py-2 text-gray-400 hidden sm:table-cell">{order.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-3">
        <div className="text-xs text-yellow-700 font-medium mb-1">⚠️ Shopify API Blocker</div>
        <div className="text-xs text-yellow-600">Shopify Admin API token not yet configured. Orders above are sample data. Connect Shopify to enable live order sync.</div>
      </div>
    </div>
  )
}

function CoffeePipeline() {
  const stages = ['意向', 'hot', 'warm', 'cold']

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-gray-900">☕ Coffee Pipeline — Rwanda A1/A2</h2>
        <div className="flex gap-2">
          <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded-full font-bold">
            🔴 CIIE DEADLINE: AUG 31
          </span>
        </div>
      </div>

      {/* CIIE Banner */}
      <div className="bg-gradient-to-r from-red-600 to-red-700 rounded-xl p-4 text-white">
        <div className="flex items-start gap-3">
          <span className="text-2xl">🇨🇳</span>
          <div>
            <div className="font-bold text-base">CIIE 2026 — Shanghai, November 2026</div>
            <div className="text-red-100 text-xs mt-0.5">China International Import Expo — world's largest import expo</div>
            <div className="mt-2 bg-red-500/30 rounded-lg p-2 text-xs">
              <span className="font-semibold">Target buyers:</span> Luckin Coffee (28,000+ stores) · Tim Hortons China · Starbucks China
            </div>
            <div className="mt-2 text-xs text-red-100">
              📋 Protocol: SA green coffee → China effective <strong className="text-white">July 20, 2026 — LIVE NOW</strong>
            </div>
          </div>
        </div>
      </div>

      {/* Pricing Reference */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
          <div className="text-xs text-gray-500 uppercase tracking-wide">FOB Price (USD/kg)</div>
          <div className="text-xl font-bold text-gray-900 mt-1">$18–24</div>
          <div className="text-xs text-gray-400 mt-0.5">Rwanda A1 — lock in before prices rise</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
          <div className="text-xs text-gray-500 uppercase tracking-wide">SA Market (ZAR/kg)</div>
          <div className="text-xl font-bold text-gray-900 mt-1">R280–380</div>
          <div className="text-xs text-gray-400 mt-0.5">Hotels & restaurants — current</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
          <div className="text-xs text-gray-500 uppercase tracking-wide">China Target (RMB/kg)</div>
          <div className="text-xl font-bold text-orange-600 mt-1">¥220–280</div>
          <div className="text-xs text-gray-400 mt-0.5">Luckin / specialty — fob inbound</div>
        </div>
      </div>

      {/* Pipeline Board */}
      <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
        <div className="text-sm font-semibold text-gray-700 mb-3">Lead Pipeline</div>
        <div className="flex gap-2 overflow-x-auto pb-2">
          {stages.map(stage => {
            const leads = coffeeLeads.filter(l => l.stage === stage)
            return (
              <div key={stage} className="flex-shrink-0 w-48">
                <div className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2 flex items-center gap-1">
                  {stage === '意向' ? '🎯 意向' : stage.toUpperCase()}
                  <span className="bg-gray-100 text-gray-600 px-1.5 rounded text-xs">{leads.length}</span>
                </div>
                <div className="space-y-2">
                  {leads.map((lead, i) => (
                    <div key={i} className={`border rounded-lg p-2.5 text-xs ${PIPELINE_COLORS[lead.stage] || 'bg-gray-50'}`}>
                      <div className="font-semibold text-gray-900">{lead.company}</div>
                      <div className="text-gray-500 mt-0.5">{lead.contact}</div>
                      <div className="text-gray-400 mt-1 italic">"{lead.notes}"</div>
                      <div className="text-gray-400 mt-1 text-[10px]">Last: {lead.lastContact}</div>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Next Actions */}
      <div className="bg-gray-900 rounded-xl p-4 text-white">
        <div className="text-sm font-bold mb-3">🚀 Next Actions — Coffee Pipeline</div>
        <div className="space-y-2 text-xs">
          <div className="flex items-start gap-2">
            <span className="text-red-400 font-bold">1.</span>
            <span><strong className="text-white">Register CIIE booth</strong> — ciie.org — DEADLINE AUG 31. <span className="text-red-300">This week.</span></span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-red-400 font-bold">2.</span>
            <span><strong className="text-white">Lock Rwanda A1 FOB pricing</strong> — coffee prices at 10-year high globally. Price in USD now.</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-red-400 font-bold">3.</span>
            <span><strong className="text-white">Contact Luckin Coffee buyer</strong> — LinkedIn or trade intermediary. Rwanda origin story = differentiator.</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-red-400 font-bold">4.</span>
            <span><strong className="text-white">SA hotel outreach letter</strong> — Tsogo Sun, City Lodge, Southern Sun. Proof-of-concept before export.</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// ─── Blocker Banner ──────────────────────────────────────────────────────────
function BlockerBanner() {
  const blockers = [
    { text: 'Shopify Admin API token', owner: 'Tumelo' },
    { text: 'Meta permanent access token', owner: 'Tumelo' },
    { text: 'Orgo VM ID — VM needs reconnect', owner: 'Tumelo' },
    { text: 'AgentMail DNS — send.studexmeat.com INVALID', owner: 'Tumelo' },
    { text: 'Blotato OAuth — connect FB account', owner: 'Tumelo' },
  ]
  return (
    <div className="bg-red-50 border border-red-200 rounded-xl p-3">
      <div className="text-xs text-red-700 font-bold mb-2">🚫 {blockers.length} Blockers Blocking Builds</div>
      <div className="flex flex-wrap gap-1">
        {blockers.map((b, i) => (
          <span key={i} className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full">
            {b.text} <span className="text-red-400">({b.owner})</span>
          </span>
        ))}
      </div>
    </div>
  )
}

// ─── Main App ────────────────────────────────────────────────────────────────
type Tab = 'agents' | 'delivery' | 'coffee'

export default function App() {
  const [tab, setTab] = useState<Tab>('agents')

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Header */}
      <header className="bg-gray-900 text-white shadow-lg">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">🏗️</span>
              <div>
                <h1 className="text-xl font-black tracking-tight">STUDEX WAR ROOM</h1>
                <div className="text-xs text-gray-400">Studex Meat Co. — Operations Command Center</div>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-400">July 16, 2026</div>
            <div className="text-xs text-gray-400">Build Hour — Shipped by Robusca CEO 🤖</div>
          </div>
        </div>

        {/* Nav */}
        <div className="max-w-6xl mx-auto px-4">
          <nav className="flex gap-1">
            {([
              ['agents', '🤖', 'Agent Dock'],
              ['delivery', '📦', 'Delivery KPIs'],
              ['coffee', '☕', 'Coffee Pipeline'],
            ] as [Tab, string, string][]).map(([key, icon, label]) => (
              <button
                key={key}
                onClick={() => setTab(key)}
                className={`px-4 py-2 text-xs font-bold rounded-t-lg transition-colors ${
                  tab === key
                    ? 'bg-gray-800 text-white border-t-2 border-orange-500'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              >
                <span className="mr-1">{icon}</span>{label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-6xl mx-auto px-4 py-6 space-y-4">
        <BlockerBanner />

        {tab === 'agents' && <AgentDock />}
        {tab === 'delivery' && <DeliveryKPIs />}
        {tab === 'coffee' && <CoffeePipeline />}
      </main>

      <footer className="max-w-6xl mx-auto px-4 py-4 text-center">
        <p className="text-xs text-gray-400">
          Studex War Room · Built by Robusca CEO · {new Date().toLocaleDateString('en-ZA')}
        </p>
      </footer>
    </div>
  )
}
