import glob
import json
import os
import streamlit as st
from main import run_sre_pipeline

# Page Config
st.set_page_config(page_title="SRE Agent Pipeline", layout="wide", page_icon="🚨")

st.title("🚨 Autonomous SRE Remediation Engine")
st.markdown("Human-in-the-Loop Infrastructure Approval Dashboard")

# Ensure sessions directory exists
os.makedirs("data/sessions", exist_ok=True)

# Sidebar: Controls
st.sidebar.header("Agent Controls")
if st.sidebar.button("🚨 Simulate New Outage", type="primary", use_container_width=True):
    with st.spinner("Multi-Agent Team investigating live telemetry..."):
        run_sre_pipeline()
    st.toast("Pipeline execution complete!", icon="✅")
    st.rerun()

st.sidebar.divider()
st.sidebar.header("Active Incidents")

# Load session files
session_files = glob.glob("data/sessions/*.json")

if not session_files:
    st.info("No active incidents found. Click **'Simulate New Outage'** in the sidebar to generate an incident.")
else:
    selected_file = st.sidebar.selectbox("Select Incident Ticket", session_files)

    with open(selected_file, "r", encoding="utf-8") as f:
        session = json.load(f)

    st.sidebar.metric("Status", session.get("status", "UNKNOWN"))
    st.sidebar.metric("Assigned Agent", session.get("current_agent", "None"))

    # Main Dashboard Layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📡 Intake & Telemetry")
        with st.expander("Raw Alert Payload", expanded=False):
            st.json(session.get("raw_alert", {}))

        st.markdown("**Context Pruner (Token Optimization):**")
        st.json(session.get("compressed_telemetry", {}))

        st.subheader("🕵️ Diagnostic Findings")
        report = session.get("diagnostic_report", {})
        st.error(f"**Root Cause Identified:**\n\n{report.get('root_cause_analysis', 'N/A')}")
        with st.expander("Evidence Metrics (MCP Tools)", expanded=False):
            st.json(report.get("evidence_metrics", {}))

    with col2:
        st.subheader("🛠️ Remediation Proposal")
        remedy = session.get("remediation_plan", {})

        st.info(f"**Action Plan:**\n\n{remedy.get('proposed_plan', 'N/A')}")

        st.markdown("**Executable Fix:**")
        st.code(remedy.get("executable_script", ""), language="bash")

        st.divider()
        st.subheader("Human-in-the-Loop Approval")

        if remedy.get("requires_human_approval"):
            st.warning(f"**Risk Level:** {remedy.get('risk_level', 'UNKNOWN')}")
            if st.button("✅ Approve & Execute Fix", type="primary", use_container_width=True):
                st.toast("Executing AWS CLI command...", icon="🚀")
                st.success(f"Incident {session.get('incident_id')} resolved successfully!")
                st.balloons()