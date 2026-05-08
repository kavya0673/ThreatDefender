from app.scanner.plugins.base import BaseDetector
from typing import List, Dict, Any

class ConfigDetector(BaseDetector):
    EXPOSED_PATHS = [
        ".env", ".git/HEAD", "config.php", "wp-config.php",
        "backup.sql", "backup.zip", "admin/", "phpinfo.php",
        ".htaccess", ".DS_Store", "server-status"
    ]

    async def detect(self, url: str, html: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
        findings = []
        h = {k.lower(): v for k, v in headers.items()}
        
        # 1. Header Security Analysis
        findings.extend(self.analyze_headers(url, h))
        
        # 2. Cookie Security Analysis
        # Note: In a real app, we'd get cookie info from the response object
        # For this foundation, we'll check the Set-Cookie header if present
        if "set-cookie" in h:
            findings.extend(self.analyze_cookies(url, h["set-cookie"]))

        # 3. Directory Listing Check
        if "Index of /" in html or "Parent Directory" in html:
            findings.append({
                "type": "Directory Listing Enabled",
                "severity": "medium",
                "url": url,
                "description": "The server allows directory listing, which can expose sensitive files.",
                "remediation": "Disable directory indexing in server configuration (e.g., 'Options -Indexes' in Apache)."
            })

        return findings

    def analyze_headers(self, url: str, h: Dict[str, str]) -> List[Dict[str, Any]]:
        findings = []
        
        # CSP
        if "content-security-policy" not in h:
            findings.append({
                "type": "Missing CSP",
                "severity": "high",
                "url": url,
                "description": "Content-Security-Policy header is missing. Increases risk of XSS.",
                "remediation": "Implement a strict Content-Security-Policy."
            })

        # HSTS
        if "strict-transport-security" not in h:
            findings.append({
                "type": "Missing HSTS",
                "severity": "high",
                "url": url,
                "description": "Strict-Transport-Security header is missing. Connection can be downgraded to HTTP.",
                "remediation": "Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains'."
            })

        # X-Frame-Options
        if "x-frame-options" not in h and "frame-ancestors" not in h.get("content-security-policy", ""):
            findings.append({
                "type": "Missing X-Frame-Options",
                "severity": "medium",
                "url": url,
                "description": "X-Frame-Options header missing. Page is vulnerable to Clickjacking.",
                "remediation": "Add 'X-Frame-Options: DENY' or 'SAMEORIGIN'."
            })

        # CORS
        cors = h.get("access-control-allow-origin", "")
        if cors == "*":
            findings.append({
                "type": "Weak CORS Policy",
                "severity": "medium",
                "url": url,
                "description": "Access-Control-Allow-Origin is set to '*'. Allows any domain to read response data.",
                "remediation": "Restrict CORS to specific trusted domains."
            })

        # Server Information Leakage
        server = h.get("server", "")
        x_powered = h.get("x-powered-by", "")
        if server or x_powered:
            findings.append({
                "type": "Exposed Server Header",
                "severity": "low",
                "url": url,
                "description": f"Server identifies as '{server or x_powered}'. Aids in targeted attacks.",
                "remediation": "Configure server to suppress identifying information headers."
            })

        return findings

    def analyze_cookies(self, url: str, cookie_header: str) -> List[Dict[str, Any]]:
        findings = []
        cookies = cookie_header.split(",")
        for cookie in cookies:
            c_lower = cookie.lower()
            name = cookie.split("=")[0].strip()
            if "httponly" not in c_lower:
                findings.append({
                    "type": "Insecure Cookie (Missing HttpOnly)",
                    "severity": "medium",
                    "url": url,
                    "description": f"Cookie '{name}' is missing the HttpOnly flag.",
                    "remediation": "Set the HttpOnly flag for all sensitive cookies."
                })
            if "secure" not in c_lower and url.startswith("https"):
                findings.append({
                    "type": "Insecure Cookie (Missing Secure)",
                    "severity": "medium",
                    "url": url,
                    "description": f"Cookie '{name}' is missing the Secure flag on an HTTPS site.",
                    "remediation": "Set the Secure flag for all cookies."
                })
        return findings
