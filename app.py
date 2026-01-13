import os
import json
import re
import streamlit as st
from google import genai

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(page_title="SOAR Playbook Generator", layout="wide")
st.caption("Built by Srinivas")

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("GEMINI_API_KEY not set. Please set it and restart.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def build_prompt(use_case: str) -> str:
    return f"""
You are a SOAR playbook generation engine.

Return STRICT JSON only.

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

def extract_json(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except Exception:
        return None

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🛡️ SOAR Playbook Generator")

use_case_input = st.text_area(
    "SOAR Use Case Description",
    height=220,
    placeholder="Account Compromise – Brute Force Success"
)

generate = st.button("Generate Playbook")

# -------------------------------------------------
# RUN
# -------------------------------------------------
if generate:
    if not use_case_input.strip():
        st.warning("Please enter a use case.")
        st.stop()

    with st.spinner("Generating playbook..."):
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=build_prompt(use_case_input),
        )
        raw_output = response.text

    parsed = extract_json(raw_output)

    if not parsed or not parsed.get("blocks"):
        st.error("No valid playbook blocks returned.")
        st.text_area("Raw AI Output", raw_output, height=300)
        st.stop()

    blocks = parsed["blocks"]
    documentation = parsed.get("documentation", "")

    st.success("Playbook generated successfully")

    # -------------------------------------------------
    # TEXT BLOCKS
    # -------------------------------------------------
    st.header("🧩 Playbook Blocks")

    for i, b in enumerate(blocks, start=1):
        with st.expander(f"Block {i}: {b['block_name']}"):
            st.markdown(f"**Purpose:** {b['purpose']}")
            st.markdown(f"**Inputs:** {', '.join(b['inputs'])}")
            st.markdown(f"**Outputs:** {', '.join(b['outputs'])}")
            st.markdown(f"**Failure Handling:** {b['failure_handling']}")
            st.markdown(f"**SLA Impact:** {b['sla_impact']}")
            st.markdown(f"**Analyst Notes:** {b['analyst_notes']}")

    # -------------------------------------------------
    # GRAPHICAL SOAR FLOW (NON-LINEAR)
    # -------------------------------------------------
    st.header("🔗 SOAR Flow (Graphical)")

    def box(label, color):
        return f"""
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
        {label}
        </div>
        """

    arrow = "<div style='font-size:28px;margin:0 12px;'>→</div>"
    down = "<div style='font-size:28px;'>↓</div>"

    html = f"""
    <div style="overflow-x:auto;padding:20px">

      <!-- Trigger -->
      <div style="display:flex;justify-content:center;margin-bottom:20px">
        {box("Trigger: SIEM Alert Ingestion", "#0f766e")}
      </div>

      <div style="display:flex;justify-content:center;margin-bottom:20px">{down}</div>

      <!-- Enrichment Phase -->
      <div style="display:flex;justify-content:center;gap:20px;margin-bottom:30px">
        {box("Enrich User Context (Azure AD)", "#15803d")}
        {box("IP Threat Intelligence", "#15803d")}
        {box("Endpoint Context (EDR)", "#15803d")}
      </div>

      <div style="display:flex;justify-content:center;margin-bottom:20px">{down}</div>

      <!-- Decision -->
      <div style="display:flex;justify-content:center;margin-bottom:30px">
        {box("Decision: Compromise Confidence?", "#d97706")}
      </div>

      <!-- Branches -->
      <div style="display:flex;justify-content:space-around;margin-bottom:30px">

        <div style="display:flex;flex-direction:column;align-items:center;gap:14px">
          {box("HIGH Confidence", "#b91c1c")}
          {box("Disable User & Block IP", "#b91c1c")}
          {box("Preserve Evidence", "#7f1d1d")}
          {box("Notify SOC + Manager", "#7f1d1d")}
        </div>

        <div style="display:flex;flex-direction:column;align-items:center;gap:14px">
          {box("MEDIUM Confidence", "#7c3aed")}
          {box("Escalate to L2 Analyst", "#6d28d9")}
          {box("Request User Validation", "#6d28d9")}
        </div>

        <div style="display:flex;flex-direction:column;align-items:center;gap:14px">
          {box("LOW Confidence", "#374151")}
          {box("Monitor Activity", "#4b5563")}
          {box("Auto-Close if Clean", "#4b5563")}
        </div>

      </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    # -------------------------------------------------
    # DOCUMENTATION
    # -------------------------------------------------
    st.header("📄 Playbook Documentation")
    st.markdown(documentation or "_No documentation returned_")
