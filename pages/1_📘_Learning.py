import streamlit as st

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide",
)

# -------------------------------------------------
# Session state init
# -------------------------------------------------
if "selected_level" not in st.session_state:
    st.session_state.selected_level = None

# -------------------------------------------------
# Learning content (LEVEL-SPECIFIC)
# -------------------------------------------------
LEARNING_CONTENT = {
    "Beginner": {
        "title": "Beginner Level — SOC Foundations",
        "sections": [
            ("What is a SOC?", "A Security Operations Center (SOC) monitors, detects, and responds to security threats across an organization."),
            ("SOC Analyst Day-to-Day", "SOC analysts review alerts, investigate incidents, escalate threats, and document findings."),
            ("What is SIEM?", "SIEM aggregates logs and generates alerts based on correlation and detection rules."),
            ("What is SOAR?", "SOAR automates repetitive SOC tasks and orchestrates response workflows."),
            ("Alert → Incident lifecycle", "Alerts are triaged, investigated, classified, and either closed or escalated."),
            ("Why humans still matter", "Automation assists analysts, but judgment and context come from humans."),
        ],
    },
    "Intermediate": {
        "title": "Intermediate Level — SOC Workflows & Automation",
        "sections": [
            ("SOC Investigation Flow", "Learn how alerts move through enrichment, validation, and response."),
            ("Enrichment & Context", "Threat intel, asset context, and user behavior improve decisions."),
            ("SOAR Playbooks", "Playbooks define structured, repeatable response actions."),
            ("Human vs Automated Decisions", "Not all actions should be automated."),
            ("False Positives", "Reducing noise is critical to SOC efficiency."),
            ("Metrics that matter", "MTTD, MTTR, alert volume, and escalation rates."),
        ],
    },
    "Advanced": {
        "title": "Advanced Level — Detection Engineering & SOAR Design",
        "sections": [
            ("Detection Engineering", "Design high-fidelity detections aligned to threat models."),
            ("Threat Modeling", "Map detections to attacker behavior and kill chains."),
            ("SOAR Architecture", "Design scalable and resilient automation systems."),
            ("Playbook Governance", "Versioning, approvals, and auditability."),
            ("Failure Handling", "Design for automation failures and edge cases."),
            ("Measuring Automation ROI", "Quantify time saved and risk reduced."),
        ],
    },
}

# -------------------------------------------------
# Header
# -------------------------------------------------
col_title, col_home = st.columns([6, 1])
with col_title:
    st.title("SOAR Learning Platform")
with col_home:
    st.page_link("Home.py", label="🏠 Home")

st.divider()

# -------------------------------------------------
# Level selection (ONLY shown if not started)
# -------------------------------------------------
if st.session_state.selected_level is None:
    st.subheader("Select your current level")

    level = st.radio(
        "",
        ["Beginner", "Intermediate", "Advanced"],
        horizontal=False,
    )

    if st.button("Start Learning"):
        st.session_state.selected_level = level
        st.rerun()

    st.stop()

# -------------------------------------------------
# Render selected level
# -------------------------------------------------
level = st.session_state.selected_level
content = LEARNING_CONTENT[level]

left, right = st.columns([2, 1])

# -------------------------------------------------
# LEFT COLUMN — Learning Path & Content
# -------------------------------------------------
with left:
    st.subheader(f"{level} Level — Learning Path")
    st.markdown("### Progress Tracker")

    total = len(content["sections"])
    completed = total  # static for now

    for title, _ in content["sections"]:
        st.checkbox(title, value=True, disabled=True)

    st.progress(completed / total)
    st.caption(f"Progress: {completed} / {total} sections completed")

    st.divider()

    st.subheader(content["title"])

    for idx, (title, body) in enumerate(content["sections"], start=1):
        with st.expander(f"{idx}. {title}", expanded=False):
            st.write(body)

# -------------------------------------------------
# RIGHT COLUMN — Workflow Diagram
# -------------------------------------------------
with right:
    st.subheader("Workflow Diagram")
    st.info("Workflow diagram will appear here.")

