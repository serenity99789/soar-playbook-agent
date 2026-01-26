import sys
from pathlib import Path

# --- Ensure project root is available for imports ---
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import streamlit as st
from core.playbook_engine import generate_playbook


# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="SOAR Playbook Deployment",
    page_icon="🚀",
    layout="centered"
)

# ------------------ UI ------------------
st.title("🚀 SOAR Playbook Deployment")
st.caption("Generate a production-ready SOAR playbook for execution")

st.subheader("🔔 SIEM Alert Input")
alert_text = st.text_area(
    "",
    placeholder=(
        "Example: Multiple failed login attempts detected from a single external IP "
        "targeting multiple user accounts..."
    )
)

# ------------------ ACTION ------------------
if st.button("Generate Deployment Playbook"):
    if not alert_text.strip():
        st.warning("Please describe the SIEM alert.")
    else:
        with st.spinner("Generating deployment playbook..."):
            data = generate_playbook(
                alert_text=alert_text,
                mode="deployment"
            )

        st.success("Deployment playbook generated")

        for i, block in enumerate(data.get("blocks", []), start=1):
            st.markdown(f"### Step {i}: {block.get('title', 'Playbook Step')}")
            st.write(block.get("description", ""))
            st.markdown("---")
