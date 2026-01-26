import streamlit as st
import streamlit.components.v1 as components

# --------------------------------
# Page config
# --------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide"
)

# --------------------------------
# Session state init
# --------------------------------
if "current_view" not in st.session_state:
    st.session_state.current_view = "home"

if "selected_level" not in st.session_state:
    st.session_state.selected_level = "Beginner"

if "show_siemmy" not in st.session_state:
    st.session_state.show_siemmy = False

# --------------------------------
# Header
# --------------------------------
col1, col2 = st.columns([6, 1])
with col1:
    st.title("SOAR Learning Platform")
with col2:
    if st.button("🏠 Home"):
        st.session_state.current_view = "home"
        st.session_state.show_siemmy = False

st.divider()

# =========================================================
# HOME VIEW — LEVEL SELECTION
# =========================================================
if st.session_state.current_view == "home":
    st.header("Select your current level")

    st.radio(
        "",
        ["Beginner", "Intermediate", "Advanced"],
        key="selected_level"
    )

    if st.button("Start Learning"):
        st.session_state.current_view = "learning"

# =========================================================
# LEARNING VIEW
# =========================================================
if st.session_state.current_view == "learning":

    left, right = st.columns([2, 1])

    # --------------------------------
    # LEFT: Learning Content
    # --------------------------------
    with left:
        st.header(f"{st.session_state.selected_level} Level — Learning Content")

        st.subheader("SOC Foundations")
        st.markdown("""
**What you’ll learn:**
- What a SOC actually does  
- SOC analyst day-to-day work  
- What SIEM means in real operations  
- What SOAR automates (and what it doesn’t)  
- How alerts become incidents  
- Why humans still matter in security  
""")

        st.divider()

        st.markdown("""
### 1. What is a SOC?
A Security Operations Center (SOC) monitors, detects, investigates,
and responds to security threats.

### 2. SOC Analyst Day-to-Day
Review alerts, enrich context, validate threats, escalate incidents,
and document actions.

### 3. What is SIEM?
SIEM collects and correlates logs — it **does not respond**.

### 4. What is SOAR?
SOAR automates investigation and response **after detection**.

### 5. Alert → Incident Lifecycle
Not every alert becomes an incident. Humans decide.

### 6. Why Humans Still Matter
Automation supports analysts — accountability stays human.
""")

    # --------------------------------
    # RIGHT: Workflow Diagram
    # --------------------------------
    with right:
        st.subheader("Workflow Diagram")

        mermaid_code = """
        graph LR
            A[Alert Trigger] --> B[Initial Triage]
            B --> C[Basic Enrichment]
            C --> D{Confidence High?}
            D -- No --> E[Human Review]
            D -- Yes --> F[Automated Action]
            E --> F
            F --> G[Update Case]
        """

        components.html(
            f"""
            <div style="background:#f8f9fa;padding:12px;border-radius:8px;">
                <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
                <div class="mermaid">
                {mermaid_code}
                </div>
                <script>
                    mermaid.initialize({{ startOnLoad: true, theme: "default" }});
                </script>
            </div>
            """,
            height=320
        )

# --------------------------------
# SIEMMY (Floating Mentor)
# --------------------------------
st.markdown("""
<style>
#siemmy-box {
    position: fixed;
    bottom: 90px;
    right: 24px;
    width: 320px;
    background: white;
    border-radius: 12px;
    padding: 14px;
    box-shadow: 0 12px 24px rgba(0,0,0,0.25);
    z-index: 9999;
}
</style>
""", unsafe_allow_html=True)

if st.button("👋 Siemmy"):
    st.session_state.show_siemmy = not st.session_state.show_siemmy

if st.session_state.show_siemmy:
    st.markdown("""
    <div id="siemmy-box">
        <b>👋 Hi, I’m Siemmy</b><br><br>
        I help you understand:
        <ul>
            <li>SOC workflows</li>
            <li>SIEM vs SOAR</li>
            <li>Why automation stops</li>
        </ul>
        <i>Ask me anything — I’m here to guide you.</i>
    </div>
    """, unsafe_allow_html=True)
