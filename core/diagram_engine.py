# core/diagram_engine.py

def build_soar_mermaid(blocks: list[dict]) -> str:
    """
    Builds a SOAR-style Mermaid diagram similar to Splunk SOAR / XSOAR.
    """

    lines = []
    lines.append("flowchart LR")
    lines.append("")

    # ---- Subgraphs (SOAR phases) ----
    lines.append("subgraph Intake [Alert Intake]")
    lines.append("direction TB")
    lines.append("A[SIEM Alert Received]")
    lines.append("end")
    lines.append("")

    lines.append("subgraph Enrichment [Context Enrichment]")
    lines.append("direction TB")
    lines.append("B[Normalize & Parse]")
    lines.append("C[Asset / User / IP Enrichment]")
    lines.append("D[Threat Intel Lookup]")
    lines.append("end")
    lines.append("")

    lines.append("subgraph Decision [Decision Point]")
    lines.append("direction TB")
    lines.append("E{Threat Confirmed?}")
    lines.append("end")
    lines.append("")

    lines.append("subgraph Response [Automated Response]")
    lines.append("direction TB")
    lines.append("F[Containment Action]")
    lines.append("G[Block IP / Isolate Host]")
    lines.append("H[Preserve Evidence]")
    lines.append("end")
    lines.append("")

    lines.append("subgraph Human [Human-in-the-Loop]")
    lines.append("direction TB")
    lines.append("I[SOC Analyst Review]")
    lines.append("J[Approve / Escalate]")
    lines.append("end")
    lines.append("")

    lines.append("subgraph Closure [Incident Closure]")
    lines.append("direction TB")
    lines.append("K[Notify IR Team]")
    lines.append("L[Update Case & Close]")
    lines.append("end")
    lines.append("")

    # ---- Main Flow ----
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
    lines.append("J --> F")

    lines.append("")

    # ---- Styling (SOAR-like colors) ----
    lines.append("classDef intake fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,rx:6,ry:6;")
    lines.append("classDef enrich fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,rx:6,ry:6;")
    lines.append("classDef decision fill:#FFF3E0,stroke:#EF6C00,stroke-width:2px;")
    lines.append("classDef response fill:#FCE4EC,stroke:#C2185B,stroke-width:2px,rx:6,ry:6;")
    lines.append("classDef human fill:#F3E5F5,stroke:#6A1B9A,stroke-width:2px,rx:6,ry:6;")
    lines.append("classDef closure fill:#E0F2F1,stroke:#00695C,stroke-width:2px,rx:6,ry:6;")

    lines.append("")
    lines.append("class A intake")
    lines.append("class B,C,D enrich")
    lines.append("class E decision")
    lines.append("class F,G,H response")
    lines.append("class I,J human")
    lines.append("class K,L closure")

    return "\n".join(lines)
