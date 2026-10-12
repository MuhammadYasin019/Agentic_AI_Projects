from typing import Any, Dict, List


class ContextPruner:
    """Filters noisy raw infrastructure telemetry to optimize token context."""

    @staticmethod
    def prune_telemetry(raw_metrics: Dict[str, Any], raw_logs: List[str]) -> Dict[str, Any]:
        # Filter log lines for high-signal error signatures
        critical_keywords = ["timeout", "deadlock", "exceeded", "504", "fatal", "pool full"]
        condensed_logs = [
            line.strip()
            for line in raw_logs
            if any(kw in line.lower() for kw in critical_keywords)
        ]

        # Extract only metric anomalies beyond normal operational bands
        anomalies = {}
        for metric, val in raw_metrics.items():
            if "connections" in metric and val > 80:
                anomalies[metric] = f"CRITICAL_HIGH: {val} active conns"
            elif "latency" in metric and val > 1000:
                anomalies[metric] = f"LATENCY_SPIKE: {val}ms"
            elif "cpu" in metric and val > 85:
                anomalies[metric] = f"CPU_THROTTLED: {val}%"
            else:
                anomalies[metric] = f"NOMINAL: {val}"

        return {
            "anomalies_detected": anomalies,
            "pruned_log_count": f"{len(condensed_logs)} / {len(raw_logs)} lines retained",
            "key_log_extracts": condensed_logs[:5],  # Retain top 5 critical entries
        }