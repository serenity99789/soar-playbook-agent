import os
import json
import re
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

# ---------------- PROMPT ----------------
def build_playbook_prompt(text: str) -> str:
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
  ],
  "documentation": ""
}}

Input:
{text}
"""

# ---------------- HELPERS ----------------
def parse_json(text):
    cleaned = re.sub(r"```json|```", "", text).strip()
    return json.loads(cleaned)

def extract_pdf(f):
    return "\n".join(p.extract_text() or "" for p in PdfReader(f).pages)

def extract_docx(f):
    return "\n".join(p.text for p in Document(f).paragraphs)

def extract_txt(f):
    return f.getvalue().decode("utf-8", errors="ignore")

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

mode = st.radio(
    "Input Type",
    ["Use Case (Text)", "IRP (Paste Text)", "IRP (Upload – Preview Only)"],
    horizontal=True
)

input_text = ""

# ---------- USE CASE ----------
if mode == "Use Case (Text)":
    input_text = st.text_area(
        "SOAR Use Case",
        height=260,
        placeholder="Account Compromise – Brute Force Success"
    )

# ---------- IRP PASTE ----------
elif mode == "IRP (Paste Text)":
    input_text = st.text_area(
        "Paste IRP Text",
        height=260,
        placeholder="Paste IRP steps / procedures here"
    )

# ---------- IRP UPLOAD (SAFE MODE) ----------
else:
    uploaded = st.file_uploader("Upload IRP (PDF / DOCX / TXT)", type=["pdf","docx","txt"])
    if uploaded:
        raw = (
            extract_pdf(uploaded)
            if uploaded.type == "application/pdf"
            else extract_docx(uploaded)
            if uploaded.type.endswith("document")
            else extract_txt(uploaded)
        )

        with st.expander("Extracted IRP Text (Preview Only)"):
            st.text(raw)

        st.info("For now, copy relevant steps and paste them into IRP (Paste Text) mode.")

# ---------- GENERATE ----------
if st.button("Generate Playbook"):
    if not input_text.strip():
        st.warning("Please provide input.")
        st.stop()

    with st.spinner("Generating playbook..."):
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=build_playbook_prompt(input_text)
        )

    data = parse_json(response.text)

    st.success("Playbook generated")

    for i, b in enumerate(data["blocks"], start=1):
        with st.expander(f"Step {i}: {b['block_name']}"):
            st.markdown(b["purpose"])

    doc_pdf = make_pdf(data["documentation"])
    st.download_button("Download Documentation PDF", doc_pdf, "playbook.pdf")
