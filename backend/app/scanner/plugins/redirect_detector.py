from app.scanner.plugins.base import BaseDetector
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

class RedirectDetector(BaseDetector):
    REDIRECT_PARAMS = ["url", "next", "redirect", "target", "return", "goto"]
    REDIRECT_PAYLOAD = "https://evil-ares-example.com"

    async def detect(self, url: str, html: str) -> List[Dict[str, Any]]:
        findings = []
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if not params:
            return findings

        for param_name in params:
            if param_name.lower() in self.REDIRECT_PARAMS:
                if await self.verify_redirect(url, param_name):
                    findings.append({
                        "type": "Open Redirect",
                        "severity": "medium",
                        "url": url,
                        "parameter": param_name,
                        "description": f"The parameter '{param_name}' appears vulnerable to Open Redirect attacks.",
                        "remediation": "Validate all redirect targets against a whitelist of allowed domains.",
                        "evidence": f"Redirected to {self.REDIRECT_PAYLOAD}"
                    })
        
        return findings

    async def verify_redirect(self, url: str, param: str) -> bool:
        target_url = self.inject_payload(url, param, self.REDIRECT_PAYLOAD)
        try:
            # We use follow_redirects=False to catch the Location header
            resp = await self.client.get(target_url, timeout=5.0, follow_redirects=False)
            if resp.status_code in [301, 302, 303, 307, 308]:
                location = resp.headers.get("Location", "")
                if self.REDIRECT_PAYLOAD in location:
                    return True
        except Exception:
            pass
        return False

    def inject_payload(self, url: str, param: str, payload: str) -> str:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        params[param] = [payload]
        new_query = urlencode(params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))
