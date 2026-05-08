import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar.jsx'
import Topbar from './Topbar.jsx'

export default function Layout() {
  return (
    <div className="enterprise-shell">
      <Sidebar />
      <div className="enterprise-frame">
        <Topbar />
        <main className="enterprise-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
