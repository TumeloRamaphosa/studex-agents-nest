import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import App from './App'
import CIIE2026 from './CIIE2026'
import SaB2BOnePager from './SaB2BOnePager'

function Navigation() {
  const location = useLocation()
  const isCIIE = location.pathname === '/ciie2026'
  const isB2B = location.pathname === '/b2b'

  if (isCIIE || isB2B) return null

  return (
    <div className="bg-stone-900 border-t border-stone-800 px-8 py-4 text-center">
      <div className="flex items-center justify-center gap-6 text-sm">
        <Link to="/b2b" className="text-stone-400 hover:text-emerald-400 transition">B2B South Africa & UAE →</Link>
        <Link to="/ciie2026" className="text-red-400 hover:text-red-300 transition font-semibold">🇨🇳 CIIE 2026 China Export →</Link>
      </div>
    </div>
  )
}

function CIIEFooter() {
  const location = useLocation()
  if (location.pathname !== '/ciie2026') return null
  return (
    <div className="bg-red-950/30 border-t border-red-900/40 px-8 py-6 text-center">
      <p className="text-red-400 text-sm font-semibold mb-2">🇨🇳 CIIE 2026 · China International Import Expo · Shanghai, Nov 5–10, 2026</p>
      <p className="text-stone-500 text-xs">Studex Meat · Robusca Group (Pty) Ltd · Booth 7.2A-06 · charlie@agent.studexmeat.com</p>
    </div>
  )
}

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<><App /><Navigation /></>} />
        <Route path="/b2b" element={<><SaB2BOnePager /><Navigation /></>} />
        <Route path="/ciie2026" element={<><CIIE2026 /><CIIEFooter /></>} />
      </Routes>
    </BrowserRouter>
  )
}
