import os
from typing import Dict, Any

from google import genai


# -------------------------
# Gemini Client
# -------------------------
def get_gemini_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set")

    return genai.Client(api_key=api_key)


# -------------------------
# Main Playbook Generator
# -------------------------
def generate_playbook(
    alert_text: str,
    mode: str = "deployment",
    depth: str = "Advanced",
) -> Dict[str, Any]:
    """
    Generates a SOAR playbook using Gemini.
    This is REAL generation — no cache, no placeholders.
    """

    client = get_gemini_client()

    system_prompt = f"""
You are an enterprise-grade SOAR architect.

Analyze the given SIEM alert deeply and produce a REAL, technical SOAR playbook.

Rules:
- NO generic steps
- NO placeholders
- Think like a SOC + IR lead
- Use conditional logic, decision points, and real security controls
- Assume tools like SIEM, EDR, IAM, Firewall, SOAR platform exist
- Output must be structured and actionable

Mode: {mode}
Depth: {depth}
"""

    user_prompt = f"""
SIEM Alert / Use Case:
{alert_text}

Generate:
1. Detailed SOAR execution stages
2. Decision logic (conditions, branches)
3. Automation vs Human checkpoints
4. Incident lifecycle actions
"""

    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=[
                {"role": "system", "parts": [{"text": system_prompt}]},
                {"role": "user", "parts": [{"text": user_prompt}]},
            ],
            config={
                "temperature": 0.3,
                "top_p": 0.9,
                "max_output_tokens": 2048,
            },
        )
    except Exception as e:
        raise RuntimeError(f"Gemini request failed: {e}")

    # -------------------------
    # Parse response safely
    # -------------------------
    try:
        text_output = response.text
    except Exception:
        raise RuntimeError("Gemini returned no text output")

    return {
        "raw_text": text_output,
        "mode": mode,
        "depth": depth,
    }
