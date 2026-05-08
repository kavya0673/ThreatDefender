import { FileText, Download, Clock3, CheckCircle2 } from 'lucide-react'
import { useAppStore } from '../store/useAppStore.jsx'

export default function ReportsPage() {
  const reports = useAppStore((state) => state.reports)

  return (
    <div className="page-shell">
      <div className="page-head">
        <div>
          <p className="eyebrow">Reporting & Compliance</p>
          <h1>Executive Intelligence Reports</h1>
          <p>Generate compliance-ready summaries, risk assessments, and scheduled SOC reports.</p>
        </div>
        <div className="hero-pill green">Audit-ready</div>
      </div>

      <div className="grid-3">
        <section className="glass-card report-card">
          <h2>Executive Summary</h2>
          <p>Overview of current risk posture, open findings, and compliance status.</p>
          <div className="report-metrics">
            <div><strong>45</strong><span>Open threats</span></div>
            <div><strong>92%</strong><span>Compliance score</span></div>
            <div><strong>12</strong><span>Scheduled reports</span></div>
          </div>
        </section>

        <section className="glass-card report-card">
          <h2>Compliance Reports</h2>
          <div className="report-grid">
            <div><strong>PCI-DSS</strong><span>Monitoring</span></div>
            <div><strong>SOC 2</strong><span>In progress</span></div>
            <div><strong>ISO 27001</strong><span>Configured</span></div>
          </div>
        </section>

        <section className="glass-card report-card">
          <h2>Risk Assessment</h2>
          <ul className="report-checklist">
            <li><CheckCircle2 size={16} /> Asset discovery complete</li>
            <li><CheckCircle2 size={16} /> Report pipeline healthy</li>
            <li><CheckCircle2 size={16} /> SLA thresholds met</li>
          </ul>
        </section>
      </div>

      <div className="glass-card report-table-card">
        <div className="card-head">
          <div>
            <h2>Report Library</h2>
            <p>Download the latest executive and compliance deliverables.</p>
          </div>
          <button className="btn-primary"><Download size={16} /> Generate PDF</button>
        </div>
        <div className="table-scroll">
          <table className="enterprise-table">
            <thead><tr><th>Report</th><th>Status</th><th>Last updated</th><th>Action</th></tr></thead>
            <tbody>
              {reports.map((report) => (
                <tr key={report.id}>
                  <td>{report.name}</td>
                  <td>{report.status}</td>
                  <td>{report.date}</td>
                  <td><button className="btn-secondary">Download</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid-2">
        <section className="glass-card schedule-card">
          <div className="card-head">
            <h2>Scheduled Reports</h2>
          </div>
          <div className="schedule-list">
            <div><span>Daily SOC Brief</span><strong>06:00 UTC</strong></div>
            <div><span>Weekly Executive</span><strong>Monday</strong></div>
            <div><span>Monthly Compliance</span><strong>1st day</strong></div>
          </div>
        </section>

        <section className="glass-card analytics-card">
          <div className="card-head">
            <h2>Trend Analysis</h2>
          </div>
          <div className="trend-chart">
            <div className="trend-bar bar1" /><div className="trend-bar bar2" /><div className="trend-bar bar3" /><div className="trend-bar bar4" /><div className="trend-bar bar5" />
          </div>
        </section>
      </div>
    </div>
  )
}
