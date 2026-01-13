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
    st.error("GEMINI_API_KEY not set")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# PROMPT
# -------------------------------------------------
def build_prompt(use_case: str) -> str:
    return f"""
Return STRICT JSON only.

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
# PARSERS
# -------------------------------------------------
def extract_blocks(text):
    match = re.search(r'\{{.*\}}', text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except Exception:
        return None

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🛡️ SOAR Playbook Generator")

use_case = st.text_area("SOAR Use Case Description", height=220)
generate = st.button("Generate Playbook")

if not generate:
    st.stop()

# -------------------------------------------------
# GENERATE
# -------------------------------------------------
with st.spinner("Generating playbook..."):
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=build_prompt(use_case)
    )
    raw = response.text

data = extract_blocks(raw)
if not data:
    st.error("Model did not return valid JSON")
    st.code(raw)
    st.stop()

blocks = data["blocks"]
documentation = data["documentation"]

# -------------------------------------------------
# TEXT BLOCKS
# -------------------------------------------------
st.success("Playbook generated successfully")

st.header("🧩 Playbook Blocks")
for i, b in enumerate(blocks, 1):
    with st.expander(f"Block {i}: {b['block_name']}"):
        st.write(b)

# -------------------------------------------------
# GRAPHICAL FLOW (REAL RENDER)
# -------------------------------------------------
st.header("🔗 SOAR Flow (Graphical)")

flow_html = """
<div style="display:flex; flex-direction:column; align-items:center; gap:20px">

<div style="background:#0f766e;color:white;padding:14px 22px;border-radius:14px;font-weight:600">
Trigger: Account Compromise Alert
</div>

<div style="font-size:28px">↓</div>

<div style="background:#15803d;color:white;padding:14px 22px;border-radius:14px;font-weight:600">
Enrichment: Azure AD + IP Reputation
</div>

<div style="font-size:28px">↓</div>

<div style="background:#1e293b;color:white;padding:14px 22px;border-radius:14px;font-weight:600">
Validation: Sign-in + EDR + Firewall Logs
</div>

<div style="font-size:28px">↓</div>

<div style="background:#d97706;color:white;padding:14px 22px;border-radius:14px;font-weight:600">
Decision: Compromise Confidence?
</div>

<div style="display:flex; gap:80px; margin-top:10px">

  <div style="display:flex; flex-direction:column; align-items:center; gap:10px">
    <div style="font-size:24px">↙</div>
    <div style="background:#b91c1c;color:white;padding:14px 22px;border-radius:14px;font-weight:600">
    HIGH Confidence → Containment
    </div>
    <div style="background:#7f1d1d;color:white;padding:12px 18px;border-radius:12px">
    Disable User · Block IP · Reset Credentials
    </div>
  </div>

  <div style="display:flex; flex-direction:column; align-items:center; gap:10px">
    <div style="font-size:24px">↘</div>
    <div style="background:#2563eb;color:white;padding:14px 22px;border-radius:14px;font-weight:600">
    MEDIUM / LOW → Analyst Review
    </div>
    <div style="background:#1e40af;color:white;padding:12px 18px;border-radius:12px">
    Assign L2 Task · Add Context
    </div>
  </div>

</div>

<div style="font-size:28px;margin-top:10px">↓</div>

<div style="background:#334155;color:white;padding:14px 22px;border-radius:14px;font-weight:600">
Preserve Evidence · Notify SOC · Update Incident
</div>

</div>
"""

st.markdown(flow_html, unsafe_allow_html=True)

# -------------------------------------------------
# DOCUMENTATION
# -------------------------------------------------
st.header("📄 Playbook Documentation")
st.write(documentation)
