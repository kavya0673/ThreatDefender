import { Search, Bell, Moon, Sun, Activity } from 'lucide-react'
import { useAppStore } from '../store/useAppStore.jsx'

export default function Topbar() {
  const theme = useAppStore((state) => state.theme)
  const toggleTheme = useAppStore((state) => state.toggleTheme)
  const notifications = useAppStore((state) => state.notifications)

  return (
    <header className="enterprise-topbar">
      <div className="topbar-search">
        <Search size={16} />
        <input type="search" placeholder="Search threats, assets, reports..." />
      </div>
      <div className="topbar-actions">
        <button className="icon-btn" title="Notifications">
          <Bell size={18} />
          {notifications.length > 0 && <span className="notification-dot" />}
        </button>
        <button className="icon-btn" title="Theme toggle" onClick={toggleTheme}>
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <div className="topbar-chip">
          <Activity size={14} />
          <span>Live</span>
        </div>
      </div>
    </header>
  )
}
