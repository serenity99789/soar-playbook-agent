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
    text = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)

    return "\n".join(text)


def extract_text_from_docx(uploaded_file) -> str:
    try:
        from docx import Document
    except ImportError:
        return ""

    document = Document(uploaded_file)
    return "\n".join(p.text for p in document.paragraphs if p.text.strip())


# -------------------------------------------------
# Input Mode Selector
# -------------------------------------------------
st.subheader("Input Source")

input_mode = st.radio(
    label="Choose input method",
    options=["SIEM Alert Text", "Upload Incident Response Plan (IRP)"],
    horizontal=True
)


# -------------------------------------------------
# Side-by-Side Layout
# -------------------------------------------------
left_col, right_col = st.columns(2)


with left_col:
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
        ),
        disabled=(input_mode != "SIEM Alert Text")
    )


with right_col:
    st.subheader("Incident Response Plan (IRP)")

    irp_file = st.file_uploader(
        label="Upload IRP (PDF / DOC / DOCX)",
        type=["pdf", "doc", "docx"],
        disabled=(input_mode != "Upload Incident Response Plan (IRP)")
    )


# -------------------------------------------------
# Generate Button
# -------------------------------------------------
if st.button("Generate Deployment Playbook", type="primary"):

    combined_input: Optional[str] = None

    if input_mode == "SIEM Alert Text":
        if not alert_text.strip():
            st.warning("Please paste a SIEM alert before generating the playbook.")
        else:
            combined_input = alert_text

    elif input_mode == "Upload Incident Response Plan (IRP)":
        if irp_file is None:
            st.warning("Please upload an Incident Response Plan file.")
        else:
            file_name = irp_file.name.lower()

            if file_name.endswith(".pdf"):
                irp_text = extract_text_from_pdf(irp_file)
            else:
                irp_text = extract_text_from_docx(irp_file)

            if not irp_text.strip():
                st.warning("Unable to extract text from the uploaded IRP.")
            else:
                combined_input = (
                    "INCIDENT RESPONSE PLAN (IRP):\n"
                    f"{irp_text}"
                )

    if combined_input:
        with st.spinner("Generating SOAR deployment playbook..."):

            result = generate_playbook(
                alert_text=combined_input,
                mode="Deployment",
                depth="Deep"
            )

            st.session_state.deployment_result = result

        st.success("Deployment playbook generated")


# -------------------------------------------------
# Render Output
# -------------------------------------------------
if st.session_state.deployment_result:

    result = st.session_state.deployment_result

    # ---------------- Executive Summary ----------------
    st.subheader("Executive Summary")
    st.write(result.get("summary", "No summary generated."))

    st.markdown("---")

    # ---------------- SOAR Execution Flow ----------------
    st.subheader("SOAR Execution Flow")

    mermaid_diagram = build_soar_mermaid(
        blocks=result.get("blocks", [])
    )

    mermaid_html = f"""
    <html>
      <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
          mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
        </script>
      </head>
      <body>
        <div class="mermaid">
        {mermaid_diagram}
        </div>
      </body>
    </html>
    """

    components.html(mermaid_html, height=650, scrolling=True)

    st.markdown("---")

    # ---------------- Confidence ----------------
    st.subheader("Model Confidence")
    confidence = result.get("confidence", "N/A")
    st.info(f"Confidence Score: **{confidence}**")
