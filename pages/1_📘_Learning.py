import streamlit as st

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide"
)

# --------------------------------------------------
# Session State Init (SAFE)
# --------------------------------------------------
if "lp_state" not in st.session_state:
    st.session_state.lp_state = "intro"

if "lp_level" not in st.session_state or st.session_state.lp_level is None:
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
    st.session_state.siemmy_open = False
    st.session_state.siemmy_messages = []

def safe_level_label():
    level = st.session_state.lp_level
    if not isinstance(level, str):
        return "Beginner"
    return level.capitalize()

def siemmy_reply(user_text: str) -> str:
    text = user_text.lower().strip()

    if text in ["hi", "hello", "hey", "hi siemmy", "hello siemmy"]:
        return (
            "Hey 👋 I’m **Siemmy**.\n\n"
            "I can help you learn:\n"
            "- 🛡️ SOC fundamentals\n"
            "- 📊 SIEM concepts\n"
            "- 🤖 SOAR playbooks\n\n"
            "What would you like to start with?"
        )

    return (
        "That’s a good question.\n\n"
        "In real SOCs, automation exists to **assist analysts**, not replace them.\n"
        "SOAR reduces noise, enforces consistency, and speeds response — while humans stay in control.\n\n"
        "Want a simple real-world example?"
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

    level_choice = st.radio(
        "",
        ["Beginner", "Intermediate", "Advanced"],
        index=0
    )

    st.session_state.lp_level = level_choice.lower()

    if st.button("Start Learning"):
        st.session_state.lp_state = "learning"

# --------------------------------------------------
# LEARNING STATE
# --------------------------------------------------
if st.session_state.lp_state == "learning":
    st.caption(f"Level: {safe_level_label()}")

    st.markdown(
        """
        ### Learning Content
        This section will expand with structured lessons,
        diagrams, and explanations based on your level.
        """
    )

# --------------------------------------------------
# Floating Siemmy Styles
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

# --------------------------------------------------
# Floating Button
# --------------------------------------------------
st.markdown('<div class="siemmy-btn">', unsafe_allow_html=True)
if st.button("👋 Siemmy"):
    st.session_state.siemmy_open = not st.session_state.siemmy_open
st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# Siemmy Chat (ONLY ONE INSTANCE)
# --------------------------------------------------
if st.session_state.siemmy_open:
    st.markdown('<div class="siemmy-box">', unsafe_allow_html=True)

    st.markdown("### 👋 Hi, I’m **Siemmy**")
    st.caption("Your SOC learning mentor")

    for msg in st.session_state.siemmy_messages:
        st.markdown(msg)

    user_input = st.text_input("Ask Siemmy…")

    if user_input:
        st.session_state.siemmy_messages.append(f"**You:** {user_input}")
        st.session_state.siemmy_messages.append(
            f"**Siemmy:** {siemmy_reply(user_input)}"
        )
        st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)
