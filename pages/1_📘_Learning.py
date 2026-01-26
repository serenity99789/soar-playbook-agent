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
# Helpers
# -------------------------------------------------
def load_learning_markdown(level: str) -> str:
    path = os.path.join("learning", f"{level}.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "_Content coming soon._"


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
            D --> E[Threat Intel Sync]
            E --> F[Notify SOC + IR]

            C -- No --> G[Analyst Decision]
            G --> H[Manual Response or Close]
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
# Session State
# -------------------------------------------------
if "lp_state" not in st.session_state:
    st.session_state.lp_state = "intro"

if "lp_level" not in st.session_state:
    st.session_state.lp_level = "beginner"

# -------------------------------------------------
# Header
# -------------------------------------------------
st.title("SOAR Learning Platform")
st.markdown("---")

# -------------------------------------------------
# Intro / Level Selection
# -------------------------------------------------
if st.session_state.lp_state == "intro":

    st.subheader("How SOC teams think — not just what they automate")

    st.markdown(
        "Learn **SOC, SIEM, and SOAR** the way analysts actually use them. "
        "Choose your level and start learning with real workflows."
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

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(f"## {level.capitalize()} Level — SOC Workflows & Automation")
        st.markdown(load_learning_markdown(level))

    with col2:
        st.markdown("### Workflow Diagram")
        render_workflow_diagram(level)

    st.markdown("---")

    if st.button("Change Level"):
        st.session_state.lp_state = "intro"
        st.rerun()
