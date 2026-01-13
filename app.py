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
    st.error("GEMINI_API_KEY not set. Please set it in Streamlit secrets.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# PROMPT (STRICT + JSON-SAFE)
# -------------------------------------------------
def build_prompt(use_case: str) -> str:
    return f"""
You are a SOAR playbook generation engine.

CRITICAL RULES:
- Output MUST be valid JSON
- Output MUST start with {{ and end with }}
- Do NOT include explanations, markdown, headings, or extra text
- Do NOT include bullet points outside JSON
- If JSON is invalid, the response is unusable

You MUST follow this EXACT schema:

{{
  "blocks": [
    {{
      "block_name": "Incident_Ingestion_and_Triage",
      "purpose": "Brief purpose",
      "inputs": ["input1", "input2"],
      "outputs": ["output1"],
      "failure_handling": "Failure handling steps",
      "sla_impact": "SLA impact",
      "analyst_notes": "Notes for SOC analysts"
    }}
  ],
  "documentation": "SOC-ready documentation text"
}}

If you cannot comply, return EXACTLY this JSON and nothing else:

{{
  "blocks": [],
  "documentation": "Generation failed"
}}

Generate the playbook for the following use case:

{use_case}
"""

# -------------------------------------------------
# PARSERS (ROBUST)
# -------------------------------------------------
def extract_json(text: str):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except Exception:
        return None

def derive_confidence(blocks):
    score = 0
    signals = []

    names = " ".join(b.get("block_name", "").lower() for b in blocks)

    if "ip" in names:
        score += 1
        signals.append("IP reputation checks present")

    if "endpoint" in names or "edr" in names:
        score += 1
        signals.append("Endpoint / EDR analysis present")

    if "contain" in names or "reset" in names:
        score += 1
        signals.append("Containment actions defined")

    if score >= 3:
        return "HIGH", signals, "Automated containment recommended"
    elif score == 2:
        return "MEDIUM", signals, "Analyst approval recommended"
    else:
        return "LOW", signals, "Monitor only"

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🛡️ SOAR Playbook Generator")

use_case_input = st.text_area(
    "SOAR Use Case Description",
    height=240,
    placeholder="Describe the SOAR use case here…"
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

    if not parsed or "blocks" not in parsed:
        st.error("No valid playbook blocks returned.")
        st.text_area("Raw AI Output", raw_output, height=300)
        st.stop()

    blocks = parsed.get("blocks", [])
    documentation = parsed.get("documentation", "")

    if not blocks:
        st.error("Model returned empty blocks.")
        st.text_area("Raw AI Output", raw_output, height=300)
        st.stop()

    st.success("Playbook generated successfully")

    # -------------------------------------------------
    # BLOCKS
    # -------------------------------------------------
    st.header("🧩 Playbook Blocks")

    for i, block in enumerate(blocks, start=1):
        with st.expander(f"Block {i}: {block.get('block_name')}"):
            st.markdown(f"**Purpose:** {block.get('purpose')}")
            st.markdown(f"**Inputs:** {', '.join(block.get('inputs', []))}")
            st.markdown(f"**Outputs:** {', '.join(block.get('outputs', []))}")
            st.markdown(f"**Failure Handling:** {block.get('failure_handling')}")
            st.markdown(f"**SLA Impact:** {block.get('sla_impact')}")
            st.markdown(f"**Analyst Notes:** {block.get('analyst_notes')}")

    # -------------------------------------------------
    # FLOW
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


