import os
import json
import re
import streamlit as st
from google import genai
from graphviz import Digraph

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
# HELPERS
# -------------------------------------------------
def build_prompt(use_case: str) -> str:
    return f"""
You are a SOAR playbook generation engine.

Return STRICT JSON only. No explanations, no markdown.

JSON schema:
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
    match = re.search(r"\{{.*\}}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except Exception:
        return None

def derive_confidence(blocks):
    score = 0
    names = " ".join(b["block_name"].lower() for b in blocks)

    if "trigger" in names:
        score += 1
    if "enrich" in names or "context" in names:
        score += 1
    if "contain" in names or "reset" in names:
        score += 1

    if score >= 3:
        return "HIGH", "Automated containment recommended"
    elif score == 2:
        return "MEDIUM", "Analyst validation recommended"
    else:
        return "LOW", "Monitor only"

def build_flowchart(blocks):
    dot = Digraph(comment="SOAR Playbook Flow", graph_attr={"rankdir": "TB"})

    for i, block in enumerate(blocks):
        dot.node(
            str(i),
            f"{block['block_name']}\n\n{block['purpose']}",
            shape="box"
        )

        if i > 0:
            dot.edge(str(i - 1), str(i))

    return dot

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

    with st.spinner("Generating SOAR playbook..."):
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
    # PLAYBOOK BLOCKS (TEXT)
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
    # GRAPHICAL SOAR FLOW (THIS IS THE NEW PART)
    # -------------------------------------------------
    st.header("🧭 SOAR Execution Flow (Graphical)")

    flowchart = build_flowchart(blocks)
    st.graphviz_chart(flowchart)

    # -------------------------------------------------
    # DECISION SUMMARY
    # -------------------------------------------------
    st.header("🧠 SOC Decision Summary")

    confidence, recommendation = derive_confidence(blocks)
    st.markdown(f"**Confidence Level:** `{confidence}`")
    st.markdown(f"**Recommended Action:** `{recommendation}`")

    # -------------------------------------------------
    # DOCUMENTATION
    # -------------------------------------------------
    st.header("📄 Playbook Documentation")
    st.markdown(documentation or "_No documentation returned_")
