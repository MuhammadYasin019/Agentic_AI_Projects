import json
from src.state.session_manager import SessionManager
from src.state.context_pruner import ContextPruner
from src.agents.triage import TriageAgent
from src.agents.diagnostic import DiagnosticAgent
from src.agents.remediation import RemediationAgent


def run_sre_pipeline():
    # 1. Initialize Mock Infrastructure Alert
    raw_alert = {
        "incident_id": "INC-8832",
        "service": "prod-aurora-pg-01",
        "error_signature": "HTTP 504 Gateway Timeout / Pool Full",
        "active_connections": 498,
        "raw_logs": [
            "2026-10-05T18:20:01Z [INFO] Connection pool health check OK",
            "2026-10-05T18:23:40Z [ERROR] Remaining connection slots: 2.",
            "2026-10-05T18:24:15Z [ALERT] ALB targets returning HTTP 504 Gateway Timeout"
        ]
    }
    
    print("\n" + "="*50)
    print("🚀 INITIATING AUTONOMOUS SRE PIPELINE")
    print("="*50)

    # 2. ADK Session Management Initialization
    session_mgr = SessionManager()
    session = session_mgr.create_session(raw_alert["incident_id"], raw_alert)
    incident_id = session["incident_id"]

    # 3. Initialize Agents
    triage = TriageAgent()
    diagnostic = DiagnosticAgent()
    remediation = RemediationAgent()

    # --- STAGE 1: TRIAGE ---
    triage_result = triage.process_alert(raw_alert)
    if triage_result["requires_escalation"]:
        session_mgr.record_handoff(
            incident_id, triage.name, diagnostic.name, "ESCALATED_TO_DIAGNOSTICS", triage_result["triage_notes"]
        )
        
        # --- STAGE 2: DIAGNOSTICS & CONTEXT WINDOW MANAGEMENT ---
        # Prune context to save tokens before heavy diagnostic work
        pruned_logs = ContextPruner.prune_telemetry({"active_connections": raw_alert["active_connections"]}, raw_alert["raw_logs"])
        session["compressed_telemetry"] = pruned_logs
        
        diag_report = diagnostic.investigate(raw_alert)
        session["diagnostic_report"] = diag_report
        session_mgr.save_session(incident_id, session)
        
        session_mgr.record_handoff(
            incident_id, diagnostic.name, remediation.name, "ESCALATED_TO_REMEDIATION", "Root cause identified."
        )

        # --- STAGE 3: REMEDIATION ---
        remedy = remediation.generate_fix(diag_report)
        session["remediation_plan"] = remedy
        session_mgr.save_session(incident_id, session)
        
        print("\n" + "="*50)
        print("✅ PIPELINE EXECUTION COMPLETE. HUMAN APPROVAL REQUIRED.")
        print("="*50)
        print(f"Root Cause: {diag_report['root_cause_analysis']}")
        print(f"Fix Proposed: {remedy['proposed_plan']}")
        print(f"CLI Command: {remedy['executable_script']}")
        
    else:
        print("Incident resolved at Triage stage. No escalation needed.")

if __name__ == "__main__":
    run_sre_pipeline()