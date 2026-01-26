import os
import json
import re
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from io import BytesIO, StringIO
from docx import Document
from PyPDF2 import PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="SOAR Playbook Generator", layout="wide")
st.caption("Built by Accenture")

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
defaults = {
    "blocks": None,
    "diagram": None,
    "doc": None,
    "generated": False,
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# -------------------------------------------------
# API
# -------------------------------------------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("GEMINI_API_KEY not set")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# PROMPTS
# -------------------------------------------------
def playbook_prompt(text):
    return f"""
Return ONLY valid JSON.

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
  ]
}}

Input:
{text}
"""

# -------------------------------------------------
# JSON SAFETY
# -------------------------------------------------
def extract_json(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{{[\s\S]*\}}", text)
        if match:
            return json.loads(match.group())
        raise ValueError("Invalid JSON")

# -------------------------------------------------
# FILE HELPERS
# -------------------------------------------------
def read_pdf(f): return "\n".join(p.extract_text() or "" for p in PdfReader(f).pages)
def read_docx(f): return "\n".join(p.text for p in Document(f).paragraphs)
def read_txt(f): return StringIO(f.getvalue().decode()).read()

# -------------------------------------------------
# MERMAID
# -------------------------------------------------
def mermaid(blocks):
    lines = ["flowchart LR"]
    for i, b in enumerate(blocks):
        lines.append(f'B{i}["{b["block_name"]}"]:::core')
        if i > 0:
            lines.append(f"B{i-1} --> B{i}")

    lines += [
        'D{"Threat Confidence?"}:::decision',
        f'B{len(blocks)-1} --> D',
        'D -->|High| HC1["Auto Containment"]:::contain --> HC2["Disable / Block"] --> HC3["Preserve Evidence"] --> HC4["Notify L2 / IR"]',
        'D -->|Low / Medium| LC1["Manual Review"]:::manual --> LC2["L1 Analysis"] --> LC3["Close / Escalate"]'
    ]

    lines += [
        "classDef core fill:#2563eb,color:#fff",
        "classDef decision fill:#f59e0b",
        "classDef contain fill:#dc2626,color:#fff",
        "classDef manual fill:#6b7280,color:#fff"
    ]
    return "\n".join(lines)

def render_mermaid(code):
    components.html(f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{startOnLoad:true}});</script>
    <div class="mermaid">{code}</div>
    """, height=500)

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🛡️ SOAR Playbook Generator")

learning_level = st.radio(
    "Learning Depth",
    ["Beginner", "Intermediate"],
    horizontal=True
)

mode = st.radio("Input Type", ["Use Case", "IRP (Document Upload)"], horizontal=True)

input_text = ""
if mode == "IRP (Document Upload)":
    f = st.file_uploader("Upload IRP", ["pdf", "docx", "txt"])
    if f:
        input_text = read_pdf(f) if f.type == "application/pdf" else read_docx(f) if "doc" in f.type else read_txt(f)
else:
    input_text = st.text_area("Use Case", height=220)

# -------------------------------------------------
# GENERATE
# -------------------------------------------------
if st.button("Generate Playbook"):
    with st.spinner("Generating playbook..."):
        r = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=playbook_prompt(input_text)
        )
        data = extract_json(r.text)
        st.session_state.blocks = data["blocks"]
        st.session_state.diagram = mermaid(data["blocks"])
        st.session_state.generated = True

# -------------------------------------------------
# OUTPUT
# -------------------------------------------------
if st.session_state.generated:
    st.success("Playbook generated")

    st.header("📘 Block-Level Learning")

    for i, b in enumerate(st.session_state.blocks, 1):
        with st.expander(f"Step {i}: {b['block_name']}"):
            if learning_level == "Beginner":
                st.markdown(f"""
**Why this step exists:**  
{b['purpose']}

**If skipped:**  
May increase false positives or delay response.
""")
            else:
                st.markdown(f"""
**Operational Purpose:**  
{b['purpose']}

**SLA Impact:**  
{b['sla_impact']}

**Failure Handling:**  
{b['failure_handling']}

**SOC Analyst Notes:**  
{b['analyst_notes']}
""")

    st.header("🔁 SOAR Workflow")
    render_mermaid(st.session_state.diagram)
