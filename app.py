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
# WORKFLOW SUMMARY
# -------------------------------------------------
def generate_workflow_steps(blocks):
    steps = []
    for i, block in enumerate(blocks, start=1):
        steps.append(f"{i}. {block['block_name']} – {block['purpose']}")
    return steps

# -------------------------------------------------
# MERMAID PLAYBOOK (COLOR CODED)
# -------------------------------------------------
def generate_mermaid_diagram(blocks):
    lines = []
    lines.append("flowchart LR")

    # Block nodes
    for i, block in enumerate(blocks):
        label = block["block_name"].replace('"', "").replace("_", " ")
        lines.append(f'B{i}["{label}"]:::enrich')
        if i > 0:
            lines.append(f'B{i-1} --> B{i}')

    # Decision
    lines.append('D1{"Threat Confidence?"}:::decision')
    lines.append(f'B{len(blocks)-1} --> D1')

    # High confidence path
    lines.append('HC["Auto Containment"]:::contain')
    lines.append('HC2["Disable / Block Entity"]:::contain')
    lines.append('HC3["Preserve Evidence"]:::evidence')
    lines.append('HC4["Notify L2 / IR"]:::notify')

    lines.append('D1 -->|High| HC')
    lines.append('HC --> HC2 --> HC3 --> HC4')

    # Low / Medium confidence path
    lines.append('LC["Manual Review"]:::manual')
    lines.append('LC2["L1 Analysis"]:::manual')
    lines.append('LC3["Close or Escalate"]:::notify')

    lines.append('D1 -->|Low / Medium| LC')
    lines.append('LC --> LC2 --> LC3')

    # Styles
    lines.append("classDef enrich fill:#2563eb,color:#ffffff,stroke:#1e3a8a,stroke-width:2px")
    lines.append("classDef decision fill:#f59e0b,color:#000000,stroke:#b45309,stroke-width:3px")
    lines.append("classDef contain fill:#dc2626,color:#ffffff,stroke:#7f1d1d,stroke-width:3px")
    lines.append("classDef evidence fill:#7c3aed,color:#ffffff,stroke:#4c1d95,stroke-width:2px")
    lines.append("classDef notify fill:#16a34a,color:#ffffff,stroke:#14532d,stroke-width:2px")
    lines.append("classDef manual fill:#6b7280,color:#ffffff,stroke:#374151,stroke-width:2px")

    return "\n".join(lines)

# -------------------------------------------------
# MERMAID RENDERER
# -------------------------------------------------
def render_mermaid(mermaid_code):
    html = f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
      mermaid.initialize({{
        startOnLoad: true,
        theme: "base",
        flowchart: {{
          curve: "basis",
          nodeSpacing: 60,
          rankSpacing: 80
        }}
      }});
    </script>

    <div class="mermaid">
    {mermaid_code}
    </div>
    """
    components.html(html, height=650, scrolling=True)

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
    # TEXTUAL PLAYBOOK
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
    # COLORED SOAR PLAYBOOK DIAGRAM
    # -------------------------------------------------
    st.header("🔗 SOAR Playbook Workflow")
    render_mermaid(generate_mermaid_diagram(blocks))

    # -------------------------------------------------
    # DOCUMENTATION
    # -------------------------------------------------
    st.header("📄 Playbook Documentation")
    st.markdown(documentation)
