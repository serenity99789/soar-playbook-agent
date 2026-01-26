import os
import json
import re
import streamlit as st
import streamlit.components.v1 as components
from google import genai

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide"
)

st.caption("Built by Accenture")

st.title("📘 SOAR Learning Platform")

st.info(
    "This section is designed to teach how SIEM detections translate into SOAR workflows, "
    "why each response step exists, and how SOC teams reason during incidents."
)

# -------------------------------------------------
# API CONFIG
# -------------------------------------------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("GEMINI_API_KEY not set")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# UI — LEARNING CONTROLS
# -------------------------------------------------
learning_depth = st.radio(
    "Learning Depth",
    ["Beginner", "Intermediate", "Advanced"],
    horizontal=True
)

use_case = st.text_area(
    "Describe the alert raised by SIEM",
    height=180,
    placeholder="Example: Multiple failed login attempts from a single external IP..."
)

generate = st.button("Generate Learning Playbook")

# -------------------------------------------------
# PROMPT
# -------------------------------------------------
def learning_prompt(text, level):
    return f"""
You are a senior SOC architect and SOAR engineer.

Explain the SOAR workflow for the alert below.

Learning level: {level}

Return ONLY valid JSON.
No markdown. No explanations outside JSON.

Schema:
{{
  "steps": [
    {{
      "step_name": "",
      "why_this_exists": "",
      "soc_role": "",
      "if_skipped": "",
      "siem_mapping": {{
        "detection_type": "",
        "log_sources": [],
        "mitre_technique": ""
      }},
      "automation_level": ""
    }}
  ]
}}

Alert:
{text}
"""

# -------------------------------------------------
# SAFE JSON EXTRACTION
# -------------------------------------------------
def extract_json(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
        raise ValueError("Invalid JSON returned by model")

# -------------------------------------------------
# GENERATION
# -------------------------------------------------
if generate and use_case.strip():
    with st.spinner("Teaching SOAR logic like a senior analyst…"):
        resp = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=learning_prompt(use_case, learning_depth)
        )

    try:
        data = extract_json(resp.text)

        st.success("Learning playbook generated")

        st.header("🧠 Block-Level Learning")

        for i, step in enumerate(data["steps"], 1):
            with st.expander(f"Step {i}: {step['step_name']}"):
                st.markdown(f"**Why this step exists:** {step['why_this_exists']}")
                st.markdown(f"**SOC Role:** {step['soc_role']}")
                st.markdown(f"**If skipped:** {step['if_skipped']}")

                st.markdown("**🔎 SIEM → SOAR Mapping**")
                st.markdown(f"- Detection Type: {step['siem_mapping']['detection_type']}")
                st.markdown(f"- Log Sources: {', '.join(step['siem_mapping']['log_sources'])}")
                st.markdown(f"- MITRE Technique: {step['siem_mapping']['mitre_technique']}")

                st.markdown(f"**Automation Level:** {step['automation_level']}")

    except Exception as e:
        st.error("Learning output could not be parsed. Try again.")
