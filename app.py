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
        if "blocks" not in data:
            raise ValueError("Missing blocks")
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
# DOCUMENTATION
# -------------------------------------------------
def build_full_documentation(blocks):
    parts = []
    parts.append("SOAR PLAYBOOK DOCUMENTATION\n")
    parts.append("1. Overview\nThis document defines an automated SOAR incident response workflow.\n")

    parts.append("2. Workflow Steps\n")
    for i, b in enumerate(blocks, start=1):
        parts.append(
            f"Step {i}: {b['block_name']}\n"
            f"Purpose: {b['purpose']}\n"
            f"Inputs: {', '.join(b['inputs'])}\n"
            f"Outputs: {', '.join(b['outputs'])}\n"
            f"SLA Impact: {b['sla_impact']}\n"
            f"Failure Handling: {b['failure_handling']}\n"
            f"Analyst Notes: {b['analyst_notes']}\n"
        )

    parts.append("3. Decision & Escalation\nHigh confidence incidents are auto-contained.\n")
    return "\n\n".join(parts)

# -------------------------------------------------
# MERMAID DIAGRAM (FULL SOAR STYLE)
# -------------------------------------------------
def generate_mermaid_diagram(blocks):
    lines = ["flowchart LR"]

    # Main flow
    for i, b in enumerate(blocks):
        label = b["block_name"].replace("_", " ")
        lines.append(f'B{i}["{label}"]:::core')
        if i > 0:
            lines.append(f'B{i-1} --> B{i}')

    # Decision
    lines.append('D1{"Threat Confidence?"}:::decision')
    lines.append(f'B{len(blocks)-1} --> D1')

    # High confidence branch
    lines.append('HC1["Auto Containment"]:::contain')
    lines.append('HC2["Disable / Block Entity"]:::contain')
    lines.append('HC3["Preserve Evidence"]:::evidence')
    lines.append('HC4["Notify L2 / IR"]:::notify')

    lines.append('D1 -->|High| HC1')
    lines.append('HC1 --> HC2 --> HC3 --> HC4')

    # Low / Medium branch
    lines.append('LC1["Manual Review"]:::manual')
    lines.append('LC2["L1 Analysis"]:::manual')
    lines.append('LC3["Close or Escalate"]:::notify')

    lines.append('D1 -->|Low / Medium| LC1')
    lines.append('LC1 --> LC2 --> LC3')

    # Styles
    lines.append("classDef core fill:#2563eb,color:#fff,stroke:#1e3a8a,stroke-width:2px")
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

    <button onclick="downloadSVG()" style="margin-bottom:10px;">
        ⬇️ Download Workflow (SVG)
    </button>

    <div class="mermaid">{code}</div>
    """
    components.html(html, height=650, scrolling=True)

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
        with st.spinner("📥 Reading IRP..."):
            raw = (
                extract_text_from_pdf(uploaded)
                if uploaded.type == "application/pdf"
                else extract_text_from_docx(uploaded)
                if uploaded.type.endswith("document")
                else extract_text_from_txt(uploaded)
            )

        with st.spinner("🧠 Extracting actionable steps..."):
            st.session_state.irp_summary = client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=build_irp_extraction_prompt(raw)
            ).text

        with st.expander("📄 Extracted IRP Summary (Used as Input)", expanded=True):
            st.markdown(st.session_state.irp_summary)

        input_text = st.session_state.irp_summary
else:
    input_text = st.text_area("Use Case", height=240)

if st.button("Generate Playbook"):
    with st.spinner("⚙️ Generating SOAR playbook logic..."):
        resp = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=build_playbook_prompt(input_text, mode)
        )

    data, err = safe_parse_json(resp.text)
    if err:
        st.error("Model returned invalid output. Try again.")
    else:
        st.session_state.blocks = data["blocks"]
        st.session_state.diagram_code = generate_mermaid_diagram(data["blocks"])
        st.session_state.documentation = build_full_documentation(data["blocks"])
        st.session_state.generated = True

if st.session_state.generated:
    st.success("Playbook generated")

    st.header("🔗 SOAR Workflow")
    render_mermaid(st.session_state.diagram_code)

    st.header("📄 Playbook Documentation")
    with st.expander("View Documentation", expanded=True):
        st.markdown(st.session_state.documentation)

    st.download_button(
        "⬇️ Download Documentation (PDF)",
        generate_doc_pdf(st.session_state.documentation),
        "soar_playbook.pdf",
        mime="application/pdf"
    )
