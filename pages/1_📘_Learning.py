import streamlit as st
import streamlit.components.v1 as components
import os

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide"
)

# --------------------------------------------------
# Session state
# --------------------------------------------------
if "learning_started" not in st.session_state:
    st.session_state.learning_started = False

if "lp_level" not in st.session_state:
    st.session_state.lp_level = None

# --------------------------------------------------
# Helpers
# --------------------------------------------------
LEARNING_DIR = "learning"

LEVEL_FILE_MAP = {
    "beginner": "beginner.md",
    "intermediate": "intermediate.md",
    "advanced": "advanced.md",
}


def load_markdown(level: str) -> str:
    path = os.path.join(LEARNING_DIR, LEVEL_FILE_MAP[level])
    if not os.path.exists(path):
        return "❌ Learning content not found."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def reset_learning():
    st.session_state.learning_started = False
    st.session_state.lp_level = None


def render_mermaid(mermaid_code: str, height: int = 360):
    html = f"""
    <html>
      <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
          mermaid.initialize({{
            startOnLoad: true,
            theme: 'default'
          }});
        </script>
      </head>
      <body>
        <div class="mermaid">
{mermaid_code}
        </div>
      </body>
    </html>
    """
    components.html(html, height=height, scrolling=False)


def render_diagram(level: str):
    if level == "beginner":
        render_mermaid(
            """
flowchart LR
    A[SIEM Alert] --> B[Analyst Reviews Alert]
    B --> C{Suspicious?}
    C -- No --> D[Close Alert]
    C -- Yes --> E[Investigate]
    E --> F[Incident Response]
            """,
            height=320
        )

    elif level == "intermediate":
        render_mermaid(
            """
flowchart LR
    A[Alert Trigger] --> B[Context Enrichment]
    B --> C{Confidence High?}
    C -- Yes --> D[Automated Action]
    C -- No --> E[Human Review]
    E --> D
    D --> F[Update Case]
            """,
            height=360
        )

    elif level == "advanced":
        render_mermaid(
            """
flowchart LR
    A[Playbook Change] --> B[Peer Review]
    B --> C{Approved?}
    C -- No --> D[Rework]
    C -- Yes --> E[Deploy to Prod]
    E --> F[Monitor & Audit]
            """,
            height=320
        )


# --------------------------------------------------
# Top navigation
# --------------------------------------------------
top_left, top_right = st.columns([6, 1])

with top_right:
    if st.button("🏠 Home"):
        reset_learning()
        st.rerun()

# --------------------------------------------------
# HERO / LEVEL SELECTION
# --------------------------------------------------
if not st.session_state.learning_started:
    st.markdown("# SOAR Learning Platform")
    st.markdown("---")

    st.markdown(
        """
        ## How SOC teams think — not just what they automate

        Learn **SOC, SIEM, and SOAR** the way analysts actually use them.
        Choose your level and start learning with **real workflows**, not theory dumps.
        """
    )

    st.markdown("### Select your current level")

    selected_level = st.radio(
        label="",
        options=["Beginner", "Intermediate", "Advanced"],
        horizontal=True
    )

    if st.button("Start Learning"):
        st.session_state.lp_level = selected_level.lower()
        st.session_state.learning_started = True
        st.rerun()

# --------------------------------------------------
# LEARNING VIEW
# --------------------------------------------------
else:
    level = st.session_state.lp_level

    st.markdown(f"# {level.capitalize()} Level")
    st.caption("Structured learning + visual workflow")
    st.markdown("---")

    left, right = st.columns([3, 2])

    with left:
        st.markdown(load_markdown(level), unsafe_allow_html=True)

    with right:
        st.subheader("Workflow Diagram")
        render_diagram(level)

    st.markdown("---")

    bottom_cols = st.columns([1, 1, 6])
    with bottom_cols[0]:
        if st.button("🔁 Change Level"):
            reset_learning()
            st.rerun()
