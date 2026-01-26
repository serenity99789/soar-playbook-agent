import sys
from pathlib import Path

# ---- HARD GUARANTEED ROOT PATH FIX ----
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from core.playbook_engine import generate_playbook


st.set_page_config(
    page_title="SOAR Playbook Deployment",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 SOAR Playbook Deployment")
st.caption("Generate a production-ready SOAR playbook")

alert_text = st.text_area(
    "SIEM Alert Input",
    placeholder=(
        "Example: Multiple failed login attempts detected from a single external IP "
        "targeting multiple user accounts..."
    )
)

if st.button("Generate Deployment Playbook"):
    if not alert_text.strip():
        st.warning("Please enter an alert description.")
    else:
        with st.spinner("Generating deployment playbook..."):
            result = generate_playbook(
                alert_text=alert_text,
                mode="deployment"
            )

        st.success("Deployment playbook generated")

        for i, block in enumerate(result.get("blocks", []), start=1):
            st.markdown(f"### Step {i}: {block.get('title', 'Step')}")
            st.write(block.get("description", ""))
            st.divider()
