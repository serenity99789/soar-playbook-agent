import streamlit as st

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide"
)

# -----------------------------
# Session state defaults
# -----------------------------
if "lp_level" not in st.session_state:
    st.session_state.lp_level = "beginner"

# -----------------------------
# Header
# -----------------------------
col_title, col_home = st.columns([8, 2])
with col_title:
    st.title("SOAR Learning Platform")
with col_home:
    if st.button("🏠 Home"):
        st.session_state.lp_level = "beginner"
        st.rerun()

st.divider()

# -----------------------------
# Level selector (top)
# -----------------------------
st.subheader("Select your current level")

level = st.radio(
    "",
    ["Beginner", "Intermediate", "Advanced"],
    index=["Beginner", "Intermediate", "Advanced"].index(
        st.session_state.lp_level.capitalize()
    )
)

if st.button("Start Learning"):
    st.session_state.lp_level = level.lower()
    st.rerun()

st.divider()

# -----------------------------
# Beginner Learning Path
# -----------------------------
if st.session_state.lp_level == "beginner":

    col_left, col_right = st.columns([3, 2])

    # ---------- LEFT: Learning Path ----------
    with col_left:
        st.header("Beginner Level — Learning Path")
        st.subheader("Progress Tracker")

        checklist = [
            "What is a SOC?",
            "SOC Analyst Day-to-Day",
            "What is SIEM?",
            "What is SOAR?",
            "Alert → Incident lifecycle",
            "Why humans still matter"
        ]

        for item in checklist:
            st.checkbox(item, value=True, disabled=True)

        st.progress(1.0)
        st.caption("Progress: 6 / 6 sections completed")

    # ---------- RIGHT: Diagram ----------
    with col_right:
        st.subheader("Workflow Diagram")
        st.image(
            "https://raw.githubusercontent.com/serenity99789/soar-playbook-agent/main/soar_playbook.svg",
            use_container_width=True
        )

    st.divider()

    # -----------------------------
    # DETAILED CONTENT (RESTORED)
    # -----------------------------
    st.header("Beginner Level — SOC Foundations")

    with st.expander("1️⃣ What is a SOC?", expanded=True):
        st.write("""
A **Security Operations Center (SOC)** is the team responsible for monitoring,
detecting, investigating, and responding to security threats across an organization.

Think of it as:
- The *control room* for cybersecurity
- Where alerts become decisions
- Where tools support humans — not replace them
        """)

    with st.expander("2️⃣ SOC Analyst Day-to-Day"):
        st.write("""
A SOC analyst’s daily work typically includes:
- Reviewing security alerts
- Validating whether alerts are real threats
- Investigating logs, users, endpoints, and network activity
- Escalating confirmed incidents
- Documenting actions taken
        """)

    with st.expander("3️⃣ What is SIEM?"):
        st.write("""
**SIEM (Security Information and Event Management)** platforms:
- Collect logs from many systems
- Correlate events
- Generate alerts based on rules or detections

SIEM answers:  
➡️ *“What is happening across the environment right now?”*
        """)

    with st.expander("4️⃣ What is SOAR?"):
        st.write("""
**SOAR (Security Orchestration, Automation, and Response)** platforms:
- Take alerts from SIEM
- Enrich them with context
- Automate repeatable actions
- Guide analysts through playbooks

SOAR answers:  
➡️ *“What should we do next?”*
        """)

    with st.expander("5️⃣ Alert → Incident Lifecycle"):
        st.write("""
Typical lifecycle:
1. Alert triggered
2. Initial triage
3. Context enrichment
4. Analyst decision
5. Containment / response
6. Closure or escalation
        """)

    with st.expander("6️⃣ Why humans still matter"):
        st.write("""
Automation is powerful — but:
- Context matters
- Business impact matters
- False positives exist
- Attackers adapt

Humans provide judgment, intuition, and accountability.
        """)

# -----------------------------
# Placeholder for other levels
# -----------------------------
elif st.session_state.lp_level == "intermediate":
    st.header("Intermediate Level — Coming Next")
    st.info("This level will focus on workflows, playbooks, and automation boundaries.")

elif st.session_state.lp_level == "advanced":
    st.header("Advanced Level — Coming Next")
    st.info("This level will focus on detection engineering, tuning, and scale.")
