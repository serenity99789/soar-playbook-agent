import streamlit as st
import streamlit.components.v1 as components
import os
from google import genai

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide"
)

# ----------------------------------
# Session State
# ----------------------------------
if "lp_state" not in st.session_state:
    st.session_state.lp_state = "intro"

if "lp_level" not in st.session_state:
    st.session_state.lp_level = "beginner"

if "siemmy_messages" not in st.session_state:
    st.session_state.siemmy_messages = []

# ----------------------------------
# Gemini Client
# ----------------------------------
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

# ----------------------------------
# Siemmy Prompt
# ----------------------------------
def siemmy_prompt(user_q: str) -> str:
    return f"""
You are Siemmy — a SOC learning mentor.

User level: {st.session_state.lp_level}

Rules:
- Explain concepts clearly
- No vendor marketing
- Use real SOC examples
- Be concise but educational
- Focus on SIEM, SOAR, SOC operations

Question:
{user_q}
""".strip()

# ----------------------------------
# Header
# ----------------------------------
col1, col2 = st.columns([8, 2])
with col1:
    st.title("SOAR Learning Platform")
with col2:
    if st.button("🏠 Home"):
        st.session_state.lp_state = "intro"

st.divider()

# ----------------------------------
# INTRO
# ----------------------------------
if st.session_state.lp_state == "intro":

    st.subheader("How SOC teams think — not just what they automate")
    st.write(
        "Learn **SOC, SIEM, and SOAR** the way analysts actually use them. "
        "Choose your level and start learning with real workflows."
    )

    st.write("### Select your current level")

    level = st.radio(
        "",
        ["Beginner", "Intermediate", "Advanced"],
        horizontal=True
    )

    if st.button("Start Learning"):
        st.session_state.lp_level = level.lower()
        st.session_state.lp_state = "learning"
        st.rerun()

# ----------------------------------
# LEARNING
# ----------------------------------
else:
    st.caption(f"Level: {st.session_state.lp_level.capitalize()}")

    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.subheader("Learning Content")
        st.info("Static learning modules will load here per level.")

    with col_r:
        st.subheader("SOAR Workflow")
        st.image(
            "https://raw.githubusercontent.com/serenity99789/soar-playbook-agent/main/soar_playbook.svg",
            use_container_width=True
        )

# ----------------------------------
# SIEMMY (ALWAYS VISIBLE)
# ----------------------------------
components.html(
    """
    <style>
    .siemmy-box {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 360px;
        height: 420px;
        background: white;
        border-radius: 14px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        z-index: 99999;
        display: flex;
        flex-direction: column;
        font-family: sans-serif;
    }
    .siemmy-header {
        background: #ff4b4b;
        color: white;
        padding: 12px;
        font-weight: 600;
        border-radius: 14px 14px 0 0;
    }
    .siemmy-body {
        flex: 1;
        padding: 10px;
        overflow-y: auto;
        font-size: 14px;
    }
    .siemmy-footer {
        padding: 10px;
        border-top: 1px solid #eee;
    }
    </style>

    <div class="siemmy-box">
        <div class="siemmy-header">
            👋 Siemmy
        </div>
        <div class="siemmy-body">
            <p><b>Hey 👋 I’m Siemmy.</b><br>
            Want help understanding <b>SOC, SIEM, or SOAR</b>?</p>
            <p style="color:#888;font-size:12px;">
            Ask questions anytime — I’m always here.
            </p>
        </div>
        <div class="siemmy-footer">
            <em style="font-size:12px;color:#888;">
            Type below ⬇️
            </em>
        </div>
    </div>
    """,
    height=450
)

# ----------------------------------
# REAL CHAT INPUT (Streamlit-side)
# ----------------------------------
st.write("")  # spacing
user_q = st.chat_input("Ask Siemmy…")

if user_q:
    st.session_state.siemmy_messages.append(("user", user_q))

    client = get_gemini_client()
    if client:
        try:
            resp = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=siemmy_prompt(user_q)
            )
            answer = resp.text or "I’m thinking… try again."
        except Exception as e:
            answer = f"Error: {e}"
    else:
        answer = "Gemini API key not configured."

    st.session_state.siemmy_messages.append(("siemmy", answer))

# ----------------------------------
# Chat History
# ----------------------------------
for role, msg in st.session_state.siemmy_messages:
    with st.chat_message(role):
        st.write(msg)
