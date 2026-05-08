import asyncio
import time
import random
import string
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from app.scanner.plugins.base import BaseDetector

class SQLIDetector(BaseDetector):
    # Core payloads for different SQLi types
    MAX_PARAMS = 3
    ERROR_PAYLOADS = ["'", "\"", "';--", "') OR 1=1--"]
    
    BOOLEAN_TESTS = [
        (" AND 1=1", " AND 1=2"),
        ("' AND '1'='1", "' AND '1'='2"),
        ("\" AND \"1\"=\"1", "\" AND \"1\"=\"2"),
        (") AND (1=1", ") AND (1=2")
    ]
    
    TIME_PAYLOADS = []
    
    COMMON_ERRORS = [
        "SQL syntax", "mysql_fetch", "ORA-01756", "SQLite3::prepare",
        "PostgreSQL query failed", "Microsoft OLE DB Provider for SQL Server",
        "Driver] [SQL Server]", "SQLSTATE[42000]", "MariaDB server version",
        "syntax error at or near", "unterminated quoted string"
    ]

    async def detect(self, url: str, html: str) -> List[Dict[str, Any]]:
        findings = []
        parsed = urlparse(url)
        url_params = parse_qs(parsed.query)
        
        # 1. Extract Form Parameters from HTML
        import re
        form_params = re.findall(r'<(?:input|select|textarea)[^>]+name=["\']([^"\']+)["\']', html, re.IGNORECASE)
        
        # Combine all testable parameters
        all_params = list(dict.fromkeys(list(url_params.keys()) + form_params))[:self.MAX_PARAMS]
        
        if not all_params:
            return findings

        for param in all_params:
            # A. Error-Based SQLi
            for payload in self.ERROR_PAYLOADS:
                is_vuln, evidence = await self.check_error_sqli(url, param, payload)
                if is_vuln:
                    findings.append(self.create_finding(url, param, "Error-based SQL Injection", "critical", evidence))
                    break # Found one, move to next param or type

            # B. Boolean-Based SQLi (If error-based didn't hit)
            found_sqli = any(f["parameter"] == param for f in findings)
            if not found_sqli:
                is_vuln, evidence = await self.check_boolean_sqli(url, param)
                if is_vuln:
                    findings.append(self.create_finding(url, param, "Boolean-based SQL Injection", "high", evidence))

            # C. Time-Based SQLi
            found_sqli = any(f["parameter"] == param for f in findings)
            if not found_sqli:
                for payload, delay in self.TIME_PAYLOADS:
                    is_vuln, evidence = await self.check_time_sqli(url, param, payload, delay)
                    if is_vuln:
                        findings.append(self.create_finding(url, param, "Time-based SQL Injection", "critical", evidence))
                        break

        return findings

    async def check_error_sqli(self, url: str, param: str, payload: str) -> (bool, str):
        target_url = self.inject_payload(url, param, payload)
        try:
            resp = await self.client.get(target_url, timeout=4.0)
            for error_pattern in self.COMMON_ERRORS:
                if error_pattern.lower() in resp.text.lower():
                    return True, f"SQL Error pattern '{error_pattern}' found in response for payload: {payload}"
        except Exception:
            pass
        return False, ""

    async def check_boolean_sqli(self, url: str, param: str) -> (bool, str):
        try:
            # Get baseline
            base_resp = await self.client.get(url, timeout=4.0)
            base_content = base_resp.text
            
            for true_p, false_p in self.BOOLEAN_TESTS:
                true_url = self.inject_payload(url, param, true_p)
                false_url = self.inject_payload(url, param, false_p)
                
                t_resp = await self.client.get(true_url, timeout=4.0)
                f_resp = await self.client.get(false_url, timeout=4.0)
                
                # Compare responses
                if t_resp.text != f_resp.text:
                    # Check if response length or content significantly differs
                    if abs(len(t_resp.text) - len(f_resp.text)) > 20:
                        return True, f"Boolean differential detected: Response content changed between '{true_p}' and '{false_p}'"
        except Exception:
            pass
        return False, ""

    async def check_time_sqli(self, url: str, param: str, payload: str, delay: int) -> (bool, str):
        target_url = self.inject_payload(url, param, payload)
        
        try:
            start_time = time.time()
            await self.client.get(target_url, timeout=delay + 10.0)
            elapsed = time.time() - start_time
            
            if elapsed >= delay:
                # Re-test to confirm (avoid network jitter)
                start_time = time.time()
                await self.client.get(target_url, timeout=delay + 10.0)
                if (time.time() - start_time) >= delay:
                    return True, f"Time-based delay detected: Response took {elapsed:.2f}s with payload: {payload}"
        except Exception:
            pass
        return False, ""

    def inject_payload(self, url: str, param: str, payload: str) -> str:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # If param doesn't exist in query, add it
        if param not in params:
            params[param] = ["test" + payload]
        else:
            original = params[param][0]
            params[param] = [original + payload]
            
        new_query = urlencode(params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))

    def create_finding(self, url: str, param: str, type: str, severity: str, evidence: str) -> Dict[str, Any]:
        return {
            "type": type,
            "severity": severity,
            "url": url,
            "parameter": param,
            "description": f"Target appears vulnerable to {type} via parameter '{param}'.",
            "remediation": "Implement parameterized queries (prepared statements) and use an ORM to interact with the database. Sanitize and validate all user-supplied data.",
            "evidence": evidence
        }
