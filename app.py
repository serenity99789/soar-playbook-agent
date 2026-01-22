import os
import json
import re
import unicodedata
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from io import BytesIO, StringIO
from docx import Document
from PyPDF2 import PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="SOAR Playbook Generator", layout="wide")
st.caption("Built by Srinivas")

# -------------------------------------------------
# API CONFIG
# -------------------------------------------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("GEMINI_API_KEY not set")
    st.stop()

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# TEXT SANITIZATION (CRITICAL FIX)
# -------------------------------------------------
def clean_text(text: str) -> str:
    if not text:
        return ""

    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)

    # Remove null bytes
    text = text.replace("\x00", "")

    # Remove non-printable/control chars
    text = "".join(ch for ch in text if ch.isprintable())

    # Collapse excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()

# -------------------------------------------------
# PROMPTS
# -------------------------------------------------
def build_irp_maker_prompt(clean_irp: str) -> str:
    return f"""
You are an IRP ingestion agent.

Your job:
- Read the Incident Response Procedure below
- Extract ONLY operational response logic:
  - detection & intake
  - triage steps
  - decision points
  - containment actions
  - escalation paths
  - evidence handling
- Ignore:
  - policy text
  - legal language
  - roles & responsibilities
  - repetition and fluff

Return a compact, analyst-readable IRP summary.
No markdown. Plain text only.

IRP:
{clean_irp}
"""

def build_playbook_prompt(text: str, mode: str) -> str:
    context = (
        "You are given a SOAR use case description."
        if mode == "Use Case"
        else "You are given a normalized Incident Response Procedure."
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
  ],
  "documentation": ""
}}

Input:
{text}
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
    return StringIO(file.getvalue().decode("utf-8", errors="ignore")).read()

def generate_workflow_steps(blocks):
    return [
        f"{i}. {b['block_name']} – {b['purpose']}"
        for i, b in enumerate(blocks, start=1)
    ]

# -------------------------------------------------
# MERMAID DIAGRAM
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
    html = f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
      mermaid.initialize({{ startOnLoad:true, theme:"base" }});
    </script>
    <div class="mermaid">{code}</div>
    """
    components.html(html, height=550, scrolling=True)

# -------------------------------------------------
# PDF GENERATOR
# -------------------------------------------------
def generate_doc_pdf(text: str) -> bytes:
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    story = [Paragraph(p, styles["Normal"]) for p in text.split("\n")]
    SimpleDocTemplate(buffer).build(story)
    buffer.seek(0)
    return buffer.read()

# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("🛡️ SOAR Playbook Generator")

mode = st.radio(
    "Input Type",
    ["Use Case", "IRP (Document Upload)"],
    horizontal=True
)

input_text = ""

# ---------- IRP DOCUMENT PIPELINE ----------
if mode == "IRP (Document Upload)":
    uploaded = st.file_uploader("Upload IRP (PDF / DOCX / TXT)", type=["pdf", "docx", "txt"])

    if uploaded:
        with st.spinner("📥 Extracting raw text..."):
            raw = (
                extract_text_from_pdf(uploaded)
                if uploaded.type == "application/pdf"
                else extract_text_from_docx(uploaded)
                if uploaded.type.endswith("document")
                else extract_text_from_txt(uploaded)
            )

        clean_irp = clean_text(raw)

        if not clean_irp:
            st.error("Could not extract readable text from this document.")
            st.stop()

        with st.spinner("🧠 IRP Maker Agent analyzing document..."):
            irp_summary = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=build_irp_maker_prompt(clean_irp)
            ).text

        irp_summary = clean_text(irp_summary)

        with st.expander("📄 Normalized IRP (Agent Output)", expanded=False):
            st.markdown(irp_summary)

        input_text = irp_summary

else:
    input_text = st.text_area(
        "SOAR Use Case",
        height=260,
        placeholder="Account Compromise – Brute Force Success"
    )

# ---------- PLAYBOOK GENERATION ----------
if st.button("Generate Playbook"):

    if not input_text.strip():
        st.warning("Please provide input.")
        st.stop()

    with st.spinner("⚙️ Generating SOAR playbook..."):
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=build_playbook_prompt(
                input_text,
                "Use Case" if mode == "Use Case" else "IRP"
            )
        )

    data = parse_model_output(response.text)
    blocks = data["blocks"]
    documentation = data["documentation"]

    st.success("Playbook generated")

    st.header("🧩 Playbook Steps")
    for i, b in enumerate(blocks, start=1):
        with st.expander(f"Step {i}: {b['block_name']}"):
            st.markdown(b["purpose"])

    st.header("📌 Workflow Summary")
    for step in generate_workflow_steps(blocks):
        st.markdown(step)

    st.header("🔗 SOAR Playbook Workflow")
    render_mermaid(generate_mermaid_diagram(blocks))

    st.header("📄 Playbook Documentation (Detailed)")
    with st.expander("View Documentation", expanded=True):
        st.markdown(
            f"<div style='font-size:16px;line-height:1.6'>{documentation}</div>",
            unsafe_allow_html=True
        )

    pdf_bytes = generate_doc_pdf(documentation)
    st.download_button(
        "⬇️ Download Playbook Documentation (PDF)",
        data=pdf_bytes,
        file_name="soar_playbook_documentation.pdf",
        mime="application/pdf"
    )
