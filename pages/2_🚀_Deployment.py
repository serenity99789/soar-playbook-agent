import streamlit as st
import streamlit.components.v1 as components
from core.playbook_engine import generate_playbook
from core.diagram_engine import generate_soar_mermaid

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Deployment Playbook",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 SOAR Deployment Playbook")
st.caption("Production-grade SOAR execution flow")

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "deployment_result" not in st.session_state:
    st.session_state.deployment_result = None

if "deployment_mermaid" not in st.session_state:
    st.session_state.deployment_mermaid = None

# -------------------------------------------------
# INPUT SECTION
# -------------------------------------------------
st.subheader("Describe the SIEM alert")

use_case = st.text_area(
    "Deployment use case",
    placeholder=(
        "Example:\n"
        "Multiple failed authentication attempts detected from a single external IP.\n"
        "Followed by a successful login to a privileged account."
    ),
    height=160
)

col1, col2 = st.columns([1, 3])

with col1:
    generate_btn = st.button("Generate Deployment Playbook", use_container_width=True)

with col2:
    st.markdown(
        "This view shows **how SOAR executes safely in production**, "
        "including governance, conditional automation, and human checkpoints."
    )

# -------------------------------------------------
# GENERATION
# -------------------------------------------------
if generate_btn:
    if not use_case.strip():
        st.warning("Please provide a SIEM alert description.")
    else:
        with st.spinner("Analyzing alert and building deployment playbook..."):
            result = generate_playbook(
                alert_text=use_case,
                mode="deployment",
                depth="Advanced"
            )

            mermaid_code = generate_soar_mermaid(result)

            st.session_state.deployment_result = result
            st.session_state.deployment_mermaid = mermaid_code

        st.success("Deployment playbook generated")

# -------------------------------------------------
# OUTPUT SECTION
# -------------------------------------------------
if st.session_state.deployment_result:

    result = st.session_state.deployment_result

    # -----------------------------
    # DEPLOYMENT STEPS
    # -----------------------------
    st.divider()
    st.header("📋 Deployment Steps")

    for i, block in enumerate(result["blocks"], 1):
        with st.expander(f"Step {i}: {block['name']}"):
            st.markdown(f"**Category:** {block['category']}")
            st.markdown(f"**Purpose:** {block['purpose']}")
            st.markdown(f"**Automation Level:** {block['automation_level']}")
            st.markdown(f"**Failure Impact:** {block['failure_impact']}")

    # -----------------------------
    # SOAR EXECUTION FLOW
    # -----------------------------
    st.divider()
    st.header("🧭 SOAR Execution Flow")

    mermaid = st.session_state.deployment_mermaid

    components.html(
        f"""
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: "dark",
                flowchart: {{
                    curve: "basis",
                    nodeSpacing: 40,
                    rankSpacing: 70,
                    padding: 10
                }}
            }});
        </script>
        <div class="mermaid" style="overflow-x:auto; padding:20px;">
        {mermaid}
        </div>
        """,
        height=600,
        scrolling=True
    )

    # -----------------------------
    # DOWNLOAD (NO RESET)
    # -----------------------------
    st.download_button(
        label="⬇️ Download Mermaid Diagram",
        data=mermaid,
        file_name="soar_deployment_playbook.mmd",
        mime="text/plain",
        use_container_width=False
    )

    # -----------------------------
    # GOVERNANCE SUMMARY
    # -----------------------------
    st.divider()
    st.header("🔐 Automation Governance")

    st.markdown(
        """
        - ✅ **Data collection & enrichment** fully automated  
        - ⚠️ **Containment actions** are conditional  
        - 👤 **Identity actions** require SOC approval  
        - 📁 **Evidence preserved before response**  
        - 🚫 **No single-signal automation**
        """
    )

# -------------------------------------------------
# PLACEHOLDER: IRP INPUT (NEXT)
# -------------------------------------------------
st.divider()
st.caption("🔜 IRP upload & mapping will be added next (radio toggle).")
