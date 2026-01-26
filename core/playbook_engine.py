import os
import json
from pathlib import Path
from google import genai

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
REFERENCE_DIR = BASE_DIR

REFERENCE_FILES = [
    "reference_context.txt",
    "reference_chunks.txt",
    "reference_sources.txt"
]

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

client = genai.Client(api_key=API_KEY)

# -------------------------------------------------
# LOAD REFERENCE KNOWLEDGE
# -------------------------------------------------
def load_reference_material():
    content = []
    for file_name in REFERENCE_FILES:
        path = REFERENCE_DIR / file_name
        if path.exists():
            content.append(f"\n--- {file_name} ---\n")
            content.append(path.read_text(encoding="utf-8"))
    return "\n".join(content)

REFERENCE_CONTEXT = load_reference_material()

# -------------------------------------------------
# CORE AGENT (REAL REASONING)
# -------------------------------------------------
def generate_playbook(alert_text: str, mode: str, depth: str):
    """
    mode: learning | deployment
    depth: Beginner | Intermediate | Advanced
    """

    system_prompt = f"""
You are a SENIOR SOC SOAR ARCHITECT designing production-grade SOAR playbooks.

You MUST:
- Think like an enterprise SOC
- Follow SOAR governance and safety principles
- Avoid over-automation of destructive actions
- Explicitly model decision points and human approvals
- Be technically accurate (SIEM, EDR, IAM, IR, DFIR)

REFERENCE MATERIAL (MANDATORY TO USE):
{REFERENCE_CONTEXT}

OUTPUT RULES:
- Return ONLY valid JSON
- NO markdown
- NO explanation
- NO prose outside JSON
"""

    user_prompt = f"""
ALERT INPUT:
{alert_text}

MODE:
{mode}

LEARNING DEPTH:
{depth}

TASK:
Analyze the alert and design a SOAR playbook.

You MUST determine:
1. Alert category (e.g., brute force, malware, phishing, lateral movement)
2. Required investigations
3. Confidence scoring logic
4. Which actions are SAFE to automate
5. Which actions REQUIRE human approval
6. Evidence preservation steps
7. Incident escalation logic

RETURN THIS EXACT JSON SCHEMA:

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
        contents=[
            {"role": "system", "parts": [system_prompt]},
            {"role": "user", "parts": [user_prompt]}
        ]
    )

    try:
        result = json.loads(response.text)
    except Exception:
        raise ValueError("Gemini returned invalid JSON. Raw output:\n" + response.text)

    return result
