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
Return ONLY valid JSON.
No markdown. No backticks.

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
# UI HELPERS
# -------------------------------------------------
def box(title, subtitle, color):
    return f"""
    <div style="
        padding:12px 18px;
        border-radius:14px;
        background:{color};
        color:white;
        font-weight:600;
        text-align:center;
        white-space:nowrap;
        box-shadow:0 6px 14px rgba(0,0,0,0.18);
    ">
        {title}<br/>
        <span style="font-size:12px;font-weight:400;">
            {subtitle}
        </span>
    </div>
    """

def arrow_down():
    return "<div style='font-size:26px;text-align:center;'>↓</div>"

def arrow_right():
    return "<div style='font-size:26px;text-align:center;'>→</div>"

# -------------------------------------------------
# MAIN UI
# -------------------------------------------------
st.title("🛡️ SOAR Playbook Generator")

use_case = st.text_area(
    "SOAR Use Case Description",
    height=220,
    placeholder="Account Compromise – Brute Force Success"
)

if st.button("Generate Playbook"):

    if not use_case.strip():
        st.warning("Please enter a use case.")
        st.stop()

    with st.spinner("Generating playbook..."):
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=build_prompt(use_case)
        )

    try:
        data = parse_model_output(response.text)
        documentation = data["documentation"]
    except Exception:
        st.error("Model output could not be parsed.")
        st.stop()

    # -------------------------------------------------
    # GRAPHICAL FLOW (GRID-BASED)
    # -------------------------------------------------
    st.header("🔗 SOAR Flow (Graphical)")

    flow_html = f"""
    <div style="
        display:grid;
        grid-template-columns: 1fr 1fr 1fr;
        grid-template-rows: auto auto auto auto;
        gap:30px;
        justify-items:center;
        align-items:center;
        margin-top:20px;
    ">

        <!-- ROW 1 -->
        <div style="grid-column:2;">
            {box("Trigger", "SIEM Brute Force", "#0f766e")}
        </div>

        <!-- ARROW -->
        <div style="grid-column:2;">
            {arrow_down()}
        </div>

        <!-- ROW 2 -->
        <div style="grid-column:2;">
            {box("Enrichment", "Azure AD + IP", "#15803d")}
        </div>

        <!-- ARROW -->
        <div style="grid-column:2;">
            {arrow_down()}
        </div>

        <!-- ROW 3 -->
        <div style="grid-column:2;">
            {box("Threat Intel", "IP Reputation", "#374151")}
        </div>

        <!-- ARROW -->
        <div style="grid-column:2;">
            {arrow_down()}
        </div>

        <!-- DECISION -->
        <div style="grid-column:2;">
            {box("Decision", "Compromise Confidence?", "#d97706")}
        </div>

        <!-- BRANCH ARROWS -->
        <div style="grid-column:1;">
            {arrow_down()}
        </div>

        <div style="grid-column:3;">
            {arrow_down()}
        </div>

        <!-- LEFT BRANCH (HIGH) -->
        <div style="grid-column:1;">
            {box("HIGH", "Auto Containment", "#b91c1c")}
        </div>

        <!-- RIGHT BRANCH (LOW/MED) -->
        <div style="grid-column:3;">
            {box("LOW / MED", "Manual Review", "#2563eb")}
        </div>

        <!-- LEFT FLOW -->
        <div style="grid-column:1;">
            {arrow_down()}
        </div>

        <div style="grid-column:3;">
            {arrow_down()}
        </div>

        <div style="grid-column:1;">
            {box("Account Actions", "Disable / Revoke", "#7f1d1d")}
        </div>

        <div style="grid-column:3;">
            {box("L1 Analysis", "Validate & Decide", "#1e40af")}
        </div>

        <!-- FINAL -->
        <div style="grid-column:1;">
            {arrow_down()}
        </div>

        <div style="grid-column:3;">
            {arrow_down()}
        </div>

        <div style="grid-column:1;">
            {box("Preserve Evidence", "Logs + EDR", "#1f2937")}
        </div>

        <div style="grid-column:3;">
            {box("Close / Escalate", "Next Steps", "#0f172a")}
        </div>

    </div>
    """

    st.markdown(flow_html, unsafe_allow_html=True)

    # -------------------------------------------------
    # DOCUMENTATION
    # -------------------------------------------------
    st.header("📄 Playbook Documentation")
    st.markdown(documentation)
