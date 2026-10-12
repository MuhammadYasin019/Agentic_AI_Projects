import json
import os
from datetime import datetime
from typing import Any, Dict, Optional


class SessionManager:
    """Manages isolated incident session states persisted to disk."""

    def __init__(self, storage_dir: str = "data/sessions"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_filepath(self, incident_id: str) -> str:
        return os.path.join(self.storage_dir, f"{incident_id}.json")

    def create_session(self, incident_id: str, raw_alert: Dict[str, Any]) -> Dict[str, Any]:
        session_data = {
            "incident_id": incident_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "status": "TRIAGE",
            "current_agent": "TriageAgent",
            "raw_alert": raw_alert,
            "compressed_telemetry": None,
            "diagnostic_report": None,
            "remediation_plan": None,
            "history": [
                {
                    "stage": "INTAKE",
                    "timestamp": datetime.utcnow().isoformat(),
                    "note": f"Incident {incident_id} registered.",
                }
            ],
        }
        self.save_session(incident_id, session_data)
        return session_data

    def load_session(self, incident_id: str) -> Optional[Dict[str, Any]]:
        filepath = self._get_filepath(incident_id)
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_session(self, incident_id: str, data: Dict[str, Any]) -> None:
        data["updated_at"] = datetime.utcnow().isoformat()
        filepath = self._get_filepath(incident_id)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def record_handoff(self, incident_id: str, from_agent: str, to_agent: str, stage_status: str, notes: str) -> Dict[str, Any]:
        session = self.load_session(incident_id)
        if not session:
            raise ValueError(f"Session {incident_id} not found.")
        session["current_agent"] = to_agent
        session["status"] = stage_status
        session["history"].append({
            "stage": stage_status,
            "from": from_agent,
            "to": to_agent,
            "timestamp": datetime.utcnow().isoformat(),
            "note": notes,
        })
        self.save_session(incident_id, session)
        return session