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
NO markdown.
NO backticks.
NO explanations.

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
# SAFE JSON PARSER (FIX)
# -------------------------------------------------
def safe_parse_json(text: str):
    # Remove ```json and ``` if present
    cleaned = re.sub(r"```json|```", "", text).strip()
    return json.loads(cleaned)

# -------------------------------------------------
# UI HELPERS
# -------------------------------------------------
def block(title, subtitle, color):
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

use_case_input = st.text_area("SOAR Use Case Description", height=220)

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
        data = safe_parse_json(response.text)
        blocks = data["blocks"]
        documentation = data["documentation"]
    except Exception:
        st.error("Model response could not be parsed safely")
        st.stop()

    # -------------------------------------------------
    # TEXT PLAYBOOK (NO CODE SHOWN)
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
    # GRAPHICAL FLOW (DECISION AWARE)
    # -------------------------------------------------
    st.header("🔗 SOAR Flow (Graphical)")

    st.markdown("<div style='display:flex;gap:18px;align-items:center;overflow-x:auto;'>", unsafe_allow_html=True)

    block("Trigger: SIEM Alert", "Brute force success", "#0f766e")
    arrow()
    block("Enrich Context", "Azure AD + User", "#15803d")
    arrow()
    block("Threat Intel", "IP reputation", "#374151")
    arrow()
    block("Decision Node", "Compromise confidence?", "#d97706")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='display:flex;gap:80px;margin-top:30px;'>", unsafe_allow_html=True)

    # HIGH PATH
    st.markdown("<div>", unsafe_allow_html=True)
    block("HIGH Confidence", "Auto containment", "#b91c1c")
    arrow()
    block("Disable Account", "Azure AD actions", "#7f1d1d")
    arrow()
    block("Preserve Evidence", "Logs + EDR", "#1f2937")
    arrow()
    block("Notify L2 SOC", "Incident created", "#065f46")
    st.markdown("</div>", unsafe_allow_html=True)

    # LOW/MED PATH
    st.markdown("<div>", unsafe_allow_html=True)
    block("LOW / MEDIUM", "Manual review", "#2563eb")
    arrow()
    block("L1 Investigation", "Validate legitimacy", "#1e40af")
    arrow()
    block("Close / Escalate", "Based on findings", "#0f172a")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # DOCUMENTATION
    # -------------------------------------------------
    st.header("📄 Playbook Documentation")
    st.markdown(documentation)
