import { useState } from 'react'

const sections = [
  {
    id: 'vision',
    icon: '🎯',
    title: 'The Vision',
    content: `A virtual world as our operating system — data centers and software factories where agents walk around as characters, report to the Obsidian knowledge graph, can be spoken to via voice or chat, where our VMs are locations we can fly to, with Linear and Notion integrated, rendered on a game engine.`
  },
  {
    id: 'validation',
    icon: '✅',
    title: 'Validation: Is This Achievable?',
    content: `YES. The individual pieces already exist and work. The challenge is integration, not invention.\n\nWhat you described is three layers working as one:\n• Knowledge Graph / Brain — Obsidian vault, CORE OS memory\n• 3D Immersive World — Data center rooms, walking agents, interactive dashboards\n• Agent Communication — Voice (RileyJarvis), Chat (OpenClaw), Pixel Agents\n• Integrations — Linear, Notion, Tailscale SSH, Shopify\n• Game Engine Rendering — For photorealistic 3D`
  },
  {
    id: 'gameengine',
    icon: '🎮',
    title: 'Game Engine vs Web-Native',
    lines: [
      { label: 'Godot (❌ NOT recommended)', color: 'red', detail: 'Desktop engine — complex web export, no React integration, slow iteration' },
      { label: 'React Three Fiber (✅ YES)', color: 'green', detail: 'Web-native, React dashboards, MCP connectivity, fast iteration, already proven by SEO-OS' },
    ]
  },
  {
    id: 'layers',
    icon: '🏗️',
    title: 'Five-Layer Architecture',
    layers: [
      { name: 'STUDEx OS — Immersive 3D World (R3F)', detail: 'Data Center | War Room | VM Corridors | Agent Characters walking between rooms' },
      { name: 'AGENT LAYER', detail: 'Charlie (CEO) | Naledi (CMO) | Hermes (DevOps) | You (Robusca)' },
      { name: 'CORE OS LAYER', detail: 'Memory knowledge graph, 50+ MCP connectors: Linear | Notion | Shopify | Tailscale | GitHub' },
      { name: 'VOICE LAYER', detail: 'RileyJarvis (OpenAI Realtime API) | ElevenLabs voice synthesis' },
      { name: 'DATA LAYER', detail: 'Shopify orders, Meta ads, AgentMail, War Room — all live KPIs as 3D dashboard panels' },
    ]
  },
  {
    id: 'navigation',
    icon: '🗺️',
    title: 'Navigation: How Flying to VMs Works',
    portals: [
      { name: 'Orgo VM (Meat Auto)', location: '67.213.119.157', detail: 'Live: War Room dashboard, VM stats, n8n workflows' },
      { name: 'RileyJarvis MacBook', location: 'Tailscale tailnet', detail: 'Live: Desktop camera, file access, voice input' },
      { name: 'Cursor / Devin', location: 'AI coding VMs', detail: 'Live: Code being written, terminal output' },
      { name: 'Studex Website', location: 'Public VM', detail: 'Live: Traffic, orders, analytics dashboards' },
      { name: 'Naledi Content Studio', location: 'Content pipeline', detail: 'Live: Content queue, scheduled posts, Meta scheduling' },
    ]
  },
  {
    id: 'integrations',
    icon: '🔌',
    title: 'Integrations Map',
    table: [
      { service: 'Obsidian Vault', status: '✅ Working', note: 'Filesystem reads via Node.js' },
      { service: 'CORE OS', status: '🔶 Clone needed', note: 'MCP server, gateway-protocol' },
      { service: 'Pixel Agents', status: '🔶 Setup needed', note: 'HTTP POST hooks to Fastify server' },
      { service: 'RileyJarvis', status: '🔶 Mac needed', note: 'OpenAI Realtime API + macOS permissions' },
      { service: 'Linear', status: '❌ No key', note: 'Linear API v2024.10.0' },
      { service: 'Notion', status: '❌ No key', note: 'Notion API' },
      { service: 'Tailscale', status: '🔶 API key needed', note: 'Tailscale API + SSH' },
      { service: 'Shopify', status: '❌ No token', note: 'Admin API' },
      { service: 'AgentMail', status: '🔶 DNS pending', note: 'REST API' },
      { service: 'Meta/Facebook', status: '❌ Token expired', note: 'Graph API' },
    ]
  },
  {
    id: 'phases',
    icon: '🗓️',
    title: 'Phased Build Plan',
    phases: [
      { phase: 'PHASE 1', timeline: 'This Week', goal: 'Running 3D world with live data', tasks: ['Upgrade War Room to underwater datacenter theme', 'Connect live Shopify KPIs as floating 3D panels', 'Deploy studex-os full system to new URL', 'Get foundation solid'] },
      { phase: 'PHASE 2', timeline: 'Week 2', goal: 'Agent characters visible & working', tasks: ['Install Pixel Agents on Orgo VM', 'Connect hooks to Charlie + Naledi sub-agents', 'Add 3D avatar panels in War Room', 'Build agent status dock — who is active and doing what'] },
      { phase: 'PHASE 3', timeline: 'Week 3', goal: 'Voice layer — talk to any agent', tasks: ['Set up OpenAI Realtime API (RileyJarvis or War Room panel)', 'Connect voice → Charlie orchestrator → assigns tasks', 'Agent responses read aloud via ElevenLabs'] },
      { phase: 'PHASE 4', timeline: 'Week 4+', goal: 'Full world — fly between VMs', tasks: ['Build portal corridors between VMs via Tailscale SSH', 'Add Linear and Notion as 3D panel rooms', 'Build VM corridor — Orgo, MacBook, Cursor as navigable spaces', 'Particle effects, animations, ambient motion'] },
    ]
  },
  {
    id: 'risks',
    icon: '⚠️',
    title: 'Risks & Honest Assessment',
    risks: [
      { risk: 'Pixel Agents + R3F character rendering conflict', likelihood: 'Medium', mitigation: 'Use R3F for world, Pixel Agents for desktop overlay (separate surfaces)' },
      { risk: 'Voice latency kills immersion', likelihood: 'High', mitigation: 'Use push-to-talk, not continuous streaming' },
      { risk: 'Tailscale SSH to MacBook unreliable', likelihood: 'Medium', mitigation: 'Use macOS Screen Sharing + VNC as fallback' },
      { risk: 'Too many live connections at once', likelihood: 'Medium', mitigation: 'Build one room well first before expanding' },
    ]
  },
  {
    id: 'next',
    icon: '🚀',
    title: 'Next Action',
    action: 'PHASE 1 — Upgrade the War Room to underwater datacenter theme, connect live Shopify data, deploy. Get the foundation solid before Phase 2.'
  }
]

function App() {
  const [activeSection, setActiveSection] = useState('vision')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const section = sections.find(s => s.id === activeSection) || sections[0]

  return (
    <div style={{
      display: 'flex',
      height: '100vh',
      background: '#0a0a0f',
      color: '#e0e0e0',
      fontFamily: 'Inter, system-ui, sans-serif',
      overflow: 'hidden'
    }}>
      {/* Sidebar */}
      <div style={{
        width: sidebarOpen ? 260 : 60,
        background: '#111118',
        borderRight: '1px solid #1e1e2e',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 0.3s',
        overflowY: 'auto'
      }}>
        <div style={{ padding: '20px 16px', borderBottom: '1px solid #1e1e2e' }}>
          <div style={{ fontSize: 11, color: '#00ff88', fontWeight: 700, letterSpacing: 2, marginBottom: 4 }}>STUDEX OS</div>
          <div style={{ fontSize: 13, color: '#888', fontWeight: 500 }}>Architecture Plan</div>
          <div style={{ fontSize: 10, color: '#444', marginTop: 4 }}>v1.0 — July 3, 2026</div>
        </div>
        {sections.map(s => (
          <button
            key={s.id}
            onClick={() => setActiveSection(s.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '10px 16px',
              background: activeSection === s.id ? '#1a2e1a' : 'transparent',
              color: activeSection === s.id ? '#00ff88' : '#888',
              border: 'none',
              borderLeft: activeSection === s.id ? '2px solid #00ff88' : '2px solid transparent',
              cursor: 'pointer',
              textAlign: 'left',
              fontSize: 12,
              fontWeight: activeSection === s.id ? 600 : 400,
              transition: 'all 0.2s'
            }}
          >
            <span style={{ fontSize: 14 }}>{s.icon}</span>
            {sidebarOpen && <span>{s.title}</span>}
          </button>
        ))}
        <div style={{ flex: 1 }} />
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          style={{
            padding: '12px 16px',
            background: '#0f0f14',
            border: 'none',
            borderTop: '1px solid #1e1e2e',
            color: '#555',
            cursor: 'pointer',
            fontSize: 11,
            textAlign: 'center'
          }}
        >
          {sidebarOpen ? '◀ Collapse' : '▶ Expand'}
        </button>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '40px 48px', maxWidth: 900 }}>
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 11, color: '#00ff88', fontWeight: 700, letterSpacing: 2, marginBottom: 8 }}>STUDEX OS — IMMERSIVE VIRTUAL WORLD</div>
          <h1 style={{ fontSize: 32, fontWeight: 700, color: '#fff', margin: 0, lineHeight: 1.2 }}>
            {section.icon} {section.title}
          </h1>
          <div style={{ width: 40, height: 3, background: '#00ff88', marginTop: 16, borderRadius: 2 }} />
        </div>

        <div style={{ fontSize: 14, lineHeight: 1.8, color: '#b0b0b0' }}>
          {section.content && section.content.split('\n\n').map((p, i) => (
            <p key={i} style={{ marginBottom: 12 }}>{p}</p>
          ))}
        </div>

        {section.lines && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {section.lines.map((l, i) => (
              <div key={i} style={{
                padding: '14px 18px',
                background: l.color === 'red' ? '#2a0a0a' : '#0a2a1a',
                border: `1px solid ${l.color === 'red' ? '#ff4444' : '#00ff88'}`,
                borderRadius: 8,
                fontSize: 13
              }}>
                <div style={{ color: l.color === 'red' ? '#ff6666' : '#00ff88', fontWeight: 700, marginBottom: 4 }}>{l.label}</div>
                <div style={{ color: '#888' }}>{l.detail}</div>
              </div>
            ))}
          </div>
        )}

        {section.layers && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {section.layers.map((l, i) => (
              <div key={i} style={{
                padding: '14px 18px',
                background: i % 2 === 0 ? '#0f0f1a' : '#141420',
                borderLeft: '3px solid #00ff88',
                borderRadius: '0 6px 6px 0'
              }}>
                <div style={{ color: '#00ff88', fontWeight: 700, fontSize: 12, marginBottom: 4 }}>{l.name}</div>
                <div style={{ color: '#888', fontSize: 12 }}>{l.detail}</div>
              </div>
            ))}
          </div>
        )}

        {section.portals && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {section.portals.map((p, i) => (
              <div key={i} style={{
                padding: '14px 18px',
                background: '#0f0f1a',
                border: '1px solid #1e2e3e',
                borderRadius: 8,
                display: 'flex',
                alignItems: 'center',
                gap: 16
              }}>
                <div style={{ fontSize: 20 }}>🚀</div>
                <div style={{ flex: 1 }}>
                  <div style={{ color: '#fff', fontWeight: 700, fontSize: 13 }}>{p.name}</div>
                  <div style={{ color: '#00ff88', fontSize: 11, fontFamily: 'monospace', marginTop: 2 }}>{p.location}</div>
                  <div style={{ color: '#666', fontSize: 11, marginTop: 4 }}>{p.detail}</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {section.table && (
          <div style={{ border: '1px solid #1e1e2e', borderRadius: 8, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
              <thead>
                <tr style={{ background: '#111118' }}>
                  <th style={{ padding: '10px 14px', textAlign: 'left', color: '#00ff88', borderBottom: '1px solid #1e1e2e' }}>Service</th>
                  <th style={{ padding: '10px 14px', textAlign: 'left', color: '#00ff88', borderBottom: '1px solid #1e1e2e' }}>Status</th>
                  <th style={{ padding: '10px 14px', textAlign: 'left', color: '#00ff88', borderBottom: '1px solid #1e1e2e' }}>Note</th>
                </tr>
              </thead>
              <tbody>
                {section.table.map((row, i) => (
                  <tr key={i} style={{ background: i % 2 === 0 ? '#0a0a0f' : '#0f0f14' }}>
                    <td style={{ padding: '8px 14px', color: '#ccc', borderBottom: '1px solid #1a1a24' }}>{row.service}</td>
                    <td style={{ padding: '8px 14px', color: row.status.includes('❌') ? '#ff6666' : row.status.includes('✅') ? '#00ff88' : '#ffaa00', borderBottom: '1px solid #1a1a24' }}>{row.status}</td>
                    <td style={{ padding: '8px 14px', color: '#666', borderBottom: '1px solid #1a1a24' }}>{row.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {section.phases && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {section.phases.map((p, i) => (
              <div key={i} style={{
                padding: 20,
                background: '#0f0f1a',
                border: '1px solid #1e2e3e',
                borderRadius: 10,
                borderTop: `3px solid ${['#00ff88','#00aaff','#ffaa00','#aa88ff'][i]}`
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                  <span style={{ fontSize: 10, fontWeight: 800, color: '#fff', background: '#1a1a2e', padding: '3px 8px', borderRadius: 4 }}>{p.phase}</span>
                  <span style={{ fontSize: 11, color: '#666' }}>{p.timeline}</span>
                </div>
                <div style={{ color: '#fff', fontWeight: 700, fontSize: 14, marginBottom: 10 }}>{p.goal}</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  {p.tasks.map((t, j) => (
                    <div key={j} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: '#999' }}>
                      <span style={{ color: '#00ff88', fontSize: 8 }}>▸</span> {t}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {section.risks && (
          <div style={{ border: '1px solid #1e1e2e', borderRadius: 8, overflow: 'hidden' }}>
            {section.risks.map((r, i) => (
              <div key={i} style={{
                padding: '12px 16px',
                background: i % 2 === 0 ? '#0a0a0f' : '#0f0f14',
                borderBottom: i < section.risks.length - 1 ? '1px solid #1a1a24' : 'none'
              }}>
                <div style={{ color: '#fff', fontWeight: 600, fontSize: 13, marginBottom: 4 }}>{r.risk}</div>
                <div style={{ display: 'flex', gap: 16, fontSize: 11 }}>
                  <span style={{ color: r.likelihood === 'High' ? '#ff6666' : '#ffaa00' }}>⚠ {r.likelihood}</span>
                  <span style={{ color: '#888' }}>Fix: {r.mitigation}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {section.action && (
          <div style={{
            padding: '24px 28px',
            background: 'linear-gradient(135deg, #0a2a1a 0%, #0a1a2a 100%)',
            border: '1px solid #00ff88',
            borderRadius: 12
          }}>
            <div style={{ color: '#00ff88', fontWeight: 700, fontSize: 13, marginBottom: 8 }}>🚀 RECOMMENDED NEXT STEP</div>
            <div style={{ color: '#ccc', fontSize: 14, lineHeight: 1.7 }}>{section.action}</div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
