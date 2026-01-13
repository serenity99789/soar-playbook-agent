import os
import json
import streamlit as st
from google import genai

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(page_title="SOAR Playbook Generator", layout="wide")
st.caption("Built by Srinivas")

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("GEMINI_API_KEY not set. Please set it in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def build_prompt(use_case: str) -> str:
    return f"""
Return ONLY valid JSON. No explanations. No markdown.

The JSON MUST strictly follow this schema:

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

If valid JSON cannot be produced, return exactly:

{{
  "blocks": [],
  "documentation": "Generation failed"
}}

Use case:
{use_case}
"""

def parse_response(text: str):
    try:
        data = json.loads(text)
        blocks = data.get("blocks", [])
        documentation = data.get("documentation", "")
        return blocks, documentation
    except Exception:
        return [], ""

def derive_confidence(blocks):
    signals = []
    score = 0

    block_names = " ".join(b.get("block_name", "").lower() for b in blocks)

    if "ip" in block_names:
        score += 1
        signals.append("Suspicious IP reputation checks present")

    if "endpoint" in block_names or "edr" in block_names:
        score += 1
        signals.append("Endpoint / EDR context evaluated")

    if "contain" in block_names or "reset" in block_names:
        score += 1
        signals.append("Containment actions defined")

    if score >= 3:
        return "HIGH", signals, "Automated containment recommended"
    elif score == 2:
        return "MEDIUM", signals, "Analyst review recommended"
    else:
        return "LOW", signals, "Monitor only"

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
        raw_output = response.text.strip()

    blocks, documentation = parse_response(raw_output)

    if not blocks:
        st.error("No valid playbook blocks returned.")
        st.text_area("Raw AI Output", raw_output, height=300)
        st.stop()

    st.success("Playbook blocks generated successfully")

    # -------------------------------------------------
    # PLAYBOOK BLOCKS
    # -------------------------------------------------
    st.header("🧩 Playbook Blocks")

    for i, block in enumerate(blocks, start=1):
        with st.expander(f"Block {i}: {block['block_name']}"):
            st.markdown(f"**Purpose:** {block['purpose']}")
            st.markdown(f"**Inputs:** {', '.join(block['inputs'])}")
            st.markdown(f"**Outputs:** {', '.join(block['outputs'])}")
            st.markdown(f"**Failure Handling:** {block['failure_handling']}")
            st.markdown(f"**SLA Impact:** {block['sla_impact']}")
            st.markdown(f"**Analyst Notes:** {block['analyst_notes']}")

    # -------------------------------------------------
    # PLAYBOOK FLOW
    # -------------------------------------------------
    st.header("🧭 Playbook Flow")
    flow = " → ".join(b["block_name"].replace("_", " ") for b in blocks)
    st.code(flow)

    # -------------------------------------------------
    # DECISION SUMMARY
    # -------------------------------------------------
    st.header("🧠 Decision Summary")

    confidence, signals, recommendation = derive_confidence(blocks)

    st.markdown(f"**Overall Confidence Level:** `{confidence}`")
    st.markdown("**Signals Considered:**")
    for s in signals:
        st.markdown(f"- {s}")

    st.markdown(f"**Recommended Action Mode:** `{recommendation}`")

    # -------------------------------------------------
    # DOCUMENTATION
    # -------------------------------------------------
    st.header("📄 Playbook Documentation")
    st.markdown(documentation or "_No documentation returned_")

