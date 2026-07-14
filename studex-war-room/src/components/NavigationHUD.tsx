import { useEffect, useState } from 'react';

export type NavTab = 'WAR ROOM' | 'INTEL' | 'WORKFLOW' | 'CONTENT' | 'COFFEE' | 'AGENTS' | 'TASKS' | 'COMMS' | 'BRAIN' | 'PIPELINE';

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

const tabs: NavTab[] = ['BRAIN', 'WAR ROOM', 'INTEL', 'WORKFLOW', 'CONTENT', 'AGENTS', 'COFFEE', 'TASKS', 'COMMS', 'PIPELINE'];

export default function NavigationHUD({ activeTab, onTabChange }: Props) {
  const [time, setTime] = useState(getSASTTime());
  const [date, setDate] = useState(getSASTDate());

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(getSASTTime());
      setDate(getSASTDate());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
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

      {/* Right: Clock + Status */}
      <div className="nav-right">
        <div className="nav-clock">
          <div className="clock-time">{time}</div>
          <div className="clock-label">SAST // JOHANNESBURG</div>
        </div>
        <div className="nav-divider" />
        <div className="nav-status">
          <div className={`status-dot ${true ? 'active' : 'idle'}`} />
          <span className="status-text">SYSTEM ONLINE</span>
        </div>
        <div className="nav-date">{date}</div>
      </div>
    </header>
  );
}
