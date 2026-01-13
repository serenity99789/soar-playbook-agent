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
    st.error("GEMINI_API_KEY not set. Please set it in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# PROMPT
# -------------------------------------------------
def build_prompt(use_case: str) -> str:
    return f"""
You are a SOAR Playbook Generation Engine.

You MUST return STRICT VALID JSON ONLY.
NO markdown.
NO explanations.
NO text outside JSON.

The JSON schema MUST be EXACTLY:

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
- The FIRST block MUST be a Trigger block.
- The flow MUST be linear (top to bottom).
- Use SOC / SOAR terminology.
- Assume enterprise environment.

Use case:
{use_case}
"""

# -------------------------------------------------
# PARSERS
# -------------------------------------------------
def extract_json(text: str):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        return json.loads(match.group())
    except Exception:
        return None

# -------------------------------------------------
# FLOWCHART (CLOUD SAFE)
# -------------------------------------------------
def build_flowchart_dot(blocks):
    dot = "digraph SOAR {\n"
    dot += "rankdir=TB;\n"
    dot += "node [shape=box style=rounded fontname=Arial];\n"

    for i, block in enumerate(blocks):
        label = f"{block['block_name']}\\n\\n{block['purpose']}"
        dot += f'node{i} [label="{label}"];\n'
        if i > 0:
            dot += f"node{i-1} -> node{i};\n"

    dot += "}"
    return dot

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🛡️ SOAR Playbook Generator")

use_case_input = st.text_area(
    "SOAR Use Case Description",
    height=220,
    placeholder="Describe the security scenario..."
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

    data = extract_json(raw_output)

    if not data or "blocks" not in data:
        st.error("No valid playbook JSON returned.")
        st.text_area("Raw AI Output", raw_output, height=300)
        st.stop()

    blocks = data["blocks"]
    documentation = data.get("documentation", "")

    st.success("Playbook generated successfully")

    # -------------------------------------------------
    # BLOCKS (TEXT)
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
    # FLOWCHART (GUI)
    # -------------------------------------------------
    st.header("🔗 SOAR Flow (Graphical)")

    dot_flow = build_flowchart_dot(blocks)
    st.graphviz_chart(dot_flow)

    # -------------------------------------------------
    # DOCUMENTATION
    # -------------------------------------------------
    st.header("📄 Playbook Documentation")
    st.markdown(documentation or "_No documentation provided_")
