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
    st.error("GEMINI_API_KEY not set in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# PROMPT
# -------------------------------------------------
def build_prompt(use_case: str) -> str:
    return f"""
You are a SOAR Playbook Generation Engine.

Return STRICT JSON ONLY.
No explanations. No markdown. No extra text.

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

Rules:
- FIRST block MUST be a Trigger block
- Blocks must be linear (no branching yet)
- Use SOC / SOAR terminology

Use case:
{use_case}
"""

# -------------------------------------------------
# PARSER
# -------------------------------------------------
def extract_json(text: str):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except Exception:
        return None

# -------------------------------------------------
# COLOR LOGIC
# -------------------------------------------------
def block_color(name: str) -> str:
    name = name.lower()
    if "trigger" in name:
        return "#0f766e"   # teal
    if any(x in name for x in ["enrich", "context", "lookup", "query"]):
        return "#15803d"   # green
    if any(x in name for x in ["analy", "validate", "check"]):
        return "#1d4ed8"   # blue
    if any(x in name for x in ["decision", "confidence", "evaluate"]):
        return "#c2410c"   # orange
    if any(x in name for x in ["contain", "reset", "disable", "block"]):
        return "#b91c1c"   # red
    if any(x in name for x in ["notify", "document", "update"]):
        return "#6d28d9"   # purple
    return "#374151"      # gray

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
            contents=build_prompt(use_case_input)
        )
        raw_output = response.text

    data = extract_json(raw_output)

    if not data or "blocks" not in data:
        st.error("No valid playbook JSON returned.")
        st.text_area("Raw AI Output", raw_output, height=300)
        st.stop()

    blocks = data["blocks"]
    documentation = data.get("documentation", "")

    st.success("Playbook generated successfully")

    # -------------------------------------------------
    # TEXT BLOCKS
    # -------------------------------------------------
    st.header("🧩 Playbook Blocks (Text)")

    for i, block in enumerate(blocks, start=1):
        with st.expander(f"Block {i}: {block['block_name']}"):
            st.markdown(f"**Purpose:** {block['purpose']}")
            st.markdown(f"**Inputs:** {', '.join(block['inputs'])}")
            st.markdown(f"**Outputs:** {', '.join(block['outputs'])}")
            st.markdown(f"**Failure Handling:** {block['failure_handling']}")
            st.markdown(f"**SLA Impact:** {block['sla_impact']}")
            st.markdown(f"**Analyst Notes:** {block['analyst_notes']}")

    # -------------------------------------------------
    # GRAPHICAL FLOW (REAL RENDER)
    # -------------------------------------------------
    st.header("🔗 SOAR Flow (Graphical)")

    flow_html = "<div style='display:flex; align-items:center; gap:16px; overflow-x:auto; padding:12px;'>"

    for i, block in enumerate(blocks):
        color = block_color(block["block_name"])

        flow_html += f"""
        <div style="
            min-width:260px;
            padding:14px;
            border-radius:14px;
            background:{color};
            color:white;
            font-weight:600;
            text-align:center;
            box-shadow:0 4px 10px rgba(0,0,0,0.15);
        ">
            {block['block_name']}
        </div>
        """

        if i < len(blocks) - 1:
            flow_html += "<div style='font-size:28px; color:#6b7280;'>➜</div>"

    flow_html += "</div>"

    # 🔴 THIS is the critical fix
    st.markdown(flow_html, unsafe_allow_html=True)

    # -------------------------------------------------
    # DOCUMENTATION
    # -------------------------------------------------
    st.header("📄 Playbook Documentation")
    st.markdown(documentation or "_No documentation provided_")
