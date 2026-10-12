import json
import os
from typing import Any, Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class RemediationAgent:
    """Agent 3: Synthesizes diagnostic findings into an executable CLI fix via LLM."""

    def __init__(self):
        self.name = "RemediationAgent"
        self.role = "Principal SRE Architect"
        # Initializing the OpenAI client to point to Groq's free endpoint
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY")
        )

    def generate_fix(self, diagnostic_report: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[{self.name}] Drafting safe remediation script via Groq (Llama 3.3)...")
        
        prompt = f"""
        You are a Principal SRE Architect. Based on the following root cause analysis, generate a precise remediation plan and the exact CLI command to fix the issue.
        
        Root Cause Report: {json.dumps(diagnostic_report, indent=2)}
        
        Respond STRICTLY in JSON format with the following keys:
        - "proposed_plan": string (summary of the fix)
        - "executable_script": string (the exact AWS CLI or bash command to resolve the issue)
        - "requires_human_approval": boolean (always set to true for infrastructure changes)
        - "risk_level": string (e.g., "LOW", "MEDIUM", "HIGH", "CRITICAL")
        """

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "system", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.2
        )
        
        return json.loads(response.choices[0].message.content)