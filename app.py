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

def box(title, subtitle, color):
    return f"""
    <div style="
        padding:10px 16px;
        border-radius:12px;
        background:{color};
        color:white;
        font-weight:600;
        text-align:center;
        box-shadow:0 4px 10px rgba(0,0,0,0.18);
        white-space:nowrap;
        font-size:14px;
    ">
        {title}<br/>
        <span style="font-size:11px;font-weight:400;">
            {subtitle}
        </span>
    </div>
    """

def arrow(symbol):
    return f"<div style='font-size:22px;text-align:center;line-height:1;'>{symbol}</div>"

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

    flow = f"""
    <div style="
        display:grid;
        grid-template-columns: 1fr auto 1fr;
        gap:18px 40px;
        justify-items:center;
        align-items:center;
        margin-top:20px;
    ">

        {box("Trigger", "SIEM Brute Force", "#0f766e")}
        {arrow("↓")}
        <div></div>

        {box("Enrichment", "Azure AD + IP", "#15803d")}
        {arrow("↓")}
        <div></div>

        {box("Threat Intel", "IP Reputation", "#374151")}
        {arrow("↓")}
        <div></div>

        {box("Decision", "Compromise Confidence?", "#d97706")}
        {arrow("↓")}
        {arrow("↓")}

        {box("HIGH", "Auto Containment", "#b91c1c")}
        <div></div>
        {box("LOW / MED", "Manual Review", "#2563eb")}

        {arrow("↓")}
        <div></div>
        {arrow("↓")}

        {box("Account Actions", "Disable / Revoke", "#7f1d1d")}
        <div></div>
        {box("L1 Analysis", "Validate & Decide", "#1e40af")}

        {arrow("↓")}
        <div></div>
        {arrow("↓")}

        {box("Preserve Evidence", "Logs + EDR", "#1f2937")}
        <div></div>
        {box("Close / Escalate", "Next Steps", "#0f172a")}

    </div>
    """

    st.markdown(flow, unsafe_allow_html=True)

    st.header("📄 Playbook Documentation")
    st.markdown(data.get("documentation", ""))
