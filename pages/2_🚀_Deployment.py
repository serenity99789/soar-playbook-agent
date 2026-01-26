import sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import base64

# ------------------ PATH FIX ------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from core.playbook_engine import generate_playbook

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="SOAR Deployment View",
    page_icon="🚀",
    layout="wide"
)

st.caption("Built by Accenture")

st.title("🚀 SOAR Deployment View")
st.markdown(
    "Production-ready **automated response flow** showing decisions, "
    "containment, and human approvals."
)

# ------------------ INPUT ------------------
alert_text = st.text_area(
    "Describe the SIEM alert",
    height=160,
    placeholder="Suspicious PowerShell execution detected on multiple endpoints..."
)

# ------------------ MERMAID ------------------
def build_mermaid(blocks):
    lines = ["flowchart TD"]

    for i, b in enumerate(blocks):
        lines.append(f'S{i}["{b["title"]}"]:::auto')
        if i > 0:
            lines.append(f"S{i-1} --> S{i}")

    lines += [
        'D{"Threat Confirmed?"}:::decision',
        f"S{len(blocks)-1} --> D",
        'D -->|Yes| C1["Auto Containment"]:::contain',
        'C1 --> C2["Isolate Host / Block IP"]:::contain',
        'C2 --> C3["Preserve Evidence"]:::evidence',
        'C3 --> C4["Notify IR Team"]:::notify',
        'D -->|No| H1["Human Review"]:::manual',
        'H1 --> H2["SOC Analyst Decision"]:::manual',
        "classDef auto fill:#2563eb,color:#fff,stroke:#1e3a8a,stroke-width:2px",
        "classDef decision fill:#f59e0b,stroke:#b45309,stroke-width:3px",
        "classDef contain fill:#dc2626,color:#fff",
        "classDef evidence fill:#7c3aed,color:#fff",
        "classDef notify fill:#16a34a,color:#fff",
        "classDef manual fill:#6b7280,color:#fff",
    ]
    return "\n".join(lines)

def render_mermaid(code):
    components.html(
        f"""
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: "default"
            }});
        </script>
        <div class="mermaid">{code}</div>
        """,
        height=650,
        scrolling=True
    )

def download_svg_button(mermaid_code):
    svg_html = f"""
    <html>
    <body>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
    mermaid.initialize({{ startOnLoad: true }});
    </script>
    <div class="mermaid">{mermaid_code}</div>
    </body>
    </html>
    """
    b64 = base64.b64encode(svg_html.encode()).decode()
    st.download_button(
        "⬇️ Download SOAR Playbook (SVG)",
        data=base64.b64decode(b64),
        file_name="soar_playbook.svg",
        mime="image/svg+xml"
    )

# ------------------ GENERATE ------------------
if st.button("Generate Deployment Playbook"):
    if not alert_text.strip():
        st.warning("Please describe the SIEM alert.")
    else:
        with st.spinner("Generating production SOAR playbook..."):
            result = generate_playbook(
                alert_text=alert_text,
                mode="deployment",
                depth="Advanced"
            )

        blocks = result["blocks"]

        st.success("Deployment playbook generated")

        # -------- TEXT STEPS --------
        st.header("📋 Deployment Steps")
        for i, b in enumerate(blocks, 1):
            with st.expander(f"Step {i}: {b['title']}"):
                st.markdown(f"**Purpose:** {b.get('description','')}")
                if b.get("automation"):
                    st.markdown(f"🤖 **Automation:** {b['automation']}")
                if b.get("human"):
                    st.markdown(f"👤 **Human Approval:** {b['human']}")

        # -------- VISUAL FLOW --------
        st.header("🧭 SOAR Execution Flow")
        mermaid_code = build_mermaid(blocks)
        render_mermaid(mermaid_code)

        download_svg_button(mermaid_code)
