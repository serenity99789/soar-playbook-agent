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
# Helper: Extract text from PDF
# -------------------------------------------------
def extract_text_from_pdf(uploaded_file) -> str:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        return ""

    reader = PdfReader(uploaded_file)
    text_chunks = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_chunks.append(page_text)

    return "\n".join(text_chunks)


# -------------------------------------------------
# SIEM Alert Input
# -------------------------------------------------
st.subheader("SIEM Alert Input")

alert_text = st.text_area(
    label="Paste the SIEM alert / incident description",
    height=180,
    placeholder=(
        "Example:\n"
        "Multiple One-Time Password (OTP) messages were detected being sent to a user's "
        "registered mobile number from unknown sources within a short time window. "
        "The activity is associated with repeated DigiLocker login attempts and may "
        "indicate brute-force authentication attempts, SMS spoofing, or SIM swap activity."
    )
)


# -------------------------------------------------
# IRP Upload
# -------------------------------------------------
st.subheader("Incident Response Plan (Optional)")

irp_file = st.file_uploader(
    label="Upload IRP (PDF)",
    type=["pdf"],
    help="If provided, the SOAR playbook will be generated using your organization's IRP."
)


# -------------------------------------------------
# Generate Button
# -------------------------------------------------
if st.button("Generate Deployment Playbook", type="primary"):

    if not alert_text.strip():
        st.warning("Please paste a SIEM alert before generating the playbook.")
    else:
        with st.spinner("Generating SOAR deployment playbook..."):

            irp_text: Optional[str] = None

            if irp_file is not None:
                irp_text = extract_text_from_pdf(irp_file)

            # Combine alert + IRP context
            combined_input = alert_text

            if irp_text:
                combined_input = (
                    "SIEM ALERT:\n"
                    f"{alert_text}\n\n"
                    "INCIDENT RESPONSE PLAN (IRP):\n"
                    f"{irp_text}"
                )

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
