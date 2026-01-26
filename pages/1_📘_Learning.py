import streamlit as st
import streamlit.components.v1 as components

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
    st.session_state.lp_state = "intro"   # intro | learning

if "lp_level" not in st.session_state:
    st.session_state.lp_level = "beginner"

if "siemmy_open" not in st.session_state:
    st.session_state.siemmy_open = False

if "siemmy_messages" not in st.session_state:
    st.session_state.siemmy_messages = []

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def reset_home():
    st.session_state.lp_state = "intro"
    st.session_state.lp_level = "beginner"

def siemmy_reply(user_text: str) -> str:
    text = user_text.lower().strip()

    # Greeting handling
    if text in ["hi", "hello", "hey", "hi siemmy", "hello siemmy"]:
        return (
            "Hey 👋 I’m **Siemmy**.\n\n"
            "I can help you understand:\n"
            "- 🛡️ SOC basics\n"
            "- 📊 SIEM\n"
            "- 🤖 SOAR & playbooks\n\n"
            "What would you like to start with?"
        )

    # Fallback mentor response (safe + neutral)
    return (
        "Good question.\n\n"
        "In SOC environments, automation exists to **support analysts — not replace judgment**.\n"
        "SOAR helps reduce noise, enforce consistency, and speed up response while keeping humans in control.\n\n"
        "Want me to explain this with an example?"
    )

# --------------------------------------------------
# Header
# --------------------------------------------------
col1, col2 = st.columns([8, 2])
with col1:
    st.title("SOAR Learning Platform")
with col2:
    st.button("🏠 Home", on_click=reset_home)

st.markdown("---")

# --------------------------------------------------
# INTRO STATE
# --------------------------------------------------
if st.session_state.lp_state == "intro":
    st.markdown(
        """
        ## How SOC teams think — not just what they automate

        Learn **SOC, SIEM, and SOAR** the way analysts actually use them.
        Choose your level and start learning with **real workflows**, not theory dumps.
        """
    )

    st.markdown("### Select your current level")

    st.session_state.lp_level = st.radio(
        "",
        ["Beginner", "Intermediate", "Advanced"],
        index=["Beginner", "Intermediate", "Advanced"].index(
            st.session_state.lp_level.capitalize()
        )
    ).lower()

    if st.button("Start Learning"):
        st.session_state.lp_state = "learning"

# --------------------------------------------------
# LEARNING STATE
# --------------------------------------------------
if st.session_state.lp_state == "learning":
    st.caption(f"Level: {st.session_state.lp_level.capitalize()}")

    st.markdown(
        """
        ### Learning Content
        Content will expand here level-by-level.
        """
    )

# --------------------------------------------------
# SIEMMY FLOATING BUTTON
# --------------------------------------------------
st.markdown(
    """
    <style>
    .siemmy-btn {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 1000;
    }
    .siemmy-box {
        position: fixed;
        bottom: 90px;
        right: 24px;
        width: 320px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.2);
        padding: 16px;
        z-index: 1000;
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
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# SIEMMY CHAT (ONLY WHEN OPEN)
# --------------------------------------------------
if st.session_state.siemmy_open:
    st.markdown('<div class="siemmy-box">', unsafe_allow_html=True)

    st.markdown("### 👋 Hi, I’m **Siemmy**")
    st.caption("Ask me anything about SOC, SIEM, or SOAR.")

    for msg in st.session_state.siemmy_messages:
        st.markdown(msg)

    user_input = st.text_input(
        "Ask Siemmy…",
        key="siemmy_input"
    )

    if user_input:
        st.session_state.siemmy_messages.append(f"**You:** {user_input}")
        reply = siemmy_reply(user_input)
        st.session_state.siemmy_messages.append(f"**Siemmy:** {reply}")
        st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)
