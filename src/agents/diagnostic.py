import json
import os
from typing import Any, Dict
from openai import OpenAI
from dotenv import load_dotenv
from src.tools.mcp_telemetry import MCPTelemetryServer

load_dotenv()


class DiagnosticAgent:
    """Agent 2: Queries infrastructure state using MCP tools and deduces root cause via LLM."""

    def __init__(self):
        self.name = "DiagnosticAgent"
        self.role = "SRE Cloud Investigator"
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def investigate(self, alert_context: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[{self.name}] Executing MCP tools to gather telemetry...")

        # 1. Fetch live metrics via MCP Tools
        metrics_response = MCPTelemetryServer.execute_tool(
            "query_cloudwatch_metrics",
            {"instance_id": alert_context.get("service", "prod-aurora-pg-01")},
        )
        metrics_data = json.loads(metrics_response)

        param_response = MCPTelemetryServer.execute_tool(
            "describe_db_parameters",
            {"parameter_group_name": "prod-pg-params"},
        )
        param_data = json.loads(param_response)

        print(f"[{self.name}] Analyzing telemetry via Groq (Llama 3.3) to find root cause...")

        # 2. Feed the tool output to the LLM for analysis
        prompt = f"""
        You are a Principal SRE Cloud Investigator. Analyze the alert context alongside the live database metrics and parameter states.
        
        Alert Context: {json.dumps(alert_context, indent=2)}
        Live Metrics: {json.dumps(metrics_data['metrics'], indent=2)}
        DB Parameters: {json.dumps(param_data['parameters'], indent=2)}
        
        Identify the exact root cause of the failure.
        Respond STRICTLY in JSON format with this key:
        - "root_cause_analysis": string (detailed explanation of what is failing and why)
        """

        response = self.client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "system", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        analysis = json.loads(response.choices[0].message.content)

        return {
            "root_cause_analysis": analysis.get("root_cause_analysis", "Unable to determine root cause."),
            "evidence_metrics": metrics_data.get("metrics", {}),
            "parameter_state": param_data.get("parameters", {}),
        }