import streamlit as st
import app

st.set_page_config(
    page_title="SOAR Playbook Deployment",
    page_icon="🚀",
    layout="wide"
)

st.caption("Production-ready SOAR execution")

st.title("🚀 SOAR Playbook Deployment")

alert_text = st.text_area(
    "Describe the SIEM alert",
    placeholder="Multiple failed login attempts detected from external IP...",
    height=160
)

if st.button("Generate Deployment Playbook"):
    if not alert_text.strip():
        st.warning("Please describe the SIEM alert.")
    else:
        with st.spinner("Generating deployment playbook..."):
            result = app.generate_playbook(
                alert_text=alert_text,
                mode="deployment",
                depth="Advanced"
            )

        st.success("Deployment playbook generated")
        st.json(result)
