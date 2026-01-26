import streamlit as st
from core.playbook_engine import generate_playbook
from core.diagram_engine import generate_soar_svg

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="SOAR Deployment View",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 SOAR Deployment View")
st.caption("Production-ready SOAR execution with governance and control")

# ---------------- SESSION STATE ----------------
if "deployment_result" not in st.session_state:
    st.session_state.deployment_result = None

# ---------------- INPUT ----------------
st.subheader("Describe the SIEM alert")

alert_text = st.text_area(
    "Example:",
    placeholder="Suspicious PowerShell execution detected on multiple endpoints...",
    height=160
)

# ---------------- GENERATE ----------------
if st.button("Generate Deployment Playbook"):
    if not alert_text.strip():
        st.warning("Please describe the SIEM alert.")
    else:
        with st.spinner("Generating deployment playbook..."):
            st.session_state.deployment_result = generate_playbook(
                alert_text=alert_text,
                mode="deployment",
                depth="Advanced"
            )

# ---------------- OUTPUT ----------------
if st.session_state.deployment_result:

    result = st.session_state.deployment_result
    blocks = result["blocks"]

    st.success("Deployment playbook generated")

    # ---------- DEPLOYMENT STEPS ----------
    st.header("📋 Deployment Steps")

    for i, block in enumerate(blocks, 1):
        with st.expander(f"Step {i}: {block['title']}"):
            st.markdown(f"**Purpose:** {block.get('description', '—')}")

    # ---------- EXECUTION FLOW ----------
    st.header("🧭 SOAR Execution Flow")

    graph = generate_soar_svg(blocks)

    # Render SVG
    st.graphviz_chart(graph, use_container_width=True)

    # ---------- DOWNLOAD SVG (NO RESET) ----------
    svg_bytes = graph.pipe(format="svg")

    st.download_button(
        label="⬇️ Download SOAR Playbook (SVG)",
        data=svg_bytes,
        file_name="soar_playbook.svg",
        mime="image/svg+xml"
    )
