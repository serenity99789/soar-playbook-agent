import os
import json
import re
from typing import Dict, Any

from google import genai


# -----------------------------
# Gemini Client
# -----------------------------
def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY / GOOGLE_API_KEY not set")

    return genai.Client(api_key=api_key)


# -----------------------------
# Safe JSON extraction
# -----------------------------
def extract_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("No valid JSON found in model output")
        return json.loads(match.group())


# -----------------------------
# Prompt Builder
# -----------------------------
def build_prompt(alert_text: str, mode: str, depth: str) -> str:
    return f"""
You are an enterprise-grade SOAR architect working in a Tier-1 SOC.

Your task:
- Analyze the SIEM alert below
- Design a REAL production SOAR playbook
- Use SOC reasoning, not generic steps
- Reflect how tools like Cortex XSOAR / Splunk SOAR actually work

Rules:
- DO NOT be generic
- DO NOT invent fake tools
- Use realistic SOC actions
- Be technically precise
- Assume this will be reviewed by security leadership

Output MUST be valid JSON only.
No markdown. No explanations. No extra text.

JSON Schema:
{{
  "summary": "One-paragraph technical summary of the incident",
  "confidence": "Low | Medium | High",
  "blocks": [
    {{
      "id": "string",
      "title": "string",
      "type": "enrichment | decision | automation | human",
      "description": "string"
    }}
  ]
}}

Mode: {mode}
Depth: {depth}

SIEM Alert:
{alert_text}
""".strip()


# -----------------------------
# Main Playbook Generator
# -----------------------------
def generate_playbook(
    alert_text: str,
    mode: str,
    depth: str
) -> Dict[str, Any]:

    client = get_gemini_client()
    prompt = build_prompt(alert_text, mode, depth)

    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
        )
    except Exception as e:
        raise RuntimeError(f"Gemini request failed: {e}")

    if not response.text:
        raise RuntimeError("Empty response from Gemini")

    data = extract_json(response.text)

    if "blocks" not in data:
        raise RuntimeError("Invalid playbook structure returned")

    return data
