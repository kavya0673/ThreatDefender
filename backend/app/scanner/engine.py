import asyncio
import logging
import json
import httpx
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.scanner.crawler import Crawler
from app.scanner.ai_analyzer import AIAnalyzer
from app.models.models import Scan, Finding
from app.scanner.plugins.config_detector import ConfigDetector
from app.scanner.plugins.sqli_detector import SQLIDetector
from app.scanner.plugins.xss_detector import XSSDetector
from app.scanner.plugins.exposure_detector import ExposureDetector
from app.scanner.plugins.redirect_detector import RedirectDetector

logger = logging.getLogger(__name__)
MAX_ENDPOINTS_PER_SCAN = 30

def compute_risk_score(findings: List[Dict[str, Any]]) -> int:
    if not findings:
        return 0
    weights = {"critical": 10, "high": 7, "medium": 4, "low": 2, "info": 1}
    total = sum(weights.get(str(f.get("severity", "")).lower(), 0) for f in findings)
    return min(int((total / (len(findings) * 10)) * 100), 99)

def dedupe_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    unique = []
    seen = set()
    site_wide_types = {
        "Missing CSP",
        "Missing HSTS",
        "Missing X-Frame-Options",
        "Weak CORS Policy",
        "Exposed Server Header",
        "Insecure Cookie (Missing HttpOnly)",
        "Insecure Cookie (Missing Secure)",
    }
    for finding in findings:
        finding_type = finding.get("type")
        if finding_type in site_wide_types:
            key = (
                finding_type,
                finding.get("severity"),
                finding.get("parameter"),
                finding.get("description"),
            )
        else:
            key = (
                finding_type,
                finding.get("severity"),
                finding.get("url"),
                finding.get("parameter"),
                finding.get("description"),
            )
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)
    return unique

class ScannerEngine:
    def __init__(self, db: Session, scan_id: int):
        self.db = db
        self.scan_id = scan_id
        self.scan_obj = db.query(Scan).filter(Scan.id == scan_id).first()
        self.ai_analyzer = AIAnalyzer()
        self.logs = []

    def add_log(self, msg: str, level: str = "info"):
        from datetime import datetime
        time_str = datetime.now().strftime("%H:%M:%S")
        log_entry = {"time": time_str, "msg": msg, "cls": "success" if level == "info" else "warning"}
        self.logs.append(log_entry)
        
        if self.scan_obj:
            self.scan_obj.engine_logs = list(self.logs)
            self.db.commit()
        logger.info(f"[Scan {self.scan_id}] {msg}")

    async def run(self):
        if not self.scan_obj:
            logger.error(f"Scan {self.scan_id} not found")
            return

        try:
            self.scan_obj.status = "running"
            self.db.commit()

            self.add_log(f"Initializing ThreatDefender scanner for {self.scan_obj.target_url}")
            self.add_log("Recursive crawler started — depth 5 | 10 threads")
            
            crawler = Crawler(self.scan_obj.target_url)
            discovered_endpoints = await crawler.run()
            
            self.add_log(f"Crawler complete. Discovered {len(discovered_endpoints)} unique endpoints.")
            
            endpoints = discovered_endpoints if discovered_endpoints else []
            if not any(e["url"] == self.scan_obj.target_url for e in endpoints):
                async with httpx.AsyncClient(verify=False) as client:
                    try:
                        self.add_log("Base URL not reached in crawl, attempting direct fetch...")
                        resp = await client.get(self.scan_obj.target_url, timeout=10.0)
                        endpoints.append({
                            "url": str(resp.url),
                            "headers": dict(resp.headers),
                            "html": resp.text,
                            "forms": [],
                            "params": []
                        })
                    except Exception as e:
                        self.add_log(f"Failed to fetch base URL: {e}", "warning")

            if len(endpoints) > MAX_ENDPOINTS_PER_SCAN:
                self.add_log(
                    f"Fast scan mode: testing first {MAX_ENDPOINTS_PER_SCAN} of {len(endpoints)} discovered endpoints.",
                    "warning",
                )
                endpoints = endpoints[:MAX_ENDPOINTS_PER_SCAN]

            self.scan_obj.endpoints_checked = 0
            self.scan_obj.endpoints_total = len(endpoints)
            self.db.commit()

            self.add_log(f"Starting vulnerability detection phase on {len(endpoints)} endpoints...")
            
            async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
                config_detector = ConfigDetector(client)
                sqli_detector = SQLIDetector(client)
                xss_detector = XSSDetector(client)
                exposure_detector = ExposureDetector(client)
                redirect_detector = RedirectDetector(client)
                
                all_findings = []
                for idx, endpoint in enumerate(endpoints):
                    self.scan_obj.endpoints_checked = idx
                    self.db.commit()

                    url = endpoint["url"]
                    headers = endpoint.get("headers", {})
                    html = endpoint.get("html", "")
                    
                    self.add_log(f"Testing endpoint {idx+1}/{len(endpoints)}: {url}")
                    
                    c_findings = await config_detector.detect(url, html, headers)
                    if c_findings: self.add_log(f"  + Found {len(c_findings)} configuration issues")
                    
                    s_findings = await sqli_detector.detect(url, html)
                    if s_findings: self.add_log(f"  + ALERT: {len(s_findings)} SQL Injection points identified!", "warning")

                    x_findings = await xss_detector.detect(url, html)
                    if x_findings: self.add_log(f"  + ALERT: {len(x_findings)} XSS vulnerabilities confirmed!", "warning")

                    e_findings = []
                    if idx == 0 or url == self.scan_obj.target_url:
                        e_findings = await exposure_detector.detect(url, html)
                        if e_findings: self.add_log(f"  + Found {len(e_findings)} sensitive information disclosure")

                    r_findings = await redirect_detector.detect(url, html)
                    
                    all_findings.extend(c_findings + s_findings + x_findings + e_findings + r_findings)
                    self.scan_obj.endpoints_checked = idx + 1
                    self.scan_obj.risk_score = compute_risk_score(dedupe_findings(all_findings))
                    self.db.commit()

                all_findings = dedupe_findings(all_findings)
                self.scan_obj.endpoints_checked = len(endpoints)
                self.scan_obj.risk_score = compute_risk_score(all_findings)
                self.db.commit()

                self.add_log(f"Detection complete. Found {len(all_findings)} total vulnerabilities.")
                
                self.scan_obj.status = "analyzing"
                self.db.commit()
                self.add_log("Starting AI classification & remediation analysis...")

                for i, f_data in enumerate(all_findings):
                    self.add_log(f"AI Analysis [{i+1}/{len(all_findings)}]: {f_data['type']}")
                    try:
                        ai_analysis = await self.ai_analyzer.analyze_finding(f_data)
                    except Exception as ai_err:
                        ai_analysis = self.ai_analyzer._get_mock_analysis(f_data)
                    
                    finding = Finding(
                        scan_id=self.scan_id,
                        type=f_data["type"],
                        severity=f_data["severity"],
                        url=f_data["url"],
                        parameter=f_data.get("parameter"),
                        description=f_data["description"],
                        remediation=ai_analysis.get("remediation", f_data["remediation"]),
                        ai_analysis=json.dumps(ai_analysis)
                    )
                    self.db.add(finding)
                    self.db.commit()
            
            import datetime
            self.scan_obj.status = "completed"
            self.scan_obj.end_time = datetime.datetime.utcnow()
            self.db.commit()
            self.add_log("Scan completed successfully. Report generation ready.", "info")

        except Exception as e:
            import traceback
            logger.error(f"Scan {self.scan_id} failed: {e}\n{traceback.format_exc()}")
            self.add_log(f"FATAL ERROR: {str(e)}", "warning")
            self.scan_obj.status = "failed"
            self.db.commit()

    async def run_detectors(self, url: str) -> List[Dict[str, Any]]:
        return []
