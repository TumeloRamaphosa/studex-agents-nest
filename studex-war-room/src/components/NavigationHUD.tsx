import { useEffect, useState } from 'react';

export type NavTab = 'WAR ROOM' | 'INTEL' | 'WORKFLOW' | 'WORKFLOWS' | 'CONTENT' | 'COFFEE' | 'AGENTS' | 'TASKS' | 'COMMS' | 'BRAIN' | 'PIPELINE' | 'OUTREACH' | 'WARMUP' | 'BOOTH' | 'CAVIAR';

interface Props {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
}

function getSASTTime(): string {
  const now = new Date();
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const saTime = new Date(utc + 2 * 60 * 60 * 1000);
  return saTime.toLocaleTimeString('en-ZA', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

function getSASTDate(): string {
  const now = new Date();
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const saTime = new Date(utc + 2 * 60 * 60 * 1000);
  return saTime.toLocaleDateString('en-ZA', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function getCIIEDays(): number {
  const ciie = new Date('2026-11-05T00:00:00+02:00');
  const now = new Date();
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const saTime = new Date(utc + 2 * 60 * 60 * 1000);
  return Math.ceil((ciie.getTime() - saTime.getTime()) / 86400000);
}

const tabs: NavTab[] = ['BRAIN', 'WAR ROOM', 'INTEL', 'WORKFLOW', 'WORKFLOWS', 'CONTENT', 'AGENTS', 'COFFEE', 'OUTREACH', 'BOOTH', 'TASKS', 'COMMS', 'PIPELINE', 'WARMUP', 'CAVIAR'];

export default function NavigationHUD({ activeTab, onTabChange }: Props) {
  const [time, setTime] = useState(getSASTTime());
  const [date, setDate] = useState(getSASTDate());
  const [ciieDays, setCiieDays] = useState(getCIIEDays());

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(getSASTTime());
      setDate(getSASTDate());
      setCiieDays(getCIIEDays());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const ciieUrgent = ciieDays <= 10;
  const ciieSoon = ciieDays <= 20;

  return (
    <>
      {/* CIIE Countdown Banner */}
      {ciieDays > 0 && (
        <div
          className="ciie-banner"
          style={{
            background: ciieUrgent ? '#ff4444' : ciieSoon ? '#d4a017' : '#4a9eff',
            color: '#fff',
            textAlign: 'center',
            padding: '5px 16px',
            fontSize: '11px',
            fontWeight: 700,
            letterSpacing: '0.08em',
            cursor: 'pointer',
          }}
          onClick={() => onTabChange('BOOTH')}
          title="Go to CIIE Booth Application"
        >
          🚨 CIIE SHANGHAI 2026 — {ciieDays} DAY{ciieDays !== 1 ? 'S' : ''} UNTIL NOV 5 — CATALOG PDF + BOOTH APPLICATION URGENT ⬅ CLICK HERE
        </div>
      )}
      <header className="nav-hud">
      {/* Left: Logo + Title */}
      <div className="nav-left">
        <div className="nav-logo">
          <span className="nav-logo-icon">🥩</span>
          <div className="nav-logo-text">
            <span className="nav-title">STUDEX</span>
            <span className="nav-subtitle">OS v1.0 // PHASE 1</span>
          </div>
        </div>
      </div>

      {/* Center: Navigation Tabs */}
      <nav className="nav-tabs">
        {tabs.map(tab => (
          <button
            key={tab}
            className={`nav-tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => onTabChange(tab)}
          >
            {tab}
          </button>
        ))}
      </nav>

      {/* Right: Status cluster + Clock */}
      <div className="nav-status-cluster">
        {/* Status indicators — taste-skill semantic colors */}
        <div className="status-indicator">
          <div className="dot ok" />
          <span>DISCORD</span>
        </div>
        <div className="status-indicator">
          <div className="dot warn" />
          <span>SHOPIFY</span>
        </div>
        <div className="status-indicator">
          <div className="dot crit" />
          <span>META</span>
        </div>
        <div className="status-indicator">
          <div className="dot off" />
          <span>AGENTMAIL</span>
        </div>
        <div className="nav-divider" />
        <div className="nav-clock">
          <div className="clock-time">{time}</div>
          <div className="clock-label">SAST // JHB</div>
        </div>
        <div className="nav-date">{date}</div>
      </div>
    </header>
    </>
  );
}
