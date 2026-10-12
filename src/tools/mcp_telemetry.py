import json
from typing import Any, Dict


# MCP-compliant tool schemas
MCP_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "query_cloudwatch_metrics",
            "description": "Retrieves real-time CPU, connection count, and query latency for an RDS instance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "instance_id": {"type": "string", "description": "The RDS DB instance identifier."},
                    "time_window_minutes": {"type": "integer", "description": "Lookback window in minutes."},
                },
                "required": ["instance_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "describe_db_parameters",
            "description": "Inspects database parameter group values such as max_connections and lock timeouts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "parameter_group_name": {"type": "string", "description": "The RDS parameter group name."},
                },
                "required": ["parameter_group_name"],
            },
        },
    },
]


class MCPTelemetryServer:
    """Simulates an external MCP server exposing AWS telemetry resources."""

    @staticmethod
    def query_cloudwatch_metrics(instance_id: str, time_window_minutes: int = 15) -> Dict[str, Any]:
        return {
            "instance_id": instance_id,
            "window_minutes": time_window_minutes,
            "metrics": {
                "cpu_utilization_pct": 94.2,
                "db_active_connections": 498,
                "max_allowed_connections": 500,
                "query_latency_ms": 3410,
                "504_gateway_timeout_rate_pct": 28.6,
            },
            "recent_logs": [
                "2026-10-05T18:20:01Z [INFO] Connection pool health check OK",
                "2026-10-05T18:22:14Z [WARN] Client connection queue building up (480 conns)",
                "2026-10-05T18:23:40Z [ERROR] Remaining connection slots: 2. Rejecting incoming pool requests.",
                "2026-10-05T18:24:02Z [ERROR] PostgreSQL: FATAL: remaining connection slots are reserved for non-replication superuser connections",
                "2026-10-05T18:24:15Z [ALERT] ALB targets returning HTTP 504 Gateway Timeout",
            ],
        }

    @staticmethod
    def describe_db_parameters(parameter_group_name: str) -> Dict[str, Any]:
        return {
            "parameter_group_name": parameter_group_name,
            "parameters": {
                "max_connections": "500",
                "idle_in_transaction_session_timeout": "0",  # Unbounded idle leaks
                "statement_timeout": "0",
            },
        }

    @classmethod
    def execute_tool(cls, tool_name: str, arguments: Dict[str, Any]) -> str:
        if tool_name == "query_cloudwatch_metrics":
            result = cls.query_cloudwatch_metrics(
                instance_id=arguments.get("instance_id", "prod-aurora-pg-01"),
                time_window_minutes=arguments.get("time_window_minutes", 15),
            )
            return json.dumps(result)
        elif tool_name == "describe_db_parameters":
            result = cls.describe_db_parameters(
                parameter_group_name=arguments.get("parameter_group_name", "prod-pg-params")
            )
            return json.dumps(result)
        return json.dumps({"error": f"Tool {tool_name} not recognized."})