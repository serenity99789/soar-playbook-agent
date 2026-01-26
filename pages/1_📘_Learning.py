import sys
from pathlib import Path

# ---- HARD GUARANTEED ROOT PATH FIX ----
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from core.playbook_engine import generate_playbook


st.set_page_config(
    page_title="SOAR Learning Platform",
    page_icon="📘",
    layout="centered"
)

st.markdown("Built by Accenture")
st.title("📘 SOAR Learning Platform")

st.info(
    "This section explains how SIEM alerts translate into SOAR workflows, "
    "why each step exists, and how SOC teams reason during incidents."
)

depth = st.radio(
    "Learning Depth",
    ["Beginner", "Intermediate", "Advanced"],
    horizontal=True
)

alert_text = st.text_area(
    "Describe the alert raised by SIEM",
    placeholder="Example: Multiple failed login attempts from a single external IP..."
)

if st.button("Generate Learning Playbook"):
    if not alert_text.strip():
        st.warning("Please enter an alert description.")
    else:
        with st.spinner("Generating learning playbook..."):
            result = generate_playbook(
                alert_text=alert_text,
                mode="learning",
                depth=depth
            )

        st.success("Playbook generated")

        for i, block in enumerate(result.get("blocks", []), start=1):
            with st.expander(f"Step {i}: {block.get('title', 'Step')}"):
                st.write(block.get("description", ""))
