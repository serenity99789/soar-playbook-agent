import streamlit as st
from pathlib import Path
import importlib.util

# -------------------------------------------------
# LOAD CORE ENGINE BY FILE PATH (GUARANTEED)
# -------------------------------------------------
ENGINE_PATH = Path(__file__).resolve().parents[1] / "core" / "playbook_engine.py"

spec = importlib.util.spec_from_file_location(
    "playbook_engine",
    ENGINE_PATH
)
playbook_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(playbook_engine)

generate_playbook = playbook_engine.generate_playbook

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    page_icon="📘",
    layout="wide"
)

st.caption("Built for enterprise SOC learning")

st.title("📘 SOAR Learning Platform")
st.info(
    "This section teaches how SIEM alerts translate into SOAR workflows, "
    "why each response step exists, and how SOC teams reason during incidents."
)

# -------------------------------------------------
# UI
# -------------------------------------------------
depth = st.radio(
    "Learning Depth",
    ["Beginner", "Intermediate", "Advanced"],
    horizontal=True
)

alert_text = st.text_area(
    "Describe the alert raised by SIEM",
    placeholder="Multiple failed login attempts from a single external IP...",
    height=160
)

# -------------------------------------------------
# GENERATE
# -------------------------------------------------
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
