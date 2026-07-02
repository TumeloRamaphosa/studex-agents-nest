import { useState } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';

const tokenData = [
  { name: 'Mon', input: 4200, output: 1800, saved: 1200 },
  { name: 'Tue', input: 3800, output: 1600, saved: 2100 },
  { name: 'Wed', input: 5100, output: 2200, saved: 1900 },
  { name: 'Thu', input: 2900, output: 1200, saved: 2800 },
  { name: 'Fri', input: 4600, output: 2000, saved: 1600 },
  { name: 'Sat', input: 1800, output: 800, saved: 3200 },
  { name: 'Sun', input: 2200, output: 900, saved: 2900 },
];

const projectCompare = [
  { project: 'studex-war-room', tokens: 3400000, color: '#4a9eff' },
  { project: 'robusca-brain', tokens: 2100000, color: '#d4a017' },
  { project: 'nest agents', tokens: 890000, color: '#3a3aff' },
  { project: 'content-hub', tokens: 560000, color: '#cc88ff' },
  { project: 'openwolf-enabled', tokens: 425000, color: '#44ffaa' },
];

const recentSessions = [
  { id: 'sess_001', project: 'studex-war-room', duration: '12m', tokens: 48200, status: 'saved', saved: 16100 },
  { id: 'sess_002', project: 'robusca-brain', duration: '8m', tokens: 22100, status: 'saved', saved: 9400 },
  { id: 'sess_003', project: 'nest agents', duration: '23m', tokens: 87400, status: 'saved', saved: 38200 },
  { id: 'sess_004', project: 'content-hub', duration: '5m', tokens: 11400, status: 'active', saved: 0 },
  { id: 'sess_005', project: 'studex-war-room', duration: '31m', tokens: 128600, status: 'saved', saved: 51400 },
];

const topFiles = [
  { path: 'WarRoomCanvas.tsx', reads: 24, tokens: 8820 },
  { path: 'App.tsx', reads: 18, tokens: 6340 },
  { path: 'NavigationHUD.tsx', reads: 12, tokens: 4180 },
  { path: 'OpsDashboard.tsx', reads: 9, tokens: 3120 },
  { path: 'index.css', reads: 7, tokens: 2140 },
];

type IntelTab = 'OVERVIEW' | 'PROJECTS' | 'SESSIONS' | 'FILES' | 'SETUP';

export default function IntelPanel() {
  const [activeTab, setActiveTab] = useState<IntelTab>('OVERVIEW');

  const tabs: IntelTab[] = ['OVERVIEW', 'PROJECTS', 'SESSIONS', 'FILES', 'SETUP'];

  return (
    <div className="intel-panel">
      {/* Header */}
      <div className="intel-header">
        <div className="intel-logo">
          <span className="intel-logo-icon">🐺</span>
          <div>
            <div className="intel-title">OPENWOLF</div>
            <div className="intel-subtitle">TOKEN INTELLIGENCE</div>
          </div>
        </div>
        <div className="intel-live-badge">
          <span className="live-dot" />
          LIVE
        </div>
      </div>

      {/* Tab Nav */}
      <div className="intel-tabs">
        {tabs.map(t => (
          <button
            key={t}
            className={`intel-tab ${activeTab === t ? 'active' : ''}`}
            onClick={() => setActiveTab(t)}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="intel-content">

        {activeTab === 'OVERVIEW' && (
          <div className="intel-overview">
            {/* KPI Cards */}
            <div className="intel-kpis">
              <div className="intel-kpi">
                <div className="kpi-label">TOTAL TOKENS</div>
                <div className="kpi-value">7.2M</div>
                <div className="kpi-delta up">↑ 12% vs last week</div>
              </div>
              <div className="intel-kpi">
                <div className="kpi-label">OPENWOLF SAVINGS</div>
                <div className="kpi-value gold">65.8%</div>
                <div className="kpi-delta down">↓ avg across 20 projects</div>
              </div>
              <div className="intel-kpi">
                <div className="kpi-label">READS BLOCKED</div>
                <div className="kpi-value">71%</div>
                <div className="kpi-delta neutral">of repeated reads caught</div>
              </div>
              <div className="intel-kpi">
                <div className="kpi-label">SESSIONS TRACKED</div>
                <div className="kpi-value">132+</div>
                <div className="kpi-delta neutral">across all projects</div>
              </div>
            </div>

            {/* Charts Row */}
            <div className="intel-charts">
              <div className="intel-chart-card">
                <div className="chart-title">USAGE OVER TIME — LAST 7 DAYS</div>
                <ResponsiveContainer width="100%" height={180}>
                  <LineChart data={tokenData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(212,160,23,0.1)" />
                    <XAxis dataKey="name" stroke="#7a8099" fontSize={11} />
                    <YAxis stroke="#7a8099" fontSize={11} />
                    <Tooltip
                      contentStyle={{
                        background: '#0d1422', border: '1px solid rgba(212,160,23,0.4)',
                        color: '#e8e8f0', borderRadius: 8, fontSize: 12
                      }}
                    />
                    <Line type="monotone" dataKey="input" stroke="#4a9eff" strokeWidth={2} dot={false} name="Input" />
                    <Line type="monotone" dataKey="output" stroke="#d4a017" strokeWidth={2} dot={false} name="Output" />
                    <Line type="monotone" dataKey="saved" stroke="#44ffaa" strokeWidth={2} dot={false} name="Saved" />
                  </LineChart>
                </ResponsiveContainer>
                <div className="chart-legend">
                  <span className="legend-item"><span className="dot" style={{ background: '#4a9eff' }} />Input</span>
                  <span className="legend-item"><span className="dot" style={{ background: '#d4a017' }} />Output</span>
                  <span className="legend-item"><span className="dot" style={{ background: '#44ffaa' }} />Saved</span>
                </div>
              </div>

              <div className="intel-chart-card">
                <div className="chart-title">TOKEN COMPARISON</div>
                <ResponsiveContainer width="100%" height={180}>
                  <BarChart data={projectCompare} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(212,160,23,0.1)" horizontal={false} />
                    <XAxis type="number" stroke="#7a8099" fontSize={11} tickFormatter={v => `${(v/1e6).toFixed(1)}M`} />
                    <YAxis type="category" dataKey="project" stroke="#7a8099" fontSize={10} width={100} />
                    <Tooltip
                      contentStyle={{
                        background: '#0d1422', border: '1px solid rgba(212,160,23,0.4)',
                        color: '#e8e8f0', borderRadius: 8, fontSize: 12
                      }}
                      formatter={(v: number) => [`${(v/1e6).toFixed(2)}M tokens`, 'Total']}
                    />
                    <Bar dataKey="tokens" fill="#d4a017" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Wolf Status */}
            <div className="intel-wolf-status">
              <div className="wolf-status-item">
                <span className="wolf-dot active" />
                <span>Cerebrum.md — 48 entries</span>
              </div>
              <div className="wolf-status-item">
                <span className="wolf-dot active" />
                <span>anatomy.md — 124 files mapped</span>
              </div>
              <div className="wolf-status-item">
                <span className="wolf-dot active" />
                <span>buglog.json — 23 known fixes</span>
              </div>
              <div className="wolf-status-item">
                <span className="wolf-dot active" />
                <span>token-ledger.json — synced</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'PROJECTS' && (
          <div className="intel-section">
            <div className="section-header">PROJECT TOKEN LEDGER</div>
            <div className="project-list">
              {projectCompare.map(p => (
                <div key={p.project} className="project-row">
                  <div className="project-name">{p.project}</div>
                  <div className="project-bar-wrap">
                    <div className="project-bar" style={{
                      width: `${(p.tokens / 3400000) * 100}%`,
                      background: p.color
                    }} />
                  </div>
                  <div className="project-tokens">{(p.tokens / 1e6).toFixed(2)}M</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'SESSIONS' && (
          <div className="intel-section">
            <div className="section-header">RECENT SESSIONS</div>
            <table className="intel-table">
              <thead>
                <tr>
                  <th>Session</th>
                  <th>Project</th>
                  <th>Duration</th>
                  <th>Tokens</th>
                  <th>Saved</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentSessions.map(s => (
                  <tr key={s.id}>
                    <td className="mono">{s.id}</td>
                    <td>{s.project}</td>
                    <td className="mono">{s.duration}</td>
                    <td className="mono">{(s.tokens / 1e3).toFixed(1)}K</td>
                    <td className="mono green">{s.saved > 0 ? `${(s.saved / 1e3).toFixed(1)}K` : '—'}</td>
                    <td>
                      <span className={`status-badge ${s.status}`}>{s.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'FILES' && (
          <div className="intel-section">
            <div className="section-header">HOT FILES — MOST READ</div>
            <table className="intel-table">
              <thead>
                <tr>
                  <th>File Path</th>
                  <th>Reads</th>
                  <th>Tokens</th>
                  <th>Density</th>
                </tr>
              </thead>
              <tbody>
                {topFiles.map(f => (
                  <tr key={f.path}>
                    <td className="mono">{f.path}</td>
                    <td className="mono">{f.reads}x</td>
                    <td className="mono">{(f.tokens / 1e3).toFixed(1)}K</td>
                    <td>
                      <div className="density-bar">
                        <div className="density-fill" style={{ width: `${(f.reads / 24) * 100}%` }} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'SETUP' && (
          <div className="intel-section">
            <div className="section-header">OPENWOLF INSTALLATION</div>
            <div className="setup-card">
              <pre className="setup-code">{`# Install globally
npm install -g openwolf

# Navigate to project
cd /workspace/robusca-brain

# Initialize OpenWolf
openwolf init

# Start the dashboard
openwolf dashboard

# Run a design QC
openwolf designqc`}</pre>
              <div className="setup-status">
                <div className="setup-req">
                  <span className="req-icon ok">✓</span>
                  <span>Node.js 20+ installed</span>
                </div>
                <div className="setup-req">
                  <span className="req-icon ok">✓</span>
                  <span>Claude Code CLI detected</span>
                </div>
                <div className="setup-req">
                  <span className="req-icon pending">○</span>
                  <span>.wolf/ directory — not initialized</span>
                </div>
              </div>
              <button className="setup-btn">
                ▶ RUN openwolf init
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
