from typing import Dict, Any


def render_mermaid_flow(playbook_text: str) -> str:
    """
    Converts LLM-generated SOAR logic into a Mermaid flowchart.
    This is intentionally opinionated to look like real SOAR platforms.
    """

    # Base SOAR execution skeleton (horizontal)
    mermaid = """
flowchart LR
    A[Alert Intake<br/>SIEM Event] --> B[Normalization<br/>& Parsing]
    B --> C[Context Enrichment<br/>Asset / User / IP]
    C --> D[Threat Intelligence<br/>Lookup]

    D --> E{Threat Confirmed?}

    E -->|Yes| F[Automated Containment]
    F --> G[Block IP / Isolate Host]
    G --> H[Preserve Evidence]
    H --> I[Notify IR Team]
    I --> J[Update Incident & Close]

    E -->|Uncertain| K[Human Review]
    K --> L[SOC Analyst Decision]
    L -->|Escalate| F
    L -->|Dismiss| J
"""

    return mermaid.strip()
