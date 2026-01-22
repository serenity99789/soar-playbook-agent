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
for key in [
    "blocks",
    "documentation",
    "diagram_code",
    "irp_summary",
    "generated"
]:
    if key not in st.session_state:
        st.session_state[key] = None

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
You are given an Incident Response Procedure document.

Extract ONLY:
- actionable response steps
- decision points
- escalation logic
- containment actions

Ignore policy, legal, and background text.

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
# DOCUMENTATION BUILDER
# -------------------------------------------------
def build_full_documentation(blocks):
    sections = []

    sections.append(
        "1. Playbook Overview\n"
        "This SOAR playbook defines the automated and semi-automated response workflow for the "
        "identified security incident, including enrichment, decision-making, containment, and escalation."
    )

    sections.append(
        "2. Scope and Trigger Conditions\n"
        "This playbook is triggered by security alerts originating from SIEM, EDR, or identity platforms "
        "indicating potential malicious activity."
    )

    sections.append("3. Workflow Description")
    for i, b in enumerate(blocks, start=1):
        sections.append(
            f"Step {i}: {b['block_name']}\n"
            f"Purpose: {b['purpose']}\n"
            f"Inputs: {', '.join(b['inputs'])}\n"
            f"Outputs: {', '.join(b['outputs'])}"
        )

    sections.append(
        "4. Decision Logic\n"
        "Threat confidence is evaluated using enrichment results and contextual indicators to determine "
        "automated containment versus manual analyst review."
    )

    sections.append("5. Containment and Escalation")
    for b in blocks:
        sections.append(
            f"{b['block_name']}:\n"
            f"SLA Impact: {b['sla_impact']}\n"
            f"Failure Handling: {b['failure_handling']}"
        )

    sections.append("6. Analyst Notes and Execution Guidance")
    for b in blocks:
        sections.append(f"{b['block_name']}: {b['analyst_notes']}")

    return "\n\n".join(sections)

# -------------------------------------------------
# MERMAID DIAGRAM (COLORED)
# -------------------------------------------------
def generate_mermaid_diagram(blocks):
    lines = ["flowchart LR"]

    for i, block in enumerate(blocks):
        label = block["block_name"].replace("_", " ")
        lines.append(f'B{i}["{label}"]:::enrich')
        if i > 0:
            lines.append(f'B{i-1} --> B{i}')

    lines.append('D1{"Threat Confidence?"}:::decision')
    lines.append(f'B{len(blocks)-1} --> D1')

    lines.append('HC["Auto Containment"]:::contain')
    lines.append('HC2["Disable / Block Entity"]:::contain')
    lines.append('HC3["Preserve Evidence"]:::evidence')
    lines.append('HC4["Notify L2 / IR"]:::notify')

    lines.append('D1 -->|High| HC')
    lines.append('HC --> HC2 --> HC3 --> HC4')

    lines.append('LC["Manual Review"]:::manual')
    lines.append('LC2["L1 Analysis"]:::manual')
    lines.append('LC3["Close or Escalate"]:::notify')

    lines.append('D1 -->|Low / Medium| LC')
    lines.append('LC --> LC2 --> LC3')

    lines.append("classDef enrich fill:#2563eb,color:#fff,stroke:#1e3a8a,stroke-width:2px")
    lines.append("classDef decision fill:#f59e0b,color:#000,stroke:#b45309,stroke-width:3px")
    lines.append("classDef contain fill:#dc2626,color:#fff,stroke:#7f1d1d,stroke-width:3px")
    lines.append("classDef evidence fill:#7c3aed,color:#fff,stroke:#4c1d95,stroke-width:2px")
    lines.append("classDef notify fill:#16a34a,color:#fff,stroke:#14532d,stroke-width:2px")
    lines.append("classDef manual fill:#6b7280,color:#fff,stroke:#374151,stroke-width:2px")

    return "\n".join(lines)

def render_mermaid(code):
    components.html(
        f"""
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
          mermaid.initialize({{ startOnLoad:true, theme:"base" }});
        </script>
        <div class="mermaid">{code}</div>
        """,
        height=550,
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

# ---------- IRP DOCUMENT UPLOAD ----------
if mode == "IRP (Document Upload)":
    uploaded = st.file_uploader("Upload IRP (PDF / DOCX / TXT)", type=["pdf", "docx", "txt"])

    if uploaded:
        with st.spinner("📥 Reading document..."):
            raw = (
                extract_text_from_pdf(uploaded)
                if uploaded.type == "application/pdf"
                else extract_text_from_docx(uploaded)
                if uploaded.type.endswith("document")
                else extract_text_from_txt(uploaded)
            )

        with st.spinner("🧠 Extracting actionable IRP content..."):
            st.session_state.irp_summary = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=build_irp_extraction_prompt(raw)
            ).text

        with st.expander("📄 Extracted IRP Summary (Used as Input)", expanded=True):
            st.markdown(st.session_state.irp_summary)

        input_text = st.session_state.irp_summary

else:
    input_text = st.text_area(
        "Input",
        height=260,
        placeholder="Account Compromise – Brute Force Success"
    )

# ---------- GENERATE ----------
if st.button("Generate Playbook", disabled=st.session_state.generated):
    with st.spinner("⚙️ Generating SOAR playbook logic..."):
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

# ---------- OUTPUT ----------
if st.session_state.generated:
    st.success("Playbook generated")

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
