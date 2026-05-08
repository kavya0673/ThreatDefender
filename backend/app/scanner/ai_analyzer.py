import json
import logging
from typing import Dict, List, Optional
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None

    async def analyze_finding(self, finding: Dict) -> Dict:
        """
        Uses AI to provide deep analysis of a security finding.
        """
        if not self.client:
            logger.warning("OpenAI API key missing. Using mock analysis.")
            return self._get_mock_analysis(finding)

        prompt = self._build_prompt(finding)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a senior security researcher and penetration tester. Provide detailed, technical, and actionable security analysis."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
        except Exception as e:
            logger.error(f"AI Analysis failed: {e}")
            return self._get_mock_analysis(finding)

    def _build_prompt(self, finding: Dict) -> str:
        return f"""
        Analyze the following security finding discovered by an automated scanner:
        
        URL: {finding.get('url')}
        Type: {finding.get('type')}
        Parameter: {finding.get('parameter', 'N/A')}
        Evidence: {finding.get('evidence', 'N/A')}
        Initial Severity: {finding.get('severity')}
        
        Please provide a JSON response with the following fields:
        1. explanation: Clear technical explanation of the vulnerability.
        2. attack_possibility: How an attacker would practically exploit this.
        3. business_impact: Potential impact on the business (data loss, reputation, etc.).
        4. false_positive_reduction: Reasoning why this might be a false positive or why it's a true positive.
        5. remediation: Step-by-step technical remediation instructions.
        6. risk_score: A numerical risk score from 0-10 based on CVSS principles.
        7. prioritized_action: One-sentence priority action for the dev team.
        """

    def _get_mock_analysis(self, finding: Dict) -> Dict:
        vuln_type = finding.get("type", "Unknown")
        return {
            "explanation": f"The scanner detected a potential {vuln_type}. This vulnerability occurs when the application fails to properly validate or sanitize user-supplied data before processing it.",
            "attack_possibility": "An attacker could inject malicious payloads to manipulate server logic or steal user data.",
            "business_impact": "Medium to High. Potential for unauthorized data access or disruption of service.",
            "false_positive_reduction": "True positive likely based on reflection/response patterns.",
            "remediation": f"Implement strict validation and use secure coding patterns specifically for {vuln_type}.",
            "risk_score": 7.5,
            "prioritized_action": "Verify the endpoint and implement server-side validation immediately."
        }
