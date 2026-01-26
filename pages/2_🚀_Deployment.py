import streamlit as st
import streamlit.components.v1 as components
from typing import Optional

from core.playbook_engine import generate_playbook
from core.diagram_engine import build_soar_mermaid


# -------------------------------------------------
# Page Configuration
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Deployment Playbook",
    layout="wide"
)

st.title("🚀 SOAR Deployment Playbook")


# -------------------------------------------------
# Session State
# -------------------------------------------------
if "deployment_result" not in st.session_state:
    st.session_state.deployment_result = None


# -------------------------------------------------
# Helpers: File Text Extraction
# -------------------------------------------------
def extract_text_from_pdf(uploaded_file) -> str:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        return ""

    reader = PdfReader(uploaded_file)
    pages = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)

    return "\n".join(pages)


def extract_text_from_docx(uploaded_file) -> str:
    try:
        from docx import Document
    except ImportError:
        return ""

    document = Document(uploaded_file)
    return "\n".join(p.text for p in document.paragraphs if p.text.strip())


# -------------------------------------------------
# Input Source Selector
# -------------------------------------------------
st.subheader("Input Source")

input_mode = st.radio(
    label="Choose input method",
    options=[
        "SIEM Alert Text",
        "Upload Incident Response Plan (IRP)"
    ],
    horizontal=True
)


# -------------------------------------------------
# Conditional Input Panels
# -------------------------------------------------
combined_input: Optional[str] = None

if input_mode == "SIEM Alert Text":

    st.subheader("SIEM Alert Input")

    alert_text = st.text_area(
        label="Paste the SIEM alert / incident description",
        height=220,
        placeholder=(
            "Example:\n"
            "Multiple One-Time Password (OTP) messages were detected being sent to a user's "
            "registered mobile number from unknown sources within a short time window. "
            "The activity is associated with repeated DigiLocker login attempts and may "
            "indicate brute-force authentication attempts, SMS spoofing, or SIM swap activity."
        )
    )

    if alert_text.strip():
        combined_input = alert_text


elif input_mode == "Upload Incident Response Plan (IRP)":

    st.subheader("Incident Response Plan (IRP)")

    irp_file = st.file_uploader(
        label="Upload IRP (PDF / DOC / DOCX)",
        type=["pdf", "doc", "docx"]
    )

    if irp_file is not None:
        filename = irp_file.name.lower()

        if filename.endswith(".pdf"):
            irp_text = extract_text_from_pdf(irp_file)
        else:
            irp_text = extract_text_from_docx(irp_file)

        if irp_text.strip():
            combined_input = (
                "INCIDENT RESPONSE PLAN (IRP):\n"
                f"{irp_text}"
            )


# -------------------------------------------------
# Generate Button
# -------------------------------------------------
if st.button("Generate Deployment Playbook", type="primary"):

    if not combined_input:
        st.warning("Please provide a valid input before generating the playbook.")
    else:
        with st.spinner("Generating SOAR deployment playbook..."):

            result = generate_playbook(
                alert_text=combined_input,
                mode="Deployment",
                depth="Deep"
            )

            st.session_state.deployment_result = result

        st.success("Deployment playbook generated")


# -------------------------------------------------
# Render Output + SVG Download
# -------------------------------------------------
if st.session_state.deployment_result:

    result = st.session_state.deployment_result

    st.subheader("Executive Summary")
    st.write(result.get("summary", "No summary generated."))

    st.markdown("---")
    st.subheader("SOAR Execution Flow")

    mermaid_diagram = build_soar_mermaid(
        blocks=result.get("blocks", [])
    )

    mermaid_html = f"""
    <html>
      <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
          mermaid.initialize({{ startOnLoad: false, theme: 'default' }});

          async function renderAndDownload() {{
            const {{ svg }} = await mermaid.render('soarDiagram', `{mermaid_diagram}`);
            const blob = new Blob([svg], {{ type: 'image/svg+xml' }});
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = 'soar_playbook.svg';
            a.click();

            URL.revokeObjectURL(url);
          }}

          document.addEventListener("DOMContentLoaded", async () => {{
            const {{ svg }} = await mermaid.render('soarDiagram', `{mermaid_diagram}`);
            document.getElementById("diagram").innerHTML = svg;
          }});
        </script>
      </head>
      <body>
        <div id="diagram"></div>
        <br/>
        <button onclick="renderAndDownload()">⬇ Download SVG</button>
      </body>
    </html>
    """

    components.html(mermaid_html, height=700, scrolling=True)

    st.markdown("---")
    st.subheader("Model Confidence")
    st.info(f"Confidence Score: **{result.get('confidence', 'N/A')}**")
