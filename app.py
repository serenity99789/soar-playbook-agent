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
if "blocks" not in st.session_state:
    st.session_state.blocks = None
if "diagram_code" not in st.session_state:
    st.session_state.diagram_code = None
if "documentation" not in st.session_state:
    st.session_state.documentation = None
if "generated" not in st.session_state:
    st.session_state.generated = False

# -------------------------------------------------
# API CONFIG
# -------------------------------------------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("GEMINI_API_KEY not set")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# SAFE JSON EXTRACTION (PRODUCTION SAFE)
# -------------------------------------------------
def extract_json(text):
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                return None
        return None

# -------------------------------------------------
# PROMPTS
# -------------------------------------------------
def build_playbook_prompt(text, learning_level):
    return f"""
You are a senior SOAR engineer.

Return ONLY valid JSON.
No markdown. No explanations.

Generate a FULL multi-step SOAR playbook.

Schema:
{{
  "blocks": [
    {{
      "step": "",
      "block_name": "",
      "learning_explanation": "",
      "soc_role": "",
      "if_skipped": "",
      "siem_mapping": {{
        "detection_type": "",
        "log_sources": [],
        "mitre_technique": "",
        "automation_level": ""
      }}
    }}
  ]
}}

Learning depth: {learning_level}

Input:
{text}
"""

# -------------------------------------------------
# FILE HELPERS
# -------------------------------------------------
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join(p.extract_text() or "" for p in reader.pages)

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text_from_txt(file):
    return StringIO(file.getvalue().decode()).read()

# -------------------------------------------------
# MERMAID DIAGRAM
# -------------------------------------------------
def generate_mermaid(blocks):
    lines = ["flowchart LR"]

    for i, b in enumerate(blocks):
        lines.append(f'B{i}["{b["block_name"]}"]:::core')
        if i > 0:
            lines.append(f'B{i-1} --> B{i}')

    lines.append('D{"Threat Confidence?"}:::decision')
    lines.append(f'B{len(blocks)-1} --> D')

    lines += [
        'HC1["Auto Containment"]:::contain',
        'HC2["Disable / Block"]:::contain',
        'HC3["Preserve Evidence"]:::evidence',
        'HC4["Notify L2 / IR"]:::notify',
        'D -->|High| HC1',
        'HC1 --> HC2 --> HC3 --> HC4',
        'LC1["Manual Review"]:::manual',
        'LC2["L1 Analysis"]:::manual',
        'LC3["Close / Escalate"]:::notify',
        'D -->|Low / Medium| LC1',
        'LC1 --> LC2 --> LC3',
    ]

    lines += [
        "classDef core fill:#2563eb,color:#fff,stroke:#1e3a8a,stroke-width:2px",
        "classDef decision fill:#f59e0b,stroke:#b45309,stroke-width:3px",
        "classDef contain fill:#dc2626,color:#fff",
        "classDef evidence fill:#7c3aed,color:#fff",
        "classDef notify fill:#16a34a,color:#fff",
        "classDef manual fill:#6b7280,color:#fff",
    ]

    return "\n".join(lines)

def render_mermaid(code):
    html = f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
      mermaid.initialize({{ startOnLoad:true }});
      function downloadSVG() {{
        const svg = document.querySelector(".mermaid svg");
        const s = new XMLSerializer().serializeToString(svg);
        const b = new Blob([s], {{type:"image/svg+xml"}});
        const a = document.createElement("a");
        a.href = URL.createObjectURL(b);
        a.download = "soar_workflow.svg";
        a.click();
      }}
    </script>
    <button onclick="downloadSVG()">⬇️ Download Workflow (SVG)</button>
    <div class="mermaid">{code}</div>
    """
    components.html(html, height=650, scrolling=True)

# -------------------------------------------------
# PDF
# -------------------------------------------------
def generate_pdf(text):
    buf = BytesIO()
    styles = getSampleStyleSheet()
    body = ParagraphStyle("Body", parent=styles["Normal"], spaceAfter=12)
    story = []
    for p in text.split("\n\n"):
        story.append(Paragraph(p.replace("\n", "<br/>"), body))
        story.append(Spacer(1, 12))
    SimpleDocTemplate(buf).build(story)
    buf.seek(0)
    return buf.read()

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🛡️ SOAR Playbook Generator")

output_mode = st.radio("Output Mode", ["Learning Mode", "Deployment Mode"], horizontal=True)

learning_level = None
if output_mode == "Learning Mode":
    learning_level = st.radio("Learning Depth", ["Beginner", "Intermediate", "Advanced"], horizontal=True)

input_type = st.radio("Input Type", ["Use Case", "IRP (Document Upload)"], horizontal=True)

input_text = ""

if input_type == "IRP (Document Upload)":
    file = st.file_uploader("Upload IRP", type=["pdf", "docx", "txt"])
    if file:
        input_text = (
            extract_text_from_pdf(file)
            if file.type == "application/pdf"
            else extract_text_from_docx(file)
            if file.type.endswith("document")
            else extract_text_from_txt(file)
        )
else:
    input_text = st.text_area("Use Case", height=200)

# -------------------------------------------------
# GENERATE
# -------------------------------------------------
if st.button("Generate Playbook"):
    with st.spinner("Generating SOAR playbook..."):
        resp = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=build_playbook_prompt(input_text, learning_level)
        )

    data = extract_json(resp.text)

    if not data or "blocks" not in data:
        st.error("Model returned invalid output. Please click Generate again.")
        st.stop()

    st.session_state.blocks = data["blocks"]
    st.session_state.diagram_code = generate_mermaid(data["blocks"])
    st.session_state.generated = True

# -------------------------------------------------
# OUTPUT
# -------------------------------------------------
if st.session_state.generated:
    st.success("Playbook generated")

    if output_mode == "Learning Mode":
        st.header("📘 Block-Level Learning")
        for b in st.session_state.blocks:
            with st.expander(f'{b["step"]}: {b["block_name"]}'):
                st.markdown(f"**Why this step exists:** {b['learning_explanation']}")
                st.markdown(f"**SOC Role:** {b['soc_role']}")
                st.markdown(f"**If skipped:** {b['if_skipped']}")
                st.markdown("**SIEM → SOAR Mapping**")
                st.markdown(f"- Detection Type: {b['siem_mapping']['detection_type']}")
                st.markdown(f"- Log Sources: {', '.join(b['siem_mapping']['log_sources'])}")
                st.markdown(f"- MITRE: {b['siem_mapping']['mitre_technique']}")
                st.markdown(f"- Automation Level: {b['siem_mapping']['automation_level']}")

    st.header("SOAR Workflow")
    render_mermaid(st.session_state.diagram_code)
