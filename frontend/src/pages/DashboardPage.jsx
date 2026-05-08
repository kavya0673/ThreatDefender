import { BarChart3, ShieldCheck, Clock3, Layers, Activity, TrendingUp, Sparkles } from 'lucide-react'
import { useAppStore } from '../store/useAppStore.jsx'

function MetricTile({ icon: Icon, label, value, trend, detail, accent }) {
  return (
    <div className={`metric-tile ${accent}`}>
      <div className="metric-icon"><Icon size={20} /></div>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
      </div>
      {trend && <span className="metric-trend">{trend}</span>}
      {detail && <small>{detail}</small>}
    </div>
  )
}

export default function DashboardPage() {
  const findings = useAppStore((state) => state.findings)
  const scans = useAppStore((state) => state.scans)
  const assets = useAppStore((state) => state.assets)

  const critical = findings.filter((item) => item.severity === 'Critical').length
  const high = findings.filter((item) => item.severity === 'High').length
  const medium = findings.filter((item) => item.severity === 'Medium').length
  const low = findings.filter((item) => item.severity === 'Low').length
  const open = findings.filter((item) => item.status === 'Open').length

  return (
    <div className="page-shell">
      <div className="page-head">
        <div>
          <p className="eyebrow">SOC Command Center</p>
          <h1>Enterprise Vulnerability Management</h1>
          <p>Live threat telemetry, attack surface analytics, and remediation intelligence in a single pane.</p>
        </div>
        <div className="hero-pill">Real-time posture: <strong>Protected</strong></div>
      </div>

      <div className="grid-4">
        <MetricTile icon={ShieldCheck} label="Risk Score" value="78" trend="+5%" detail="Threats contained" accent="red" />
        <MetricTile icon={BarChart3} label="Active Scans" value={`${scans.length}`} trend="2 Running" detail="Queue depth 3" accent="blue" />
        <MetricTile icon={Activity} label="Open Findings" value={`${findings.length}`} trend={`${open} Active`} detail="High risk prioritized" accent="orange" />
        <MetricTile icon={Layers} label="Top Assets" value={`${assets.length}`} trend="4 Critical" detail="Business-critical coverage" accent="green" />
      </div>

      <div className="grid-3">
        <section className="glass-card chart-card">
          <div className="card-head">
            <div>
              <h2>Threat Severity Distribution</h2>
              <p>Real-time severity breakdown across the environment.</p>
            </div>
            <span className="tag">Live</span>
          </div>
          <div className="severity-bars">
            <div><span>Critical</span><strong>{critical}</strong><div className="progress-line critical" style={{ width: `${Math.min(critical * 16, 100)}%` }} /></div>
            <div><span>High</span><strong>{high}</strong><div className="progress-line high" style={{ width: `${Math.min(high * 14, 100)}%` }} /></div>
            <div><span>Medium</span><strong>{medium}</strong><div className="progress-line medium" style={{ width: `${Math.min(medium * 12, 100)}%` }} /></div>
            <div><span>Low</span><strong>{low}</strong><div className="progress-line low" style={{ width: `${Math.min(low * 10, 100)}%` }} /></div>
          </div>
        </section>

        <section className="glass-card activity-card">
          <div className="card-head">
            <div>
              <h2>Scan Activity Timeline</h2>
              <p>Latest enterprise scan events and processing milestones.</p>
            </div>
          </div>
          <ul className="timeline-list">
            <li><strong>12:05</strong> Scanned perimeter gateway with 18 endpoints.</li>
            <li><strong>11:58</strong> New external scan queued for critical assets.</li>
            <li><strong>11:42</strong> Rule pack updated with new OWASP indicators.</li>
            <li><strong>11:18</strong> AI analysis classified 6 new findings.</li>
          </ul>
        </section>

        <section className="glass-card status-card">
          <div className="card-head">
            <div>
              <h2>System Status</h2>
              <p>Platform telemetry and active monitoring indicators.</p>
            </div>
          </div>
          <div className="status-grid">
            <div><span>Data Pipeline</span><strong>Healthy</strong></div>
            <div><span>Threat Feeds</span><strong>Up-to-date</strong></div>
            <div><span>API Services</span><strong>99.99%</strong></div>
            <div><span>SOC Queue</span><strong>{scans.length} Jobs</strong></div>
          </div>
        </section>
      </div>

      <div className="grid-2">
        <section className="glass-card asset-card">
          <div className="card-head">
            <div>
              <h2>Top Vulnerable Assets</h2>
              <p>Assets with the highest risk exposure and priority remediation.</p>
            </div>
            <span className="tag premium">High priority</span>
          </div>
          <table className="enterprise-table">
            <thead><tr><th>Asset</th><th>Risk</th><th>Category</th><th>Status</th></tr></thead>
            <tbody>
              {assets.map((asset) => (
                <tr key={asset.name}>
                  <td>{asset.name}</td>
                  <td><strong>{asset.risk}%</strong></td>
                  <td>{asset.category}</td>
                  <td><span className="badge open">Review</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="glass-card intelligence-card">
          <div className="card-head">
            <div>
              <h2>Threat Intelligence</h2>
              <p>Latest signatures, attack vectors, and analyst insights.</p>
            </div>
            <span className="tag">Analysis</span>
          </div>
          <div className="intelligence-grid">
            <div>
              <span>Phishing</span>
              <strong>54%</strong>
            </div>
            <div>
              <span>API Abuse</span>
              <strong>23%</strong>
            </div>
            <div>
              <span>Ransomware</span>
              <strong>14%</strong>
            </div>
            <div>
              <span>Insider Risk</span>
              <strong>9%</strong>
            </div>
          </div>
          <div className="mini-graph">
            <div className="sparkline"><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div>
          </div>
        </section>
      </div>
    </div>
  )
}
