from typing import Dict, Any, List


# -------------------------------------------------
# SOAR Mermaid Diagram Engine
# -------------------------------------------------
def build_soar_mermaid(blocks: List[Dict[str, Any]]) -> str:
    """
    Builds a SOAR-style Mermaid diagram similar to Splunk SOAR / Cortex XSOAR.

    Guarantees:
    - Same lanes
    - Same layout
    - Same decision diamond
    - Same colors

    Adds:
    - Visual rendering for Nested Playbooks (dashed border)
    """

    lines: List[str] = []

    # -------------------------------------------------
    # Base diagram
    # -------------------------------------------------
    lines.append("flowchart LR")
    lines.append("")

    # -------------------------------------------------
    # Lanes (DO NOT CHANGE STRUCTURE)
    # -------------------------------------------------
    lines.append("subgraph Intake [Alert Intake]")
    lines.append("direction TB")
    lines.append("A[SIEM Alert Received]")
    lines.append("end")
    lines.append("")

    lines.append("subgraph Enrichment [Context Enrichment]")
    lines.append("direction TB")
    lines.append("B[Normalize & Parse]")
    lines.append("C[Asset / User / IP Enrichment]")
    lines.append("D[Threat Intelligence Lookup]")
    lines.append("end")
    lines.append("")

    lines.append("subgraph Decision [Decision Point]")
    lines.append("direction TB")
    lines.append("E{Threat Confirmed?}")
    lines.append("end")
    lines.append("")

    lines.append("subgraph Response [Automated Response]")
    lines.append("direction TB")
    lines.append("F[Automated Containment]")
    lines.append("G[Block IP / Isolate Host]")
    lines.append("H[Preserve Evidence]")
    lines.append("end")
    lines.append("")

    lines.append("subgraph Human [Human-in-the-Loop]")
    lines.append("direction TB")
    lines.append("I[Human Review]")
    lines.append("J[SOC Analyst Decision]")
    lines.append("end")
    lines.append("")

    lines.append("subgraph Closure [Incident Closure]")
    lines.append("direction TB")
    lines.append("K[Notify IR Team]")
    lines.append("L[Update Incident & Close]")
    lines.append("end")
    lines.append("")

    # -------------------------------------------------
    # Main Flow (UNCHANGED)
    # -------------------------------------------------
    lines.append("A --> B")
    lines.append("B --> C")
    lines.append("C --> D")
    lines.append("D --> E")

    lines.append("E -->|Yes| F")
    lines.append("F --> G")
    lines.append("G --> H")
    lines.append("H --> K")
    lines.append("K --> L")

    lines.append("E -->|Uncertain| I")
    lines.append("I --> J")
    lines.append("J -->|Escalate| F")
    lines.append("J -->|Dismiss| L")
    lines.append("")

    # -------------------------------------------------
    # Styling (BASE SOAR COLORS)
    # -------------------------------------------------
    lines.append("classDef intake fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,rx:6,ry:6;")
    lines.append("classDef enrich fill:#E0F7FA,stroke:#00838F,stroke-width:2px,rx:6,ry:6;")
    lines.append("classDef decision fill:#FFF3E0,stroke:#EF6C00,stroke-width:2px;")
    lines.append("classDef response fill:#FCE4EC,stroke:#C2185B,stroke-width:2px,rx:6,ry:6;")
    lines.append("classDef human fill:#EDE7F6,stroke:#4527A0,stroke-width:2px,rx:6,ry:6;")
    lines.append("classDef closure fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,rx:6,ry:6;")

    # Nested playbook style (ADD ONLY)
    lines.append(
        "classDef nested stroke-dasharray: 5 5,stroke-width:2px,fill:#F5F5F5;"
    )
    lines.append("")

    # -------------------------------------------------
    # Base Class Assignment
    # -------------------------------------------------
    lines.append("class A intake")
    lines.append("class B,C,D enrich")
    lines.append("class E decision")
    lines.append("class F,G,H response")
    lines.append("class I,J human")
    lines.append("class K,L closure")

    # -------------------------------------------------
    # Nested Playbook Detection (VISUAL ONLY)
    # -------------------------------------------------
    nested_keywords = ("nested", "sub-playbook", "playbook")

    node_title_map = {
        "B": "Normalize & Parse",
        "C": "Asset / User / IP Enrichment",
        "D": "Threat Intelligence Lookup",
        "F": "Automated Containment",
        "G": "Block IP / Isolate Host",
        "H": "Preserve Evidence",
        "I": "Human Review",
        "J": "SOC Analyst Decision",
    }

    for node_id, title in node_title_map.items():
        title_lower = title.lower()
        if any(k in title_lower for k in nested_keywords):
            lines.append(f"class {node_id} nested")

    return "\n".join(lines)
