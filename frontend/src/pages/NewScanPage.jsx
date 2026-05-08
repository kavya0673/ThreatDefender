import { useState, useEffect } from 'react'
import { PlayCircle, Shield, Settings2, Terminal, Layers, Award } from 'lucide-react'
import { useAppStore } from '../store/useAppStore.jsx'

const profiles = [
  { id: 'external', title: 'External Perimeter', description: 'Full network perimeter audit with external asset discovery.' },
  { id: 'app-layer', title: 'Application Security', description: 'Deep application scan with OWASP Top 10 and API checks.' },
  { id: 'privileged', title: 'Privileged Access', description: 'Credentialed audit for identity and access risks.' },
]

export default function NewScanPage() {
  const scans = useAppStore((state) => state.scans)
  const [selected, setSelected] = useState('external')
  const [depth, setDepth] = useState(3)
  const [auth, setAuth] = useState({ sso: true, creds: false, token: false })
  const [progress, setProgress] = useState(0)
  const [running, setRunning] = useState(false)

  const startScan = () => {
    setRunning(true)
    setProgress(8)
  }

  useEffect(() => {
    if (!running) return
    const timer = setInterval(() => {
      setProgress((value) => {
        if (value >= 100) {
          clearInterval(timer)
          setRunning(false)
          return 100
        }
        return value + 7
      })
    }, 450)
    return () => clearInterval(timer)
  }, [running])

  return (
    <div className="page-shell">
      <div className="page-head">
        <div>
          <p className="eyebrow">Scan Orchestration</p>
          <h1>Advanced Vulnerability Discovery</h1>
          <p>Configure enterprise-grade scan profiles, authentication workflows, and advanced targeting.</p>
        </div>
        <div className="hero-pill purple">Multi-target support</div>
      </div>

      <div className="grid-2">
        <section className="glass-card profile-card">
          <div className="card-head">
            <div>
              <h2>Scan Profiles</h2>
              <p>Select an enterprise scan profile with security depth presets.</p>
            </div>
          </div>
          <div className="profile-list">
            {profiles.map((profile) => (
              <button
                key={profile.id}
                className={`profile-item ${selected === profile.id ? 'selected' : ''}`}
                onClick={() => setSelected(profile.id)}
              >
                <div>
                  <strong>{profile.title}</strong>
                  <p>{profile.description}</p>
                </div>
                {selected === profile.id && <span className="selected-pill">Active</span>}
              </button>
            ))}
          </div>

          <div className="scan-config">
            <label>Scan Depth: {depth}</label>
            <input type="range" min="1" max="6" value={depth} onChange={(e) => setDepth(Number(e.target.value))} />
            <div className="scan-options">
              <label><input type="checkbox" checked={auth.sso} onChange={() => setAuth((prev) => ({ ...prev, sso: !prev.sso }))} /> SSO Authentication</label>
              <label><input type="checkbox" checked={auth.creds} onChange={() => setAuth((prev) => ({ ...prev, creds: !prev.creds }))} /> Credentialed Access</label>
              <label><input type="checkbox" checked={auth.token} onChange={() => setAuth((prev) => ({ ...prev, token: !prev.token }))} /> API Token Mode</label>
            </div>
          </div>

          <button className="btn-action" onClick={startScan} disabled={running}>
            <PlayCircle size={18} /> {running ? 'Scanning...' : 'Launch Enterprise Scan'}
          </button>
        </section>

        <section className="glass-card scan-status-card">
          <div className="card-head">
            <div>
              <h2>Scan Queue & Live Logs</h2>
              <p>Monitor active scans and watch live pipeline events.</p>
            </div>
          </div>
          <div className="scan-status">
            {scans.map((scan) => (
              <div key={scan.id} className="scan-entry">
                <strong>{scan.profile}</strong>
                <span>{scan.status}</span>
                <div className="progress-line blue" style={{ width: `${scan.progress}%` }} />
              </div>
            ))}
          </div>
          <div className="terminal-box">
            <div className="terminal-header"><Terminal size={16} /><span>Live engine feed</span></div>
            <div className="terminal-body">
              <p>[11:53:22] Running OWASP Top 10 checks…</p>
              <p>[11:53:46] Validating authentication policy.</p>
              <p>[11:54:05] Discovering new assets behind WAF.</p>
            </div>
          </div>
        </section>
      </div>

      <div className="grid-3">
        <section className="glass-card mini-card">
          <span className="icon-box"><Shield size={18} /></span>
          <div>
            <p>OWASP Coverage</p>
            <strong>100%</strong>
          </div>
        </section>
        <section className="glass-card mini-card">
          <span className="icon-box"><Layers size={18} /></span>
          <div>
            <p>Multi-targets</p>
            <strong>8 Active</strong>
          </div>
        </section>
        <section className="glass-card mini-card">
          <span className="icon-box"><Award size={18} /></span>
          <div>
            <p>Secure Baselines</p>
            <strong>Aligned</strong>
          </div>
        </section>
      </div>
    </div>
  )
}
