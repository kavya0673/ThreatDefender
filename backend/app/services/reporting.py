import os
import json
from fpdf import FPDF
from datetime import datetime
from typing import Dict, Any
from app.models.models import Scan, Finding

class SecurityReport(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('helvetica', 'I', 8)
            self.set_text_color(128)
            self.cell(0, 10, 'ThreatDefender Security Assessment Report - Confidential', 0, 0, 'R')
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 16)
        self.set_fill_color(30, 41, 59) # Deep Blue
        self.set_text_color(255)
        self.cell(0, 12, f'  {title}', 0, 1, 'L', True)
        self.ln(4)

    def sub_title(self, title):
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(37, 99, 235) # Primary Blue
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

class ReportingService:
    def __init__(self, output_dir: str | None = None):
        if output_dir is None:
            output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf(self, scan: Scan, findings: list) -> str:
        pdf = SecurityReport()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # 1. Cover Page
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 32)
        pdf.set_y(80)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 20, 'ThreatDefender', 0, 1, 'C')
        pdf.set_font('helvetica', 'B', 20)
        pdf.cell(0, 15, 'Enterprise Security Assessment', 0, 1, 'C')
        
        pdf.set_y(150)
        pdf.set_font('helvetica', '', 12)
        pdf.cell(0, 10, f'Target: {scan.target_url}', 0, 1, 'C')
        pdf.cell(0, 10, f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
        pdf.cell(0, 10, f'Risk Score: {scan.risk_score}/100', 0, 1, 'C')
        
        # 2. Executive Summary
        pdf.add_page()
        pdf.chapter_title('1. Executive Summary')
        pdf.set_font('helvetica', '', 11)
        pdf.set_text_color(0)
        summary = f"The security assessment of {scan.target_url} identified {len(findings)} total vulnerabilities. " \
                  f"The overall risk posture is rated as {self._get_rating(scan.risk_score)} based on the findings."
        pdf.multi_cell(0, 8, summary)
        pdf.ln(5)
        
        # 3. Technical Findings
        pdf.add_page()
        pdf.chapter_title('2. Technical Findings')
        
        for idx, f in enumerate(findings, 1):
            pdf.sub_title(f"{idx}. {f.type}")
            
            # Severity Table
            pdf.set_font('helvetica', 'B', 10)
            pdf.set_fill_color(241, 245, 249)
            pdf.cell(40, 10, ' Severity:', 1, 0, 'L', True)
            
            # Color coding
            if f.severity.lower() == 'critical': pdf.set_text_color(220, 38, 38)
            elif f.severity.lower() == 'high': pdf.set_text_color(234, 88, 12)
            else: pdf.set_text_color(0)
            
            pdf.cell(50, 10, f' {f.severity.upper()}', 1, 0, 'L')
            pdf.set_text_color(0)
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(40, 10, ' CVSS Score:', 1, 0, 'L', True)
            pdf.set_font('helvetica', '', 10)
            pdf.cell(50, 10, f' {self._get_cvss(f)}', 1, 1, 'L')
            
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(40, 10, ' Endpoint:', 1, 0, 'L', True)
            pdf.set_font('helvetica', '', 9)
            pdf.cell(140, 10, f' {f.url}', 1, 1, 'L')
            
            pdf.ln(5)
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(0, 8, 'Description:', 0, 1)
            pdf.set_font('helvetica', '', 10)
            pdf.multi_cell(0, 6, f.description or "No description supplied.")
            
            pdf.ln(3)
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(0, 8, 'Remediation:', 0, 1)
            pdf.set_font('helvetica', '', 10)
            pdf.multi_cell(0, 6, f.remediation or "Review the affected endpoint and apply the appropriate mitigation.")
            
            # AI Insight
            if f.ai_analysis:
                try:
                    ai = json.loads(f.ai_analysis)
                except (TypeError, json.JSONDecodeError):
                    ai = {"explanation": str(f.ai_analysis)}
                pdf.ln(3)
                pdf.set_fill_color(239, 246, 255)
                pdf.set_font('helvetica', 'B', 10)
                pdf.cell(0, 8, ' AI Security Analysis:', 0, 1, 'L', True)
                pdf.set_font('helvetica', 'I', 9)
                pdf.multi_cell(0, 6, ai.get('explanation') or ai.get('summary') or '')
            
            pdf.ln(10)

        filename = f"Report_{scan.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        pdf.output(filepath)
        return filepath

    def _get_rating(self, score: int) -> str:
        if score >= 70: return "CRITICAL RISK"
        if score >= 40: return "MEDIUM RISK"
        return "SECURE"

    def _get_cvss(self, f: Finding) -> float:
        # In a real app, this would be a field
        return 9.8 if f.severity == 'critical' else 7.5 if f.severity == 'high' else 5.0
