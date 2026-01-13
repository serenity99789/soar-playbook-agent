import os
from datetime import datetime
from google import genai

# ---------- CONFIG ----------
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set. Set it and re-run.")

client = genai.Client(api_key=API_KEY)

# ---------- INTERACTIVE INPUT ----------
print("\nEnter SOAR use case details.")
print("Press Enter on an empty line to submit.\n")

lines = []
while True:
    line = input("> ")
    if line.strip() == "":
        break
    lines.append(line)

USE_CASE = "\n".join(lines)

if not USE_CASE.strip():
    raise RuntimeError("No use case provided. Exiting.")

# ---------- PROMPT ----------
PROMPT = f"""
You are an AI agent for SOAR Playbook Automation.

STRICT OUTPUT FORMAT.
DO NOT add explanations outside the defined sections.

SECTION A: BLOCKS_JSON
Return a JSON array. Each object must contain:
- block_name
- purpose
- inputs
- outputs
- failure_handling
- sla_impact
- analyst_notes

SECTION B: DOCUMENTATION_TEXT
Clear, professional SOC-ready documentation per block.

Align where relevant with:
- MITRE ATT&CK
- NIST Incident Response
- SOC SOPs

Use case:
{USE_CASE}
"""

# ---------- RUN ----------
response = client.models.generate_content(
    model="models/gemini-2.5-flash",
    contents=PROMPT,
)

output_text = response.text

print("\n===== AI OUTPUT START =====\n")
print(output_text)
print("\n===== AI OUTPUT END =====\n")

# ---------- SAVE OUTPUT ----------
os.makedirs("playbooks", exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"playbooks/PB_generated_{timestamp}.txt"

with open(filename, "w", encoding="utf-8") as f:
    f.write(output_text)

print(f"\nSaved output to {filename}")
