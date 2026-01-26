import streamlit as st
from core.playbook_engine import generate_playbook
import streamlit.components.v1 as components

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Deployment View",
    page_icon="🚀",
    layout="wide"
)

st.markdown("Built by Accenture")

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("🚀 SOAR Deployment View")
st.caption("Production-ready response flow with governed automation")

st.divider()

# -------------------------------------------------
# INPUT
# -------------------------------------------------
st.subheader("Describe the SIEM alert")
alert_text = st.text_area(
    "",
    placeholder="Suspicious PowerShell execution detected on endpoint...",
    height=140
)

# -------------------------------------------------
# GENERATE
# -------------------------------------------------
if st.button("Generate Deployment Playbook"):
    if not alert_text.strip():
        st.warning("Please describe the SIEM alert.")
        st.stop()

    with st.spinner("Generating deployment playbook..."):
        result = generate_playbook(
            alert_text=alert_text,
            mode="deployment",
            depth="Production"
        )

    st.success("Deployment playbook generated")

    # -------------------------------------------------
    # DEPLOYMENT STEPS
    # -------------------------------------------------
    st.header("📋 Deployment Steps")

    for i, block in enumerate(result["blocks"], 1):
        with st.expander(f"Step {i}: {block['title']}"):
            st.markdown(f"**Purpose:** {block['description']}")

    # -------------------------------------------------
    # GOVERNANCE SECTION (STATIC – LEADERSHIP READY)
    # -------------------------------------------------
    st.divider()
    st.header("🛡️ SOAR Governance & Automation Boundaries")

    st.markdown("""
This SOAR playbook follows **enterprise governance principles** to ensure
safe, auditable, and responsible automation.
""")

    # --- Automation Principles ---
    st.subheader("🔐 Automation Principles")

    st.markdown("""
- ✅ SOAR automates **data collection, enrichment, and correlation**
- ⚠️ High-impact actions are **conditionally executed**
- 👤 Identity-related actions require **human validation**
- 🧾 Evidence is preserved **before containment**
- 🚫 No response is executed based on a **single signal**
""")

    # --- Decision Ownership ---
    st.subheader("👥 Decision Ownership Matrix")

    st.table({
        "Action Type": [
            "Log enrichment & context gathering",
            "Threat intelligence scoring",
            "Network IP blocking",
            "Endpoint isolation",
            "User account lock / reset",
            "Incident escalation & closure"
        ],
        "Owner": [
            "SOAR Automation",
            "SOAR Automation",
            "SOAR (Conditional)",
            "SOAR (Conditional)",
            "SOC Analyst",
            "Incident Response Team"
        ]
    })

    # --- Automation Confidence ---
    st.subheader("📊 Automation Confidence Levels")

    st.markdown("""
- 🟢 **Fully Automated** – Safe, reversible, low-risk actions  
- 🟡 **Conditional Automation** – Executed after confidence thresholds  
- 🔴 **Human Approval Required** – High-impact or identity actions  
""")

    # -------------------------------------------------
    # EXECUTION FLOW (MERMAID)
    # -------------------------------------------------
    st.divider()
    st.header("🧭 SOAR Execution Flow")

    mermaid_code = """
    flowchart TD
        A[Alert Validation & Enrichment] --> B[Threat Intelligence Lookup]
        B --> C[Containment Decision]
        C -->|Confirmed Threat| D[Auto Containment]
        D --> E[Isolate Host / Block IP]
        E --> F[Preserve Evidence]
        F --> G[Notify IR Team]
        C -->|Uncertain| H[Human Review]
        H --> I[SOC Analyst Decision]
    """

    components.html(
        f"""
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>mermaid.initialize({{ startOnLoad: true }});</script>
        <div class="mermaid">{mermaid_code}</div>
        """,
        height=520
    )

    # -------------------------------------------------
    # DOWNLOAD SVG
    # -------------------------------------------------
    st.download_button(
        label="⬇️ Download SOAR Playbook (SVG)",
        data=mermaid_code,
        file_name="soar_execution_flow.svg",
        mime="image/svg+xml"
    )

    # -------------------------------------------------
    # FINAL NOTE
    # -------------------------------------------------
    st.info(
        "This deployment playbook is designed for **controlled automation**, "
        "clear human ownership, and enterprise SOC operations."
    )
