import streamlit as st

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
    # Possible values: "intro", "level_select", "learning"
    st.session_state.lp_state = "intro"

if "learning_level" not in st.session_state:
    # Possible values: "Beginner", "Intermediate", "Advanced"
    st.session_state.learning_level = None


# -------------------------------------------------
# Helper: Reset to Level Selection
# -------------------------------------------------
def reset_level():
    st.session_state.lp_state = "level_select"
    st.session_state.learning_level = None


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
# STATE 1 — LEVEL SELECTION (CARDS)
# =================================================
elif st.session_state.lp_state == "level_select":

    st.title("Choose your learning path")
    st.write("Select the option that best matches your current experience.")

    st.markdown("")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 🔰 Beginner")
        st.write(
            "I’m new to SOC, SIEM, or SOAR and want to understand the fundamentals."
        )
        if st.button("Select Beginner", use_container_width=True):
            st.session_state.learning_level = "Beginner"
            st.session_state.lp_state = "learning"

    with c2:
        st.markdown("### ⚙️ Intermediate")
        st.write(
            "I understand SOC alerts and investigations and want to learn automation and playbooks."
        )
        if st.button("Select Intermediate", use_container_width=True):
            st.session_state.learning_level = "Intermediate"
            st.session_state.lp_state = "learning"

    with c3:
        st.markdown("### 🧠 Advanced")
        st.write(
            "I understand SOC workflows and want to learn SOAR design and governance."
        )
        if st.button("Select Advanced", use_container_width=True):
            st.session_state.learning_level = "Advanced"
            st.session_state.lp_state = "learning"


# =================================================
# STATE 2 — LEARNING MODE (PLACEHOLDER)
# =================================================
elif st.session_state.lp_state == "learning":

    # ---------------- Top Bar ----------------
    top_left, top_right = st.columns([4, 1])

    with top_left:
        st.title("SOAR Learning Platform")
        st.caption(f"Level: {st.session_state.learning_level}")

    with top_right:
        st.button("Change level", on_click=reset_level)

    st.markdown("---")

    # ---------------- Main Layout ----------------
    left, right = st.columns([2, 1])

    with left:
        st.subheader("Learning Content")
        st.info(
            "Static learning content will appear here.\n\n"
            "This will be rendered from predefined markdown files "
            "based on the selected learning level."
        )

        st.write("This is intentionally empty in Build Step 1.")

    with right:
        st.subheader("SOAR Workflow Diagram")
        st.info(
            "The SOAR workflow diagram will be shown here.\n\n"
            "The diagram layout will remain constant across all learning levels."
        )

    st.markdown("---")

    st.caption(
        "Next: Add markdown-based learning content, diagram rendering, "
        "and collapsible sections."
    )
