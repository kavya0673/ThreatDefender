import httpx
import asyncio
from typing import List, Dict
import logging

class VulnerabilityModule:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.findings = []

    async def scan(self, endpoint: Dict):
        raise NotImplementedError

class SQLInjectionModule(VulnerabilityModule):
    PAYLOADS = [
        "' OR '1'='1",
        "'; WAITFOR DELAY '0:0:5'--",
        "\" OR \"1\"=\"1",
        "admin'--",
        "' UNION SELECT NULL, NULL, NULL--"
    ]

    async def scan(self, endpoint: Dict):
        url = endpoint["url"]
        method = endpoint.get("method", "GET")
        
        if method == "GET":
            # Test query parameters
            # Simplified: just append to URL for now
            for payload in self.PAYLOADS:
                try:
                    # Very basic check: look for SQL errors in response
                    test_url = f"{url}?id={payload}" # Placeholder logic
                    response = await self.client.get(test_url)
                    if self._check_sql_errors(response.text):
                        self.findings.append({
                            "type": "SQL Injection",
                            "severity": "High",
                            "url": url,
                            "payload": payload,
                            "description": "Potential SQL Injection detected via error-based analysis."
                        })
                except Exception:
                    pass

    def _check_sql_errors(self, html: str) -> bool:
        errors = [
            "SQL syntax", "mysql_fetch", "ORA-01756", 
            "SQLite/JDBCDriver", "PostgreSQL query failed"
        ]
        return any(error in html for error in errors)

class XSSModule(VulnerabilityModule):
    PAYLOADS = [
        "<script>alert(1)</script>",
        "\"><script>alert(1)</script>",
        "<img src=x onerror=alert(1)>"
    ]

    async def scan(self, endpoint: Dict):
        url = endpoint["url"]
        for payload in self.PAYLOADS:
            try:
                response = await self.client.get(url, params={"q": payload})
                if payload in response.text:
                    self.findings.append({
                        "type": "Cross-Site Scripting (XSS)",
                        "severity": "Medium",
                        "url": url,
                        "payload": payload,
                        "description": "Reflected XSS detected: payload found in response body."
                    })
            except Exception:
                pass

class SecurityHeaderModule(VulnerabilityModule):
    async def scan(self, endpoint: Dict):
        url = endpoint["url"]
        try:
            response = await self.client.get(url)
            headers = response.headers
            
            missing = []
            if "Content-Security-Policy" not in headers:
                missing.append("Content-Security-Policy")
            if "X-Frame-Options" not in headers:
                missing.append("X-Frame-Options")
            if "Strict-Transport-Security" not in headers:
                missing.append("Strict-Transport-Security")
                
            if missing:
                self.findings.append({
                    "type": "Missing Security Headers",
                    "severity": "Low",
                    "url": url,
                    "description": f"Missing headers: {', '.join(missing)}"
                })
        except Exception:
            pass
