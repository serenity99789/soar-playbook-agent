import os
import json
from pathlib import Path
from groq import Groq

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

REFERENCE_FILES = [
    "reference_context.txt",
    "reference_chunks.txt",
    "reference_sources.txt",
]

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set")

client = Groq(api_key=GROQ_API_KEY)

# -------------------------------------------------
# LOAD + LIMIT REFERENCE MATERIAL
# -------------------------------------------------
def load_reference_material(max_chars: int = 6000) -> str:
    """
    Load SOC / SOAR reference material with a hard safety limit.
    """
    content = []

    for name in REFERENCE_FILES:
        path = BASE_DIR / name
        if path.exists():
            content.append(f"\n--- {name} ---\n")
            content.append(path.read_text(encoding="utf-8"))

    joined = "\n".join(content)

    if len(joined) > max_chars:
        joined = joined[:max_chars] + "\n\n[TRUNCATED FOR SAFETY]"

    return joined


REFERENCE_CONTEXT = load_reference_material()

# -------------------------------------------------
# DYNAMIC SOAR AGENT (LLM-DRIVEN, NOT TEMPLATE)
# -------------------------------------------------
def generate_playbook(alert_text: str, mode: str, depth: str) -> dict:
    """
    Dynamic SOAR reasoning engine.
    LLM decides the flow, engine enforces structure.
    """

    system_prompt = f"""
You are a SENIOR ENTERPRISE SOAR ARCHITECT.

Your job is to ANALYZE security incidents and DESIGN
SAFE, REALISTIC, ENTERPRISE-GRADE SOAR EXECUTION PLANS.

You MUST:
- Think like a SOC analyst (L1 → L3)
- Apply SIEM, EDR, IAM, DFIR reasoning
- Avoid unsafe or irreversible automation
- Introduce decision points where risk exists
- Preserve evidence BEFORE containment
- Clearly separate automated vs human actions

REFERENCE MATERIAL:
{REFERENCE_CONTEXT}

OUTPUT RULES:
- RETURN ONLY VALID JSON
- NO markdown
- NO explanations
- NO filler text
"""

    user_prompt = f"""
ALERT INPUT:
{alert_text}

MODE:
{mode}

DEPTH:
{depth}

TASK:
Dynamically reason about this alert and produce a SOAR execution plan.

The plan MUST be scenario-specific and technically accurate.

JSON SCHEMA (STRICT):
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

    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as e:
        raise RuntimeError(f"Groq request failed: {e}")

    raw_output = response.choices[0].message.content.strip()

    try:
        return json.loads(raw_output)
    except Exception:
        raise ValueError(
            "LLM returned invalid JSON.\n\nRAW OUTPUT:\n" + raw_output
        )
