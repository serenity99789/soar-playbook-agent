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
    st.error("GEMINI_API_KEY not set. Please configure it in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# PROMPT
# -------------------------------------------------
def build_prompt(use_case: str) -> str:
    return f"""
You are a SOAR Playbook Generation Engine.

You MUST return STRICT JSON only.
No markdown. No explanations. No prose.

The FIRST block MUST ALWAYS be a TRIGGER block.
The trigger must be derived from the use case text.

JSON schema (exact):

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
- Block 1 = Trigger
- Remaining blocks must follow SOAR logic
- Align with MITRE ATT&CK, NIST IR, SOC SOPs where relevant

Use case:
{use_case}
"""

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🛡️ SOAR Playbook Generator")

use_case_input = st.text_area(
    "SOAR Use Case Description",
    height=260,
    placeholder="Describe the security scenario that should trigger a SOAR playbook."
)

generate = st.button("Generate Playbook")

# -------------------------------------------------
# RUN
# -------------------------------------------------
if generate:
    if not use_case_input.strip():
        st.warning("Please enter a SOAR use case.")
        st.stop()

    with st.spinner("Generating SOAR playbook..."):
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=build_prompt(use_case_input),
        )

    try:
        data = json.loads(response.text)
        blocks = data.get("blocks", [])
        documentation = data.get("documentation", "")
    except Exception:
        st.error("AI did not return valid JSON.")
        st.text_area("Raw Output", response.text, height=300)
        st.stop()

    if not blocks:
        st.error("No playbook blocks returned.")
        st.stop()

    # -------------------------------------------------
    # BLOCKS VIEW
    # -------------------------------------------------
    st.success("Playbook generated successfully")

    st.header("🧩 Playbook Blocks")

    for idx, block in enumerate(blocks, start=1):
        with st.expander(f"Block {idx}: {block['block_name']}"):
            st.markdown(f"**Purpose:** {block['purpose']}")
            st.markdown(f"**Inputs:** {', '.join(block['inputs'])}")
            st.markdown(f"**Outputs:** {', '.join(block['outputs'])}")
            st.markdown(f"**Failure Handling:** {block['failure_handling']}")
            st.markdown(f"**SLA Impact:** {block['sla_impact']}")
            st.markdown(f"**Analyst Notes:** {block['analyst_notes']}")

    # -------------------------------------------------
    # FLOW VIEW (SOAR LOGIC)
    # -------------------------------------------------
    st.header("🧭 SOAR Playbook Flow")

    flow = " → ".join(b["block_name"].replace("_", " ") for b in blocks)
    st.code(flow)

    # -------------------------------------------------
    # DOCUMENTATION
    # -------------------------------------------------
    st.header("📄 Playbook Documentation")
    st.markdown(documentation or "_No documentation returned_")
