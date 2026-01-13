import os
import json
import re
import streamlit as st
from google import genai

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Playbook Generator",
    layout="wide"
)

st.caption("Built by Srinivas")

# -------------------------------------------------
# API CONFIG
# -------------------------------------------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("GEMINI_API_KEY not set in Streamlit secrets")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# PROMPT
# -------------------------------------------------
def build_prompt(use_case: str) -> str:
    return f"""
You MUST return ONLY valid JSON.
Do NOT use markdown.
Do NOT wrap in ```json.
Do NOT add commentary.

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
# ROBUST JSON EXTRACTOR
# -------------------------------------------------
def extract_json(text: str):
    if not text:
        return None

    # Remove markdown code fences if present
    text = text.strip()
    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^```", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    # Extract JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🛡️ SOAR Playbook Generator")

use_case = st.text_area(
    "SOAR Use Case Description",
    height=240
)

generate = st.button("Generate Playbook")

if not generate:
    st.stop()

# -------------------------------------------------
# MODEL CALL
# -------------------------------------------------
with st.spinner("Generating SOAR playbook..."):
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=build_prompt(use_case)
    )
    raw_output = response.text

data = extract_json(raw_output)

if not data:
    st.error("Model returned output but JSON could not be parsed")
    st.code(raw_output)
    st.stop()

blocks = data.get("blocks", [])
documentation = data.get("documentation", "")

# -------------------------------------------------
# TEXT BLOCKS
# -------------------------------------------------
st.success("Playbook generated successfully")

st.header("🧩 Playbook Blocks")
for idx, block in enumerate(blocks, start=1):
    with st.expander(f"Block {idx}: {block['block_name']}"):
        st.json(block)

# -------------------------------------------------
# GRAPHICAL SOAR FLOW (NON-LINEAR)
# -------------------------------------------------
st.header("🔗 SOAR Flow (Graphical)")

flow_html = """
<div style="display:flex;flex-direction:column;align-items:center;gap:22px">

<div style="background:#0f766e;color:white;padding:14px 26px;border-radius:14px;font-weight:600">
Trigger: Brute Force Success Alert
</div>

<div style="font-size:28px">↓</div>

<div style="background:#15803d;color:white;padding:14px 26px;border-radius:14px;font-weight:600">
Enrichment: User + IP Context
</div>

<div style="font-size:28px">↓</div>

<div style="background:#1e293b;color:white;padding:14px 26px;border-radius:14px;font-weight:600">
Correlation: Azure AD · EDR · Firewall
</div>

<div style="font-size:28px">↓</div>

<div style="background:#d97706;color:white;padding:14px 26px;border-radius:14px;font-weight:600">
Decision: Compromise Confidence
</div>

<div style="display:flex;gap:90px;margin-top:10px">

  <div style="display:flex;flex-direction:column;align-items:center;gap:12px">
    <div style="font-size:24px">↙</div>
    <div style="background:#b91c1c;color:white;padding:14px 22px;border-radius:14px;font-weight:600">
      HIGH Confidence
    </div>
    <div style="background:#7f1d1d;color:white;padding:12px 18px;border-radius:12px">
      Disable User<br>Block IP<br>Revoke Sessions
    </div>
  </div>

  <div style="display:flex;flex-direction:column;align-items:center;gap:12px">
    <div style="font-size:24px">↘</div>
    <div style="background:#2563eb;color:white;padding:14px 22px;border-radius:14px;font-weight:600">
      MEDIUM / LOW
    </div>
    <div style="background:#1e40af;color:white;padding:12px 18px;border-radius:12px">
      L1/L2 Review<br>Manual Validation
    </div>
  </div>

</div>

<div style="font-size:28px">↓</div>

<div style="background:#334155;color:white;padding:14px 26px;border-radius:14px;font-weight:600">
Preserve Evidence · Create Incident · Notify SOC
</div>

</div>
"""

st.markdown(flow_html, unsafe_allow_html=True)

# -------------------------------------------------
# DOCUMENTATION
# -------------------------------------------------
st.header("📄 Playbook Documentation")
st.write(documentation)
