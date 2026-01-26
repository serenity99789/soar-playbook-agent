import streamlit as st
from core.playbook_engine import generate_playbook

st.set_page_config(
    page_title="SOAR Learning Platform",
    page_icon="📘",
    layout="wide"
)

st.title("📘 SOAR Learning Platform")
st.caption("How SOC teams think, not just what they automate")

depth = st.radio(
    "Learning depth",
    ["Beginner", "Intermediate", "Advanced"],
    horizontal=True
)

alert_text = st.text_area(
    "Describe the SIEM alert",
    height=180,
    placeholder="Multiple failed login attempts from a single IP..."
)

if st.button("Generate Learning Playbook"):
    if not alert_text.strip():
        st.warning("Please describe the alert.")
    else:
        with st.spinner("Generating learning playbook..."):
            result = generate_playbook(
                alert_text=alert_text,
                mode="learning",
                depth=depth
            )

        for i, block in enumerate(result["blocks"], 1):
            with st.expander(f"Step {i}: {block['title']}"):
                st.markdown(block["description"])
                if block.get("reasoning"):
                    st.caption(f"💡 SOC reasoning: {block['reasoning']}")
