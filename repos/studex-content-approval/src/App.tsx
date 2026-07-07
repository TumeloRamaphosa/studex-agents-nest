import { useState } from 'react'

export type ContentStatus = 'pending' | 'approved' | 'rejected'
export type Platform = 'TikTok' | 'Instagram' | 'Facebook' | 'YouTube' | 'LinkedIn' | 'X' | 'Threads' | 'All'
export type Format = 'IMAGE' | 'VIDEO' | 'CAROUSEL' | 'STORY' | 'REELS' | 'THREAD'

export interface ContentItem {
  id: string
  title: string
  platform: Platform[]
  format: Format
  scheduledDate: string
  status: ContentStatus
  caption: string
  hashtags: string
  imagePrompt?: string
  notes?: string
  createdBy: string
  createdAt: string
}

const INITIAL_CONTENT: ContentItem[] = [
  // ─── YOUTUBE ────────────────────────────────────────────────────────
  {
    id: 'yt-001',
    title: '🔥 I Built an AI War Room for My Meat Business',
    platform: ['YouTube'],
    format: 'VIDEO',
    scheduledDate: '2026-07-15',
    status: 'pending',
    caption: `Most small businesses run their ops on WhatsApp and Excel. We just spent 6 months building something completely different. This is the Studex War Room — and this is what a South African meat company looks like in 2026.

I'm Tumelo Ramaphosa. I founded Studex Meat 10 years ago — premium Halaal Wagyu beef and biltong, delivered nationwide in South Africa. For 7 of those 10 years, I couldn't open a business bank account because of who I am. So I stopped waiting for the system to work for me. I started building.

This is Charlie — our Chief Operating Agent. This is Naledi — our Chief Marketing Officer Agent. And this is the War Room.`,
    hashtags: '#BuildInPublic #AIAgents #SouthAfrica #WagyuBeef #Biltong #Startup #Automation #StudexMeat #GlobalExpansion',
    notes: '7-8 min video. Film 15 min screen + talking, edit down. Tumelo on camera intro/outro + B-roll. Voiceover alternative available. Music: royalty-free cinematic only.',
    createdBy: 'Robusca',
    createdAt: '2026-07-06',
  },

  // ─── YOUTH DAY — FREEKPIK (TikTok) ─────────────────────────────────
  {
    id: 'fd-001',
    title: '🎤 YOUNG & WATCHING — Youth Day TikTok',
    platform: ['TikTok'],
    format: 'VIDEO',
    scheduledDate: '2026-06-16',
    status: 'pending',
    caption: `🎤 YOUNG & WATCHING 🌍

1976 they tried to silence us with bullets.
2026 we building empires with Wagyu. 🤯

This Heritage Month we're not just commemorating —
we're CARRYING. 💪🏿

My people built this country. We also building this economy.
Support Black-owned. Not charity — EVOLUTION.

🔗 DM for wholesale. Link in bio.`,
    hashtags: '#YouthDay #BlackOwned #TownshipEconomy #StudexMeat',
    createdBy: 'Robusca (Naledi CMO)',
    createdAt: '2026-06-17',
  },
  {
    id: 'fd-002',
    title: '📢 THREAD — Why "support Black business" is STRATEGY',
    platform: ['TikTok', 'X'],
    format: 'VIDEO',
    scheduledDate: '2026-06-16',
    status: 'pending',
    caption: `📢 THREAD: Why "support Black business" is STRATEGY not charity 🧵👇

When you spend R100 at Studex instead of Pick n Pay:
→ That R100 employs YOUR community
→ That R100 compounds into next generation infrastructure
→ That R100 says: "we matter"

This Youth Day — redirect ONE shop. That's it.
Your future self will thank you. 🤝`,
    hashtags: '#BuyBlack #YouthDay2026 #StudexMeat',
    createdBy: 'Robusca (Naledi CMO)',
    createdAt: '2026-06-17',
  },
  {
    id: 'fd-003',
    title: '👨‍🍳 REAL TALK — What R2,000 Wagyu Tastes Like',
    platform: ['TikTok'],
    format: 'VIDEO',
    scheduledDate: '2026-06-16',
    status: 'pending',
    caption: `👨‍🍳 REAL TALK: This is what R2,000 Wagyu tastes like. 🎥

[Video: Slicing premium Wagyu biltong, close-up]

We don't compete on price. We compete on LEGACY.
Every pack = stamp of Black excellence.

🎁 Corporate gifting available. DM for bulk.`,
    hashtags: '#Wagyu #StudexMeat #YouthDay',
    imagePrompt: 'Premium Wagyu biltong sliced thin on a wooden board, dramatic lighting, cinematic food photography',
    createdBy: 'Robusca (Naledi CMO)',
    createdAt: '2026-06-17',
  },

  // ─── YOUTH DAY — HIGGSFIKD (Instagram/FB) ───────────────────────────
  {
    id: 'ig-001',
    title: '🔥 Fire & Feast — Youth Day Carousel (5-7 slides)',
    platform: ['Instagram', 'Facebook'],
    format: 'CAROUSEL',
    scheduledDate: '2026-06-16',
    status: 'pending',
    caption: `This Youth Day we remember the 1976 generation with action, not just words. 🇿🇦

We are the generation that turns pain into precision, heritage into heat, and township kitchens into national brands.

Studex Meat is Black-owned. Halaal-certified. Proudly SA. 🇿🇦

📦 Shop now: link in bio
🏭 Wholesale enquiries: DM
🎁 Corporate gifting: tumelo@studexmeat.com`,
    hashtags: '#YouthDay #June16 #StudexMeat #BuyBlackBusiness #HalaalMeat #SouthAfrica',
    notes: 'Slide 1: Hero — flame-grilled Wagyu "The Youth Shall Inherit the Flame". Slide 2: Collage SA youth 1976 vs 2026 entrepreneurs. Slide 3: Product shot. Slide 4: Infographic — local supply chain. Slide 5: Tumelo quote. Slide 6: Youth Day special offer. Slide 7: CTA.',
    createdBy: 'Robusca (Naledi CMO)',
    createdAt: '2026-06-17',
  },
  {
    id: 'ig-002',
    title: '📸 Story Set — Youth Day Engagement',
    platform: ['Instagram'],
    format: 'STORY',
    scheduledDate: '2026-06-16',
    status: 'pending',
    caption: `Story 1: Poll — "Favourite way to eat biltong?" (Straight / In a wrap / On a board)
Story 2: BTS packing process
Story 3: UGC — customer enjoying Studex
Story 4: Countdown to Youth Day special
Story 5: Link to shop`,
    hashtags: '#YouthDay #StudexMeat',
    createdBy: 'Robusca (Naledi CMO)',
    createdAt: '2026-06-17',
  },

  // ─── REGULAR CONTENT ─────────────────────────────────────────────────
  {
    id: 'reg-001',
    title: '🍽️ Monday Weekly Promo — Wagyu Spotlight',
    platform: ['Facebook', 'Instagram', 'TikTok'],
    format: 'IMAGE',
    scheduledDate: 'Every Monday',
    status: 'pending',
    caption: `This week we're spotlighting our premium Halaal Wagyu biltong — dry-aged, hand-sliced, and packed with heritage.

From R450 per 200g pack.

📦 Nationwide delivery. DM to order.
🔗 Link in bio.`,
    hashtags: '#Wagyu #Biltong #PremiumMeat #Halaal #StudexMeat #SouthAfrica #BuyBlack',
    createdBy: 'Robusca (Naledi CMO)',
    createdAt: '2026-07-07',
  },
  {
    id: 'reg-002',
    title: '📚 Tuesday Education — How to Read a Wagyu Label',
    platform: ['LinkedIn', 'X'],
    format: 'IMAGE',
    scheduledDate: 'Every Tuesday',
    status: 'pending',
    caption: `A5, A4, BMS Score 6-9... what does it all mean?

Here's how to read a Wagyu beef label so you always know what you're paying for:

→ BMS = Beef Marbling Score (1-12, higher = more fat marbling)
→ A5 = Japanese yield grade + quality grade
→ F1, F2, F3 = generation of Wagyu crossbreeding

Studex Wagyu: BMS 6-9, A3-A5 equivalent, F1-F4 depending on cut.

DM us — we'll walk you through the full range. 🐂`,
    hashtags: '#Wagyu #FoodEducation #BeefLabel #StudexMeat #PremiumMeat',
    createdBy: 'Robusca (Naledi CMO)',
    createdAt: '2026-07-07',
  },
  {
    id: 'reg-003',
    title: '🌿 Wednesday Lifestyle — Farm to Table ASMR',
    platform: ['TikTok', 'Instagram'],
    format: 'REELS',
    scheduledDate: 'Every Wednesday',
    status: 'pending',
    caption: `Slow. Precise. Satisfying. 🐂

Our dry-aging process takes 21-45 days. What comes out is something else entirely.

🎥 ASMR slicing video coming this Wednesday.
Stay tuned.`,
    hashtags: '#ASMR #FarmToTable #DryAged #Wagyu #StudexMeat',
    imagePrompt: 'Chef slicing dry-aged Wagyu biltong in slow motion, dramatic side lighting, dark background, cinematic food video style',
    createdBy: 'Robusca (Naledi CMO)',
    createdAt: '2026-07-07',
  },
  {
    id: 'reg-004',
    title: '🗳️ Thursday Poll — favourite cut',
    platform: ['Instagram'],
    format: 'STORY',
    scheduledDate: 'Every Thursday',
    status: 'pending',
    caption: `QUIZ TIME 🗳️

Which Studex cut are you ordering this weekend?

A) Wagyu T-Bone
B) Dry-Aged Ribeye
C) Premium Ox Tail
D) Sides + Biltong sampler

Drop your letter in the comments 👇`,
    hashtags: '#StudexMeat #BeefCut #WeekendVibes',
    createdBy: 'Robusca (Naledi CMO)',
    createdAt: '2026-07-07',
  },
  {
    id: 'reg-005',
    title: '🍷 Friday Recipe — Wagyu with red wine reduction',
    platform: ['Facebook', 'Instagram'],
    format: 'CAROUSEL',
    scheduledDate: 'Every Friday',
    status: 'pending',
    caption: `Friday = Wagyu night. No arguments. 🥩🍷

RECIPE: Reverse-seared Studex Wagyu Ribeye with red wine reduction.

① Remove from fridge 1hr before cooking
② Season with salt only — let it breathe
③ Sear in cast iron 90s per side
④ Rest 10min
⑤ Glaze with red wine + butter reduction

Full recipe in the link. Tag someone who needs to see this. 👇`,
    hashtags: '#WagyuRecipe #FridayVibes #StudexMeat #Foodie #BeefLover',
    createdBy: 'Robusca (Naledi CMO)',
    createdAt: '2026-07-07',
  },
  {
    id: 'reg-006',
    title: '💬 Saturday Community — UGC Feature',
    platform: ['Instagram', 'Threads'],
    format: 'IMAGE',
    scheduledDate: 'Every Saturday',
    status: 'pending',
    caption: `We love seeing how you enjoy Studex. 🥩❤️

Feature your next Studex meal and tag us — you might make our page.

Best posts get a 15% off code for your next order. 🎁`,
    hashtags: '#StudexMeat #CustomerLove #UGC #CommunityFirst',
    createdBy: 'Robusca (Naledi CMO)',
    createdAt: '2026-07-07',
  },

  // ─── CAMPAIGN: CHINA WINDOW ──────────────────────────────────────────
  {
    id: 'cn-001',
    title: '🌏 China Coffee Window — LinkedIn Outreach',
    platform: ['LinkedIn'],
    format: 'CAROUSEL',
    scheduledDate: '2026-07-20',
    status: 'pending',
    caption: `South African green coffee has a rare window to enter the Chinese market — July 20 opens a 90-day import clearance window under the new SA-China protocol.

We're Studex Coffee — Rwandan A1/A2 grade, wildlife-verified, PROWTC-certified, competitive FOB pricing.

Target buyers: Luckin Coffee, Tim Hortons China, Pacific Coffee, JD.com, Alibaba Food.

We're exhibiting at CIIE November 2026 — Booth space allocation begins July 25.

DM to schedule a call this week. 🇨🇳`,
    hashtags: '#ChinaMarket #SouthAfricaCoffee #RwandanCoffee #CIIE2026 #B2BCoffee #ImportExport #CoffeeTrade',
    createdBy: 'Robusca',
    createdAt: '2026-07-06',
  },
  {
    id: 'cn-002',
    title: '🐄 Ankole Tokenization — The Big One',
    platform: ['YouTube', 'LinkedIn'],
    format: 'VIDEO',
    scheduledDate: '2026-08-01',
    status: 'pending',
    caption: `A single Ankole bull was cited by Bloomberg at R11 million.

African heritage animals — Ankole, Nguni, Afrikaner — are worth millions. Yet most farmers can't access that equity because the animals aren't tradable.

We're building the platform to fractionalize African heritage animal ownership on blockchain — drone surveillance, DNA verification, global investor access.

This is wealth-building infrastructure for African agriculture.

First herd listing: Q4 2026. Waitlist open now. 🐂🌍`,
    hashtags: '#Ankole #Blockchain #AfricanWealth #AgriTech #Web3 #CattleTokenization',
    createdBy: 'Robusca',
    createdAt: '2026-07-06',
  },

  // ─── COFFEE ─────────────────────────────────────────────────────────
  {
    id: 'cf-001',
    title: "☕ Rwanda A1 Washed — UAE Roaster Spotlight",
    platform: ['Instagram', 'Facebook'],
    format: 'CAROUSEL',
    scheduledDate: '2026-07-20',
    status: 'pending',
    caption: `🌍 RWANDA A1 GRADE — WASHED PROCESS

Cup profile: jasmine, stone fruit, clean finish
Grade: SPOT Premium Grade A1
Certification: Rainforest Alliance, PROWTC
Min order: 60kg bags
FOB Kigali: from USD 4.80/kg

For UAE and SA roasters serious about single-origin African coffee — this is your next house blend.

📩 Inquire: coffee@studexmeat.com`,
    hashtags: '#RwandanCoffee #UAE #SingleOrigin #CoffeeTrade #SpecialtyCoffee #PROWTC',
    createdBy: 'Robusca',
    createdAt: '2026-07-06',
  },
]

function PlatformBadge({ platform }: { platform: Platform }) {
  const colors: Record<Platform, string> = {
    TikTok: 'bg-pink-600/20 text-pink-400 border-pink-500/30',
    Instagram: 'bg-purple-600/20 text-purple-400 border-purple-500/30',
    Facebook: 'bg-blue-600/20 text-blue-400 border-blue-500/30',
    YouTube: 'bg-red-600/20 text-red-400 border-red-500/30',
    LinkedIn: 'bg-sky-600/20 text-sky-400 border-sky-500/30',
    X: 'bg-gray-600/20 text-gray-300 border-gray-500/30',
    Threads: 'bg-sky-600/20 text-sky-300 border-sky-400/30',
    All: 'bg-amber-600/20 text-amber-400 border-amber-500/30',
  }
  return (
    <span className={`text-xs px-2 py-0.5 rounded border font-medium ${colors[platform]}`}>
      {platform}
    </span>
  )
}

function StatusBadge({ status }: { status: ContentStatus }) {
  if (status === 'approved')
    return <span className="text-xs font-bold text-green-400 bg-green-500/10 px-2 py-1 rounded border border-green-500/30">✓ APPROVED</span>
  if (status === 'rejected')
    return <span className="text-xs font-bold text-red-400 bg-red-500/10 px-2 py-1 rounded border border-red-500/30">✗ REJECTED</span>
  return <span className="text-xs font-bold text-yellow-400 bg-yellow-500/10 px-2 py-1 rounded border border-yellow-500/30">⏳ AWAITING APPROVAL</span>
}

function ContentCard({ item, onApprove, onReject }: { item: ContentItem; onApprove: () => void; onReject: () => void }) {
  const [expanded, setExpanded] = useState(false)
  const isDone = item.status !== 'pending'

  return (
    <div className={`rounded-xl border transition-all duration-200 ${isDone ? 'bg-zinc-900/40 border-zinc-800' : 'bg-zinc-900/80 border-zinc-700'} ${item.status === 'approved' ? 'border-green-500/30' : item.status === 'rejected' ? 'border-red-500/30' : 'border-yellow-500/20'}`}>
      {/* Card Header */}
      <div className="p-5">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`text-xs px-2 py-0.5 rounded border font-mono font-bold ${item.format === 'VIDEO' ? 'bg-orange-500/10 text-orange-400 border-orange-500/30' : item.format === 'CAROUSEL' ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30' : item.format === 'STORY' ? 'bg-pink-500/10 text-pink-400 border-pink-500/30' : item.format === 'REELS' ? 'bg-purple-500/10 text-purple-400 border-purple-500/30' : 'bg-zinc-700/50 text-zinc-300 border-zinc-600'}`}>
              {item.format}
            </span>
            {item.platform.map(p => <PlatformBadge key={p} platform={p} />)}
          </div>
          <StatusBadge status={item.status} />
        </div>

        <h3 className="text-white font-bold text-base leading-snug mb-2">{item.title}</h3>

        <p className="text-zinc-400 text-xs mb-3 flex items-center gap-2">
          <span className="text-zinc-600">📅</span>
          <span className={item.scheduledDate.includes('Every') ? 'text-cyan-400/70' : 'text-amber-400/70'}>
            {item.scheduledDate}
          </span>
          <span className="text-zinc-700">•</span>
          <span className="text-zinc-500">Created by {item.createdBy}</span>
          <span className="text-zinc-700">•</span>
          <span className="text-zinc-500">{item.createdAt}</span>
        </p>

        {/* Caption preview */}
        <div className="bg-zinc-800/60 rounded-lg p-3 mb-3">
          <p className="text-zinc-300 text-xs leading-relaxed font-mono whitespace-pre-wrap">
            {expanded ? item.caption : item.caption.slice(0, 180) + (item.caption.length > 180 ? '…' : '')}
          </p>
          {item.caption.length > 180 && (
            <button onClick={() => setExpanded(!expanded)} className="text-cyan-400 text-xs mt-1 hover:underline">
              {expanded ? 'Show less' : 'Read more'}
            </button>
          )}
        </div>

        {item.hashtags && (
          <p className="text-zinc-500 text-xs leading-relaxed mb-3">{item.hashtags}</p>
        )}

        {item.notes && (
          <div className="bg-amber-500/5 border border-amber-500/20 rounded-lg p-3 mb-3">
            <p className="text-amber-300/80 text-xs font-semibold mb-1">📋 Notes</p>
            <p className="text-zinc-400 text-xs leading-relaxed">{item.notes}</p>
          </div>
        )}

        {item.imagePrompt && (
          <div className="bg-purple-500/5 border border-purple-500/20 rounded-lg p-3 mb-3">
            <p className="text-purple-300/80 text-xs font-semibold mb-1">🎨 Image Prompt</p>
            <p className="text-zinc-400 text-xs leading-relaxed italic">{item.imagePrompt}</p>
          </div>
        )}

        {/* Actions */}
        {item.status === 'pending' && (
          <div className="flex items-center gap-3 mt-2">
            <button
              onClick={onApprove}
              className="flex-1 py-2.5 rounded-lg border border-green-500/50 text-green-400 text-sm font-bold hover:bg-green-500/10 transition-colors"
            >
              ✓ APPROVE
            </button>
            <button
              onClick={onReject}
              className="flex-1 py-2.5 rounded-lg border border-red-500/50 text-red-400 text-sm font-bold hover:bg-red-500/10 transition-colors"
            >
              ✗ REJECT
            </button>
            <button
              onClick={onApprove}
              className="flex-1 py-2.5 rounded-lg border border-yellow-500/50 text-yellow-400 text-sm font-bold hover:bg-yellow-500/10 transition-colors"
            >
              🤖 REVIEW
            </button>
          </div>
        )}

        {item.status === 'approved' && (
          <div className="flex items-center gap-3 mt-2">
            <button
              onClick={onReject}
              className="flex-1 py-2 rounded-lg border border-red-500/30 text-red-400 text-xs font-bold hover:bg-red-500/10 transition-colors"
            >
              ✗ CHANGE TO REJECTED
            </button>
            <button
              onClick={() => {}}
              className="flex-1 py-2 rounded-lg border border-zinc-700 text-zinc-500 text-xs font-bold hover:bg-zinc-800 transition-colors cursor-not-allowed opacity-50"
              disabled
            >
              ✓ APPROVED
            </button>
          </div>
        )}

        {item.status === 'rejected' && (
          <div className="flex items-center gap-3 mt-2">
            <button
              onClick={onApprove}
              className="flex-1 py-2 rounded-lg border border-green-500/30 text-green-400 text-xs font-bold hover:bg-green-500/10 transition-colors"
            >
              ✓ CHANGE TO APPROVED
            </button>
            <button
              onClick={() => {}}
              className="flex-1 py-2 rounded-lg border border-zinc-700 text-zinc-500 text-xs font-bold hover:bg-zinc-800 transition-colors cursor-not-allowed opacity-50"
              disabled
            >
              ✗ REJECTED
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default function App() {
  const [content, setContent] = useState<ContentItem[]>(INITIAL_CONTENT)
  const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('all')
  const [platformFilter, setPlatformFilter] = useState<Platform | 'All'>('All')
  const [search, setSearch] = useState('')

  const approveAll = () => setContent(c => c.map(i => i.status === 'pending' ? { ...i, status: 'approved' } : i))
  const reviewAll = () => {
    // Just a visual indicator — in production this would call an AI review
    alert('🤖 Robusca AI review would analyze all pending content here. Connect your AI provider to enable this feature.')
  }

  const filtered = content.filter(item => {
    if (filter !== 'all' && item.status !== filter) return false
    if (platformFilter !== 'All' && !item.platform.includes(platformFilter)) return false
    if (search && !item.title.toLowerCase().includes(search.toLowerCase()) && !item.caption.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  const pending = content.filter(i => i.status === 'pending').length
  const approved = content.filter(i => i.status === 'approved').length
  const rejected = content.filter(i => i.status === 'rejected').length

  return (
    <div className="min-h-screen bg-zinc-950 text-white">
      {/* Top bar */}
      <div className="sticky top-0 z-50 bg-zinc-950/95 backdrop-blur border-b border-zinc-800">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-xl font-black text-white tracking-tight">📋 Studex Content Approval</h1>
              <p className="text-zinc-500 text-xs mt-0.5">Robusca OS — Content Queue</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="flex items-center gap-4 text-xs">
                  <span className="text-yellow-400 font-bold">{pending} ⏳ Pending</span>
                  <span className="text-green-400 font-bold">{approved} ✓ Approved</span>
                  <span className="text-red-400 font-bold">{rejected} ✗ Rejected</span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={approveAll}
              className="px-4 py-2 rounded-lg border border-green-500/50 text-green-400 text-xs font-bold hover:bg-green-500/10 transition-colors"
            >
              ✓ APPROVE ALL
            </button>
            <button
              onClick={reviewAll}
              className="px-4 py-2 rounded-lg border border-yellow-500/50 text-yellow-400 text-xs font-bold hover:bg-yellow-500/10 transition-colors"
            >
              🤖 ROBUSCA REVIEW ALL
            </button>

            <div className="flex-1" />

            {/* Platform filter */}
            <div className="flex items-center gap-1 bg-zinc-900 rounded-lg p-1 border border-zinc-800">
              {(['All', 'TikTok', 'Instagram', 'Facebook', 'YouTube', 'LinkedIn', 'X', 'Threads'] as const).map(p => (
                <button
                  key={p}
                  onClick={() => setPlatformFilter(p as Platform | 'All')}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${platformFilter === p ? 'bg-zinc-700 text-white' : 'text-zinc-500 hover:text-zinc-300'}`}
                >
                  {p}
                </button>
              ))}
            </div>

            {/* Status filter */}
            <div className="flex items-center gap-1 bg-zinc-900 rounded-lg p-1 border border-zinc-800">
              {(['all', 'pending', 'approved', 'rejected'] as const).map(s => (
                <button
                  key={s}
                  onClick={() => setFilter(s)}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium capitalize transition-colors ${filter === s ? 'bg-zinc-700 text-white' : 'text-zinc-500 hover:text-zinc-300'}`}
                >
                  {s === 'all' ? 'All' : s}
                </button>
              ))}
            </div>

            {/* Search */}
            <input
              type="text"
              placeholder="Search content..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="bg-zinc-900 border border-zinc-700 text-white text-xs rounded-lg px-3 py-2 w-48 focus:outline-none focus:border-zinc-500 placeholder-zinc-600"
            />
          </div>
        </div>
      </div>

      {/* Content grid */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 text-zinc-600">
            <span className="text-5xl mb-4">📭</span>
            <p className="text-lg font-bold text-zinc-500">No content found</p>
            <p className="text-sm text-zinc-600 mt-1">Try adjusting your filters</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {filtered.map(item => (
              <ContentCard
                key={item.id}
                item={item}
                onApprove={() => setContent(c => c.map(i => i.id === item.id ? { ...i, status: 'approved' } : i))}
                onReject={() => setContent(c => c.map(i => i.id === item.id ? { ...i, status: 'rejected' } : i))}
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-zinc-900 mt-8 py-6 text-center text-zinc-700 text-xs">
        💬 Created by Robusca VM (MiniMax Agent) — {filtered.length} items shown — Studex Meat Content OS
      </div>
    </div>
  )
}
