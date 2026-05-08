from app.scanner.plugins.base import BaseDetector
from typing import List, Dict, Any, Optional
import httpx
from urllib.parse import urljoin

class ExposureDetector(BaseDetector):
    SENSITIVE_PATHS = [
        ".env", ".git/config", "config.php.bak", "wp-config.php",
        ".bash_history", "id_rsa", "backup.sql", "dump.sql",
        "composer.json", "package.json", "phpinfo.php",
        "server-status", ".htaccess", "config.yml"
    ]

    async def detect(self, url: str, html: str) -> List[Dict[str, Any]]:
        findings = []
        # We only run this on the base URL to avoid redundant requests
        # In a real scanner, we might run it on every directory discovered
        
        for path in self.SENSITIVE_PATHS:
            target = urljoin(url, path)
            try:
                resp = await self.client.get(target, timeout=5.0, follow_redirects=False)
                if resp.status_code == 200:
                    # Check for false positives (e.g. 200 on error page)
                    if len(resp.text) > 0 and "404" not in resp.text and "not found" not in resp.text.lower():
                        findings.append({
                            "type": "Sensitive Information Exposure",
                            "severity": "critical",
                            "url": target,
                            "description": f"Sensitive file '{path}' is publicly accessible.",
                            "remediation": "Restrict access to sensitive files or remove them from the web root.",
                            "evidence": f"Status: {resp.status_code}, Length: {len(resp.text)}"
                        })
            except Exception:
                pass
        return findings
