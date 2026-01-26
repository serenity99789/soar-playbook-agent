import streamlit as st
import os
import streamlit.components.v1 as components

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide"
)

# ----------------------------------
# Session State Init
# ----------------------------------
if "lp_state" not in st.session_state:
    st.session_state.lp_state = "intro"  # intro | learning

if "lp_level" not in st.session_state:
    st.session_state.lp_level = None

# ----------------------------------
# Helpers
# ----------------------------------
def go_home():
    st.session_state.lp_state = "intro"
    st.session_state.lp_level = None

# ----------------------------------
# Header
# ----------------------------------
col1, col2 = st.columns([8, 2])
with col1:
    st.title("SOAR Learning Platform")
with col2:
    st.button("🏠 Home", on_click=go_home)

st.divider()

# ----------------------------------
# INTRO STATE
# ----------------------------------
if st.session_state.lp_state == "intro":

    st.subheader("How SOC teams think — not just what they automate")
    st.write(
        "Learn **SOC, SIEM, and SOAR** the way analysts actually use them. "
        "Choose your level and start learning with real workflows."
    )

    st.write("")
    st.write("### Select your current level")

    level = st.radio(
        label="",
        options=["Beginner", "Intermediate", "Advanced"],
        horizontal=True
    )

    if st.button("Start Learning"):
        st.session_state.lp_level = level.lower()
        st.session_state.lp_state = "learning"
        st.rerun()

# ----------------------------------
# LEARNING STATE
# ----------------------------------
elif st.session_state.lp_state == "learning":

    st.caption(f"Level: {st.session_state.lp_level.capitalize()}")
    st.write("")

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Learning Content")
        with st.expander("Open learning sections", expanded=True):
            st.write(
                "📘 **Static learning content will live here.**\n\n"
                "- SOC fundamentals\n"
                "- SIEM concepts & alerting\n"
                "- SOAR playbooks & workflows\n"
                "- Why human review exists\n\n"
                "Content will be loaded from markdown files per level."
            )

    with col_right:
        st.subheader("SOAR Workflow")
        st.image(
            "https://raw.githubusercontent.com/serenity99789/soar-playbook-agent/main/soar_playbook.svg",
            use_container_width=True
        )

# ----------------------------------
# SIEMMY — ALWAYS VISIBLE
# ----------------------------------
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
        box-shadow: 0 6px 18px rgba(0,0,0,0.15);
        border-radius: 12px;
        overflow: hidden;
    }
    .siemmy-header {
        background: #ff4b4b;
        color: white;
        padding: 10px 12px;
        font-weight: 600;
    }
    .siemmy-body {
        background: white;
        border: 1px solid #ddd;
        border-top: none;
        padding: 12px;
        font-size: 14px;
    }
    </style>

    <div class="siemmy-container">
        <div class="siemmy-header">
            👋 Siemmy
        </div>
        <div class="siemmy-body">
            <p style="margin-top:0;">
                <b>Hey 👋 I’m Siemmy.</b><br>
                Want help understanding <b>SOC, SIEM, or SOAR</b>?
            </p>

            <input
                type="text"
                placeholder="Ask me anything…"
                style="width:100%;padding:6px;"
                disabled
            />

            <p style="font-size:12px;color:#888;margin-top:8px;">
                AI mentor logic coming next
            </p>
        </div>
    </div>
    """,
    height=1
)
