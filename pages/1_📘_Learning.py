import streamlit as st
from pathlib import Path

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide"
)

# --------------------------------------------------
# Session State Init
# --------------------------------------------------
if "lp_state" not in st.session_state:
    st.session_state.lp_state = "intro"  # intro | learning

if "lp_level" not in st.session_state:
    st.session_state.lp_level = None

if "siemmy_open" not in st.session_state:
    st.session_state.siemmy_open = False

# --------------------------------------------------
# Helpers
# --------------------------------------------------
LEARNING_DIR = Path("learning")

def load_markdown(level: str):
    path = LEARNING_DIR / f"{level}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "Content coming soon."

# --------------------------------------------------
# Header
# --------------------------------------------------
col1, col2 = st.columns([8, 2])
with col1:
    st.title("SOAR Learning Platform")
with col2:
    if st.button("🏠 Home"):
        st.session_state.lp_state = "intro"
        st.session_state.lp_level = None
        st.session_state.siemmy_open = False
        st.rerun()

st.divider()

# --------------------------------------------------
# INTRO PAGE
# --------------------------------------------------
if st.session_state.lp_state == "intro":

    st.subheader("How SOC teams think — not just what they automate")
    st.write(
        "Learn **SOC, SIEM, and SOAR** the way analysts actually use them. "
        "Choose your level and start learning with real workflows."
    )

    st.markdown("### Select your current level")

    level = st.radio(
        label="",
        options=["Beginner", "Intermediate", "Advanced"],
        horizontal=True
    )

    if st.button("Start Learning"):
        st.session_state.lp_level = level.lower()
        st.session_state.lp_state = "learning"
        st.rerun()

# --------------------------------------------------
# LEARNING PAGE
# --------------------------------------------------
if st.session_state.lp_state == "learning":

    st.caption(f"Level: {st.session_state.lp_level.capitalize()}")
    st.markdown("## Learning Content")

    content = load_markdown(st.session_state.lp_level)
    st.markdown(content)

# --------------------------------------------------
# FLOATING SIEMMY (Launcher Only)
# --------------------------------------------------
st.markdown(
    """
    <style>
    .siemmy-btn {
        position: fixed;
        bottom: 25px;
        right: 25px;
        z-index: 9999;
    }
    .siemmy-box {
        position: fixed;
        bottom: 90px;
        right: 25px;
        width: 340px;
        background: white;
        border-radius: 14px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        z-index: 9999;
        padding: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Floating button
with st.container():
    st.markdown('<div class="siemmy-btn">', unsafe_allow_html=True)
    if st.button("👋 Siemmy"):
        st.session_state.siemmy_open = not st.session_state.siemmy_open
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# SIEMMY CHAT PANEL
# --------------------------------------------------
if st.session_state.siemmy_open:
    st.markdown('<div class="siemmy-box">', unsafe_allow_html=True)
    st.markdown("### 👋 Hi, I’m **Siemmy**")
    st.write("Want help understanding **SOC, SIEM, or SOAR**?")
    st.caption("Ask anything — I’m here to guide you.")

    user_q = st.text_input("Ask Siemmy…", key="siemmy_input")

    if user_q:
        st.markdown("**Siemmy:**")
        st.write(
            "Great question. In SOC environments, this exists because "
            "automation supports analysts — it doesn’t replace judgment."
        )

    st.markdown('</div>', unsafe_allow_html=True)
