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
    page_title="SOAR Learning Platform",
    page_icon="📘",
    layout="centered"
)

# ------------------ UI ------------------
st.markdown("Built by Accenture", unsafe_allow_html=True)
st.title("📘 SOAR Learning Platform")

st.info(
    "This section is designed to teach how SIEM detections translate into SOAR workflows, "
    "why each response step exists, and how SOC teams reason during incidents."
)

st.subheader("Learning Depth")
depth = st.radio(
    "",
    ["Beginner", "Intermediate", "Advanced"],
    horizontal=True
)

st.subheader("Describe the alert raised by SIEM")
alert_text = st.text_area(
    "",
    placeholder="Example: Multiple failed login attempts from a single external IP..."
)

# ------------------ ACTION ------------------
if st.button("Generate Learning Playbook"):
    if not alert_text.strip():
        st.warning("Please describe the SIEM alert.")
    else:
        with st.spinner("Generating learning playbook..."):
            data = generate_playbook(
                alert_text=alert_text,
                mode="learning",
                depth=depth
            )

        st.success("Learning playbook generated")

        for i, block in enumerate(data.get("blocks", []), start=1):
            with st.expander(f"Step {i}: {block.get('title', 'Playbook Step')}"):
                st.write(block.get("description", ""))
