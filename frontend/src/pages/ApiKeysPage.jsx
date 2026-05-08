import { Key, ShieldCheck, Wifi } from 'lucide-react'
import { useAppStore } from '../store/useAppStore.jsx'

export default function ApiKeysPage() {
  const keys = [
    { id: 1, name: 'Enterprise Integration', created: '2026-04-30', status: 'Active' },
    { id: 2, name: 'Reporting Service', created: '2026-04-15', status: 'Active' },
  ]

  return (
    <div className="page-shell">
      <div className="page-head">
        <div>
          <p className="eyebrow">API Monitoring</p>
          <h1>API Keys & Access Control</h1>
          <p>Manage service keys, monitor API usage, and enforce enterprise access policies.</p>
        </div>
        <div className="hero-pill blue">Secure integration</div>
      </div>

      <div className="grid-3">
        <section className="glass-card api-card">
          <span className="icon-box"><Key size={18} /></span>
          <div>
            <p>Keys issued</p>
            <strong>2</strong>
          </div>
        </section>
        <section className="glass-card api-card">
          <span className="icon-box"><ShieldCheck size={18} /></span>
          <div>
            <p>Policy compliance</p>
            <strong>100%</strong>
          </div>
        </section>
        <section className="glass-card api-card">
          <span className="icon-box"><Wifi size={18} /></span>
          <div>
            <p>Usage today</p>
            <strong>1.2K req</strong>
          </div>
        </section>
      </div>

      <section className="glass-card api-table-card">
        <div className="card-head">
          <div>
            <h2>API Key Inventory</h2>
            <p>Review active keys, rotate secrets, and revoke unused credentials.</p>
          </div>
          <button className="btn-primary">Create New Key</button>
        </div>
        <div className="table-scroll">
          <table className="enterprise-table">
            <thead><tr><th>Name</th><th>Created</th><th>Status</th><th></th></tr></thead>
            <tbody>
              {keys.map((key) => (
                <tr key={key.id}>
                  <td>{key.name}</td>
                  <td>{key.created}</td>
                  <td><span className={`badge ${key.status.toLowerCase()}`}>{key.status}</span></td>
                  <td><button className="btn-secondary">Revoke</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
