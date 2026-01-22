import os
import json
import re
import streamlit as st
import streamlit.components.v1 as components
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
# MERMAID PLAYBOOK GENERATOR
# -------------------------------------------------
def generate_mermaid_diagram(blocks):
    lines = []
    lines.append("flowchart LR")

    for i, block in enumerate(blocks):
        label = block["block_name"].replace('"', "").replace("_", " ")
        lines.append(f'B{i}["{label}"]')
        if i > 0:
            lines.append(f'B{i-1} --> B{i}')

    lines.append('D1{"Threat Confidence?"}')
    lines.append(f'B{len(blocks)-1} --> D1')

    lines.append('HC["Auto Containment"]')
    lines.append('HC2["Disable / Block Entity"]')
    lines.append('HC3["Preserve Evidence"]')
    lines.append('HC4["Notify L2 / IR"]')

    lines.append('D1 -->|High| HC')
    lines.append('HC --> HC2 --> HC3 --> HC4')

    lines.append('LC["Manual Review"]')
    lines.append('LC2["L1 Analysis"]')
    lines.append('LC3["Close or Escalate"]')

    lines.append('D1 -->|Low / Medium| LC')
    lines.append('LC --> LC2 --> LC3')

    return "\n".join(lines)

# -------------------------------------------------
# MERMAID RENDERER (CRITICAL FIX)
# -------------------------------------------------
def render_mermaid(mermaid_code):
    html = f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
      mermaid.initialize({{
        startOnLoad: true,
        theme: "default",
        flowchart: {{
          curve: "basis",
          nodeSpacing: 50,
          rankSpacing: 70
        }}
      }});
    </script>

    <div class="mermaid">
    {mermaid_code}
    </div>
    """
    components.html(html, height=600, scrolling=True)

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
    # WORKFLOW SUMMARY
    # -------------------------------------------------
    st.header("📌 Workflow Summary (Technical Steps)")
    for step in generate_workflow_steps(blocks):
        st.markdown(step)

    # -------------------------------------------------
    # ACTUAL SOAR PLAYBOOK DIAGRAM (FIXED)
    # -------------------------------------------------
    st.header("🔗 SOAR Playbook Workflow")

    mermaid_code = generate_mermaid_diagram(blocks)
    render_mermaid(mermaid_code)

    # -------------------------------------------------
    # DOCUMENTATION
    # -------------------------------------------------
    st.header("📄 Playbook Documentation")
    st.markdown(documentation)
