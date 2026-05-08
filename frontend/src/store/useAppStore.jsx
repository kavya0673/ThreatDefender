import { create } from 'zustand'

const initialFindings = [
  { id: 1, title: 'Cross-site scripting (XSS) in login portal', severity: 'Critical', cve: 'CVE-2024-1234', cwe: 'CWE-79', status: 'Open', asset: 'auth.corp.local', cvss: 9.4, category: 'Web Application', risk: 'High', remediation: 'Sanitize user input and apply output encoding.', trend: 86 },
  { id: 2, title: 'SQL injection on orders API', severity: 'High', cve: 'CVE-2024-2710', cwe: 'CWE-89', status: 'In Progress', asset: 'api.corp.local', cvss: 8.1, category: 'API', risk: 'High', remediation: 'Use prepared statements and validate parameters.', trend: 72 },
  { id: 3, title: 'Misconfigured CORS policy', severity: 'Medium', cve: 'N/A', cwe: 'CWE-942', status: 'Open', asset: 'portal.corp.local', cvss: 5.7, category: 'Configuration', risk: 'Medium', remediation: 'Restrict allowed origins to approved domains.', trend: 56 },
  { id: 4, title: 'Unpatched server component', severity: 'High', cve: 'CVE-2024-9999', cwe: 'CWE-1104', status: 'Open', asset: 'db.corp.local', cvss: 7.9, category: 'Infrastructure', risk: 'High', remediation: 'Apply the latest vendor patch and reboot.', trend: 63 },
  { id: 5, title: 'Weak MFA enforcement', severity: 'Low', cve: 'N/A', cwe: 'CWE-640', status: 'Fixed', asset: 'iam.corp.local', cvss: 3.1, category: 'Identity', risk: 'Low', remediation: 'Enforce strong MFA for all privileged sessions.', trend: 39 },
  { id: 6, title: 'Open remote desktop port', severity: 'Medium', cve: 'N/A', cwe: 'CWE-200', status: 'In Progress', asset: 'rdp.corp.local', cvss: 5.2, category: 'Network', risk: 'Medium', remediation: 'Restrict RDP to trusted hosts over VPN.', trend: 48 },
]

const initialReports = [
  { id: 1, name: 'Executive Risk Summary', status: 'Ready', date: '2026-05-08', progress: 100 },
  { id: 2, name: 'Compliance Audit', status: 'Generating', date: '2026-05-07', progress: 65 },
  { id: 3, name: 'Threat Hunting Brief', status: 'Draft', date: '2026-05-06', progress: 30 },
]

const initialScans = [
  { id: 1, profile: 'External perimeter sweep', targets: 12, progress: 94, status: 'Running' },
  { id: 2, profile: 'Application layer audit', targets: 5, progress: 58, status: 'Queued' },
  { id: 3, profile: 'API fuzzing profile', targets: 8, progress: 23, status: 'Running' },
]

const initialNotifications = [
  { id: 1, label: 'New threat intelligence feed loaded', type: 'info' },
  { id: 2, label: 'Report generation completed', type: 'success' },
  { id: 3, label: 'High severity finding assigned', type: 'warning' },
]

const initialAssets = [
  { name: 'auth.corp.local', risk: 94, category: 'Web App' },
  { name: 'api.corp.local', risk: 88, category: 'API' },
  { name: 'db.corp.local', risk: 81, category: 'Database' },
  { name: 'portal.corp.local', risk: 67, category: 'Web App' },
]

export const useAppStore = create((set) => ({
  theme: 'dark',
  reports: initialReports,
  findings: initialFindings,
  scans: initialScans,
  notifications: initialNotifications,
  assets: initialAssets,
  toggleTheme: () => set((state) => ({ theme: state.theme === 'dark' ? 'light' : 'dark' })),
}))
