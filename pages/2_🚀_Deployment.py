import streamlit as st
import json
import uuid
from datetime import datetime

st.set_page_config(
    page_title="SOAR Deployment",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 SOAR Playbook Deployment")
st.caption("Generate a production-ready SOAR playbook for execution")

st.divider()

# -----------------------------
# Input Section
# -----------------------------
st.subheader("🔔 SIEM Alert Input")

use_case = st.text_area(
    "Describe the alert raised by SIEM",
    placeholder="Example: Multiple failed login attempts detected from a single external IP targeting multiple user accounts...",
    height=150
)

generate = st.button("Generate Deployment Playbook", type="primary")

# -----------------------------
# Helper: Build Playbook
# -----------------------------
def build_playbook(alert_text: str) -> dict:
    return {
        "playbook_id": f"SOAR-{uuid.uuid4()}",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "mode": "deployment",
        "alert_summary": alert_text,
        "severity": "High",
        "trigger": {
            "source": "SIEM",
            "type": "Brute Force Detection",
            "confidence_required": True
        },
        "workflow": [
            {
                "step": 1,
                "name": "Initial Alert Triage & Enrichment",
                "automation": True,
                "actions": [
                    "Fetch alert metadata",
                    "Extract source IP",
                    "Extract targeted user accounts",
                    "Collect login attempt metrics"
                ]
            },
            {
                "step": 2,
                "name": "Threat Intelligence Lookup",
                "automation": True,
                "actions": [
                    "Check IP reputation",
                    "Query threat intelligence feeds",
                    "Enrich with geo-location"
                ]
            },
            {
                "step": 3,
                "name": "Decision Gate",
                "automation": False,
                "decision": "Threat Confidence Assessment"
            },
            {
                "step": 4,
                "name": "Containment",
                "automation": True,
                "actions": [
                    "Block source IP",
                    "Disable affected user accounts (if compromised)"
                ],
                "condition": "High Confidence"
            },
            {
                "step": 5,
                "name": "Manual Review Path",
                "automation": False,
                "actions": [
                    "L1 analyst review",
                    "Escalate to L2 if required"
                ],
                "condition": "Low or Medium Confidence"
            },
            {
                "step": 6,
                "name": "Evidence Preservation & Closure",
                "automation": True,
                "actions": [
                    "Store logs and artifacts",
                    "Update incident record",
                    "Notify stakeholders"
                ]
            }
        ],
        "output": {
            "ticketing": "SOC Incident Ticket",
            "notifications": ["SOC", "IR Team"],
            "status": "Ready for Execution"
        }
    }

# -----------------------------
# Output Section
# -----------------------------
if generate:
    if not use_case.strip():
        st.error("Please describe the SIEM alert before generating a playbook.")
    else:
        with st.spinner("Generating deployment-ready SOAR playbook..."):
            playbook = build_playbook(use_case)

        st.success("Deployment playbook generated successfully")

        st.subheader("📦 Deployment Playbook (JSON)")
        st.json(playbook)

        st.download_button(
            label="⬇️ Download Playbook (JSON)",
            data=json.dumps(playbook, indent=2),
            file_name="soar_deployment_playbook.json",
            mime="application/json"
        )
