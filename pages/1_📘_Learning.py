import streamlit as st
from pathlib import Path

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    page_icon="📘",
    layout="wide"
)

# --------------------------------------------------
# Session State Defaults
# --------------------------------------------------
if "mode" not in st.session_state:
    st.session_state.mode = "home"   # home | learning

if "level" not in st.session_state:
    st.session_state.level = "Beginner"

if "progress" not in st.session_state:
    st.session_state.progress = {
        "What is a SOC?": True,
        "SOC Analyst Day-to-Day": True,
        "What is SIEM?": True,
        "What is SOAR?": True,
        "Alert → Incident lifecycle": True,
        "Why humans still matter": True,
    }

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def go_home():
    st.session_state.mode = "home"

def start_learning():
    st.session_state.mode = "learning"

def render_diagram():
    diagram_path = Path("assets/workflow.svg")
    if diagram_path.exists():
        st.image(str(diagram_path), use_container_width=True)
    else:
        st.info("Workflow diagram will appear here.")

# --------------------------------------------------
# Header (Always visible)
# --------------------------------------------------
col1, col2 = st.columns([8, 2])
with col1:
    st.title("SOAR Learning Platform")
with col2:
    if st.session_state.mode == "learning":
        st.button("🏠 Home", on_click=go_home)

st.divider()

# ==================================================
# 🏠 HOME MODE
# ==================================================
if st.session_state.mode == "home":

    st.subheader("Select your current level")

    st.session_state.level = st.radio(
        "",
        ["Beginner", "Intermediate", "Advanced"],
        index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.level)
    )

    st.button("Start Learning", on_click=start_learning)

# ==================================================
# 📘 LEARNING MODE
# ==================================================
if st.session_state.mode == "learning":

    left, right = st.columns([3, 2])

    # -------------------------------
    # LEFT: Learning Content
    # -------------------------------
    with left:
        st.header(f"{st.session_state.level} Level — Learning Path")

        st.subheader("Progress Tracker")

        completed = 0
        total = len(st.session_state.progress)

        for item, done in st.session_state.progress.items():
            st.checkbox(item, value=done, disabled=True)
            if done:
                completed += 1

        st.progress(completed / total)
        st.caption(f"Progress: {completed} / {total} sections completed")

        st.divider()

        st.header("Beginner Level — SOC Foundations")

        with st.expander("1️⃣ What is a SOC?"):
            st.write(
                "A Security Operations Center (SOC) is a centralized team responsible "
                "for monitoring, detecting, investigating, and responding to security threats."
            )

        with st.expander("2️⃣ SOC Analyst Day-to-Day"):
            st.write(
                "SOC analysts review alerts, validate incidents, investigate context, "
                "and coordinate responses."
            )

        with st.expander("3️⃣ What is SIEM?"):
            st.write(
                "SIEM aggregates logs and events, correlates activity, and generates alerts."
            )

        with st.expander("4️⃣ What is SOAR?"):
            st.write(
                "SOAR automates repetitive tasks and orchestrates response workflows."
            )

        with st.expander("5️⃣ Alert → Incident Lifecycle"):
            st.write(
                "Alerts are triaged, enriched, investigated, escalated, or closed."
            )

        with st.expander("6️⃣ Why humans still matter"):
            st.write(
                "Automation assists analysts — it does not replace judgment."
            )

    # -------------------------------
    # RIGHT: Diagram
    # -------------------------------
    with right:
        st.subheader("Workflow Diagram")
        render_diagram()
