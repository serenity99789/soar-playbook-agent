# =================================================
# BOOTSTRAP IMPORT PATH (DO NOT REMOVE)
# =================================================
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.resolve()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# =================================================
# ORIGINAL CODE (UNCHANGED)
# =================================================
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
st.caption("Built by Accenture")

# -------------------------------------------------
# API CONFIG
# -------------------------------------------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("GEMINI_API_KEY not set")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# SAFE JSON EXTRACTION
# -------------------------------------------------
def extract_json(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("Invalid JSON")
        return json.loads(match.group())

# -------------------------------------------------
# PROMPT
# -------------------------------------------------
def build_prompt(use_case, depth):
    return f"""
You are a senior SOC SOAR architect.

Return ONLY valid JSON. No markdown. No explanation.

Schema:
{{
  "blocks": [
    {{
      "title": "",
      "why": "",
      "soc_role": "",
      "if_skipped": "",
      "decision_logic": "",
      "automation_risk": "",
      "human_takeover": ""
    }}
  ]
}}

Learning depth: {depth}

Use case:
{use_case}
"""

# -------------------------------------------------
# MERMAID
# -------------------------------------------------
def generate_mermaid(blocks):
    lines = ["flowchart LR"]
    for i, b in enumerate(blocks):
        lines.append(f'B{i}["{b["title"]}"]:::core')
        if i > 0:
            lines.append(f'B{i-1} --> B{i}')

    lines.append('D{"Threat Confidence?"}:::decision')
    lines.append(f'B{len(blocks)-1} --> D')

    lines += [
        'D -->|High| HC1["Auto Containment"]:::contain',
        'HC1 --> HC2["Disable / Block"]:::contain --> HC3["Preserve Evidence"]:::evidence --> HC4["Notify L2 / IR"]:::notify',
        'D -->|Low / Medium| LC1["Manual Review"]:::manual --> LC2["L1 Analysis"]:::manual --> LC3["Close / Escalate"]:::notify',
        "classDef core fill:#2563eb,color:#fff,stroke:#1e3a8a,stroke-width:2px",
        "classDef decision fill:#f59e0b,stroke:#b45309,stroke-width:3px",
        "classDef contain fill:#dc2626,color:#fff",
        "classDef evidence fill:#7c3aed,color:#fff",
        "classDef notify fill:#16a34a,color:#fff",
        "classDef manual fill:#6b7280,color:#fff",
    ]
    return "\n".join(lines)

def render_mermaid(code):
    components.html(f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{ startOnLoad:true }});</script>
    <div class="mermaid">{code}</div>
    """, height=600)

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🛡️ SOAR Playbook Generator")

output_mode = st.radio("Output Mode", ["Learning Mode", "Deployment Mode"], horizontal=True)
learning_depth = st.radio("Learning Depth", ["Beginner", "Intermediate", "Advanced"], horizontal=True)

use_case = st.text_area(
    "Use Case",
    height=200,
    placeholder="Describe the alert raised by SIEM..."
)

# -------------------------------------------------
# GENERATE
# -------------------------------------------------
if st.button("Generate Playbook"):
    with st.spinner("Generating SOAR intelligence..."):
        resp = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=build_prompt(use_case, learning_depth)
        )

    try:
        data = extract_json(resp.text)
        blocks = data["blocks"]
        st.success("Playbook generated")

        # -----------------------------
        # BLOCK-LEVEL LEARNING
        # -----------------------------
        st.header("📘 Block-Level Learning")

        for i, b in enumerate(blocks, 1):
            with st.expander(f"Step {i}: {b['title']}"):
                st.markdown(f"**Why this step exists:** {b['why']}")
                st.markdown(f"**SOC Role:** {b['soc_role']}")
                st.markdown(f"**If skipped:** {b['if_skipped']}")
                st.markdown("---")
                st.markdown(f"🧠 **Decision Logic:** {b['decision_logic']}")
                st.markdown(f"⚠️ **Automation Risk:** {b['automation_risk']}")
                st.markdown(f"👤 **Human Takeover:** {b['human_takeover']}")

        # -----------------------------
        # WORKFLOW
        # -----------------------------
        st.header("SOAR Workflow")
        render_mermaid(generate_mermaid(blocks))

    except Exception:
        st.error("Model output could not be parsed. Click Generate again.")
