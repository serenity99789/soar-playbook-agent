import streamlit as st
import os
import streamlit.components.v1 as components

# ---------------------------------
# Page Config
# ---------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide"
)

# ---------------------------------
# Session State
# ---------------------------------
if "lp_state" not in st.session_state:
    st.session_state.lp_state = "intro"  # intro | learning

if "lp_level" not in st.session_state:
    st.session_state.lp_level = None

if "siemmy_open" not in st.session_state:
    st.session_state.siemmy_open = True

# ---------------------------------
# Helpers
# ---------------------------------
def load_learning_markdown(level: str) -> str:
    path = f"learning/{level}.md"
    if not os.path.exists(path):
        return "⚠️ Learning content not found."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def reset_learning():
    st.session_state.lp_state = "intro"
    st.session_state.lp_level = None

# ---------------------------------
# Header
# ---------------------------------
col1, col2 = st.columns([8, 2])
with col1:
    st.title("SOAR Learning Platform")
with col2:
    st.button("🏠 Home", on_click=reset_learning)

st.divider()

# ---------------------------------
# Intro / Level Selection
# ---------------------------------
if st.session_state.lp_state == "intro":

    st.subheader("How SOC teams think — not just what they automate")

    st.markdown(
        """
        Learn **SOC**, **SIEM**, and **SOAR** the way analysts actually use them.
        Choose your level and start learning with real workflows.
        """
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

# ---------------------------------
# Learning Content (SAFE)
# ---------------------------------
if st.session_state.lp_state == "learning" and st.session_state.lp_level:

    st.caption(f"Level: {st.session_state.lp_level.capitalize()}")

    left, right = st.columns([6, 4])

    with left:
        st.subheader("Learning Content")
        content = load_learning_markdown(st.session_state.lp_level)
        with st.expander("Open learning sections", expanded=True):
            st.markdown(content)

    with right:
        st.subheader("SOAR Workflow")
        if os.path.exists("soar_playbook.svg"):
            st.image("soar_playbook.svg", use_column_width=True)
        else:
            st.info("SOAR workflow diagram will appear here.")

# ---------------------------------
# 🔹 SIEMMY — FLOATING AI MENTOR
# ---------------------------------
components.html(
    """
    <style>
    .siemmy-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 320px;
        z-index: 9999;
        font-family: sans-serif;
    }
    .siemmy-header {
        background: #ff4b4b;
        color: white;
        padding: 10px;
        border-radius: 10px 10px 0 0;
        font-weight: bold;
    }
    .siemmy-body {
        background: white;
        border: 1px solid #ddd;
        border-top: none;
        padding: 10px;
    }
    </style>

    <div class="siemmy-container">
        <div class="siemmy-header">
            👋 Siemmy
        </div>
        <div class="siemmy-body">
            <p><b>Hey 👋 I’m Siemmy.</b><br>
            Want help understanding <b>SOC, SIEM, or SOAR</b>?</p>

            <input type="text"
                placeholder="Ask me anything…"
                style="width:100%;padding:6px;"
                disabled />

            <p style="font-size:12px;color:#888;margin-top:6px;">
            AI mentor logic coming next
            </p>
        </div>
    </div>
    """,
    height=0
)
