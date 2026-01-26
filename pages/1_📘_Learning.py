import streamlit as st
import os

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide"
)

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
    filename = LEVEL_FILE_MAP.get(level)
    if not filename:
        return "❌ Invalid learning level selected."

    path = os.path.join(LEARNING_DIR, filename)
    if not os.path.exists(path):
        return f"❌ Learning content not found for **{level}**."

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def reset_learning():
    st.session_state.learning_started = False
    st.session_state.lp_level = None


# --------------------------------------------------
# Session state init
# --------------------------------------------------
if "learning_started" not in st.session_state:
    st.session_state.learning_started = False

if "lp_level" not in st.session_state:
    st.session_state.lp_level = None

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
    st.caption("You can change levels anytime using the Home button.")
    st.markdown("---")

    content = load_markdown(level)
    st.markdown(content, unsafe_allow_html=True)

    st.markdown("---")

    bottom_cols = st.columns([1, 1, 6])
    with bottom_cols[0]:
        if st.button("🔁 Change Level"):
            reset_learning()
            st.rerun()
