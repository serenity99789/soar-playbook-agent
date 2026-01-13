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
# UI ELEMENTS
# -------------------------------------------------
def box(title, subtitle, color):
    st.markdown(
        f"""
        <div style="
            display:inline-block;
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
        """,
        unsafe_allow_html=True
    )

def arrow():
    st.markdown(
        "<span style='font-size:26px;margin:0 10px;'>→</span>",
        unsafe_allow_html=True
    )

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
        blocks = data["blocks"]
        documentation = data["documentation"]
    except Exception:
        st.error("Model output could not be parsed.")
        st.stop()

    # -------------------------------------------------
    # TEXTUAL STEPS (NO JSON)
    # -------------------------------------------------
    st.success("Playbook generated")

    st.header("🧩 Playbook Steps")
    for i, block in enumerate(blocks, start=1):
        with st.expander(f"Step {i}: {block['block_name']}"):
            st.markdown(f"**Purpose:** {block['purpose']}")
            st.markdown(f"**Inputs:** {', '.join(block['inputs'])}")
            st.markdown(f"**Outputs:** {', '.join(block['outputs'])}")
            st.markdown(f"**SLA Impact:** {block['sla_impact']}")
            st.markdown(f"**Analyst Notes:** {block['analyst_notes']}")

    # -------------------------------------------------
    # GRAPHICAL FLOW
    # -------------------------------------------------
    st.header("🔗 SOAR Flow (Graphical)")

    # Top flow
    st.markdown("<div style='display:flex;align-items:center;flex-wrap:wrap;'>", unsafe_allow_html=True)
    box("Trigger", "SIEM Brute Force", "#0f766e")
    arrow()
    box("Enrichment", "Azure AD + IP", "#15803d")
    arrow()
    box("Threat Intel", "IP Reputation", "#374151")
    arrow()
    box("Decision", "Confidence?", "#d97706")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Branches
    st.markdown("<div style='display:flex;gap:80px;flex-wrap:wrap;'>", unsafe_allow_html=True)

    # HIGH
    st.markdown("<div>", unsafe_allow_html=True)
    box("HIGH", "Auto Contain", "#b91c1c")
    arrow()
    box("Account Actions", "Disable / Revoke", "#7f1d1d")
    arrow()
    box("Preserve Evidence", "Logs + EDR", "#1f2937")
    arrow()
    box("Notify L2", "Incident", "#065f46")
    st.markdown("</div>", unsafe_allow_html=True)

    # LOW / MED
    st.markdown("<div>", unsafe_allow_html=True)
    box("LOW / MED", "Manual Review", "#2563eb")
    arrow()
    box("L1 Analysis", "Validate", "#1e40af")
    arrow()
    box("Close / Escalate", "Decision", "#0f172a")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # DOCUMENTATION
    # -------------------------------------------------
    st.header("📄 Playbook Documentation")
    st.markdown(documentation)
