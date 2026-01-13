import os
import json
import streamlit as st
from google import genai

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Playbook Generator",
    layout="wide"
)

st.caption("Built by Srinivas")

# -------------------------------------------------
# API CONFIG
# -------------------------------------------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("GEMINI_API_KEY not set")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# PROMPT (STRICT JSON, INTERNAL ONLY)
# -------------------------------------------------
def build_prompt(use_case: str) -> str:
    return f"""
You are a SOAR playbook generation engine.

Return ONLY valid JSON. No markdown. No explanations.

Schema:
{{
  "blocks": [
    {{
      "block_name": "",
      "purpose": "",
      "inputs": [],
      "outputs": [],
      "failure_handling": "",
      "sla_impact": "",
      "analyst_notes": ""
    }}
  ],
  "documentation": ""
}}

Use case:
{use_case}
"""

# -------------------------------------------------
# UI HELPERS
# -------------------------------------------------
def render_block_card(title, purpose, color):
    st.markdown(
        f"""
        <div style="
            min-width:260px;
            padding:14px;
            border-radius:14px;
            background:{color};
            color:white;
            font-weight:600;
            text-align:center;
            box-shadow:0 6px 14px rgba(0,0,0,0.18);
        ">
            {title}<br/>
            <span style="font-size:12px;font-weight:400;">
                {purpose}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

def arrow():
    st.markdown(
        "<div style='font-size:28px;color:#6b7280;'>→</div>",
        unsafe_allow_html=True
    )

# -------------------------------------------------
# MAIN UI
# -------------------------------------------------
st.title("🛡️ SOAR Playbook Generator")

use_case_input = st.text_area(
    "SOAR Use Case Description",
    height=220
)

if st.button("Generate Playbook"):

    if not use_case_input.strip():
        st.warning("Please enter a use case.")
        st.stop()

    with st.spinner("Generating playbook..."):
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=build_prompt(use_case_input)
        )

    try:
        data = json.loads(response.text)
        blocks = data["blocks"]
        documentation = data["documentation"]
    except Exception:
        st.error("Model did not return valid JSON")
        st.text(response.text)
        st.stop()

    # -------------------------------------------------
    # TEXT PLAYBOOK (CLIENT FRIENDLY)
    # -------------------------------------------------
    st.success("Playbook generated successfully")

    st.header("🧩 Playbook Steps")

    for i, b in enumerate(blocks, start=1):
        with st.expander(f"Step {i}: {b['block_name']}"):
            st.markdown(f"**Purpose:** {b['purpose']}")
            st.markdown(f"**Inputs:** {', '.join(b['inputs'])}")
            st.markdown(f"**Outputs:** {', '.join(b['outputs'])}")
            st.markdown(f"**SLA Impact:** {b['sla_impact']}")
            st.markdown(f"**Notes:** {b['analyst_notes']}")

    # -------------------------------------------------
    # GRAPHICAL FLOW (REAL SOAR STYLE)
    # -------------------------------------------------
    st.header("🔗 SOAR Flow (Graphical)")

    st.markdown(
        "<div style='display:flex;gap:18px;align-items:center;overflow-x:auto;'>",
        unsafe_allow_html=True
    )

    # Trigger
    render_block_card(
        "Trigger: SIEM Alert Ingestion",
        "Brute force success detected",
        "#0f766e"
    )
    arrow()

    # Enrichment
    render_block_card(
        "Enrich User Context",
        "Azure AD, MFA, role, geo",
        "#15803d"
    )
    arrow()

    # Threat Intel
    render_block_card(
        "IP Threat Intelligence",
        "Reputation, TOR, VPN",
        "#374151"
    )
    arrow()

    # Decision Node
    render_block_card(
        "Decision: Compromise Confidence?",
        "Aggregate all signals",
        "#d97706"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # BRANCHING (NOT ONE-DIMENSIONAL)
    # -------------------------------------------------
    st.markdown(
        "<div style='display:flex;gap:80px;margin-top:30px;'>",
        unsafe_allow_html=True
    )

    # HIGH CONFIDENCE PATH
    st.markdown("<div>", unsafe_allow_html=True)
    render_block_card(
        "HIGH Confidence",
        "Automated containment",
        "#b91c1c"
    )
    arrow()
    render_block_card(
        "Disable Account + Block IP",
        "Immediate containment",
        "#7f1d1d"
    )
    arrow()
    render_block_card(
        "Preserve Evidence",
        "Logs & forensic data",
        "#1f2937"
    )
    arrow()
    render_block_card(
        "Notify SOC (L2)",
        "Incident created",
        "#065f46"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # LOW / MEDIUM CONFIDENCE PATH
    st.markdown("<div>", unsafe_allow_html=True)
    render_block_card(
        "LOW / MEDIUM Confidence",
        "Manual review",
        "#2563eb"
    )
    arrow()
    render_block_card(
        "L1 Investigation",
        "Validate legitimacy",
        "#1e40af"
    )
    arrow()
    render_block_card(
        "Close or Escalate",
        "Based on findings",
        "#0f172a"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # DOCUMENTATION
    # -------------------------------------------------
    st.header("📄 Playbook Documentation")
    st.markdown(documentation)
