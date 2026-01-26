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
state_defaults = {
    "blocks": None,
    "documentation": None,
    "diagram_code": None,
    "irp_summary": None,
    "generated": False,
}
for k, v in state_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -------------------------------------------------
# API CONFIG
# -------------------------------------------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("GEMINI_API_KEY not set")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# PROMPTS
# -------------------------------------------------
def build_playbook_prompt(text):
    return f"""
You are a senior SOAR engineer designing a SOC playbook.

Return ONLY valid JSON.
No markdown. No explanation text.

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
      "analyst_notes": "",
      "learning_explanation": "",
      "soc_role": "",
      "skip_impact": ""
    }}
  ]
}}

Input:
{text}
"""

def build_irp_extraction_prompt(raw):
    return f"""
Extract only actionable incident response steps.
Ignore policy, legal, and background text.

Return plain text.

Text:
{raw}
"""

# -------------------------------------------------
# SAFE JSON EXTRACTION
# -------------------------------------------------
def extract_json_safely(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
        raise ValueError("No valid JSON found")

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
# DOCUMENTATION
# -------------------------------------------------
def build_documentation(blocks):
    parts = ["SOAR PLAYBOOK DOCUMENTATION\n"]
    for i, b in enumerate(blocks, 1):
        parts.append(
            f"Step {i}: {b['block_name']}\n"
            f"Purpose: {b['purpose']}\n"
            f"Inputs: {', '.join(b['inputs'])}\n"
            f"Outputs: {', '.join(b['outputs'])}\n"
            f"SLA Impact: {b['sla_impact']}\n"
            f"Failure Handling: {b['failure_handling']}\n"
            f"Analyst Notes: {b['analyst_notes']}\n"
        )
    return "\n\n".join(parts)

# -------------------------------------------------
# MERMAID
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
mode = st.radio("Input Type", ["Use Case", "IRP (Document Upload)"], horizontal=True)

input_text = ""

if mode == "IRP (Document Upload)":
    file = st.file_uploader("Upload IRP", type=["pdf", "docx", "txt"])
    if file:
        with st.spinner("Reading IRP..."):
            raw = (
                extract_text_from_pdf(file)
                if file.type == "application/pdf"
                else extract_text_from_docx(file)
                if file.type.endswith("document")
                else extract_text_from_txt(file)
            )
        with st.spinner("Extracting actionable steps..."):
            st.session_state.irp_summary = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=build_irp_extraction_prompt(raw)
            ).text
        with st.expander("Extracted IRP Summary", expanded=True):
            st.markdown(st.session_state.irp_summary)
        input_text = st.session_state.irp_summary
else:
    input_text = st.text_area("Use Case", height=240)

# -------------------------------------------------
# GENERATE
# -------------------------------------------------
if st.button("Generate Playbook"):
    with st.spinner("Generating playbook..."):
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=build_playbook_prompt(input_text)
        )

    try:
        data = extract_json_safely(response.text)
        st.session_state.blocks = data["blocks"]
        st.session_state.diagram_code = generate_mermaid(data["blocks"])
        st.session_state.documentation = build_documentation(data["blocks"])
        st.session_state.generated = True
    except:
        st.error("Model output could not be parsed. Try again.")

# -------------------------------------------------
# OUTPUT
# -------------------------------------------------
if st.session_state.generated:
    st.success("Playbook generated")

    if output_mode == "Learning Mode":
        st.header("📘 Block-Level Learning")
        for i, b in enumerate(st.session_state.blocks, 1):
            with st.expander(f"Step {i}: {b['block_name']}"):
                st.markdown(f"**Why this step exists:** {b.get('learning_explanation', 'This step provides necessary context and decision support in the SOAR workflow.')}")
                st.markdown(f"**SOC Role Involved:** {b.get('soc_role', 'Typically handled by L1/L2 analysts depending on automation maturity.')}")
                st.markdown(f"**If skipped:** {b.get('skip_impact', 'Skipping this step may reduce confidence, increase false positives, or delay response.')}")


    st.header("SOAR Workflow")
    render_mermaid(st.session_state.diagram_code)

    st.header("Playbook Documentation")
    with st.expander("View Documentation", expanded=True):
        st.markdown(st.session_state.documentation)

    st.download_button(
        "⬇️ Download Documentation (PDF)",
        generate_pdf(st.session_state.documentation),
        "soar_playbook.pdf",
        mime="application/pdf"
    )
