from app.scanner.plugins.base import BaseDetector
from typing import List, Dict, Any

class HeaderDetector(BaseDetector):
    async def detect(self, url: str, html: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        findings = []
        h = {k.lower(): v for k, v in headers.items()}
        
        if "strict-transport-security" not in h:
            findings.append({
                "type": "Missing HSTS",
                "severity": "high",
                "url": url,
                "description": "Strict-Transport-Security header not present.",
                "remediation": "Add HSTS header."
            })
            
        if "content-security-policy" not in h:
            findings.append({
                "type": "Missing CSP",
                "severity": "high",
                "url": url,
                "description": "Content-Security-Policy header is absent.",
                "remediation": "Implement a strict CSP."
            })
            
        return findings
