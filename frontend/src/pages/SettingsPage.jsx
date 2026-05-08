import { useState } from 'react'
import { Settings2, ShieldCheck, Bell, Users2 } from 'lucide-react'

export default function SettingsPage() {
  const [accessMode, setAccessMode] = useState('role-based')

  return (
    <div className="page-shell">
      <div className="page-head">
        <div>
          <p className="eyebrow">Platform Control</p>
          <h1>Enterprise Settings</h1>
          <p>Configure access, notifications, and audit trails for SOC teams and compliance workflows.</p>
        </div>
        <div className="hero-pill gray">Role-based UI</div>
      </div>

      <div className="grid-2">
        <section className="glass-card settings-card">
          <div className="card-head">
            <div>
              <h2>Access Management</h2>
              <p>Define roles, permissions, and service level access for analysts.</p>
            </div>
          </div>
          <div className="settings-list">
            <label className={accessMode === 'role-based' ? 'option active' : 'option'}>
              <input type="radio" name="access" checked={accessMode === 'role-based'} onChange={() => setAccessMode('role-based')} />
              <div>
                <strong>Role-based Access</strong>
                <span>Least privilege policies for teams.</span>
              </div>
            </label>
            <label className={accessMode === 'policy-driven' ? 'option active' : 'option'}>
              <input type="radio" name="access" checked={accessMode === 'policy-driven'} onChange={() => setAccessMode('policy-driven')} />
              <div>
                <strong>Policy-based Controls</strong>
                <span>Automated enforcement of security policies.</span>
              </div>
            </label>
          </div>
        </section>

        <section className="glass-card settings-card">
          <div className="card-head">
            <div>
              <h2>Audit & Notifications</h2>
              <p>Review logs, alerts, and workflow automation settings.</p>
            </div>
          </div>
          <div className="settings-summary">
            <div><Bell size={18} /><span>Active alerts</span><strong>18</strong></div>
            <div><ShieldCheck size={18} /><span>Audit logs</span><strong>Enabled</strong></div>
            <div><Users2 size={18} /><span>Team seats</span><strong>24</strong></div>
          </div>
        </section>
      </div>

      <section className="glass-card policy-card">
        <div className="card-head">
          <div>
            <h2>Global Filters & UI</h2>
            <p>Save global filters for environment scopes and manage SOC display preferences.</p>
          </div>
          <button className="btn-secondary">Edit Filters</button>
        </div>
        <div className="policy-grid">
          <div><strong>Asset groups</strong><span>Critical only</span></div>
          <div><strong>Regions</strong><span>APAC, EMEA</span></div>
          <div><strong>Threat feeds</strong><span>Enabled</span></div>
          <div><strong>Dashboard mode</strong><span>Dark</span></div>
        </div>
      </section>
    </div>
  )
}
