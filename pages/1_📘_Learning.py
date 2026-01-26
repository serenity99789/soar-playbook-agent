import streamlit as st

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    page_icon="📘",
    layout="wide"
)

# -------------------------------------------------
# Session state init
# -------------------------------------------------
if "stage" not in st.session_state:
    st.session_state.stage = "home"

if "selected_level" not in st.session_state:
    st.session_state.selected_level = None

# -------------------------------------------------
# Header + Home button
# -------------------------------------------------
col_title, col_home = st.columns([8, 2])

with col_title:
    st.title("SOAR Learning Platform")

with col_home:
    if st.button("🏠 Home"):
        st.session_state.stage = "home"
        st.session_state.selected_level = None

st.divider()

# -------------------------------------------------
# HERO / HOME STAGE
# -------------------------------------------------
if st.session_state.stage == "home":
    st.markdown(
        """
        <div style="text-align:center; padding:60px 0;">
            <h1 style="font-size:42px;">Learn SOC, SIEM & SOAR the right way</h1>
            <p style="font-size:18px; color:#555;">
                Structured learning paths with real-world security workflows.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    center_col = st.columns([3, 2, 3])[1]
    with center_col:
        start = st.button(
            "🚀 Start Learning",
            use_container_width=True
        )

    # Style the button orange
    st.markdown(
        """
        <style>
        button[kind="primary"], button {
            background-color: #ff4b4b !important;
            color: white !important;
            border-radius: 8px !important;
            height: 3.5em !important;
            font-size: 18px !important;
            font-weight: 600 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if start:
        st.session_state.stage = "level_select"

# -------------------------------------------------
# LEVEL SELECTION STAGE
# -------------------------------------------------
elif st.session_state.stage == "level_select":
    st.subheader("Select your current level")

    st.markdown("Choose the learning path that best fits your experience.")

    level = st.radio(
        "",
        ["Beginner", "Intermediate", "Advanced"],
        index=0
    )

    if st.button("➡️ Continue"):
        st.session_state.selected_level = level
        # Next stage will be content (added later)
        st.success(f"{level} level selected. Content coming next 🚧")

