import os
import json
from typing import Dict, Any

from google import genai
from google.genai import types


# -----------------------------
# Gemini Client (ONLY LLM)
# -----------------------------
def get_gemini_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set")

    return genai.Client(api_key=api_key)


# -----------------------------
# Core Playbook Generator
# -----------------------------
def generate_playbook(
    alert_text: str,
    mode: str = "deployment",
    depth: str = "Advanced",
) -> Dict[str, Any]:

    client = get_gemini_client()

    system_prompt = f"""
You are an enterprise-grade SOAR architect.

Your task:
- Analyze the SIEM alert deeply
- Design a REAL production SOAR playbook
- Use SOC terminology, not generic language
- Include branching logic, containment conditions, enrichment steps
- Assume tools like SIEM, EDR, IAM, Firewall, TI platforms exist
- NO placeholders
- NO generic advice
- NO repetition

Mode: {mode}
Depth: {depth}

Return STRICT JSON ONLY in this schema:

{{
  "summary": "one-paragraph executive summary",
  "blocks": [
    {{
      "id": "string",
      "title": "string",
      "type": "process | decision | action",
      "description": "string",
      "on_true": "id or null",
      "on_false": "id or null"
    }}
  ]
}}
"""

    user_prompt = f"""
SIEM Alert / Use Case:
{alert_text}
"""

    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=[
                types.Content(role="system", parts=[types.Part(text=system_prompt)]),
                types.Content(role="user", parts=[types.Part(text=user_prompt)]),
            ],
            generation_config=types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=4096,
            ),
        )

    except Exception as e:
        raise RuntimeError(f"Gemini request failed: {e}")

    raw_text = response.text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        raise RuntimeError(f"Invalid JSON from Gemini:\n{raw_text}")
