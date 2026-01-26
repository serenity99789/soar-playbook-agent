import os
import json
from pathlib import Path
from google import genai

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

REFERENCE_FILES = [
    "reference_context.txt",
    "reference_chunks.txt",
    "reference_sources.txt",
]

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# LOAD REFERENCE MATERIAL
# -------------------------------------------------
def load_reference_material():
    material = []
    for name in REFERENCE_FILES:
        path = BASE_DIR / name
        if path.exists():
            material.append(f"\n--- {name} ---\n")
            material.append(path.read_text(encoding="utf-8"))
    return "\n".join(material)

REFERENCE_CONTEXT = load_reference_material()

# -------------------------------------------------
# REAL SOAR AGENT (SDK-CORRECT)
# -------------------------------------------------
def generate_playbook(alert_text: str, mode: str, depth: str):
    """
    Generates a real SOAR playbook using Gemini reasoning.
    """

    prompt = f"""
You are a SENIOR SOC SOAR ARCHITECT designing production-grade SOAR playbooks.

You MUST:
- Think like an enterprise SOC
- Apply SIEM, EDR, IAM, DFIR principles
- Avoid unsafe automation
- Explicitly define decision points
- Clearly separate automated vs human actions

REFERENCE MATERIAL (MANDATORY):
{REFERENCE_CONTEXT}

ALERT INPUT:
{alert_text}

MODE:
{mode}

LEARNING DEPTH:
{depth}

TASK:
Analyze the alert and design a SOAR playbook.

You MUST determine:
1. Alert category
2. Investigations required
3. Threat confidence
4. Safe automation actions
5. Human approval checkpoints
6. Evidence preservation steps
7. Escalation logic

RETURN ONLY VALID JSON.
NO markdown.
NO commentary.

JSON SCHEMA:
{{
  "alert_type": "",
  "threat_confidence": "Low | Medium | High",
  "playbook_overview": "",
  "blocks": [
    {{
      "id": "",
      "name": "",
      "category": "Enrichment | Analysis | Decision | Containment | Notification | Governance",
      "description": "",
      "automation_level": "Automatic | Conditional | Manual",
      "depends_on": []
    }}
  ],
  "decision_points": [
    {{
      "question": "",
      "yes_path": "",
      "no_path": ""
    }}
  ],
  "governance": {{
    "human_approval_required_for": [],
    "auto_allowed_actions": [],
    "forbidden_without_approval": []
  }}
}}
"""

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt,
    )

    try:
        return json.loads(response.text)
    except Exception:
        raise ValueError(
            "Gemini returned invalid JSON.\n\nRAW OUTPUT:\n" + response.text
        )
