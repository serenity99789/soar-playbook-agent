import streamlit as st
import streamlit.components.v1 as components
from core.playbook_engine import generate_playbook

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Deployment View",
    page_icon="🚀",
    layout="wide"
)

st.caption("Built by Accenture")

# -------------------------------------------------
# MERMAID (ENTERPRISE SOAR FLOW)
# -------------------------------------------------
def build_execution_flow():
    return """
flowchart TD

A[Alert Validation & Enrichment]:::analysis
B[Threat Intelligence Lookup]:::analysis
C{Threat Confirmed?}:::decision

D[Auto Containment]:::auto
E[Isolate Host / Block IP]:::auto
F[Preserve Evidence]:::evidence
G[Notify IR Team]:::notify

H[Human Review]:::human
I[SOC Analyst Decision]:::human

A --> B --> C
C -->|Yes| D --> E --> F --> G
C -->|Uncertain| H --> I

classDef analysis fill:#2563eb,color:#ffffff,stroke:#1e3a8a,stroke-width:2px
classDef decision fill:#f59e0b,color:#000000,stroke:#b45309,stroke-width:3px
classDef auto fill:#dc2626,color:#ffffff,stroke:#7f1d1d,stroke-width:2px
classDef human fill:#7c3aed,color:#ffffff,stroke:#4c1d95,stroke-width:2px
classDef notify fill:#16a34a,color:#ffffff,stroke:#14532d,stroke-width:2px
classDef evidence fill:#0ea5e9,color:#ffffff,stroke:#075985,stroke-width:2px
"""

def render_mermaid(code: str):
    components.html(
        f"""
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: "default",
                flowchart: {{ curve: "linear" }}
            }});
        </script>
        <div class="mermaid">{code}</div>
        """,
        height=700,
        scrolling=True
    )

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🚀 SOAR Deployment View")
st.markdown("Production-ready response flow with governance controls")

st.subheader("Describe the SIEM alert")
alert_text = st.text_area(
    "Example:",
    placeholder="Suspicious PowerShell execution detected on endpoint...",
    height=150
)

if st.button("Generate Deployment Playbook"):
    if not alert_text.strip():
        st.warning("Please describe the SIEM alert.")
    else:
        with st.spinner("Generating deployment playbook..."):
            result = generate_playbook(
                alert_text=alert_text,
                mode="deployment",
                depth="Advanced"
            )

        st.success("Deployment playbook generated")

        # -----------------------------
        # DEPLOYMENT STEPS
        # -----------------------------
        st.header("📋 Deployment Steps")
        for i, block in enumerate(result["blocks"], 1):
            with st.expander(f"Step {i}: {block['title']}"):
                st.markdown(f"**Purpose:** {block.get('description','')}")
                if block.get("automation"):
                    st.markdown(f"⚙️ **Automation:** {block['automation']}")
                if block.get("human_gate"):
                    st.markdown(f"👤 **Human Gate:** {block['human_gate']}")

        # -----------------------------
        # EXECUTION FLOW
        # -----------------------------
        st.header("🧭 SOAR Execution Flow")
        flow = build_execution_flow()
        render_mermaid(flow)

        # -----------------------------
        # SVG DOWNLOAD
        # -----------------------------
        st.download_button(
            label="⬇️ Download SOAR Playbook (SVG)",
            data=flow,
            file_name="soar_execution_flow.svg",
            mime="image/svg+xml"
        )
