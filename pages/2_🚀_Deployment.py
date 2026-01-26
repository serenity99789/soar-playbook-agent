# pages/2_🚀_Deployment.py

import streamlit as st
from core.diagram_engine import generate_mermaid_flow

st.set_page_config(
    page_title="SOAR Deployment View",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 SOAR Deployment Playbook")
st.caption("How SOAR executes safely in production environments")

st.success("Deployment playbook generated")

# ===============================
# Mermaid Renderer
# ===============================
mermaid_code = generate_mermaid_flow()

st.markdown("## 🧭 SOAR Execution Flow")

st.components.v1.html(
    f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: "default" }});
    </script>

    <div class="mermaid">
    {mermaid_code}
    </div>
    """,
    height=700,
    scrolling=True
)

# ===============================
# SVG Download (Client-side)
# ===============================
st.markdown("### ⬇️ Export")

st.components.v1.html(
    """
    <button onclick="downloadSVG()" style="
        padding:10px 18px;
        background:#2563eb;
        color:white;
        border:none;
        border-radius:6px;
        cursor:pointer;
        font-size:14px;">
        Download SOAR Playbook (SVG)
    </button>

    <script>
    function downloadSVG() {
        const svg = document.querySelector("svg");
        const serializer = new XMLSerializer();
        const source = serializer.serializeToString(svg);
        const blob = new Blob([source], {type:"image/svg+xml;charset=utf-8"});
        const url = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "soar_playbook.svg";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    </script>
    """,
    height=120
)
