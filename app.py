import os
import json
import re
import streamlit as st
from google import genai

st.set_page_config(page_title="SOAR Playbook Generator", layout="wide")
st.caption("Built by Srinivas")

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("GEMINI_API_KEY not set")
    st.stop()

client = genai.Client(api_key=API_KEY)

def build_prompt(use_case: str) -> str:
    return f"""
Return ONLY valid JSON.
No markdown. No backticks.

Schema:
{{
  "blocks": [],
  "documentation": ""
}}

Use case:
{use_case}
"""

def parse_model_output(text: str):
    cleaned = re.sub(r"```json|```", "", text).strip()
    return json.loads(cleaned)

def flow_box(title, subtitle, color, arrow=None):
    arrow_html = ""
    if arrow:
        arrow_html = f"""
        <div style="
            margin-top:8px;
            font-size:20px;
            font-weight:700;
        ">{arrow}</div>
        """

    return f"""
    <div style="
        padding:12px 18px;
        border-radius:12px;
        background:{color};
        color:white;
        text-align:center;
        font-weight:600;
        box-shadow:0 4px 10px rgba(0,0,0,0.18);
        min-width:190px;
    ">
        {title}<br/>
        <span style="font-size:11px;font-weight:400;">
            {subtitle}
        </span>
        {arrow_html}
    </div>
    """

st.title("🛡️ SOAR Playbook Generator")

use_case = st.text_area(
    "SOAR Use Case Description",
    height=220,
    placeholder="Account Compromise – Brute Force Success"
)

if st.button("Generate Playbook"):

    if not use_case.strip():
        st.warning("Please enter a use case.")
        st.stop()

    with st.spinner("Generating playbook..."):
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=build_prompt(use_case)
        )

    try:
        data = parse_model_output(response.text)
    except Exception:
        st.error("Model output could not be parsed.")
        st.stop()

    st.header("🔗 SOAR Flow (Graphical)")

    flow_html = f"""
    <div style="
        display:grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap:26px 40px;
        justify-items:center;
        align-items:center;
        margin-top:20px;
    ">

        {flow_box("Trigger", "SIEM Brute Force", "#0f766e", "↓")}
        {flow_box("Enrichment", "Azure AD + IP", "#15803d", "↓")}
        {flow_box("Threat Intel", "IP Reputation", "#374151", "↓")}

        {flow_box("Decision", "Compromise Confidence?", "#d97706")}
        {flow_box("HIGH", "Auto Containment", "#b91c1c", "↓")}
        {flow_box("LOW / MED", "Manual Review", "#2563eb", "↓")}

        {flow_box("Account Actions", "Disable / Revoke", "#7f1d1d")}
        {flow_box("Preserve Evidence", "Logs + EDR", "#1f2937")}
        {flow_box("L1 Analysis", "Validate & Decide", "#1e40af")}

    </div>
    """

    st.markdown(flow_html, unsafe_allow_html=True)

    st.header("📄 Playbook Documentation")
    st.markdown(data.get("documentation", ""))
