import streamlit as st

from core.playbook_engine import generate_playbook
from core.diagram_engine import build_soar_mermaid


# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Deployment Playbook",
    layout="wide"
)

st.title("🚀 SOAR Deployment Playbook")


# -------------------------------------------------
# Session State
# -------------------------------------------------
if "deployment_result" not in st.session_state:
    st.session_state.deployment_result = None


# -------------------------------------------------
# Demo Alert (Deterministic for Leadership Demo)
# -------------------------------------------------
DEMO_ALERT_TEXT = """
Multiple One-Time Password (OTP) messages were detected being sent to a user’s
registered mobile number from unknown sources within a short time window.
The activity is associated with repeated DigiLocker login attempts and may
indicate brute-force authentication attempts, SMS spoofing, or SIM swap activity.
"""


# -------------------------------------------------
# Generate Button
# -------------------------------------------------
if st.button("Generate Deployment Playbook", type="primary"):
    with st.spinner("Generating SOAR deployment playbook..."):

        result = generate_playbook(
            alert_text=DEMO_ALERT_TEXT,
            mode="Deployment",
            depth="Deep"
        )

        st.session_state.deployment_result = result

    st.success("Deployment playbook generated")


# -------------------------------------------------
# Render Output
# -------------------------------------------------
if st.session_state.deployment_result:

    result = st.session_state.deployment_result

    # ---------------- Executive Summary ----------------
    st.subheader("Executive Summary")
    st.write(result.get("summary", "No summary generated."))

    st.markdown("---")

    # ---------------- SOAR Execution Flow ----------------
    st.subheader("SOAR Execution Flow")

    mermaid_diagram = build_soar_mermaid(
        blocks=result.get("blocks", [])
    )

    st.mermaid(mermaid_diagram)

    st.markdown("---")

    # ---------------- Confidence ----------------
    st.subheader("Model Confidence")
    confidence = result.get("confidence", "N/A")
    st.info(f"Confidence Score: **{confidence}**")
