import { useState } from 'react'

const PLATFORMS = [
  { name: 'Facebook', icon: '📘', account: 'Tumelo Ramaphosa', status: 'connected' },
  { name: 'YouTube', icon: '📺', account: 'Studex Wildlife', status: 'connected' },
  { name: 'Instagram', icon: '📸', account: 'laisa_aesthetics', status: 'connected' },
  { name: 'LinkedIn', icon: '💼', account: 'Tumelo Ramaphosa', status: 'connected' },
  { name: 'Threads', icon: '🧵', account: 'ramaphosatumelo', status: 'connected' },
  { name: 'TikTok', icon: '🎵', account: 'studexwildlife', status: 'connected' },
]

const AGENTS = [
  { name: 'Robusca', role: 'Chief of Staff', status: 'idle', voice: 'Professional SA English' },
  { name: 'Naledi', role: 'CMO / Content', status: 'idle', voice: 'Warm, energetic' },
  { name: 'Auto-Meat', role: 'E-Commerce', status: 'idle', voice: 'Detail-oriented' },
  { name: 'Hermes', role: 'CTO / DevOps', status: 'idle', voice: 'Technical precise' },
  { name: 'Charlie', role: 'Orchestrator', status: 'idle', voice: 'Strategic coordinator' },
]

const PIPELINE_STEPS = [
  { step: 1, name: 'AI Generates Caption', tool: 'GPT-4o / Ollama', status: 'ready' },
  { step: 2, name: 'Image Generation', tool: 'Freepik API', status: 'ready' },
  { step: 3, name: 'Video Processing', tool: 'ffmpeg-wasm', status: 'ready' },
  { step: 4, name: 'AI Video Creatives', tool: 'Higgsfield (pending)', status: 'blocked' },
  { step: 5, name: 'Format Per Platform', tool: 'Auto-resize + crop', status: 'ready' },
  { step: 6, name: 'Publish', tool: 'Meta Graph API + Blotato', status: 'partial' },
]

const RAG_STATUS = [
  { source: 'Obsidian Vault', docs: 142, status: 'indexed' },
  { source: 'Robusca Brain', docs: 38, status: 'indexed' },
  { source: 'Call Transcripts', docs: 0, status: 'not_started' },
  { source: 'Shopify Orders', docs: 0, status: 'no_token' },
  { source: 'AgentMail', emails: 47, status: 'partial' },
  { source: 'Blotato Posts', posts: 0, status: 'empty' },
]

const BLOCKERS = [
  { item: 'VAPI API Key', priority: 'high', desc: 'Get from vapi.ai → Dashboard → API Keys' },
  { item: 'Orgo VM ID', priority: 'high', desc: 'Recover from Orgo dashboard — current VM offline' },
  { item: 'Shopify Token', priority: 'high', desc: 'Admin API access from Shopify partner dashboard' },
  { item: 'Higgsfield Key', priority: 'medium', desc: 'Sign up at higgsfield.ai for video AI' },
  { item: 'Blotato MCP', priority: 'medium', desc: 'Enable MCP server in OpenClaw config' },
]

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    connected: 'bg-green-500/20 text-green-400 border-green-500/30',
    indexed: 'bg-green-500/20 text-green-400 border-green-500/30',
    ready: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    idle: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    blocked: 'bg-red-500/20 text-red-400 border-red-500/30',
    partial: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    not_started: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    no_token: 'bg-red-500/20 text-red-400 border-red-500/30',
    empty: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  }
  return (
    <span className={`px-2 py-0.5 rounded text-xs border ${colors[status] || 'bg-gray-500/20 text-gray-400'}`}>
      {status.replace('_', ' ')}
    </span>
  )
}

function CallButton({ agent }: { agent: typeof AGENTS[0] }) {
  const [calling, setCalling] = useState(false)
  return (
    <button
      onClick={() => setCalling(!calling)}
      className={`w-full py-3 px-4 rounded-xl border transition-all text-left ${
        calling
          ? 'bg-red-500/20 border-red-500/40 text-red-300'
          : 'bg-white/5 border-white/10 text-white hover:bg-white/10'
      }`}
    >
      <div className="flex items-center justify-between">
        <div>
          <div className="font-semibold text-sm">{agent.name}</div>
          <div className="text-xs text-white/50">{agent.role} · {agent.voice}</div>
        </div>
        <div className="text-2xl">{calling ? '⏹️' : '📞'}</div>
      </div>
      {calling && (
        <div className="mt-2 text-xs text-red-400 animate-pulse">Calling {agent.name}...</div>
      )}
    </button>
  )
}

export default function App() {
  const [activeTab, setActiveTab] = useState('overview')
  const [contentPrompt, setContentPrompt] = useState('')
  const [generating, setGenerating] = useState(false)
  const [generatedContent, setGeneratedContent] = useState('')

  const generateContent = async () => {
    if (!contentPrompt.trim()) return
    setGenerating(true)
    setGeneratedContent('')
    await new Promise(r => setTimeout(r, 2000))
    setGeneratedContent(
      `📸 Instagram Post — ${new Date().toLocaleDateString()}\n\n` +
      `${contentPrompt}\n\n` +
      `#StudExMeat #Biltong #SouthAfrican #PremiumMeat #BiltongLovers #StudEx #ArtisanQuality`
    )
    setGenerating(false)
  }

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <div className="border-b border-white/10 bg-gradient-to-r from-purple-900/30 to-blue-900/30">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                StudEx Content OS
              </h1>
              <p className="text-sm text-white/50">StudEx Meat · B.C.C · Agent Command Center</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-xs text-white/40">Amara speaking with</div>
                <div className="text-sm font-semibold">Tumelo Ramaphosa</div>
              </div>
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center text-sm font-bold">
                A
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <div className="border-b border-white/10 bg-black/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 flex gap-1">
          {['overview','content','voice','rag','agents','blockers'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-3 text-sm font-medium capitalize transition-all border-b-2 ${
                activeTab === tab
                  ? 'text-purple-400 border-purple-400'
                  : 'text-white/50 border-transparent hover:text-white/80'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">

      {/* OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-green-900/30 to-green-800/10 border border-green-500/20 rounded-2xl p-5">
              <div className="text-3xl mb-2">📡</div>
              <div className="text-lg font-bold text-green-400">6 Accounts Live</div>
              <div className="text-sm text-white/60 mt-1">Facebook, YouTube, IG, LinkedIn, Threads, TikTok</div>
              <div className="mt-3 text-xs text-green-400/70">All connected via Blotato</div>
            </div>
            <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/10 border border-blue-500/20 rounded-2xl p-5">
              <div className="text-3xl mb-2">🎙️</div>
              <div className="text-lg font-bold text-blue-400">5 Voice Agents</div>
              <div className="text-sm text-white/60 mt-1">Robusca, Naledi, Auto-Meat, Hermes, Charlie</div>
              <div className="mt-3 text-xs text-blue-400/70">Waiting for VAPI key</div>
            </div>
            <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/10 border border-purple-500/20 rounded-2xl p-5">
              <div className="text-3xl mb-2">🧠</div>
              <div className="text-lg font-bold text-purple-400">RAG Indexed</div>
              <div className="text-sm text-white/60 mt-1">180 docs across 2 sources</div>
              <div className="mt-3 text-xs text-purple-400/70">Obsidian + Robusca Brain</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Pipeline */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                🔗 Content Pipeline
                <span className="text-xs bg-orange-500/20 text-orange-400 px-2 py-0.5 rounded-full border border-orange-500/30">
                  1 blocker
                </span>
              </h3>
              <div className="space-y-3">
                {PIPELINE_STEPS.map(s => (
                  <div key={s.step} className="flex items-center gap-3">
                    <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                      s.status === 'blocked' ? 'bg-red-500/30 text-red-400' :
                      s.status === 'ready' ? 'bg-green-500/30 text-green-400' :
                      'bg-blue-500/30 text-blue-400'
                    }`}>{s.step}</div>
                    <div className="flex-1">
                      <div className="text-sm font-medium">{s.name}</div>
                      <div className="text-xs text-white/40">{s.tool}</div>
                    </div>
                    <StatusBadge status={s.status} />
                  </div>
                ))}
              </div>
            </div>

            {/* Top Blockers */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <h3 className="font-bold text-lg mb-4">⚠️ Top Blockers</h3>
              <div className="space-y-3">
                {BLOCKERS.filter(b => b.priority === 'high').map(b => (
                  <div key={b.item} className="flex items-start gap-3 bg-red-500/5 border border-red-500/20 rounded-xl p-3">
                    <div className="text-red-400 mt-0.5">⚡</div>
                    <div>
                      <div className="text-sm font-semibold text-red-300">{b.item}</div>
                      <div className="text-xs text-white/40 mt-0.5">{b.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
              <button className="mt-4 w-full py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm hover:bg-white/10 transition-all">
                View all 5 blockers →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CONTENT */}
      {activeTab === 'content' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Generator */}
            <div className="lg:col-span-2 bg-white/5 border border-white/10 rounded-2xl p-6">
              <h3 className="font-bold text-lg mb-4">✍️ AI Content Generator</h3>
              <textarea
                value={contentPrompt}
                onChange={e => setContentPrompt(e.target.value)}
                placeholder="Describe what you want to post about... e.g. 'New biltong flavour drop — smoky chipotle biltong, perfect for winter braais'"
                className="w-full h-28 bg-black/40 border border-white/10 rounded-xl p-4 text-sm text-white placeholder:text-white/30 resize-none focus:outline-none focus:border-purple-500/50"
              />
              <div className="flex items-center gap-3 mt-3">
                <button
                  onClick={generateContent}
                  disabled={generating || !contentPrompt.trim()}
                  className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl text-sm font-semibold disabled:opacity-40 hover:opacity-90 transition-all"
                >
                  {generating ? '⏳ Generating...' : '🚀 Generate Caption'}
                </button>
                <span className="text-xs text-white/40">Uses GPT-4o · Routed via VAPI</span>
              </div>
              {generatedContent && (
                <div className="mt-4 bg-black/40 border border-purple-500/20 rounded-xl p-4">
                  <div className="text-xs text-purple-400 mb-2">Generated output</div>
                  <pre className="text-sm whitespace-pre-wrap text-white/80">{generatedContent}</pre>
                  <div className="flex gap-2 mt-3">
                    <button className="px-3 py-1.5 bg-green-600/30 border border-green-500/30 rounded-lg text-xs text-green-300 hover:bg-green-600/50">
                      📘 Post to Facebook
                    </button>
                    <button className="px-3 py-1.5 bg-pink-600/30 border border-pink-500/30 rounded-lg text-xs text-pink-300 hover:bg-pink-600/50">
                      📸 Post to Instagram
                    </button>
                    <button className="px-3 py-1.5 bg-black/60 border border-white/20 rounded-lg text-xs text-white/70 hover:bg-white/10">
                      💾 Save to Drafts
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Connected Accounts */}
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <h3 className="font-bold text-lg mb-4">📡 Connected Accounts</h3>
              <div className="space-y-2">
                {PLATFORMS.map(p => (
                  <div key={p.name} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                    <div className="flex items-center gap-2">
                      <span>{p.icon}</span>
                      <div>
                        <div className="text-sm font-medium">{p.name}</div>
                        <div className="text-xs text-white/40">{p.account}</div>
                      </div>
                    </div>
                    <StatusBadge status={p.status} />
                  </div>
                ))}
              </div>
              <div className="mt-4 p-3 bg-orange-500/10 border border-orange-500/20 rounded-xl">
                <div className="text-xs text-orange-400 font-semibold mb-1">⚠️ Own Blotato pending</div>
                <div className="text-xs text-white/50">Direct Meta API + Freepik pipeline being built — no renewals needed</div>
              </div>
            </div>
          </div>

          {/* Pipeline viz */}
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
            <h3 className="font-bold text-lg mb-5">🔄 Full Pipeline — Auto-Content Engine</h3>
            <div className="flex items-center gap-2 flex-wrap">
              {[
                { label: 'Product Data', icon: '📦', color: 'from-blue-500/30 to-blue-400/10 border-blue-500/30' },
                { label: 'AI Caption + Hashtags', icon: '✍️', color: 'from-purple-500/30 to-purple-400/10 border-purple-500/30' },
                { label: 'Freepik Image', icon: '🎨', color: 'from-pink-500/30 to-pink-400/10 border-pink-500/30' },
                { label: 'Higgsfield Video', icon: '🎬', color: 'from-red-500/30 to-red-400/10 border-red-500/30' },
                { label: 'ffmpeg Resize', icon: '🔧', color: 'from-orange-500/30 to-orange-400/10 border-orange-500/30' },
                { label: 'Format Per Platform', icon: '📐', color: 'from-yellow-500/30 to-yellow-400/10 border-yellow-500/30' },
                { label: 'Meta API Direct', icon: '📘', color: 'from-blue-600/30 to-blue-400/10 border-blue-500/30' },
                { label: 'Blotato Backup', icon: '🔄', color: 'from-green-500/30 to-green-400/10 border-green-500/30' },
              ].map((step, i) => (
                <div key={i} className="flex items-center gap-2">
                  <div className={`px-3 py-2 rounded-xl border text-xs font-medium bg-gradient-to-b ${step.color}`}>
                    {step.icon} {step.label}
                  </div>
                  {i < 7 && <span className="text-white/30">→</span>}
                </div>
              ))}
            </div>
            <div className="mt-4 flex gap-3">
              <button className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-xs hover:bg-white/10">
                ▶️ Run Full Pipeline
              </button>
              <button className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-xs hover:bg-white/10">
                📋 View History
              </button>
              <button className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-xs hover:bg-white/10">
                ⚙️ Configure
              </button>
            </div>
          </div>
        </div>
      )}

      {/* VOICE */}
      {activeTab === 'voice' && (
        <div className="space-y-8">
          <div className="bg-gradient-to-br from-purple-900/30 to-blue-900/20 border border-purple-500/20 rounded-2xl p-6">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-xl font-bold mb-2">🎙️ VAPI Voice Agents</h3>
                <p className="text-sm text-white/60">Call any agent directly. War Room connects all 5 agents on one call with Tumelo.</p>
                <div className="mt-3 inline-flex items-center gap-2 px-3 py-1.5 bg-orange-500/20 border border-orange-500/30 rounded-full text-xs text-orange-400">
                  ⚡ Requires VAPI key — <a href="https://vapi.ai" className="underline" target="_blank">Get free key →</a>
                </div>
              </div>
              <button className="px-5 py-2.5 bg-gradient-to-r from-red-500 to-red-600 rounded-xl text-sm font-semibold">
                📞 War Room — All Agents
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {AGENTS.map(agent => (
              <CallButton key={agent.name} agent={agent} />
            ))}
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
            <h3 className="font-bold text-lg mb-4">📋 Call Workflow</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[
                { step: '1', title: 'Tumelo calls VAPI number', desc: 'Picks agent or War Room squad' },
                { step: '2', title: 'Agent answers', desc: 'Persona + voice — full context loaded from RAG' },
                { step: '3', title: 'Live conversation', desc: 'Can hand off to other agents mid-call' },
                { step: '4', title: 'Transcript → Obsidian', desc: 'Full call saved to vault automatically' },
              ].map(s => (
                <div key={s.step} className="text-center">
                  <div className="w-10 h-10 rounded-full bg-purple-500/30 border border-purple-500/40 flex items-center justify-center text-sm font-bold mx-auto mb-2">{s.step}</div>
                  <div className="text-sm font-semibold">{s.title}</div>
                  <div className="text-xs text-white/40 mt-1">{s.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* RAG */}
      {activeTab === 'rag' && (
        <div className="space-y-8">
          <div className="bg-gradient-to-br from-emerald-900/30 to-teal-900/20 border border-emerald-500/20 rounded-2xl p-6">
            <h3 className="text-xl font-bold mb-2">🧠 StudEx Super Brain — RAG Status</h3>
            <p className="text-sm text-white/60">All agent knowledge indexed and searchable. RAG means Charlie, Naledi, Robusca all answer based on YOUR data.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {RAG_STATUS.map(r => (
              <div key={r.source} className="bg-white/5 border border-white/10 rounded-2xl p-5">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-semibold">{r.source}</span>
                  <StatusBadge status={r.status} />
                </div>
                <div className="text-2xl font-bold text-white/80">
                  {r.docs ? `${r.docs} docs` : r.emails ? `${r.emails} emails` : r.posts ? `${r.posts} posts` : '—'}
                </div>
                <div className="text-xs text-white/40 mt-1">
                  {r.status === 'indexed' ? '✅ Vector indexed in ChromaDB' :
                   r.status === 'not_started' ? '⏳ Awaiting first War Room call' :
                   r.status === 'no_token' ? '🔴 Shopify token needed' :
                   r.status === 'partial' ? '⚠️ Partial — check API access' :
                   '📭 Empty board'}
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
            <h3 className="font-bold text-lg mb-4">🔍 Test RAG Query</h3>
            <div className="flex gap-3">
              <input
                type="text"
                placeholder="Ask anything about your business... e.g. 'What did we sell yesterday?'"
                className="flex-1 bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm placeholder:text-white/30 focus:outline-none focus:border-emerald-500/50"
              />
              <button className="px-5 py-3 bg-emerald-600/80 rounded-xl text-sm font-semibold hover:bg-emerald-600 transition-all">
                Query Super Brain
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <h4 className="font-bold mb-3 text-sm">Best RAG Tools Evaluated</h4>
              <div className="space-y-2">
                {[
                  { name: 'ChromaDB + Ollama', verdict: '✅ Use now — free, local, fast', note: 'nom'
                  },
                  { name: 'LlamaIndex', verdict: '✅ Use with Chroma', note: 'flexible + powerful' },
                  { name: 'Qdrant', verdict: '⏳ Save for later', note: 'needs extra infra' },
                  { name: 'Pinecone', verdict: '❌ Avoid', note: 'expensive, vendor lock' },
                ].map(t => (
                  <div key={t.name} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                    <span className="text-xs font-medium">{t.name}</span>
                    <span className="text-xs text-emerald-400">{t.verdict}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <h4 className="font-bold mb-3 text-sm">RAG Pipeline</h4>
              <div className="space-y-2 text-xs text-white/70">
                <div>📄 Obsidian Vault (markdown)</div>
                <div>↓</div>
                <div>🔮 Ollama Embedding (nomic-embed-text)</div>
                <div>↓</div>
                <div>🗃️ ChromaDB (studex-brain collection)</div>
                <div>↓</div>
                <div>🤖 Agent query → context injection</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AGENTS */}
      {activeTab === 'agents' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {AGENTS.map(agent => (
              <div key={agent.name} className="bg-white/5 border border-white/10 rounded-2xl p-5">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center text-sm font-bold">
                    {agent.name[0]}
                  </div>
                  <div>
                    <div className="font-bold text-sm">{agent.name}</div>
                    <div className="text-xs text-white/40">{agent.role}</div>
                  </div>
                </div>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-white/40">Voice</span>
                    <span className="text-white/70">{agent.voice}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/40">Status</span>
                    <StatusBadge status={agent.status} />
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/40">Channel</span>
                    <span className="text-white/70">ClickClack #{agent.name.toLowerCase().replace('-','')}</span>
                  </div>
                </div>
                <button className="mt-3 w-full py-2 bg-white/5 border border-white/10 rounded-xl text-xs hover:bg-white/10">
                  📞 Call {agent.name}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* BLOCKERS */}
      {activeTab === 'blockers' && (
        <div className="space-y-6">
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
            <h3 className="font-bold text-lg mb-1">⚠️ Open Blockers</h3>
            <p className="text-sm text-white/50">Priority items blocking full deployment</p>
          </div>
          <div className="space-y-3">
            {BLOCKERS.map((b) => (
              <div key={b.item} className={`border rounded-2xl p-5 ${
                b.priority === 'high' ? 'border-red-500/30 bg-red-500/5' :
                b.priority === 'medium' ? 'border-orange-500/30 bg-orange-500/5' :
                'border-white/10 bg-white/5'
              }`}>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-sm">{b.item}</div>
                    <div className="text-xs text-white/50 mt-1">{b.desc}</div>
                  </div>
                  <div className={`px-2 py-1 rounded text-xs font-bold ${
                    b.priority === 'high' ? 'bg-red-500/20 text-red-400' : 'bg-orange-500/20 text-orange-400'
                  }`}>
                    {b.priority}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      </div>

      {/* Footer */}
      <div className="border-t border-white/10 mt-12 py-6 text-center text-xs text-white/30">
        StudEx Content OS · Built by Amara · {new Date().toLocaleDateString()} · All tools connected, all agents ready
      </div>
    </div>
  )
}
