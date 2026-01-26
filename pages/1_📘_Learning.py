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
    page_title="SOAR Learning Platform",
    page_icon="📘",
    layout="wide"
)

st.markdown("Built for enterprise SOC learning")

st.title("📘 SOAR Learning Platform")
st.info(
    "This section teaches **how SIEM alerts translate into SOAR workflows**, "
    "why each response step exists, and how SOC teams reason during incidents."
)

st.subheader("Learning Depth")
depth = st.radio(
    "Choose your level",
    ["Beginner", "Intermediate", "Advanced"],
    horizontal=True
)

st.subheader("Describe the alert raised by SIEM")
alert_text = st.text_area(
    "Example:",
    placeholder="Multiple failed login attempts from a single external IP...",
    height=160
)

if st.button("Generate Learning Playbook"):
    if not alert_text.strip():
        st.warning("Please describe the SIEM alert.")
    else:
        with st.spinner("Generating learning playbook..."):
            result = generate_playbook(
                alert_text=alert_text,
                mode="learning",
                depth=depth
            )

        st.success("Playbook generated")

        for i, block in enumerate(result["blocks"], 1):
            st.markdown(f"### Step {i}: {block['title']}")
            st.markdown(block["description"])
            if block.get("reasoning"):
                st.caption(f"💡 SOC Reasoning: {block['reasoning']}")
