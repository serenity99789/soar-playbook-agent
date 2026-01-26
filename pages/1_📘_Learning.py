import streamlit as st
import app

st.set_page_config(
    page_title="SOAR Learning Platform",
    page_icon="📘",
    layout="wide"
)

st.caption("Built for enterprise SOC learning")

st.title("📘 SOAR Learning Platform")
st.info(
    "This section explains how SIEM detections translate into SOAR workflows, "
    "why each step exists, and how SOC analysts reason during incidents."
)

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

if st.button("Generate Learning Playbook"):
    if not alert_text.strip():
        st.warning("Please describe the SIEM alert.")
    else:
        with st.spinner("Generating learning playbook..."):
            result = app.generate_playbook(
                alert_text=alert_text,
                mode="learning",
                depth=depth
            )

        st.success("Playbook generated")

        for i, block in enumerate(result["blocks"], 1):
            with st.expander(f"Step {i}: {block['title']}"):
                st.markdown(f"**Why this step exists:** {block['why']}")
                st.markdown(f"**SOC Role:** {block['soc_role']}")
                st.markdown(f"**If skipped:** {block['if_skipped']}")
                st.markdown("---")
                st.markdown(f"🧠 **Decision Logic:** {block['decision_logic']}")
                st.markdown(f"⚠️ **Automation Risk:** {block['automation_risk']}")
                st.markdown(f"👤 **Human Takeover:** {block['human_takeover']}")
