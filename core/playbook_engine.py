import os
import json
import re
from typing import Dict, Any, List
from google import genai

# -------------------------------------------------
# GEMINI CLIENT
# -------------------------------------------------

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# STRICT JSON EXTRACTION
# -------------------------------------------------

def extract_json(text: str) -> Dict[str, Any]:
    """
    Extracts the first valid JSON object from model output.
    Raises ValueError if parsing fails.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("No JSON object found in model output")
        return json.loads(match.group())

# -------------------------------------------------
# PROMPT BUILDERS
# -------------------------------------------------

def build_prompt(alert_text: str, mode: str, depth: str) -> str:
    """
    Builds a deterministic prompt based on mode.
    """

    base_schema = """
Return ONLY valid JSON.
No markdown. No explanations outside JSON.

Schema:
{
  "title": "",
  "blocks": [
    {
      "step": 1,
      "name": "",
      "purpose": "",
      "soc_role": "",
      "automation_level": "",
      "inputs": [],
      "outputs": [],
      "failure_handling": "",
      "if_skipped": ""
    }
  ]
}
"""

    learning_addition = """
Include SOC reasoning, why the step exists, and how analysts think.
Explain decisions clearly but concisely.
"""

    deployment_addition = """
Focus on execution-ready actions.
No teaching tone.
No SOC theory.
Be concise and operational.
"""

    depth_map = {
        "Beginner": "Assume junior SOC analyst. Explain clearly.",
        "Intermediate": "Assume L1/L2 analyst. Moderate depth.",
        "Advanced": "Assume experienced SOC / SOAR engineer. Be precise."
    }

    return f"""
You are a senior SOAR architect.

Mode: {mode}
Learning depth: {depth}

{learning_addition if mode == "learning" else deployment_addition}

{depth_map.get(depth, "")}

{base_schema}

SIEM Alert:
{alert_text}
"""

# -------------------------------------------------
# PUBLIC ENGINE FUNCTION
# -------------------------------------------------

def generate_playbook(
    alert_text: str,
    mode: str = "learning",
    depth: str = "Beginner"
) -> Dict[str, Any]:
    """
    Main entry point used by Streamlit pages.
    """

    if mode not in ["learning", "deployment"]:
        raise ValueError("mode must be 'learning' or 'deployment'")

    prompt = build_prompt(alert_text, mode, depth)

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    )

    data = extract_json(response.text)

    # Minimal validation
    if "blocks" not in data or not isinstance(data["blocks"], list):
        raise ValueError("Invalid playbook structure returned")

    return data
