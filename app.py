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
st.caption("Built by Srinivas")

# -------------------------------------------------
# SESSION STATE INIT
# -------------------------------------------------
defaults = {
    "blocks": None,
    "documentation": None,
    "diagram_code": None,
    "irp_summary": None,
    "generated": False,
    "error": None,
}

for k, v in defaults.items():
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
def build_playbook_prompt(text: str, mode: str) -> str:
    context = (
        "You are given a SOAR use case description."
        if mode == "Use Case"
        else "You are given an Incident Response Procedure. Convert it into SOAR playbook logic."
    )

    return f"""
Return ONLY valid JSON.
No markdown. No backticks.

{context}

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

def build_irp_extraction_prompt(raw_text: str) -> str:
    return f"""
Extract ONLY actionable incident response steps from the following IRP.

Ignore:
- policy language
- legal text
- background explanation

Return a concise analyst-ready response flow.

Text:
{raw_text}
"""

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def safe_parse_json(text: str):
    try:
        cleaned = re.sub(r"```json|```", "", text).strip()
        data = json.loads(cleaned)
        if not isinstance(data, dict) or "blocks" not in data:
            raise ValueError("Missing 'blocks' key")
        return data, None
    except Exception as e:
        return None, str(e)

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text_from_txt(file):
    return StringIO(file.getvalue().decode("utf-8")).read()

# -------------------------------------------------
# DOCUMENTATION BUILDER
# -------------------------------------------------
def build_full_documentation(blocks):
    sections = []
    sections.append("SOAR PLAYBOOK DOCUMENTATION\n")
    sections.append("1. Overview\nThis document defines an automated SOAR response workflow.\n")

    sections.append("2. Workflow Steps\n")
    for i, b in enumerate(blocks, start=1):
        sections.append(
            f"Step {i}: {b['block_name']}\n"
            f"Purpose: {b['purpose']}\n"
            f"Inputs: {', '.join(b['inputs'])}\n"
            f"Outputs: {', '.join(b['outputs'])}\n"
            f"SLA Impact: {b['sla_impact']}\n"
            f"Failure Handling: {b['failure_handling']}\n"
            f"Analyst Notes: {b['analyst_notes']}\n"
        )

    sections.append("3. Decision Logic & Escalation\nHigh confidence incidents are auto-contained.")
    return "\n\n".join(sections)

# -------------------------------------------------
# MERMAID
# -------------------------------------------------
def generate_mermaid_diagram(blocks):
    lines = ["flowchart LR"]
    for i, b in enumerate(blocks):
        lines.append(f'B{i}["{b["block_name"]}"]:::step')
        if i > 0:
            lines.append(f'B{i-1} --> B{i}')

    lines.append("classDef step fill:#2563eb,color:#fff,stroke:#1e3a8a,stroke-width:2px")
    return "\n".join(lines)

def render_mermaid(code):
    html = f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
      mermaid.initialize({{ startOnLoad:true }});
      function downloadSVG() {{
        const svg = document.querySelector(".mermaid svg");
        const serializer = new XMLSerializer();
        const source = serializer.serializeToString(svg);
        const blob = new Blob([source], {{ type: "image/svg+xml" }});
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "soar_workflow.svg";
        a.click();
      }}
    </script>
    <button onclick="downloadSVG()">⬇️ Download Workflow (SVG)</button>
    <div class="mermaid">{code}</div>
    """
    components.html(html, height=600, scrolling=True)

# -------------------------------------------------
# PDF
# -------------------------------------------------
def generate_doc_pdf(text: str):
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

mode = st.radio("Input Type", ["Use Case", "IRP (Document Upload)"], horizontal=True)
input_text = ""

if mode == "IRP (Document Upload)":
    uploaded = st.file_uploader("Upload IRP", type=["pdf", "docx", "txt"])
    if uploaded:
        with st.spinner("Reading IRP..."):
            raw = (
                extract_text_from_pdf(uploaded)
                if uploaded.type == "application/pdf"
                else extract_text_from_docx(uploaded)
                if uploaded.type.endswith("document")
                else extract_text_from_txt(uploaded)
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
    st.session_state.error = None
    with st.spinner("Generating playbook..."):
        resp = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=build_playbook_prompt(input_text, mode)
        )

    data, err = safe_parse_json(resp.text)
    if err:
        st.session_state.error = "Model returned invalid output. Try again."
        st.session_state.generated = False
    else:
        st.session_state.blocks = data["blocks"]
        st.session_state.diagram_code = generate_mermaid_diagram(data["blocks"])
        st.session_state.documentation = build_full_documentation(data["blocks"])
        st.session_state.generated = True

# -------------------------------------------------
# OUTPUT
# -------------------------------------------------
if st.session_state.error:
    st.error(st.session_state.error)

if st.session_state.generated:
    st.success("Playbook generated")

    st.header("SOAR Workflow")
    render_mermaid(st.session_state.diagram_code)

    st.header("Playbook Documentation")
    with st.expander("View Documentation", expanded=True):
        st.markdown(st.session_state.documentation)

    st.download_button(
        "⬇️ Download Documentation (PDF)",
        generate_doc_pdf(st.session_state.documentation),
        "soar_playbook.pdf",
        mime="application/pdf"
    )
