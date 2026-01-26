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
# Session State Init
# -------------------------------------------------
if "lp_state" not in st.session_state:
    st.session_state.lp_state = "intro"  # intro | learning

if "lp_level" not in st.session_state:
    st.session_state.lp_level = "beginner"

if "siemmy_open" not in st.session_state:
    st.session_state.siemmy_open = False

# -------------------------------------------------
# Helpers
# -------------------------------------------------
def reset_home():
    st.session_state.lp_state = "intro"
    st.session_state.lp_level = "beginner"

def load_learning_content(level):
    path = os.path.join("learning", f"{level}.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "⚠️ Learning content not found."

# -------------------------------------------------
# Header
# -------------------------------------------------
col1, col2 = st.columns([8, 2])
with col1:
    st.title("SOAR Learning Platform")
with col2:
    st.button("🏠 Home", on_click=reset_home)

st.markdown("---")

# -------------------------------------------------
# INTRO SCREEN (STEP 1)
# -------------------------------------------------
if st.session_state.lp_state == "intro":

    st.markdown("## How SOC teams think — not just what they automate")
    st.markdown(
        "Learn **SOC, SIEM, and SOAR** the way analysts actually use them. "
        "Choose your level and start learning with real workflows."
    )

    st.markdown("### Select your current level")

    level = st.radio(
        "",
        ["Beginner", "Intermediate", "Advanced"],
        horizontal=True
    )

    if st.button("Start Learning"):
        st.session_state.lp_level = level.lower()
        st.session_state.lp_state = "learning"
        st.rerun()

# -------------------------------------------------
# LEARNING SCREEN (STEP 2)
# -------------------------------------------------
else:
    st.caption(f"Level: {st.session_state.lp_level.capitalize()}")

    col_left, col_right = st.columns([6, 4])

    with col_left:
        st.subheader("Learning Content")
        with st.expander("Open learning sections", expanded=True):
            st.markdown(load_learning_content(st.session_state.lp_level))

    with col_right:
        st.subheader("SOAR Workflow")
        st.image(
            "https://raw.githubusercontent.com/serenity99789/soar-playbook-agent/main/soar_playbook.svg",
            use_container_width=True
        )

# -------------------------------------------------
# SIEMMY FLOATING CHAT (STEP 3)
# -------------------------------------------------
siemmy_button = """
<style>
#siemmy-btn {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background-color: #ff4b4b;
    color: white;
    border-radius: 999px;
    padding: 14px 18px;
    font-weight: 600;
    cursor: pointer;
    z-index: 9999;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}
</style>

<div id="siemmy-btn" onclick="window.location.href='?siemmy=open'">
👋 Siemmy
</div>
"""

siemmy_chat = """
<style>
#siemmy-chat {
    position: fixed;
    bottom: 90px;
    right: 24px;
    width: 340px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.25);
    z-index: 10000;
    overflow: hidden;
    font-family: sans-serif;
}
#siemmy-header {
    background: #ff4b4b;
    color: white;
    padding: 12px;
    font-weight: 700;
}
#siemmy-body {
    padding: 12px;
    font-size: 14px;
}
#siemmy-input {
    border-top: 1px solid #eee;
    padding: 10px;
}
</style>

<div id="siemmy-chat">
    <div id="siemmy-header">👋 Siemmy</div>
    <div id="siemmy-body">
        <b>Hey! I’m Siemmy.</b><br>
        Want help understanding <b>SOC, SIEM, or SOAR</b>?<br><br>
        Ask me anything — I’m always here.
    </div>
    <div id="siemmy-input">
        <input type="text" placeholder="Type your question…" style="width:100%; padding:8px;">
    </div>
</div>
"""

query_params = st.experimental_get_query_params()

if "siemmy" in query_params:
    st.session_state.siemmy_open = True

if st.session_state.siemmy_open:
    components.html(siemmy_chat, height=420)
else:
    components.html(siemmy_button, height=80)
