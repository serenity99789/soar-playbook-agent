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

# ---------------- PAGE ----------------
st.set_page_config(page_title="SOAR Playbook Generator", layout="wide")
st.caption("Built by Srinivas")

# ---------------- API -----------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("GEMINI_API_KEY not set")
    st.stop()

client = genai.Client(api_key=API_KEY)

# ---------------- CLEAN ----------------
def clean_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\x00", "")
    text = "".join(ch for ch in text if ch.isprintable())
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

# ---------------- PROMPTS ----------------
def build_irp_extractor_prompt(text: str) -> str:
    return f"""
Return ONLY valid JSON. No markdown.

Schema:
{{
  "detection": [],
  "triage": [],
  "decision_points": [],
  "containment": [],
  "escalation": [],
  "evidence": []
}}

Extract ONLY operational steps from the IRP below.

IRP:
{text}
"""

def build_playbook_prompt(text: str) -> str:
    return f"""
Return ONLY valid JSON. No markdown.

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

# ---------------- HELPERS ----------------
def parse_json(text):
    return json.loads(re.sub(r"```json|```", "", text).strip())

def extract_pdf(f):
    return "\n".join(p.extract_text() or "" for p in PdfReader(f).pages)

def extract_docx(f):
    return "\n".join(p.text for p in Document(f).paragraphs)

def extract_txt(f):
    return f.getvalue().decode("utf-8", errors="ignore")

def irp_json_to_text(j):
    out = []
    for k, v in j.items():
        if v:
            out.append(f"{k.replace('_',' ').title()}:")
            for i in v:
                out.append(f"- {i}")
            out.append("")
    return "\n".join(out)

# ---------------- DIAGRAM ----------------
def mermaid(blocks):
    m = ["flowchart LR"]
    for i, b in enumerate(blocks):
        m.append(f'B{i}["{b["block_name"]}"]')
        if i > 0:
            m.append(f'B{i-1} --> B{i}')
    return "\n".join(m)

def render(code):
    components.html(f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <div class="mermaid">{code}</div>
    """, height=500)

# ---------------- PDF ----------------
def make_pdf(text):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf)
    styles = getSampleStyleSheet()
    doc.build([Paragraph(p, styles["Normal"]) for p in text.split("\n")])
    buf.seek(0)
    return buf.read()

# ---------------- UI ----------------
st.title("🛡️ SOAR Playbook Generator")

uploaded = st.file_uploader("Upload IRP (PDF / DOCX / TXT)", type=["pdf","docx","txt"])

irp_text = ""
if uploaded:
    with st.spinner("Reading IRP..."):
        raw = extract_pdf(uploaded) if uploaded.type=="application/pdf" else extract_docx(uploaded) if uploaded.type.endswith("document") else extract_txt(uploaded)
    raw = clean_text(raw)

    with st.spinner("Extracting operational logic..."):
        irp_json = parse_json(client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=build_irp_extractor_prompt(raw)
        ).text)

    irp_text = irp_json_to_text(irp_json)

    with st.expander("Normalized IRP"):
        st.text(irp_text)

if st.button("Generate Playbook") and irp_text:
    with st.spinner("Generating playbook..."):
        data = parse_json(client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=build_playbook_prompt(irp_text)
        ).text)

    st.success("Playbook generated")

    for i,b in enumerate(data["blocks"],1):
        with st.expander(f"Step {i}: {b['block_name']}"):
            st.markdown(b["purpose"])

    render(mermaid(data["blocks"]))

    pdf = make_pdf(data["documentation"])
    st.download_button("Download Documentation PDF", pdf, "playbook.pdf")
