# core/diagram_engine.py

from typing import List, Dict


def build_soar_mermaid(blocks: List[Dict]) -> str:
    """
    Build a SOAR-style Mermaid diagram with dynamic lane mapping
    based on LLM block 'type', approximating Splunk SOAR visuals.
    """

    lines = []
    lines.append("flowchart LR")
    lines.append("")

    # -------------------------------------------------
    # Lane containers (subgraphs)
    # -------------------------------------------------
    lanes = {
        "intake": [],
        "enrichment": [],
        "decision": [],
        "response": [],
        "human": [],
        "closure": []
    }

    # Always start with Intake
    lanes["intake"].append(("START", "SIEM Alert Received"))

    # Assign blocks dynamically
    for idx, block in enumerate(blocks, start=1):
        block_id = f"B{idx}"
        title = block.get("title", "Unnamed Step")
        block_type = block.get("type", "automation")

        if block_type == "enrichment":
            lanes["enrichment"].append((block_id, title))
        elif block_type == "decision":
            lanes["decision"].append((block_id, title))
        elif block_type == "human":
            lanes["human"].append((block_id, title))
        else:
            lanes["response"].append((block_id, title))

    # Always end with Closure
    lanes["closure"].append(("END", "Update Incident & Close"))

    # -------------------------------------------------
    # Render subgraphs
    # -------------------------------------------------
    def render_lane(name: str, title: str, direction="TB"):
        lines.append(f"subgraph {name.upper()} [{title}]")
        lines.append(f"direction {direction}")
        for node_id, label in lanes[name]:
            if "?" in label:
                lines.append(f'{node_id}{{{label}}}')
            else:
                lines.append(f'{node_id}["{label}"]')
        lines.append("end")
        lines.append("")

    render_lane("intake", "Alert Intake")
    render_lane("enrichment", "Context Enrichment")
    render_lane("decision", "Decision")
    render_lane("response", "Automated Response")
    render_lane("human", "Human-in-the-Loop")
    render_lane("closure", "Incident Closure")

    # -------------------------------------------------
    # Sequential flow (left → right)
    # -------------------------------------------------
    previous = "START"

    for lane_name in ["enrichment", "decision", "response", "human"]:
        for node_id, _ in lanes[lane_name]:
            lines.append(f"{previous} --> {node_id}")
            previous = node_id

    lines.append(f"{previous} --> END")
    lines.append("")

    # -------------------------------------------------
    # Styling (Splunk SOAR–like)
    # -------------------------------------------------
    lines.append("classDef intake fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,rx:6,ry:6;")
    lines.append("classDef enrichment fill:#E0F7FA,stroke:#00838F,stroke-width:2px,rx:6,ry:6;")
    lines.append("classDef decision fill:#FFF3E0,stroke:#EF6C00,stroke-width:2px;")
    lines.append("classDef response fill:#F3E5F5,stroke:#6A1B9A,stroke-width:2px,rx:6,ry:6;")
    lines.append("classDef human fill:#EDE7F6,stroke:#4527A0,stroke-width:2px,rx:6,ry:6;")
    lines.append("classDef closure fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,rx:6,ry:6;")
    lines.append("")

    for node_id, _ in lanes["intake"]:
        lines.append(f"class {node_id} intake")

    for node_id, _ in lanes["enrichment"]:
        lines.append(f"class {node_id} enrichment")

    for node_id, _ in lanes["decision"]:
        lines.append(f"class {node_id} decision")

    for node_id, _ in lanes["response"]:
        lines.append(f"class {node_id} response")

    for node_id, _ in lanes["human"]:
        lines.append(f"class {node_id} human")

    for node_id, _ in lanes["closure"]:
        lines.append(f"class {node_id} closure")

    return "\n".join(lines)
