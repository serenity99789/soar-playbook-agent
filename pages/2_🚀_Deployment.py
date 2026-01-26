import streamlit as st

from core.playbook_engine import generate_deployment_playbook
from core.diagram_engine import build_soar_mermaid


# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="SOAR Deployment Playbook",
    layout="wide"
)

st.title("🚀 SOAR Deployment Playbook")


# -----------------------------
# Session State Init
# -----------------------------
if "deployment_result" not in st.session_state:
    st.session_state.deployment_result = None


# -----------------------------
# Generate Button
# -----------------------------
if st.button("Generate Deployment Playbook", type="primary"):
    with st.spinner("Generating SOAR deployment playbook..."):
        result = generate_deployment_playbook()

        st.session_state.deployment_result = result

    st.success("Deployment playbook generated")


# -----------------------------
# Render Output
# -----------------------------
if st.session_state.deployment_result:

    result = st.session_state.deployment_result

    # -------- Executive Summary --------
    st.subheader("Executive Summary")
    st.write(result.get("summary", "No summary generated."))

    st.markdown("---")

    # -------- SOAR Execution Flow --------
    st.subheader("SOAR Execution Flow")

    mermaid_diagram = build_soar_mermaid(
        blocks=result.get("blocks", [])
    )

    st.mermaid(mermaid_diagram)

    st.markdown("---")

    # -------- Confidence --------
    st.subheader("Model Confidence")
    confidence = result.get("confidence", "N/A")
    st.info(f"Confidence Score: **{confidence}**")
