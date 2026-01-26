import streamlit as st
from core.playbook_engine import generate_playbook

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Playbook Deployment",
    layout="wide"
)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("🚀 SOAR Playbook Deployment")
st.caption("Generate a production-ready SOAR playbook for execution")

st.divider()

# -------------------------------------------------
# INPUT
# -------------------------------------------------
st.subheader("🔔 SIEM Alert Input")

alert_text = st.text_area(
    "Describe the alert raised by SIEM",
    height=180,
    placeholder="Example: Multiple failed login attempts detected from a single external IP targeting multiple user accounts..."
)

# -------------------------------------------------
# GENERATE
# -------------------------------------------------
if st.button("Generate Deployment Playbook"):
    if not alert_text.strip():
        st.warning("Please describe the SIEM alert.")
        st.stop()

    with st.spinner("Generating deployment-ready playbook..."):
        try:
            data = generate_playbook(
                alert_text=alert_text,
                mode="deployment",
                depth="Intermediate"
            )
        except Exception:
            st.error("Failed to generate deployment playbook.")
            st.stop()

    st.success("Deployment playbook generated")

    # -------------------------------------------------
    # DEPLOYMENT BLOCKS
    # -------------------------------------------------
    st.header("🧩 Executable SOAR Workflow")

    for idx, block in enumerate(data["blocks"], start=1):
        with st.expander(f"Step {idx}: {block['block_name']}"):

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Trigger / Input**")
                st.markdown(block.get("trigger", "SIEM Alert Event"))

                st.markdown("**Automated Actions**")
                for action in block.get("automated_actions", []):
                    st.markdown(f"- {action}")

            with col2:
                st.markdown("**Decision Logic**")
                st.markdown(block.get("decision_logic", "N/A"))

                st.markdown("**Outputs**")
                for output in block.get("outputs", []):
                    st.markdown(f"- {output}")

            st.divider()

            st.markdown("**Failure Handling / Escalation**")
            st.markdown(block.get("failure_handling", "Escalate to SOC L2 / IR Team"))

    # -------------------------------------------------
    # FINAL NOTE
    # -------------------------------------------------
    st.info(
        "This deployment view is intentionally execution-focused. "
        "All reasoning and learning context is handled in the Learning section."
    )
