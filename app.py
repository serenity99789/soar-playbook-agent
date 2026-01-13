import os
import json
import re
import streamlit as st
from google import genai

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="SOAR Playbook Generator", layout="wide")
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
# PROMPT
# -------------------------------------------------
def build_prompt(use_case: str) -> str:
    return f"""
You are a SOAR playbook generation engine.

Return ONLY valid JSON.
Do NOT use markdown.
Do NOT use triple backticks.
Do NOT include explanations.

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
# SAFE JSON PARSER
# -------------------------------------------------
def parse_model_output(text: str):
    cleaned = re.sub(r"```json|```", "", text).strip()
    return json.loads(cleaned)

# -------------------------------------------------
# UI COMPONENTS
# -------------------------------------------------
def render_box(title, subtitle, color):
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
                {subtitle}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

def arrow():
    st.markdown("<div style='font-size:28px;color:#6b7280;'>→</div>", unsafe_allow_html=True)

# -------------------------------------------------
# MAIN UI
# -------------------------------------------------
st.title("🛡️ SOAR Playbook Generator")

use_case_input = st.text_area(
    "SOAR Use Case Description",
    height=220,
    placeholder="Account Compromise – Brute Force Success"
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
        data = parse_model_output(response.text)
        blocks = data["blocks"]
        documentation = data["documentation"]
    except Exception:
        st.error("Model output could not be parsed safely.")
        st.stop()

    # -------------------------------------------------
    # TEXTUAL PLAYBOOK (NO CODE SHOWN)
    # -------------------------------------------------
    st.success("Playbook generated successfully")

    st.header("🧩 Playbook Steps (Readable)")
    for i, block in enumerate(blocks, start=1):
        with st.expander(f"Step {i}: {block['block_name']}"):
            st.markdown(f"**Purpose:** {block['purpose']}")
            st.markdown(f"**Inputs:** {', '.join(block['inputs'])}")
            st.markdown(f"**Outputs:** {', '.join(block['outputs'])}")
            st.markdown(f"**SLA Impact:** {block['sla_impact']}")
            st.markdown(f"**Analyst Notes:** {block['analyst_notes']}")

    # -------------------------------------------------
    # GRAPHICAL SOAR FLOW (DECISION AWARE, NON-LINEAR)
    # -------------------------------------------------
    st.header("🔗 SOAR Flow (Graphical)")

    # Top linear flow
    st.markdown("<div style='display:flex;gap:18px;align-items:center;overflow-x:auto;'>", unsafe_allow_html=True)
    render_box("Trigger", "SIEM Brute Force Success", "#0f766e")
    arrow()
    render_box("Enrichment", "Azure AD + IP Context", "#15803d")
    arrow()
    render_box("Threat Intel", "IP Reputation", "#374151")
    arrow()
    render_box("Decision", "Compromise Confidence?", "#d97706")
    st.markdown("</div>", unsafe_allow_html=True)

    # Branching paths
    st.markdown("<div style='display:flex;gap:80px;margin-top:32px;'>", unsafe_allow_html=True)

    # HIGH confidence path
    st.markdown("<div>", unsafe_allow_html=True)
    render_box("HIGH Confidence", "Auto Containment", "#b91c1c")
    arrow()
    render_box("Disable Account", "Azure AD Actions", "#7f1d1d")
    arrow()
    render_box("Preserve Evidence", "Logs + EDR", "#1f2937")
    arrow()
    render_box("Notify L2 SOC", "Incident Created", "#065f46")
    st.markdown("</div>", unsafe_allow_html=True)

    # LOW / MED confidence path
    st.markdown("<div>", unsafe_allow_html=True)
    render_box("LOW / MEDIUM", "Manual Review", "#2563eb")
    arrow()
    render_box("L1 Investigation", "Validate Activity", "#1e40af")
    arrow()
    render_box("Close or Escalate", "Based on Findings", "#0f172a")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # DOCUMENTATION
    # -------------------------------------------------
    st.header("📄 Playbook Documentation")
    st.markdown(documentation)
