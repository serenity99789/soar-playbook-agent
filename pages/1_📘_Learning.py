import streamlit as st

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide"
)

# -------------------------------------------------
# Session state initialization
# -------------------------------------------------
if "view" not in st.session_state:
    st.session_state.view = "home"   # home | level_select | content

if "level" not in st.session_state:
    st.session_state.level = None


# -------------------------------------------------
# Header + Home button
# -------------------------------------------------
header_col, home_col = st.columns([6, 1])

with header_col:
    st.markdown("## SOAR Learning Platform")

with home_col:
    if st.button("🏠 Home"):
        st.session_state.view = "home"
        st.session_state.level = None


st.divider()


# -------------------------------------------------
# VIEW A — HOME (Hero)
# -------------------------------------------------
if st.session_state.view == "home":

    st.markdown(
        """
        ### Learn how SOC teams *actually* work  
        Not just tools — but real analyst thinking, workflows, and decisions.
        """
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Start Learning", type="primary"):
        st.session_state.view = "level_select"


# -------------------------------------------------
# VIEW B — LEVEL SELECTION
# -------------------------------------------------
elif st.session_state.view == "level_select":

    st.markdown("### Select your current level")
    st.caption("Choose the learning path that best fits your experience.")

    level = st.radio(
        "",
        ["Beginner", "Intermediate", "Advanced"],
        index=0
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("➡️ Continue"):
        st.session_state.level = level
        st.session_state.view = "content"


# -------------------------------------------------
# VIEW C — CONTENT
# -------------------------------------------------
elif st.session_state.view == "content":

    left_col, right_col = st.columns([3, 2])

    # -------------------------
    # LEFT — Learning content
    # -------------------------
    with left_col:

        st.markdown(f"### {st.session_state.level} Level — Learning Content")
        st.markdown("#### SOC Foundations")

        st.markdown("""
        **What you’ll learn:**
        - What a SOC actually does
        - SOC analyst day-to-day work
        - What SIEM means in real operations
        - What SOAR automates (and what it doesn’t)
        - How alerts become incidents
        - Why humans still matter in security
        """)

        st.divider()

        st.markdown("### 1. What is a SOC?")
        st.markdown("""
        A **Security Operations Center (SOC)** is a team responsible for
        continuously monitoring, detecting, investigating, and responding
        to security threats across an organization.

        The SOC is not just tools — it is **people + process + technology**.
        """)

        st.markdown("### 2. SOC Analyst Day-to-Day")
        st.markdown("""
        A SOC analyst typically:
        - Reviews alerts from SIEM
        - Validates false positives
        - Enriches alerts with context
        - Escalates incidents when needed
        - Documents actions taken
        """)

        st.markdown("### 3. What is SIEM?")
        st.markdown("""
        **SIEM** aggregates logs, correlates events, and raises alerts.
        It answers the question:

        *“Is something suspicious happening?”*
        """)

        st.markdown("### 4. What is SOAR?")
        st.markdown("""
        **SOAR** automates response actions **after** detection.
        It answers the question:

        *“Now that we know, what do we do?”*
        """)

        st.markdown("### 5. Alert → Incident Lifecycle")
        st.markdown("""
        Not every alert is an incident.
        Analysts decide when automation can act and when human judgment is required.
        """)

        st.markdown("### 6. Why Humans Still Matter")
        st.markdown("""
        Automation supports analysts — it does **not replace them**.
        Context, intent, and risk acceptance are human decisions.
        """)

        st.divider()

        # -------------------------
        # Siemmy (simple & safe)
        # -------------------------
        st.markdown("### 👋 Ask Siemmy")

        question = st.text_input("Ask about SOC, SIEM, or SOAR")

        if question:
            st.info(
                "Great question! In real SOCs, automation assists analysts — "
                "but investigation and judgment remain human-led."
            )

    # -------------------------
    # RIGHT — Workflow diagram
    # -------------------------
    with right_col:

        st.markdown("### Workflow Diagram")

        st.markdown("""
        ```text
        Alert Trigger
             ↓
        Initial Triage
             ↓
        Basic Enrichment
             ↓
        Analyst Review
             ↓
        Close or Escalate
        ```
        """)

        st.caption("Typical SOC alert handling flow")
