import { NavLink } from 'react-router-dom'
import { ShieldAlert, PlayCircle, Bug, Globe2, FileText, Key, SlidersHorizontal } from 'lucide-react'
import { useAppStore } from '../store/useAppStore.jsx'

const NAV_LINKS = [
  { path: '/', icon: ShieldAlert, label: 'Dashboard' },
  { path: '/scan', icon: PlayCircle, label: 'New Scan' },
  { path: '/findings', icon: Bug, label: 'Findings' },
  { path: '/attack-map', icon: Globe2, label: 'Attack Map' },
  { path: '/reports', icon: FileText, label: 'Reports' },
  { path: '/api-keys', icon: Key, label: 'API Keys' },
  { path: '/settings', icon: SlidersHorizontal, label: 'Settings' },
]

export default function Sidebar() {
  const findings = useAppStore((state) => state.findings)

  return (
    <aside className="enterprise-sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">TD</div>
        <div className="brand-copy">
          <span>ThreatDefender</span>
          <strong>Enterprise SOC</strong>
        </div>
      </div>

      <div className="sidebar-nav">
        <div className="nav-title">Main</div>
        {NAV_LINKS.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={18} />
              <span>{item.label}</span>
              {item.path === '/findings' && findings.length > 0 && (
                <span className="nav-badge">{findings.length}</span>
              )}
            </NavLink>
          )
        })}
      </div>

      <div className="sidebar-status">
        <div className="status-pill online">Scanner Online</div>
        <div className="status-pill light">4 Workers</div>
      </div>

      <div className="sidebar-footer">
        <div>
          <p>Admin User</p>
          <span>Enterprise Plan</span>
        </div>
      </div>
    </aside>
  )
}
