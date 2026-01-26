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
# Session state
# --------------------------------
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
        st.experimental_rerun()

st.divider()

# --------------------------------
# Layout
# --------------------------------
left, right = st.columns([2, 1])

# --------------------------------
# LEFT: Learning Content
# --------------------------------
with left:
    st.header("Beginner Level — Learning Content")

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
A Security Operations Center (SOC) is responsible for monitoring, detecting,
investigating, and responding to security threats across an organization.

### 2. SOC Analyst Day-to-Day
Analysts review alerts, enrich context, validate threats, escalate incidents,
and document actions.

### 3. What is SIEM?
SIEM collects logs, correlates events, and raises alerts — **it does not respond**.

### 4. What is SOAR?
SOAR automates investigation and response **after** an alert exists.

### 5. Alert → Incident Lifecycle
Not every alert becomes an incident. Human judgment decides.

### 6. Why Humans Still Matter
Automation supports analysts — it never replaces accountability.
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
#siemmy-btn {
    position: fixed;
    bottom: 24px;
    right: 24px;
    background: #ff4b4b;
    color: white;
    border-radius: 999px;
    padding: 12px 18px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 6px 16px rgba(0,0,0,0.2);
    z-index: 9999;
}
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

# Toggle button
if st.button("👋 Siemmy", key="siemmy_toggle"):
    st.session_state.show_siemmy = not st.session_state.show_siemmy

# Siemmy box
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
