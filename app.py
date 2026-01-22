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
# WORKFLOW SUMMARY GENERATOR
# -------------------------------------------------
def generate_workflow_steps(blocks):
    steps = []
    for i, block in enumerate(blocks, start=1):
        name = block["block_name"].replace("_", " ")
        purpose = block["purpose"]
        steps.append(f"{i}. {name} – {purpose}")
    return steps

# -------------------------------------------------
# MERMAID PLAYBOOK GENERATOR (NEW)
# -------------------------------------------------
def generate_mermaid_diagram(blocks):
    lines = []
    lines.append("flowchart LR")

    # Core blocks
    for i, block in enumerate(blocks):
        node_id = f"B{i}"
        label = block["block_name"].replace("_", " ")
        lines.append(f'{node_id}["{label}"]')

        if i > 0:
            lines.append(f"B{i-1} --> {node_id}")

    # Decision block
    decision_id = "D1"
    lines.append(f'{decision_id}{{"Threat Confidence?"}}')
    lines.append(f"B{len(blocks)-1} --> {decision_id}")

    # High confidence path
    lines.append('HC["Auto Containment"]')
    lines.append('HC2["Disable / Block Entity"]')
    lines.append('HC3["Preserve Evidence"]')
    lines.append('HC4["Notify L2 / IR"]')

    lines.append(f'{decision_id} -->|High| HC')
    lines.append("HC --> HC2")
    lines.append("HC2 --> HC3")
    lines.append("HC3 --> HC4")

    # Low / Medium confidence path
    lines.append('LC["Manual Review"]')
    lines.append('LC2["L1 Analysis"]')
    lines.append('LC3["Close or Escalate"]')

    lines.append(f'{decision_id} -->|Low / Medium| LC')
    lines.append("LC --> LC2")
    lines.append("LC2 --> LC3")

    return "\n".join(lines)

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

    st.success("Playbook generated")

    # -------------------------------------------------
    # TEXTUAL PLAYBOOK STEPS
    # -------------------------------------------------
    st.header("🧩 Playbook Steps")
    for i, block in enumerate(blocks, start=1):
        with st.expander(f"Step {i}: {block['block_name']}"):
            st.markdown(f"**Purpose:** {block['purpose']}")
            st.markdown(f"**Inputs:** {', '.join(block['inputs'])}")
            st.markdown(f"**Outputs:** {', '.join(block['outputs'])}")
            st.markdown(f"**SLA Impact:** {block['sla_impact']}")
            st.markdown(f"**Analyst Notes:** {block['analyst_notes']}")

    # -------------------------------------------------
    # WORKFLOW SUMMARY (TECHNICAL STEPS)
    # -------------------------------------------------
    st.header("📌 Workflow Summary (Technical Steps)")
    workflow_steps = generate_workflow_steps(blocks)
    for step in workflow_steps:
        st.markdown(step)

    # -------------------------------------------------
    # SOAR PLAYBOOK WORKFLOW (DYNAMIC MERMAID)
    # -------------------------------------------------
    st.header("🔗 SOAR Playbook Workflow")

    mermaid_code = generate_mermaid_diagram(blocks)

    st.markdown(
        f"""
        ```mermaid
        {mermaid_code}
        ```
        """
    )

    # -------------------------------------------------
    # DOCUMENTATION
    # -------------------------------------------------
    st.header("📄 Playbook Documentation")
    st.markdown(documentation)
