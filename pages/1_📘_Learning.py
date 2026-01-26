import streamlit as st

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide"
)

# ---------------------------
# Session State Init
# ---------------------------
if "lp_level" not in st.session_state:
    st.session_state.lp_level = None

if "siemmy_open" not in st.session_state:
    st.session_state.siemmy_open = False

if "siemmy_messages" not in st.session_state:
    st.session_state.siemmy_messages = []

# ---------------------------
# Home Button
# ---------------------------
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🏠 Home"):
        st.session_state.lp_level = None
        st.session_state.siemmy_messages = []
        st.session_state.siemmy_open = False
        st.experimental_rerun()

# ---------------------------
# Hero Section
# ---------------------------
st.title("SOAR Learning Platform")
st.markdown("---")

st.markdown(
    """
    ## How SOC teams think — not just what they automate  
    Learn **SOC, SIEM, and SOAR** the way analysts actually use them.  
    Choose your level and start learning with real workflows.
    """
)

# ---------------------------
# Level Selection
# ---------------------------
st.markdown("### Select your current level")

level = st.radio(
    "",
    ["Beginner", "Intermediate", "Advanced"],
    index=0,
    horizontal=True
)

if st.button("Start Learning"):
    st.session_state.lp_level = level.lower()
    st.success(f"Level set to **{level}**")

# ---------------------------
# Floating Siemmy Button
# ---------------------------
st.markdown(
    """
    <style>
    .siemmy-button {
        position: fixed;
        bottom: 24px;
        right: 24px;
        background-color: #ff4b4b;
        color: white;
        padding: 12px 18px;
        border-radius: 999px;
        font-weight: 600;
        cursor: pointer;
        z-index: 1000;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }
    .siemmy-box {
        position: fixed;
        bottom: 90px;
        right: 24px;
        width: 320px;
        background: white;
        border-radius: 14px;
        padding: 16px;
        z-index: 1000;
        box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Toggle button
if st.button("👋 Siemmy", key="siemmy_toggle"):
    st.session_state.siemmy_open = not st.session_state.siemmy_open

# ---------------------------
# Floating Siemmy Chat
# ---------------------------
if st.session_state.siemmy_open:
    with st.container():
        st.markdown(
            """
            <div class="siemmy-box">
                <strong>👋 Hi, I’m Siemmy</strong><br>
                <small>Your SOC learning mentor</small>
            </div>
            """,
            unsafe_allow_html=True
        )

        user_input = st.text_input(
            "Ask Siemmy…",
            key="siemmy_input"
        )

        if user_input:
            # Greeting logic
            msg = user_input.strip().lower()

            if msg in ["hi", "hello", "hey"]:
                response = (
                    "Hey! 👋 I’m Siemmy.\n\n"
                    "I can help you understand **SOC**, **SIEM**, and **SOAR**.\n"
                    "Ask me anything, or start learning by choosing a level above."
                )
            else:
                response = (
                    "Good question. In SOC environments, automation exists to **support analysts**, "
                    "not replace judgment. Want me to explain this with a real example?"
                )

            st.session_state.siemmy_messages.append(
                ("You", user_input)
            )
            st.session_state.siemmy_messages.append(
                ("Siemmy", response)
            )

        for speaker, text in st.session_state.siemmy_messages[-6:]:
            st.markdown(f"**{speaker}:** {text}")
