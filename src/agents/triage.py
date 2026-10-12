import json
import os
from typing import Any, Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class TriageAgent:
    """Agent 1: Ingests raw alerts, evaluates severity dynamically via LLM, and routes the ticket."""
    
    def __init__(self):
        self.name = "TriageAgent"
        self.role = "L1 SOC Analyst"
        # Initializing the OpenAI client to point to Groq's free endpoint
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY")
        )

    def process_alert(self, raw_alert: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[{self.name}] Analyzing incoming alert payload via Groq (Llama 3.1)...")
        
        prompt = f"""
        You are an L1 SOC Analyst Triage Agent. Analyze the following infrastructure alert:
        {json.dumps(raw_alert, indent=2)}
        
        Determine the severity and whether it requires escalation to a specialized SRE.
        Respond STRICTLY in JSON format with the following keys:
        - "severity": string (LOW, MEDIUM, HIGH, CRITICAL)
        - "requires_escalation": boolean
        - "triage_notes": string (brief justification)
        """

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "system", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.2
        )
        
        return json.loads(response.choices[0].message.content)