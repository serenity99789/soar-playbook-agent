import streamlit as st
import os

from core.diagram_engine import build_soar_mermaid
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
    # intro | level_select | learning
    st.session_state.lp_state = "intro"

if "learning_level" not in st.session_state:
    # Beginner | Intermediate | Advanced
    st.session_state.learning_level = None


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def reset_level():
    st.session_state.lp_state = "level_select"
    st.session_state.learning_level = None


def load_learning_markdown(level: str) -> str:
    """
    Load static markdown content for the selected level.
    """
    filename_map = {
        "Beginner": "learning/beginner.md",
        "Intermediate": "learning/intermediate.md",
        "Advanced": "learning/advanced.md",
    }

    path = filename_map.get(level)

    if not path or not os.path.exists(path):
        return (
            "### Learning content not found\n\n"
            "This is expected during early build stages.\n\n"
            "The markdown file for this level will be added next."
        )

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def render_mermaid_diagram():
    """
    Render the SOAR workflow diagram using the existing diagram engine.
    """
    # Minimal static block structure for learning view
    blocks = [
        {"title": "Normalize & Parse", "type": "enrichment"},
        {"title": "Context Enrichment", "type": "enrichment"},
        {"title": "Threat Confirmed?", "type": "decision"},
        {"title": "Automated Containment", "type": "automation"},
        {"title": "Human Review", "type": "human"},
    ]

    mermaid = build_soar_mermaid(blocks)

    mermaid_html = f"""
    <html>
      <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
          mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
        </script>
      </head>
      <body>
        <div class="mermaid">
        {mermaid}
        </div>
      </body>
    </html>
    """

    components.html(mermaid_html, height=650, scrolling=True)


# =================================================
# STATE 0 — INTRO / HERO
# =================================================
if st.session_state.lp_state == "intro":

    st.markdown(
        """
        <div style="text-align:center; padding: 6rem 2rem;">
            <h1>SOAR Learning Platform</h1>
            <h4 style="font-weight:400; color:#666;">
                Learn how SOC teams detect threats and automate response — the right way.
            </h4>
            <p style="max-width:700px; margin: 1.5rem auto; color:#777; font-size:1.05rem;">
                This guided learning platform helps new joiners understand SOC operations,
                SIEM detections, and SOAR playbooks using real-world workflows.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Start Learning", type="primary", use_container_width=True):
            st.session_state.lp_state = "level_select"


# =================================================
# STATE 1 — LEVEL SELECTION
# =================================================
elif st.session_state.lp_state == "level_select":

    st.title("Choose your learning path")
    st.write("Select the option that best matches your current experience.")

    st.markdown("")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 🔰 Beginner")
        st.write("New to SOC, SIEM, or SOAR. Start from the fundamentals.")
        if st.button("Select Beginner", use_container_width=True):
            st.session_state.learning_level = "Beginner"
            st.session_state.lp_state = "learning"

    with c2:
        st.markdown("### ⚙️ Intermediate")
        st.write("Understand SOC alerts. Learn automation and playbooks.")
        if st.button("Select Intermediate", use_container_width=True):
            st.session_state.learning_level = "Intermediate"
            st.session_state.lp_state = "learning"

    with c3:
        st.markdown("### 🧠 Advanced")
        st.write("Focus on SOAR design, governance, and automation trade-offs.")
        if st.button("Select Advanced", use_container_width=True):
            st.session_state.learning_level = "Advanced"
            st.session_state.lp_state = "learning"


# =================================================
# STATE 2 — LEARNING MODE
# =================================================
elif st.session_state.lp_state == "learning":

    # ---------------- Top Bar ----------------
    left_top, right_top = st.columns([4, 1])

    with left_top:
        st.title("SOAR Learning Platform")
        st.caption(f"Level: {st.session_state.learning_level}")

    with right_top:
        st.button("Change level", on_click=reset_level)

    st.markdown("---")

    # ---------------- Main Layout ----------------
    left, right = st.columns([2, 1])

    # -------- Learning Content (Markdown) --------
    with left:
        st.subheader("Learning Content")

        markdown_text = load_learning_markdown(
            st.session_state.learning_level
        )

        # Render markdown inside expandable sections
        with st.expander("Open learning sections", expanded=True):
            st.markdown(markdown_text)

    # -------- Diagram Panel --------
    with right:
        st.subheader("SOAR Workflow")
        render_mermaid_diagram()

    st.markdown("---")
    st.caption(
        "Build Step 2 complete: Static markdown content + SOAR diagram rendered.\n\n"
        "Next: section-level accordions and AI mentor integration."
    )
