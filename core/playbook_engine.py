import os
import json
import re
from google import genai

# -----------------------------
# Gemini Client
# -----------------------------
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

client = genai.Client(api_key=API_KEY)

# -----------------------------
# Safe JSON Extraction
# -----------------------------
def _extract_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("Model did not return JSON")
        return json.loads(match.group())

# -----------------------------
# Prompt Builder
# -----------------------------
def _build_prompt(alert_text: str, mode: str, depth: str):
    return f"""
You are a senior SOC SOAR architect.

Return ONLY valid JSON. No markdown. No explanation.

Schema:
{{
  "blocks": [
    {{
      "title": "",
      "description": "",
      "reasoning": ""
    }}
  ]
}}

Mode: {mode}
Learning depth: {depth}

SIEM alert:
{alert_text}
"""

# -----------------------------
# Public Engine Function
# -----------------------------
def generate_playbook(alert_text: str, mode: str, depth: str):
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=_build_prompt(alert_text, mode, depth)
    )

    data = _extract_json(response.text)

    if "blocks" not in data:
        raise ValueError("Invalid model response")

    return data
