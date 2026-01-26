import streamlit as st
from core.playbook_engine import generate_playbook

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide"
)

st.caption("Built by Accenture")

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("📘 SOAR Learning Platform")

st.info(
    "This section is designed to teach how SIEM detections translate into SOAR workflows, "
    "why each response step exists, and how SOC teams reason during incidents."
)

# -------------------------------------------------
# LEARNING CONTROLS
# -------------------------------------------------
learning_depth = st.radio(
    "Learning Depth",
    ["Beginner", "Intermediate", "Advanced"],
    horizontal=True
)

alert_text = st.text_area(
    "Describe the alert raised by SIEM",
    height=180,
    placeholder="Example: Multiple failed login attempts from a single external IP targeting multiple users..."
)

# -------------------------------------------------
# GENERATE
# -------------------------------------------------
if st.button("Generate Learning Playbook"):
    if not alert_text.strip():
        st.warning("Please describe the SIEM alert.")
        st.stop()

    with st.spinner("Generating learning playbook..."):
        try:
            data = generate_playbook(
                alert_text=alert_text,
                mode="learning",
                depth=learning_depth
            )
        except Exception as e:
            st.error("Failed to generate learning content. Try again.")
            st.stop()

    st.success("Playbook generated")

    # -------------------------------------------------
    # BLOCK-LEVEL LEARNING
    # -------------------------------------------------
    st.header("📚 Block-Level Learning")

    for idx, block in enumerate(data["blocks"], start=1):
        with st.expander(f"Step {idx}: {block['block_name']}"):
            st.markdown(f"**Why this step exists:** {block.get('learning_explanation', 'N/A')}")
            st.markdown(f"**SOC Role Involved:** {block.get('soc_role', 'N/A')}")
            st.markdown(f"**If skipped:** {block.get('if_skipped', 'N/A')}")

            st.divider()

            st.markdown("**SIEM → SOAR Mapping**")
            st.markdown(f"- **Detection Type:** {block.get('detection_type', 'N/A')}")
            st.markdown(f"- **Log Sources:** {', '.join(block.get('log_sources', []))}")
            st.markdown(f"- **MITRE Technique:** {block.get('mitre', 'N/A')}")
            st.markdown(f"- **Automation Level:** {block.get('automation_level', 'N/A')}")

    # -------------------------------------------------
    # WORKFLOW (OPTIONAL VISUAL HOOK)
    # -------------------------------------------------
    st.header("🧭 How This Becomes Automation")
    st.markdown(
        "Once analysts understand *why* each step exists, the same logic is reused "
        "in **Deployment Mode** to generate production-ready SOAR workflows."
    )
