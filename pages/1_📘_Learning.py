import streamlit as st

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="SOAR Learning Platform", layout="wide")

# -----------------------------
# Session state init
# -----------------------------
if "lp_level" not in st.session_state:
    st.session_state.lp_level = None

if "lp_started" not in st.session_state:
    st.session_state.lp_started = False


# -----------------------------
# Helper: reset to home
# -----------------------------
def go_home():
    st.session_state.lp_level = None
    st.session_state.lp_started = False


# -----------------------------
# Header
# -----------------------------
col1, col2 = st.columns([6, 1])
with col1:
    st.title("SOAR Learning Platform")
with col2:
    st.button("🏠 Home", on_click=go_home)

st.divider()


# -----------------------------
# HOME / LEVEL SELECTION
# -----------------------------
if not st.session_state.lp_started:

    st.subheader("Select your current level")

    level = st.radio(
        label="",
        options=["Beginner", "Intermediate", "Advanced"],
        index=0,
        horizontal=False
    )

    if st.button("Start Learning"):
        st.session_state.lp_level = level
        st.session_state.lp_started = True

    st.stop()


# -----------------------------
# LEARNING CONTENT
# -----------------------------
level = st.session_state.lp_level

left, right = st.columns([2, 1])

with left:
    st.header(f"{level} Level — Learning Content")

    if level == "Beginner":
        st.markdown("""
### SOC Foundations

**What you’ll learn:**
- What a SOC actually does
- SOC analyst day-to-day work
- What SIEM means in real operations
- What SOAR automates (and what it doesn’t)
- How alerts become incidents
- Why humans still matter in security

---

### 1. What is a SOC?
A Security Operations Center (SOC) is responsible for monitoring, detecting, investigating, and responding to security threats.

### 2. SOC Analyst Day-to-Day
Analysts review alerts, validate threats, escalate incidents, and document actions.

### 3. What is SIEM?
SIEM aggregates logs, correlates events, and raises alerts.

### 4. What is SOAR?
SOAR automates repetitive steps **after** an alert exists.

### 5. Alert → Incident Lifecycle
Not every alert is an incident. Triage decides.

### 6. Why Humans Still Matter
Automation supports analysts — it does not replace judgment.
        """)

    elif level == "Intermediate":
        st.markdown("""
### SOC Workflows & Automation

**Focus:**
- Investigation flow
- Decision points
- Automation boundaries

---

- Alert ingestion
- Context enrichment
- Confidence scoring
- Human review vs automation
- Case updates
        """)

    elif level == "Advanced":
        st.markdown("""
### Advanced SOC & SOAR Design

**Focus:**
- Playbook architecture
- Failure handling
- Governance
- Metrics & tuning
- IRP → SOAR translation
        """)

with right:
    st.subheader("Workflow Diagram")
    st.info("Workflow diagram will appear here.")
