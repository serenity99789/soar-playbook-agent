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
# SESSION STATE INIT (ANTI-RELOAD FIX)
# -------------------------------------------------
defaults = {
    "blocks": None,
    "documentation": None,
    "diagram_code": None,
    "irp_summary": None,
    "generated": False
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
    return f"""
Return ONLY valid JSON.
No markdown. No backticks.

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
Extract ONLY actionable SOAR-relevant content:
- detection steps
- decision logic
- containment actions
- escalation paths

Ignore policy, legal, and background sections.

Return a clean analyst-readable summary.

Text:
{raw_text}
"""

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def parse_model_output(text: str):
    cleaned = re.sub(r"```json|```", "", text).strip()
    return json.loads(cleaned)

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text_from_txt(file):
    return StringIO(file.getvalue().decode("utf-8")).read()

# -------------------------------------------------
# DOCUMENTATION BUILDER (KEY FIX)
# -------------------------------------------------
def build_full_documentation(blocks):
    sections = []

    sections.append("1. Playbook Overview\n"
                    "This SOAR playbook defines the automated and semi-automated response workflow "
                    "for the identified security use case, including enrichment, decision-making, "
                    "containment, and escalation activities.\n")

    sections.append("2. Scope and Trigger Conditions\n"
                    "This playbook is triggered by security detections originating from SIEM or "
                    "security monitoring platforms that indicate a potential security incident.\n")

    sections.append("3. Workflow Description")
    for i, b in enumerate(blocks, start=1):
        sections.append(
            f"Step {i}: {b['block_name']}\n"
            f"Purpose: {b['purpose']}\n"
            f"Inputs: {', '.join(b['inputs'])}\n"
            f"Outputs: {', '.join(b['outputs'])}\n"
        )

    sections.append("4. Decision Logic\n"
                    "Decision points within the workflow evaluate threat confidence, contextual risk, "
                    "and enrichment results to determine whether automated containment or manual review "
                    "is required.\n")

    sections.append("5. Containment and Escalation\n"
                    "High-confidence incidents trigger automated containment actions, while low or "
                    "medium confidence incidents are routed for analyst review and validation.\n")

    sections.append("6. SLA Impact and Failure Handling")
    for b in blocks:
        sections.append(
            f"{b['block_name']}:\n"
            f"SLA Impact: {b['sla_impact']}\n"
            f"Failure Handling: {b['failure_handling']}\n"
        )

    sections.append("7. Analyst Notes and Execution Guidance")
    for b in blocks:
        sections.append(f"{b['block_name']}: {b['analyst_notes']}")

    return "\n\n".join(sections)

# -------------------------------------------------
# MERMAID DIAGRAM
# -------------------------------------------------
def generate_mermaid_diagram(blocks):
    lines = ["flowchart LR"]
    for i, b in enumerate(blocks):
        lines.append(f'B{i}["{b["block_name"]}"]')
        if i > 0:
            lines.append(f'B{i-1} --> B{i}')
    return "\n".join(lines)

def render_mermaid(code):
    components.html(
        f"""
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <div class="mermaid">{code}</div>
        """,
        height=500,
        scrolling=True
    )

# -------------------------------------------------
# PDF GENERATOR
# -------------------------------------------------
def generate_doc_pdf(text: str) -> bytes:
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    body = ParagraphStyle("Body", parent=styles["Normal"], spaceAfter=12)

    story = []
    for para in text.split("\n\n"):
        story.append(Paragraph(para.replace("\n", "<br/>"), body))
        story.append(Spacer(1, 12))

    SimpleDocTemplate(buffer).build(story)
    buffer.seek(0)
    return buffer.read()

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🛡️ SOAR Playbook Generator")

mode = st.radio(
    "Input Type",
    ["Use Case", "IRP / SOP (Text)", "IRP (Document Upload)"],
    horizontal=True
)

input_text = ""

if mode == "IRP (Document Upload)":
    uploaded = st.file_uploader("Upload IRP (PDF / DOCX / TXT)", type=["pdf", "docx", "txt"])
    if uploaded:
        raw = (
            extract_text_from_pdf(uploaded)
            if uploaded.type == "application/pdf"
            else extract_text_from_docx(uploaded)
            if uploaded.type.endswith("document")
            else extract_text_from_txt(uploaded)
        )

        with st.spinner("Extracting IRP content..."):
            st.session_state.irp_summary = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=build_irp_extraction_prompt(raw)
            ).text

        input_text = st.session_state.irp_summary

else:
    input_text = st.text_area("Input", height=260)

# -------------------------------------------------
# GENERATE BUTTON (ANTI-RELOAD)
# -------------------------------------------------
generate_clicked = st.button(
    "Generate Playbook",
    disabled=st.session_state.generated
)

if generate_clicked:
    with st.spinner("Generating SOAR playbook..."):
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=build_playbook_prompt(
                input_text,
                "Use Case" if mode == "Use Case" else "IRP"
            )
        )

    data = parse_model_output(response.text)
    st.session_state.blocks = data["blocks"]
    st.session_state.diagram_code = generate_mermaid_diagram(data["blocks"])
    st.session_state.documentation = build_full_documentation(data["blocks"])
    st.session_state.generated = True

# -------------------------------------------------
# RENDER OUTPUT (NO RELOADS)
# -------------------------------------------------
if st.session_state.generated:
    st.success("Playbook generated")

    st.header("🧩 Playbook Steps")
    for i, b in enumerate(st.session_state.blocks, start=1):
        with st.expander(f"Step {i}: {b['block_name']}"):
            st.markdown(b["purpose"])

    st.header("🔗 SOAR Workflow")
    render_mermaid(st.session_state.diagram_code)

    st.header("📄 Playbook Documentation")
    with st.expander("View Full Documentation", expanded=True):
        st.markdown(st.session_state.documentation)

    pdf_bytes = generate_doc_pdf(st.session_state.documentation)
    st.download_button(
        "⬇️ Download Full Playbook Documentation (PDF)",
        pdf_bytes,
        "soar_playbook_documentation.pdf",
        mime="application/pdf"
    )
