import streamlit as st
from core.playbook_engine import generate_playbook
from core.diagram_engine import render_mermaid_flow


st.set_page_config(
    page_title="SOAR Deployment Playbook",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 SOAR Deployment Playbook")
st.caption("Production-grade SOAR execution flow (no simulations)")

# -----------------------------
# INPUT
# -----------------------------
st.subheader("Describe the SIEM alert")

use_case = st.text_area(
    "Deployment use case",
    height=180,
    placeholder="""
Example:
Multiple failed VPN logins followed by a successful login
from a previously unseen country for a privileged user.
""",
)

# -----------------------------
# ACTION
# -----------------------------
if st.button("Generate Deployment Playbook"):
    if not use_case.strip():
        st.warning("Please describe the SIEM alert")
        st.stop()

    with st.spinner("Analyzing alert and building SOAR playbook..."):
        result = generate_playbook(
            alert_text=use_case,
            mode="deployment",
            depth="Advanced",
        )

    st.success("Deployment playbook generated")

    # -----------------------------
    # SUMMARY
    # -----------------------------
    st.subheader("Executive Summary")
    st.write(result["summary"])

    # -----------------------------
    # DIAGRAM
    # -----------------------------
    st.subheader("SOAR Execution Flow")

    mermaid_code = render_mermaid_flow(result["blocks"])
    st.markdown(f"```mermaid\n{mermaid_code}\n```")

    # -----------------------------
    # BLOCK DETAILS
    # -----------------------------
    st.subheader("Playbook Steps")

    for block in result["blocks"]:
        with st.expander(block["title"], expanded=False):
            st.markdown(f"**Type:** {block['type']}")
            st.markdown(block["description"])
