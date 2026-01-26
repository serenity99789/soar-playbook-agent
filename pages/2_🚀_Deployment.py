import sys
from pathlib import Path
import streamlit as st

# ---------------- PATH FIX ----------------
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from core.playbook_engine import generate_playbook
from core.diagram_engine import generate_soar_svg


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="SOAR Deployment View",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 SOAR Deployment View")
st.caption("Production-ready SOAR execution with governance-aware automation")

# ---------------- SESSION STATE INIT ----------------
if "deployment_generated" not in st.session_state:
    st.session_state.deployment_generated = False

if "deployment_result" not in st.session_state:
    st.session_state.deployment_result = None

if "deployment_svg" not in st.session_state:
    st.session_state.deployment_svg = None


# ---------------- INPUT ----------------
st.subheader("Describe the SIEM alert")
alert_text = st.text_area(
    "Example:",
    placeholder="Suspicious PowerShell execution detected on an endpoint...",
    height=140
)


# ---------------- GENERATE BUTTON ----------------
if st.button("Generate Deployment Playbook"):
    if not alert_text.strip():
        st.warning("Please describe the SIEM alert.")
    else:
        with st.spinner("Generating deployment playbook..."):
            result = generate_playbook(
                alert_text=alert_text,
                mode="deployment"
            )

            svg = generate_soar_svg(result["blocks"])

        st.session_state.deployment_generated = True
        st.session_state.deployment_result = result
        st.session_state.deployment_svg = svg

        st.success("Deployment playbook generated")


# ---------------- RENDER OUTPUT (STATE SAFE) ----------------
if st.session_state.deployment_generated:

    result = st.session_state.deployment_result
    svg = st.session_state.deployment_svg

    # -------- DEPLOYMENT STEPS --------
    st.markdown("## 📋 Deployment Steps")

    for i, block in enumerate(result["blocks"], 1):
        with st.expander(f"Step {i}: {block['title']}", expanded=i == 1):
            st.markdown(f"**Purpose:** {block['description']}")
            if block.get("reasoning"):
                st.caption(f"🧠 SOC Logic: {block['reasoning']}")

    # -------- EXECUTION FLOW --------
    st.markdown("## 🧭 SOAR Execution Flow")

    st.markdown(
        f"""
        <div style="display:flex; justify-content:center;">
            {svg}
        </div>
        """,
        unsafe_allow_html=True
    )

    # -------- DOWNLOAD (NO RESET) --------
    st.download_button(
        label="⬇️ Download SOAR Playbook (SVG)",
        data=svg,
        file_name="soar_deployment_playbook.svg",
        mime="image/svg+xml"
    )
