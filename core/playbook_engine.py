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
# LOAD + LIMIT REFERENCE MATERIAL
# -------------------------------------------------
def load_reference_material(max_chars: int = 6000) -> str:
    """
    Loads reference files but HARD limits total size
    to avoid Gemini request rejection.
    """
    combined = []

    for name in REFERENCE_FILES:
        path = BASE_DIR / name
        if path.exists():
            text = path.read_text(encoding="utf-8")
            combined.append(f"\n--- {name} ---\n{text}")

    joined = "\n".join(combined)

    # HARD truncate (enterprise-safe)
    if len(joined) > max_chars:
        joined = joined[:max_chars] + "\n\n[TRUNCATED FOR MODEL SAFETY]"

    return joined

REFERENCE_CONTEXT = load_reference_material()

# -------------------------------------------------
# REAL SOAR AGENT (CLOUD-SAFE)
# -------------------------------------------------
def generate_playbook(alert_text: str, mode: str, depth: str):
    """
    Generates a production-grade SOAR playbook using Gemini.
    Cloud-safe, size-limited, deterministic.
    """

    prompt = f"""
You are a SENIOR SOC SOAR ARCHITECT designing production-grade SOAR playbooks.

STRICT RULES:
- Think like an enterprise SOC
- Apply SIEM, EDR, IAM, DFIR reasoning
- Avoid unsafe automation
- Explicitly model decisions & human approval
- Be technically precise, not generic

REFERENCE MATERIAL (USE THIS CONTEXT):
{REFERENCE_CONTEXT}

ALERT INPUT:
{alert_text}

MODE:
{mode}

DEPTH:
{depth}

TASK:
Analyze the alert and design a SOAR playbook.

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

    try:
        response = client.models.generate_content(
            model="models/gemini-1.5-flash",
            contents=prompt,
        )
    except Exception as e:
        raise RuntimeError(
            "Gemini request failed (likely prompt size or model issue).\n"
            "Error: " + str(e)
        )

    raw = response.text.strip()

    try:
        return json.loads(raw)
    except Exception:
        raise ValueError(
            "Gemini returned INVALID JSON.\n\nRAW OUTPUT:\n" + raw
        )
