import sys
from pathlib import Path

# --- Ensure project root is on PYTHONPATH ---
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import streamlit as st
from core.playbook_engine import generate_playbook


# ---------------- UI ----------------
st.set_page_config(
    page_title="SOAR Playbook Deployment",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 SOAR Playbook Deployment")
st.caption("Generate a **production-ready SOAR playbook** suitable for execution")

st.divider()

st.subheader("🔔 SIEM Alert Input")
alert_text = st.text_area(
    "Describe the alert raised by SIEM",
    placeholder="Multiple failed login attempts detected from a single external IP targeting multiple user accounts...",
    height=160
)

if st.button("Generate Deployment Playbook"):
    if not alert_text.strip():
        st.warning("Please describe the SIEM alert.")
    else:
        with st.spinner("Generating deployment playbook..."):
            result = generate_playbook(
                alert_text=alert_text,
                mode="deployment"
            )

        st.success("Deployment playbook generated")

        for i, block in enumerate(result["blocks"], 1):
            st.markdown(f"### Step {i}: {block['title']}")
            st.markdown(block["description"])
