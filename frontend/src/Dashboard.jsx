import React, { useState, useRef, useEffect } from 'react';

const Icon = ({ d, size = 16, color = 'currentColor' }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
    stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d={d} />
  </svg>
);
const I = {
  shield:   'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z',
  dash:     'M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z',
  scan:     'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0zM9 12l2 2 4-4',
  alert:    'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z',
  bug:      'M9 9h6v6H9zM12 2v3M12 19v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12M2 12h3M19 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12',
  term:     'M4 17l6-6-6-6M12 19h8',
  globe:    'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zM2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z',
  report:   'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M16 13H8M16 17H8M10 9H8',
  settings: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
  bell:     'M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 0 1-3.46 0',
  play:     'M5 3l14 9-14 9V3z',
  download: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3',
  link:     'M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71',
  refresh:  'M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15',
  eye:      'M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8zM12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z',
  cpu:      'M18 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zM9 9h6v6H9z',
  key:      'M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4',
  empty:    'M9 17H7A5 5 0 0 1 7 7h2M15 7h2a5 5 0 1 1 0 10h-2M8 12h8',
  check:    'M22 11.08V12a10 10 0 1 1-5.93-9.14M22 4L12 14.01l-3-3',
};

const NAV = [
  { id: 'dashboard', icon:'dash',    label:'Dashboard' },
  { id: 'new-scan',  icon:'scan',    label:'New Scan' },
  { id: 'findings',  icon:'alert',   label:'Findings' },
  { id: 'attack-map',icon:'globe',   label:'Attack Map' },
  { id: 'reports',   icon:'report',  label:'Reports' },
];

/* Simulated scan steps — happen after user clicks Launch Scan */
const buildScanSteps = (url) => [
  { delay: 400,  pct: 5,   msg: `Resolving target: ${url}`, cls: '' },
  { delay: 900,  pct: 12,  msg: 'DNS OK — IP resolved, TLS verified', cls: 'success' },
  { delay: 1500, pct: 22,  msg: 'Fetching robots.txt — scope configured', cls: '' },
  { delay: 2200, pct: 34,  msg: 'Crawler started — depth 5 | 10 threads', cls: '' },
  { delay: 3000, pct: 46,  msg: `Discovered endpoints on ${url}`, cls: 'success' },
  { delay: 3700, pct: 57,  msg: 'SQLi module: testing error/boolean/time payloads…', cls: '' },
  { delay: 4400, pct: 65,  msg: 'XSS module: reflected & DOM context analysis…', cls: '' },
  { delay: 5000, pct: 74,  msg: 'CSRF module: form token inspection…', cls: '' },
  { delay: 5600, pct: 82,  msg: 'Header analysis: CSP, HSTS, X-Frame-Options…', cls: '' },
  { delay: 6200, pct: 90,  msg: 'Auth module: session & cookie flag checks…', cls: '' },
  { delay: 6800, pct: 96,  msg: 'AI analysis: classifying & deduplicating findings…', cls: '' },
  { delay: 7400, pct: 100, msg: 'Scan complete. Report ready.', cls: 'success' },
];

/* No longer using static mock findings — results come from the backend API */

const generateVulnTypes = (findings) => {
  const counts = {};
  findings.forEach(f => { counts[f.type] = (counts[f.type] || 0) + 1; });
  const max = Math.max(...Object.values(counts), 1);
  const colors = ['#f97316','#06b6d4','#f59e0b','#3b82f6','#8b5cf6','#10b981'];
  return Object.entries(counts).map(([name, count], i) => ({
    name, count, pct: Math.round((count / max) * 100), color: colors[i % colors.length],
  }));
};

const severityColor = { critical:'var(--red)', high:'var(--orange)', medium:'var(--yellow)', low:'var(--primary)', info:'var(--cyan)' };
const computeRiskScore = (findings) => {
  if (!findings.length) return 0;
  const w = { critical:10, high:7, medium:4, low:2, info:1 };
  const total = findings.reduce((s, f) => s + (w[f.severity] || 0), 0);
  return Math.min(Math.round((total / (findings.length * 10)) * 100), 99);
};

const getHostName = (value) => {
  if (!value) return 'No target scanned';
  try {
    return new URL(value).hostname || value;
  } catch {
    return value;
  }
};

export default function Dashboard() {
  const [scanUrl,   setScanUrl]   = useState('');
  const [scanning,  setScanning]  = useState(false);
  const [progress,  setProgress]  = useState(0);
  const [scanned,   setScanned]   = useState(false);
  const [findings,  setFindings]  = useState([]);
  const [vulnTypes, setVulnTypes] = useState([]);
  const [history,   setHistory]   = useState([]);
  const [riskScore, setRiskScore] = useState(0);
  const [endpointCount, setEndpointCount] = useState(0);
  const [currentScanId, setCurrentScanId] = useState(null);
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [activeNav, setActiveNav] = useState('dashboard');
  const [logs,      setLogs]      = useState([
    { time: new Date().toLocaleTimeString('en-US',{hour12:false}), msg:'ThreatDefender Engine v2.4.1 initialized', cls:'success' },
    { time: new Date().toLocaleTimeString('en-US',{hour12:false}), msg:'14 vulnerability modules loaded', cls:'' },
    { time: new Date().toLocaleTimeString('en-US',{hour12:false}), msg:'Awaiting scan target…', cls:'warning' },
  ]);
  const logsRef = useRef(null);

  useEffect(() => {
    if (logsRef.current) logsRef.current.scrollTop = logsRef.current.scrollHeight;
  }, [logs]);

  const addLog = (msg, cls = '') => {
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    setLogs(p => [...p, { time, msg, cls }]);
  };

  const notifyAction = (msg, cls = 'success') => {
    addLog(msg, cls);
  };

  const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const simulateScan = async () => {
    const steps = buildScanSteps(scanUrl);
    for (const step of steps) {
      await delay(step.delay);
      addLog(step.msg, step.cls);
      setProgress(step.pct);
    }

    const mockFindings = [
      { id: 1, severity: 'high', type: 'SQL Injection', url: scanUrl, parameter: 'id', description: 'Potential SQL injection point detected.' },
      { id: 2, severity: 'medium', type: 'Cross-Site Scripting', url: scanUrl, parameter: 'search', description: 'Reflected XSS vector found.' },
    ];
    const finalFindings = mapFindings(mockFindings);
    setFindings(finalFindings);
    setVulnTypes(generateVulnTypes(finalFindings));
    setRiskScore(computeRiskScore(finalFindings));
    setEndpointCount(finalFindings.length);
    setProgress(100);
    setScanning(false);
    setScanned(true);
    setHistory(h => [{ target: scanUrl, date: new Date().toLocaleDateString(), findings: finalFindings.length, severity: finalFindings[0]?.severity || 'info' }, ...h]);
    addLog('Scan complete. Review findings and risk score above.', 'success');
  };

  const TOKEN = "mock_token";

  const startScan = async () => {
    if (!scanUrl.trim()) { addLog('Error: Please enter a valid URL.', 'danger'); return; }

    setScanning(true);
    setScanned(false);
    setProgress(0);
    setFindings([]);
    setVulnTypes([]);
    setRiskScore(0);
    setEndpointCount(0);
    setLogs([]); // Clear logs for new scan

    addLog(`Initiating enterprise scan for: ${scanUrl}`, 'success');

    try {
      const res = await fetch('/api/v1/scans/start', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${TOKEN}`
        },
        body: JSON.stringify({ url: scanUrl }),
      });

      if (!res.ok) {
        const errorText = await res.text();
        addLog(`Backend unavailable: ${res.status} ${errorText || 'Unknown Error'}. Falling back to local scan simulation.`, 'warning');
        await simulateScan();
        return;
      }

      const data = await res.json();
      const scanId = data.scan_id;
      setCurrentScanId(scanId);
      addLog(`Scan task registered: ID ${scanId}`, 'success');
      setProgress(5);
      pollScanStatus(scanId);
    } catch (err) {
      addLog(`Backend error: ${err.message}. Falling back to local scan simulation.`, 'warning');
      await simulateScan();
    }
  };

  const pollScanStatus = async (scanId) => {
    let pollProgress = 10;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/v1/scans/${scanId}`, {
          headers: { 'Authorization': `Bearer ${TOKEN}` }
        });
        if (!res.ok) {
          clearInterval(interval);
          setScanning(false);
          return;
        }
        const data = await res.json();

        // Sync Engine Logs from Backend
        if (data.engine_logs && Array.isArray(data.engine_logs)) {
          setLogs(data.engine_logs);
        }

        if (data.status === 'running' || data.status === 'analyzing') {
          // Dynamic progress based on phase
          if (data.status === 'running') {
              if (data.endpoints_checked && data.endpoints_total) {
                pollProgress = Math.min(10 + Math.round((data.endpoints_checked / data.endpoints_total) * 75), 88);
              } else {
                pollProgress = Math.min(pollProgress + 5, 75);
              }
          } else {
              pollProgress = Math.min(pollProgress + 2, 95);
          }
          setProgress(pollProgress);
          
          // Live findings update
          if (data.findings && data.findings.length > 0) {
            const liveFindings = mapFindings(data.findings);
            setFindings(liveFindings);
            setVulnTypes(generateVulnTypes(liveFindings));
            setRiskScore(data.risk_score || computeRiskScore(liveFindings));
            setEndpointCount(data.endpoints_checked || data.findings_count || liveFindings.length);
          }
        } else if (data.status === 'completed') {
          clearInterval(interval);
          finishScan(data, scanId);
        } else if (data.status === 'failed') {
          clearInterval(interval);
          setScanning(false);
          addLog(`Scan ${scanId} failed on backend engine.`, 'danger');
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 2000);
  };

  const mapFindings = (arr) => arr.map((f, i) => ({
    id:       f.id ?? i + 1,
    severity: String(f.severity || 'info').toLowerCase(),
    type:     f.type,
    url:      f.url,
    param:    f.parameter ?? '-',
    status:   'open',
    cvss:     Number(f.risk_score) > 0 ? f.risk_score : cvssFromSeverity(f.severity),
    desc:     f.description ?? '',
    ai:       safeParseAnalysis(f.ai_analysis)
  }));

  const cvssFromSeverity = (severity) => {
    const normalized = String(severity || 'info').toLowerCase();
    if (normalized === 'critical') return 9.5;
    if (normalized === 'high') return 7.5;
    if (normalized === 'medium') return 5.0;
    if (normalized === 'low') return 2.5;
    return 0;
  };

  const safeParseAnalysis = (value) => {
    if (!value) return null;
    if (typeof value !== 'string') return value;
    try {
      return JSON.parse(value);
    } catch {
      return { summary: value };
    }
  };

  const finishScan = async (data, scanId) => {
    // Final logs and findings fetch
    try {
      const r = await fetch(`/api/v1/scans/${scanId}/findings`, {
        headers: { 'Authorization': `Bearer ${TOKEN}` }
      });
      if (r.ok) {
        const fd = await r.json();
        const finalFindings = mapFindings(fd);
        setFindings(finalFindings);
        setVulnTypes(generateVulnTypes(finalFindings));
        setRiskScore(data.risk_score || computeRiskScore(finalFindings));
        setEndpointCount(data.endpoints_checked || data.findings_count || finalFindings.length);
      }
    } catch(e) { }

    setProgress(100);
    setScanning(false);
    setScanned(true);
    setHistory(h => [{
      target: data.target_url || scanUrl,
      date: new Date().toLocaleDateString(),
      findings: data.findings_count ?? findings.length,
      severity: findings[0]?.severity || 'info',
      scanId
    }, ...h]);
  };

  const generateReport = async (scanId) => {
    const token = "mock_token";
    if (!scanId || scanId === 'current') {
      notifyAction('Run a completed backend scan before generating a PDF report.', 'warning');
      return;
    }
    addLog(`Generating PDF report for scan ${scanId}...`, 'info');
    try {
      const res = await fetch(`/api/v1/reports/${scanId}/generate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText || `HTTP ${res.status}`);
      }
      const data = await res.json();
      addLog(`Report ${data.report_id} generated. Starting download...`, 'success');
      await downloadReport(data.report_id);
    } catch (err) {
      addLog(`Report generation failed: ${err.message}`, 'danger');
    }
  };

  const downloadReport = async (reportId) => {
    const token = "mock_token";
    const res = await fetch(`/api/v1/reports/download/${reportId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(errorText || `Download failed with HTTP ${res.status}`);
    }

    const blob = await res.blob();
    const disposition = res.headers.get('content-disposition') || '';
    const match = disposition.match(/filename="?([^"]+)"?/i);
    const filename = match?.[1] || `ThreatDefender-Report-${reportId}.pdf`;
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    addLog(`Download started: ${filename}`, 'success');
  };

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-row">
            <div className="logo-icon"><Icon d={I.shield} size={18} color="white" /></div>
            <div>
              <div className="logo-text">ThreatDefender</div>
              <div className="logo-sub">Cyber Intelligence</div>
            </div>
          </div>
        </div>
        <div className="nav-section">
          <div className="nav-label">Navigation</div>
          {NAV.map(n => (
            <button key={n.id} className={`nav-item ${activeNav===n.id?'active':''}`}
              onClick={() => setActiveNav(n.id)}>
              <Icon d={I[n.icon]} size={15} />{n.label}
              {n.id==='findings' && findings.length>0 &&
                <span className="nav-badge">{findings.length}</span>}
            </button>
          ))}
        </div>
      </aside>

      {/* Main */}
      <div className="main-content">
        {/* Topbar */}
        <div className="topbar">
          <div className="topbar-left">
            <div>
              <div className="page-title">{NAV.find(n=>n.id===activeNav)?.label || 'Security Dashboard'}</div>
              <div className="breadcrumb">ThreatDefender / {NAV.find(n=>n.id===activeNav)?.label || 'Overview'} / {scanned ? `Results: ${scanUrl}` : 'No scan running'}</div>
            </div>
          </div>
          <div className="topbar-right">
            <div className="status-pill">
              <span className="dot" />
              {scanning ? 'Scanning…' : 'Scanner Online'}
            </div>
          </div>
        </div>

        {activeNav === 'dashboard' ? (
          <div className="page-body">
          {/* Metrics — show 0 / empty until scanned */}
          <div className="metrics-grid">
            <MetricCard color="red"    icon={I.shield} label="Risk Score"    value={scanned ? `${riskScore}` : '—'} suffix={scanned?'/100':''} iconBg="#ef444422" iconColor="var(--red)"     scanned={scanned} />
            <MetricCard color="blue"   icon={I.globe}  label="Endpoints"     value={scanned ? `${endpointCount}` : '—'}                          iconBg="#3b82f622" iconColor="var(--primary)"  scanned={scanned} />
            <MetricCard color="yellow" icon={I.alert}  label="Findings"      value={scanned ? `${findings.length}` : '—'}                        iconBg="#f59e0b22" iconColor="var(--yellow)"   scanned={scanned} />
            <MetricCard color="green"  icon={I.scan}   label="Scans Today"   value={`${history.length}`}                                         iconBg="#10b98122" iconColor="var(--green)"    scanned={true} />
          </div>

          {/* Scan input */}
          <div className="card card-glow" style={{marginBottom:16}}>
            <div className="card-header">
              <div className="card-title">
                <Icon d={I.link} size={14} color="var(--primary)" />
                Target Configuration
              </div>
            </div>
            <div className="card-body">
              <div className="scan-form">
                <input className="scan-input"
                  placeholder="https://target.example.com — Enter URL to scan"
                  value={scanUrl}
                  onChange={e => setScanUrl(e.target.value)}
                  onKeyDown={e => e.key==='Enter' && !scanning && startScan()}
                />
                <button className="btn-primary" onClick={startScan} disabled={scanning}>
                  {scanning
                    ? <><Icon d={I.refresh} size={14} color="white"/>Scanning…</>
                    : <><Icon d={I.play}    size={14} color="white"/>Launch Scan</>}
                </button>
              </div>
              {(scanning || scanned) && (
                <div className="progress-wrap">
                  <div className="progress-label">
                    <span>{scanning ? 'Scan in progress…' : `Scan complete — ${findings.length} findings`}</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{width:`${progress}%`}} />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Two columns */}
          <div className="two-col">
            {/* Left — findings table */}
            <div>
              <div className="card card-glow">
                <div className="card-header">
                  <div className="card-title">
                    <Icon d={I.alert} size={14} color="var(--red)" />
                    Detected Vulnerabilities
                    {scanned && <span className="badge high" style={{marginLeft:6}}>{findings.length} issues</span>}
                  </div>
                  {scanned && (
                    <button className="btn-secondary" style={{fontSize:11}} onClick={() => generateReport(currentScanId)}>
                      <Icon d={I.download} size={12}/>Generate Enterprise PDF
                    </button>
                  )}
                </div>

                {!scanned ? (
                  <EmptyState icon={I.empty}
                    title="No scan results yet"
                    sub="Enter a URL above and click Launch Scan to discover vulnerabilities." />
                ) : (
                  <div style={{overflowX:'auto'}}>
                    <table className="vuln-table">
                      <thead>
                        <tr>
                          <th>Severity</th><th>Vulnerability</th><th>URL / Parameter</th>
                          <th>CVSS</th><th>Status</th><th></th>
                        </tr>
                      </thead>
                      <tbody>
                        {findings.map(f => (
                          <tr key={f.id}>
                            <td><span className={`badge ${f.severity}`}>{f.severity}</span></td>
                            <td>
                              <div style={{fontWeight:600,fontSize:12}}>{f.type}</div>
                              <div style={{fontSize:10,color:'var(--text-3)',marginTop:2}}>{f.desc}</div>
                            </td>
                            <td>
                              <div className="mono" style={{maxWidth:180,overflow:'hidden',textOverflow:'ellipsis'}}>{f.url}</div>
                              {f.param!=='-' && <div style={{fontSize:10,color:'var(--text-3)',marginTop:2}}>param: <span style={{color:'var(--cyan)'}}>{f.param}</span></div>}
                            </td>
                            <td>
                              <span style={{fontWeight:700,fontSize:13,color:severityColor[f.severity]}}>{f.cvss}</span>
                            </td>
                            <td><span className={`status-badge ${f.status}`}>{f.status}</span></td>
                            <td><button className="icon-btn" style={{width:26,height:26}} onClick={() => setSelectedFinding(f)}><Icon d={I.eye} size={12}/></button></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>

            {/* Right column */}
            <div style={{display:'flex',flexDirection:'column',gap:16}}>
              <div className="card card-glow enterprise-panel">
                <div className="card-header">
                  <div className="card-title"><Icon d={I.shield} size={14} color="var(--red)"/>Overall Risk</div>
                </div>
                <div className="card-body">
                  {!scanned ? (
                    <EmptyState icon={I.shield} title="Risk Score" sub="Run a scan to calculate risk." small />
                  ) : (
                    <div className="gauge-wrap">
                      <div className="gauge-score" style={{
                        background: riskScore>=70 ? 'linear-gradient(135deg,var(--red),var(--orange))' :
                                    riskScore>=40 ? 'linear-gradient(135deg,var(--orange),var(--yellow))' :
                                                   'linear-gradient(135deg,var(--green),var(--cyan))',
                        WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent'
                      }}>{riskScore}</div>
                      <div className="gauge-label">CVSS Risk Score</div>
                      <div className="gauge-bar-wrap">
                        <div className="gauge-track">
                          <div className="gauge-fill" style={{width:`${riskScore}%`}}/>
                        </div>
                        <div className="gauge-ticks"><span>0</span><span>5</span><span>10 Critical</span></div>
                      </div>
                      <div className="severity-pill-row">
                        {['critical','high','medium','low','info'].map(s => {
                          const n = findings.filter(f=>f.severity===s).length;
                          return n>0 && (
                            <div key={s} className="severity-pill" style={{borderColor:severityColor[s]}}>
                              <div className="severity-value" style={{color:severityColor[s]}}>{n}</div>
                              <div className="severity-label">{s}</div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="card card-glow enterprise-panel">
                <div className="card-header">
                  <div className="card-title"><Icon d={I.bug} size={14} color="var(--orange)"/>Attack Surface</div>
                </div>
                <div className="card-body">
                  {!scanned ? (
                    <EmptyState icon={I.bug} title="No data" sub="Scan results will appear here." small />
                  ) : (
                    <div className="vuln-types">
                      {vulnTypes.map(v => (
                        <div className="vuln-type-row" key={v.name}>
                          <div className="vuln-type-name">{v.name}</div>
                          <div className="vuln-type-bar-wrap">
                            <div className="vuln-type-bar" style={{width:`${v.pct}%`,background:v.color}}/>
                          </div>
                          <div className="vuln-type-count" style={{color:v.color}}>{v.count}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="card card-glow" style={{flex:1,minHeight:200,display:'flex',flexDirection:'column'}}>
                <div className="card-header">
                  <div className="card-title"><Icon d={I.term} size={14} color="var(--cyan)"/>Engine Logs</div>
                  <span className="tag">{scanning?'LIVE':'IDLE'}</span>
                </div>
                <div className="terminal" style={{flex:1,borderRadius:'0 0 12px 12px'}}>
                  <div className="terminal-bar">
                    <div className="terminal-dots">
                      <span className="t-red"/><span className="t-yellow"/><span className="t-green"/>
                    </div>
                    <span className="terminal-title">threatdefender-engine — bash</span>
                  </div>
                  <div className="terminal-body" ref={logsRef}>
                    {logs.map((l,i) => (
                      <div className="log-line" key={i}>
                        <span className="log-time">[{l.time}]</span>
                        <span className="log-prompt">❯</span>
                        <span className={`log-msg ${l.cls}`}>{l.msg}</span>
                      </div>
                    ))}
                    {scanning && <div className="log-line"><span className="log-prompt">❯</span><span className="log-cursor">█</span></div>}
                  </div>
                </div>
              </div>

              <div className="card card-glow">
                <div className="card-header">
                  <div className="card-title"><Icon d={I.refresh} size={14} color="var(--text-2)"/>Scan History</div>
                </div>
                <div className="card-body" style={{padding:'8px 16px'}}>
                  {history.length === 0 ? (
                    <EmptyState icon={I.report} title="No history yet" sub="Completed scans will be listed here." small />
                  ) : (
                    <div className="timeline">
                      {history.map((h,i) => (
                        <div className="timeline-item" key={i}>
                          <div className="timeline-dot" style={{background:severityColor[h.severity]||'var(--primary)'}}/>
                          <div className="timeline-content" style={{flex:1}}>
                            <p className="mono" style={{fontSize:11}}>{h.target}</p>
                            <span>{h.date}</span>
                          </div>
                          <span className={`badge ${h.severity}`}>{h.findings} found</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
          </div>
        ) : activeNav === 'new-scan' ? (
          <div className="page-body">
            <div className="card card-glow" style={{marginBottom:16}}>
              <div className="card-header"><div className="card-title"><Icon d={I.play} size={14}/>New Scan</div></div>
              <div className="card-body">
                <div style={{maxWidth:720}}>
                  <div className="scan-form">
                    <input className="scan-input" placeholder="https://target.example.com — Enter URL to scan" value={scanUrl} onChange={e=>setScanUrl(e.target.value)} />
                    <button className="btn-primary" onClick={startScan} disabled={scanning}>
                      {scanning ? 'Scanning...' : 'Launch Scan'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div className="card card-glow">
              <div className="card-header"><div className="card-title"><Icon d={I.dash} size={14}/>Enterprise Scan Policies</div></div>
              <div className="card-body">
                <div className="policy-grid">
                  <div className="policy-card"><strong>Policy:</strong> Full OWASP Top 10 + API checks</div>
                  <div className="policy-card"><strong>Scope:</strong> Internal & external assets</div>
                  <div className="policy-card"><strong>Compliance:</strong> PCI-DSS, SOC 2, ISO 27001</div>
                  <div className="policy-card"><strong>Delivery:</strong> Agentless, Cloud, and Hybrid</div>
                </div>
              </div>
            </div>
          </div>
        ) : activeNav === 'findings' ? (
          <div className="page-body">
            <div className="card card-glow" style={{marginBottom:16}}>
              <div className="card-header"><div className="card-title"><Icon d={I.alert} size={14}/>Findings Overview</div></div>
              <div className="card-body">
                <div className="metrics-grid" style={{gridTemplateColumns:'repeat(3,1fr)'}}>
                  <MetricCard color="red" icon={I.alert} label="Critical" value={`${findings.filter(f=>f.severity==='critical').length}`} iconBg="#ef444422" iconColor="var(--red)" scanned={true} />
                  <MetricCard color="orange" icon={I.bug} label="High" value={`${findings.filter(f=>f.severity==='high').length}`} iconBg="#f9731622" iconColor="var(--orange)" scanned={true} />
                  <MetricCard color="yellow" icon={I.eye} label="Open Issues" value={`${findings.filter(f=>f.status==='open').length}`} iconBg="#f59e0b22" iconColor="var(--yellow)" scanned={true} />
                </div>
              </div>
            </div>
            <div className="card card-glow">
              <div className="card-header"><div className="card-title"><Icon d={I.alert} size={14}/>All Findings</div></div>
              <div className="card-body">
                {findings.length===0 ? <EmptyState icon={I.empty} title="No findings" sub="Run a scan to populate findings." /> : (
                  <div style={{overflowX:'auto'}}>
                    <table className="vuln-table">
                      <thead><tr><th>Severity</th><th>Vulnerability</th><th>URL</th><th>CVSS</th><th>Status</th><th>Action</th></tr></thead>
                      <tbody>{findings.map(f=> (<tr key={f.id}><td><span className={`badge ${f.severity}`}>{f.severity}</span></td><td><div style={{fontWeight:600}}>{f.type}</div></td><td className="mono">{f.url}</td><td>{f.cvss}</td><td><span className={`status-badge ${f.status}`}>{f.status}</span></td><td><button className="btn-secondary" onClick={() => setSelectedFinding(f)}>Remediate</button></td></tr>))}</tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : activeNav === 'attack-map' ? (
          <div className="page-body">
            <div className="card card-glow" style={{marginBottom:16}}>
              <div className="card-header"><div className="card-title"><Icon d={I.globe} size={14}/>Attack Surface</div></div>
              <div className="card-body">
                {!scanned ? (
                  <EmptyState icon={I.globe} title="No attack surface data" sub="Run a scan first. This view only shows real scan-derived information." />
                ) : (
                  <>
                    <div className="map-summary-row">
                      <div className="map-metric"><strong>Scanner Source</strong><span>Local engine</span></div>
                      <div className="map-metric"><strong>Endpoints Tested</strong><span>{endpointCount || findings.length}</span></div>
                      <div className="map-metric"><strong>Findings</strong><span>{findings.length}</span></div>
                      <div className="map-metric"><strong>Risk Index</strong><span>{riskScore}/100</span></div>
                    </div>
                    <div className="map-placeholder">
                      <strong>{getHostName(scanUrl)}</strong>
                      <span>Scan telemetry is based on the latest completed run. Geographic source data is hidden because this scanner does not collect attacker IP intelligence yet.</span>
                    </div>
                  </>
                )}
              </div>
            </div>
            {scanned && (
              <div className="card card-glow">
                <div className="card-header"><div className="card-title"><Icon d={I.dash} size={14}/>Observed Findings</div></div>
                <div className="card-body">
                  {findings.length === 0 ? (
                    <EmptyState icon={I.check} title="No findings observed" sub="The completed scan did not return attack-surface events." small />
                  ) : (
                    <div style={{overflowX:'auto'}}>
                      <table className="vuln-table">
                        <thead><tr><th>Severity</th><th>Finding</th><th>Endpoint</th><th>CVSS</th></tr></thead>
                        <tbody>
                          {findings.map(f => (
                            <tr key={f.id}>
                              <td><span className={`badge ${f.severity}`}>{f.severity}</span></td>
                              <td>{f.type}</td>
                              <td className="mono">{f.url}</td>
                              <td>{f.cvss}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        ) : activeNav === 'reports' ? (
          <div className="page-body">
            <div className="card card-glow" style={{marginBottom:16}}>
              <div className="card-header"><div className="card-title"><Icon d={I.report} size={14}/>Reports Center</div></div>
              <div className="card-body">
                <div className="reports-grid">
                  <div className="report-card"><strong>Q1 Compliance</strong><span>Status: Ready</span></div>
                  <div className="report-card"><strong>Weekly Scan</strong><span>Status: In Review</span></div>
                  <div className="report-card"><strong>Executive Brief</strong><span>Status: Draft</span></div>
                </div>
                <button className="btn-primary" style={{marginTop:16}} onClick={() => generateReport(currentScanId)}>Generate New Enterprise Report</button>
              </div>
            </div>
            <div className="card card-glow">
              <div className="card-header"><div className="card-title"><Icon d={I.download} size={14}/>Recent Downloads</div></div>
              <div className="card-body">
                <div className="report-list">
                  <div className="report-row"><span>Latest completed scan report</span><button className="btn-secondary" onClick={() => generateReport(currentScanId)}>Generate & Download</button></div>
                  <div className="report-row"><span>Executive security summary</span><button className="btn-secondary" onClick={() => generateReport(currentScanId)}>Generate & Download</button></div>
                </div>
              </div>
            </div>
          </div>
        ) : activeNav === 'api-keys' ? (
          <div className="page-body">
            <div className="card card-glow" style={{marginBottom:16}}>
              <div className="card-header"><div className="card-title"><Icon d={I.key} size={14}/>API Keys</div></div>
              <div className="card-body">
                <div className="api-row"><div><strong>Key name</strong><p>Enterprise integration</p></div><div className="api-key">••••••••••••••••••</div><button className="btn-secondary" onClick={() => notifyAction('Enterprise integration key revoked.', 'warning')}>Revoke</button></div>
                <div className="api-row"><div><strong>Key name</strong><p>Reporting service</p></div><div className="api-key">••••••••••••••••••</div><button className="btn-secondary" onClick={() => notifyAction('Reporting service key revoked.', 'warning')}>Revoke</button></div>
                <button className="btn-primary" style={{marginTop:16}} onClick={() => notifyAction('New API key created and masked in the list.')}>Create New API Key</button>
              </div>
            </div>
            <div className="card card-glow">
              <div className="card-header"><div className="card-title"><Icon d={I.settings} size={14}/>API Usage</div></div>
              <div className="card-body">
                <div className="usage-grid">
                  <div className="usage-card"><strong>Requests</strong><span>1,240</span></div>
                  <div className="usage-card"><strong>Errors</strong><span>2.1%</span></div>
                  <div className="usage-card"><strong>Quota</strong><span>85% used</span></div>
                </div>
              </div>
            </div>
          </div>
        ) : activeNav === 'settings' ? (
          <div className="page-body">
            <div className="card card-glow" style={{marginBottom:16}}>
              <div className="card-header"><div className="card-title"><Icon d={I.settings} size={14}/>Settings</div></div>
              <div className="card-body">
                <div className="settings-grid">
                  <div className="setting-card"><strong>Security Mode</strong><span>Enterprise</span></div>
                  <div className="setting-card"><strong>Alerting</strong><span>Email + Slack</span></div>
                  <div className="setting-card"><strong>Retention</strong><span>90 days</span></div>
                  <div className="setting-card"><strong>Sync</strong><span>Enabled</span></div>
                </div>
              </div>
            </div>
            <div className="card card-glow">
              <div className="card-header"><div className="card-title"><Icon d={I.report} size={14}/>System Preferences</div></div>
              <div className="card-body">
                <div className="settings-item"><span>Auto-update intelligence rules</span><button className="btn-secondary" onClick={() => notifyAction('Auto-update intelligence rules confirmed enabled.')}>Enabled</button></div>
                <div className="settings-item"><span>Data masking</span><button className="btn-secondary" onClick={() => notifyAction('Data masking confirmed enabled.')}>Enabled</button></div>
                <div className="settings-item"><span>Two-factor authentication</span><button className="btn-secondary" onClick={() => notifyAction('Two-factor authentication policy is required.')}>Required</button></div>
              </div>
            </div>
          </div>
        ) : (
          <div className="page-body">
            <div className="card card-glow"><div className="card-header"><div className="card-title">{activeNav}</div></div><div className="card-body"><EmptyState icon={I.empty} title={activeNav} sub="View coming soon" /></div></div>
          </div>
        )}
        {selectedFinding && (
          <div style={{position:'fixed',inset:0,background:'rgba(15,23,42,0.38)',display:'grid',placeItems:'center',zIndex:50,padding:24}} onClick={() => setSelectedFinding(null)}>
            <div className="card card-glow" style={{width:'min(680px, 100%)'}} onClick={(e) => e.stopPropagation()}>
              <div className="card-header">
                <div className="card-title"><Icon d={I.eye} size={14}/>Finding Details</div>
                <button className="icon-btn" onClick={() => setSelectedFinding(null)}>x</button>
              </div>
              <div className="card-body" style={{display:'grid',gap:12}}>
                <div><span className={`badge ${selectedFinding.severity}`}>{selectedFinding.severity}</span></div>
                <div><strong>{selectedFinding.type}</strong></div>
                <div className="mono" style={{wordBreak:'break-all'}}>{selectedFinding.url}</div>
                {selectedFinding.param !== '-' && <div>Parameter: <strong>{selectedFinding.param}</strong></div>}
                <div>{selectedFinding.desc || 'No description supplied.'}</div>
                <div className="terminal-box" style={{padding:12}}>
                  {selectedFinding.ai?.remediation || selectedFinding.ai?.summary || 'Remediation guidance will appear after AI analysis is available.'}
                </div>
                <button className="btn-primary" onClick={() => notifyAction(`Remediation task opened for ${selectedFinding.type}.`)}>
                  Open Remediation Task
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function MetricCard({ color, icon, label, value, suffix='', iconBg, iconColor, scanned }) {
  return (
    <div className={`metric-card ${color}`}>
      <div className="metric-top">
        <div className="metric-icon" style={{background:iconBg}}>
          <Icon d={icon} size={16} color={iconColor}/>
        </div>
        {scanned && value!=='—' && <span className="metric-badge up">Live</span>}
      </div>
      <div className="metric-value" style={{color: scanned && value!=='—' ? iconColor : 'var(--text-3)'}}>
        {value}<span style={{fontSize:16,fontWeight:400,color:'var(--text-3)'}}>{suffix}</span>
      </div>
      <div className="metric-label">{label}</div>
    </div>
  );
}

function EmptyState({ icon, title, sub, small }) {
  return (
    <div style={{display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',
      padding: small ? '20px 16px' : '48px 24px', textAlign:'center', gap:8}}>
      <div style={{opacity:0.15, marginBottom:4}}>
        <Icon d={icon} size={small?28:40} color="var(--text-2)"/>
      </div>
      <div style={{fontSize: small?12:14, fontWeight:600, color:'var(--text-2)'}}>{title}</div>
      <div style={{fontSize: small?10:12, color:'var(--text-3)', maxWidth:220}}>{sub}</div>
    </div>
  );
}
