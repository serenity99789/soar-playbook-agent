import streamlit as st
from core.playbook_engine import generate_playbook

st.set_page_config(
    page_title="SOAR Deployment",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 SOAR Deployment View")
st.caption("Production-ready response flow")

alert_text = st.text_area(
    "Describe the SIEM alert",
    height=180,
    placeholder="Suspicious PowerShell execution detected..."
)

if st.button("Generate Deployment Playbook"):
    if not alert_text.strip():
        st.warning("Please describe the alert.")
    else:
        with st.spinner("Generating deployment playbook..."):
            result = generate_playbook(
                alert_text=alert_text,
                mode="deployment",
                depth="Advanced"
            )

        for i, block in enumerate(result["blocks"], 1):
            st.markdown(f"### {i}. {block['title']}")
            st.markdown(block["description"])
