import { useState, useMemo } from 'react'
import { Search, Download, Filter, CircleDot, ArrowRight } from 'lucide-react'
import { useAppStore } from '../store/useAppStore.jsx'

const rowsPerPage = 5
const statusTabs = ['All', 'Open', 'In Progress', 'Fixed']

export default function FindingsPage() {
  const findings = useAppStore((state) => state.findings)
  const [query, setQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('All')
  const [page, setPage] = useState(1)
  const [activeId, setActiveId] = useState(null)

  const filtered = useMemo(() => {
    return findings
      .filter((item) =>
        (statusFilter === 'All' || item.status === statusFilter) &&
        (item.title.toLowerCase().includes(query.toLowerCase()) ||
          item.cve.toLowerCase().includes(query.toLowerCase()) ||
          item.asset.toLowerCase().includes(query.toLowerCase()))
      )
  }, [findings, query, statusFilter])

  const pages = Math.max(1, Math.ceil(filtered.length / rowsPerPage))
  const pageItems = filtered.slice((page - 1) * rowsPerPage, page * rowsPerPage)
  const selectedFinding = findings.find((item) => item.id === activeId)

  return (
    <div className="page-shell">
      <div className="page-head">
        <div>
          <p className="eyebrow">Findings Management</p>
          <h1>Vulnerability Intelligence</h1>
          <p>Search, filter, and triage vulnerabilities with remediation recommendations and risk context.</p>
        </div>
        <div className="hero-pill orange">CVE & CWE mapped</div>
      </div>

      <div className="glass-card filter-card">
        <div className="filter-grid">
          <div className="search-box">
            <Search size={16} />
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search CVE, CWE, asset, risk..." />
          </div>
          <div className="status-filters">
            {statusTabs.map((option) => (
              <button
                key={option}
                className={option === statusFilter ? 'tab active' : 'tab'}
                onClick={() => { setStatusFilter(option); setPage(1) }}
              >
                {option}
              </button>
            ))}
          </div>
          <div className="filter-actions">
            <button className="btn-secondary"><Filter size={14}/> Advanced filters</button>
            <button className="btn-primary"><Download size={14}/> Export CSV</button>
          </div>
        </div>
      </div>

      <div className="glass-card findings-table-card">
        <div className="card-head">
          <h2>Findings</h2>
          <span>{filtered.length} vulnerabilities</span>
        </div>
        <div className="table-scroll">
          <table className="enterprise-table">
            <thead>
              <tr>
                <th>Severity</th>
                <th>Finding</th>
                <th>Asset</th>
                <th>CVE / CWE</th>
                <th>CVSS</th>
                <th>Status</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {pageItems.map((item) => (
                <tr key={item.id} onClick={() => setActiveId(item.id)}>
                  <td><span className={`badge ${item.severity.toLowerCase()}`}>{item.severity}</span></td>
                  <td>{item.title}</td>
                  <td>{item.asset}</td>
                  <td>{item.cve} / {item.cwe}</td>
                  <td>{item.cvss}</td>
                  <td><span className={`badge ${item.status.toLowerCase().replace(' ', '-')}`}>{item.status}</span></td>
                  <td><ArrowRight size={16} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="pagination-row">
          <div>{pageItems.length} records shown</div>
          <div>
            <button className="page-btn" disabled={page === 1} onClick={() => setPage(page - 1)}>{'<'}</button>
            <span>{page} / {pages}</span>
            <button className="page-btn" disabled={page === pages} onClick={() => setPage(page + 1)}>{'>'}</button>
          </div>
        </div>
      </div>

      <aside className="detail-panel">
        <div className="glass-card detail-card">
          {selectedFinding ? (
            <>
              <div className="card-head">
                <h2>Finding Details</h2>
                <span className="tag">Remediation</span>
              </div>
              <div className="detail-body">
                <h3>{selectedFinding.title}</h3>
                <p>{selectedFinding.remediation}</p>
                <div className="detail-grid">
                  <div><strong>Asset</strong><span>{selectedFinding.asset}</span></div>
                  <div><strong>CVSS</strong><span>{selectedFinding.cvss}</span></div>
                  <div><strong>Risk trend</strong><span>{selectedFinding.trend}%</span></div>
                  <div><strong>Category</strong><span>{selectedFinding.category}</span></div>
                </div>
              </div>
            </>
          ) : (
            <div className="empty-detail">
              <CircleDot size={28} />
              <p>Select a vulnerability to preview risk, remediation, and tracking details.</p>
            </div>
          )}
        </div>
      </aside>
    </div>
  )
}
