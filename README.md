# 🚨 Autonomous SRE Remediation Engine

**Live Demo:** [View Dashboard](https://agenticaiprojects-daj7nb8hrdc3jmn6nkkfv6.streamlit.app/)

## Overview
This project is an autonomous multi-agent system designed to handle Site Reliability Engineering (SRE) tasks. It simulates a fully automated incident response pipeline where specialized AI agents collaborate to triage incoming cloud alerts, diagnose root causes using simulated Model Context Protocol (MCP) telemetry tools, and propose executable AWS CLI remediation scripts with a Human-in-the-Loop (HITL) approval dashboard.

## Multi-Agent Architecture
The pipeline is orchestrated using an interconnected hierarchy of task-specific agents:
* **Triage Agent:** Parses raw AWS CloudWatch/RDS alert payloads, assesses severity, and routes actionable incidents to the diagnostic tier.
* **Diagnostic Agent:** Leverages contextual prompt pruning and executes MCP tool calls to gather real-time telemetry, pinpointing bottlenecks like connection pool exhaustion or CPU saturation.
* **Remediation Agent:** Synthesizes the diagnostic findings into safe, production-grade AWS CLI commands (e.g., updating RDS parameter groups) and calculates risk levels.

## Tech Stack
* **Language:** Python 3
* **LLM Engine:** Groq API (Utilizing fast, open-weights models)
* **Orchestration:** Custom multi-agent framework with Pydantic for strict JSON structured outputs
* **User Interface:** Streamlit (deployed via Streamlit Community Cloud)
* **State Management:** Local JSON session persistence

## Key Features
* **Human-in-the-Loop Validation:** All AI-generated infrastructure modifications require explicit human approval via the web UI before execution.
* **Token Optimization:** Implements context pruning to strip redundant logs and telemetry before passing payloads to the LLM, reducing latency and cost.
* **Live Simulation:** Includes a one-click outage simulation trigger to demonstrate the multi-agent reasoning process in real-time.

## Setup Instructions (Local Development)
1. Clone the repository: `git clone https://github.com/MuhammadYasin019/Agentic_AI_Projects.git`
2. Navigate to the project directory and create a virtual environment: `python -m venv venv`
3. Activate the environment: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file and add your Groq API key: `GROQ_API_KEY="your_key_here"`
6. Run the dashboard: `streamlit run app.py`
