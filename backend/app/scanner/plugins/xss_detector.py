import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from app.scanner.plugins.base import BaseDetector

class XSSDetector(BaseDetector):
    MAX_PARAMS = 3
    # Context-aware payloads
    PAYLOADS = [
        ("<script>alert(1)</script>", "html"),
        ("\"><script>alert(1)</script>", "attribute"),
        ("'><script>alert(1)</script>", "attribute"),
        ("<img src=x onerror=alert(1)>", "html"),
        ("\" onmouseover=\"alert(1)", "attribute"),
        ("' onmouseover='alert(1)", "attribute"),
        ("\";alert(1);//", "script"),
        ("';alert(1);//", "script"),
        ("javascript:alert(1)", "url"),
    ]

    DOM_SINKS = [
        "eval(", "setTimeout(", "setInterval(", "document.write(",
        ".innerHTML", "location.href", "location.replace(", ".outerHTML"
    ]

    async def detect(self, url: str, html: str) -> List[Dict[str, Any]]:
        findings = []
        parsed = urlparse(url)
        url_params = parse_qs(parsed.query)
        
        # 1. DOM XSS Check
        if html:
            findings.extend(self.check_dom_sinks(url, html))

        # 2. Extract Form Parameters
        import re
        form_params = re.findall(r'<(?:input|select|textarea)[^>]+name=["\']([^"\']+)["\']', html, re.IGNORECASE)
        
        all_params = list(dict.fromkeys(list(url_params.keys()) + form_params))[:self.MAX_PARAMS]

        for param in all_params:
            # Check for reflection and context
            canary = f"aresxss{param}"
            reflected, context = await self.check_reflection(url, param, canary)
            
            if reflected:
                # Select payloads based on context
                test_payloads = [p for p, c in self.PAYLOADS if c == context or c == "html"]
                for payload in test_payloads:
                    if await self.verify_xss(url, param, payload):
                        findings.append(self.create_finding(
                            url, param, "Reflected XSS", "high",
                            f"Input reflected in {context} context. Payload '{payload}' successfully injected."
                        ))
                        break

        return findings

    async def check_reflection(self, url: str, param: str, canary: str) -> (bool, str):
        target_url = self.inject_payload(url, param, canary)
        try:
            resp = await self.client.get(target_url, timeout=4.0)
            text = resp.text
            if canary in text:
                if f"value=\"{canary}\"" in text or f"value='{canary}'" in text:
                    return True, "attribute"
                if f"<{canary}>" in text or f" {canary} " in text:
                    return True, "html"
                if f"'{canary}'" in text or f"\"{canary}\"" in text:
                    return True, "script"
                return True, "html"
        except Exception:
            pass
        return False, ""

    async def verify_xss(self, url: str, param: str, payload: str) -> bool:
        target_url = self.inject_payload(url, param, payload)
        try:
            resp = await self.client.get(target_url, timeout=4.0)
            if payload in resp.text:
                return True
        except Exception:
            pass
        return False

    def check_dom_sinks(self, url: str, html: str) -> List[Dict[str, Any]]:
        findings = []
        for sink in self.DOM_SINKS:
            if sink in html:
                findings.append({
                    "type": "Potential DOM XSS",
                    "severity": "medium",
                    "url": url,
                    "description": f"Found sensitive DOM sink '{sink}' in page source.",
                    "remediation": "Review client-side JavaScript code to ensure user-supplied data is not passed to this sink without proper sanitization."
                })
        return findings

    def inject_payload(self, url: str, param: str, payload: str) -> str:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        params[param] = [payload]
        new_query = urlencode(params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))

    def create_finding(self, url: str, param: str, type: str, severity: str, evidence: str) -> Dict[str, Any]:
        return {
            "type": type,
            "severity": severity,
            "url": url,
            "parameter": param,
            "description": f"{type} detected on parameter '{param}'.",
            "remediation": "Implement proper output encoding (e.g., HTML entity encoding) and use a strong Content Security Policy (CSP).",
            "evidence": evidence
        }
