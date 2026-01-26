import streamlit as st
import os
import streamlit.components.v1 as components

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide"
)

# -------------------------------------------------
# Session State
# -------------------------------------------------
if "lp_state" not in st.session_state:
    st.session_state.lp_state = "intro"

if "lp_level" not in st.session_state:
    st.session_state.lp_level = "beginner"

if "lp_progress" not in st.session_state:
    st.session_state.lp_progress = {}

# -------------------------------------------------
# Learning Structure
# -------------------------------------------------
LEARNING_SECTIONS = {
    "beginner": [
        "What is a SOC?",
        "SOC Analyst Day-to-Day",
        "What is SIEM?",
        "What is SOAR?",
        "Alert → Incident lifecycle",
        "Why humans still matter"
    ],
    "intermediate": [
        "SOC investigation flow",
        "SIEM enrichment concepts",
        "SOAR playbook structure",
        "Human vs automated decisions",
        "Case management best practices"
    ],
    "advanced": [
        "Detection engineering basics",
        "Risk-based alerting",
        "Advanced SOAR orchestration",
        "False positive reduction",
        "SOC maturity & scaling"
    ]
}

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def render_workflow_diagram(level: str):
    if level == "beginner":
        diagram = """
        flowchart LR
            A[Alert Trigger] --> B[Initial Triage]
            B --> C[Basic Enrichment]
            C --> D[Analyst Review]
            D --> E[Close or Escalate]
        """
    elif level == "intermediate":
        diagram = """
        flowchart LR
            A[Alert Trigger]
            --> B[Context Enrichment]
            --> C{Confidence High?}

            C -- Yes --> D[Automated Action]
            D --> E[Update Case]

            C -- No --> F[Human Review]
            F --> E
        """
    else:
        diagram = """
        flowchart LR
            A[Alert Trigger]
            --> B[Multi-source Enrichment]
            --> C{Risk Score > Threshold?}

            C -- Yes --> D[Auto Containment]
            D --> E[Notify IR Team]

            C -- No --> F[Analyst Decision]
            F --> G[Manual Response]
        """

    html = f"""
    <div style="width:100%; overflow-x:auto; padding-top:10px;">
        <div class="mermaid">
            {diagram}
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
      mermaid.initialize({{
        startOnLoad: true,
        theme: 'default',
        flowchart: {{
          nodeSpacing: 70,
          rankSpacing: 90,
          curve: 'linear'
        }}
      }});
    </script>
    """

    components.html(html, height=260, scrolling=False)

# -------------------------------------------------
# Header
# -------------------------------------------------
header_col, home_col = st.columns([6, 1])

with header_col:
    st.title("SOAR Learning Platform")

with home_col:
    if st.button("🏠 Home"):
        st.session_state.lp_state = "intro"
        st.session_state.lp_level = "beginner"
        st.rerun()

st.markdown("---")

# -------------------------------------------------
# Intro View
# -------------------------------------------------
if st.session_state.lp_state == "intro":
    st.subheader("How SOC teams think — not just what they automate")

    st.markdown(
        "Learn **SOC, SIEM, and SOAR** the way analysts actually use them. "
        "Choose your level and progress step-by-step."
    )

    level = st.radio(
        "Select your current level",
        ["Beginner", "Intermediate", "Advanced"],
        horizontal=True
    )

    if st.button("Start Learning"):
        st.session_state.lp_level = level.lower()
        st.session_state.lp_state = "learning"
        st.rerun()

# -------------------------------------------------
# Learning View
# -------------------------------------------------
else:
    level = st.session_state.lp_level

    if level not in st.session_state.lp_progress:
        st.session_state.lp_progress[level] = {
            section: False for section in LEARNING_SECTIONS[level]
        }

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(f"## {level.capitalize()} Level — Learning Path")

        st.markdown("### Progress Tracker")

        completed = 0

        for section in LEARNING_SECTIONS[level]:
            checked = st.checkbox(
                section,
                value=st.session_state.lp_progress[level][section]
            )
            st.session_state.lp_progress[level][section] = checked
            if checked:
                completed += 1

        progress = int((completed / len(LEARNING_SECTIONS[level])) * 100)
        st.progress(progress)

        st.caption(f"Progress: {completed}/{len(LEARNING_SECTIONS[level])} sections completed")

    with col2:
        st.markdown("### Workflow Diagram")
        render_workflow_diagram(level)
