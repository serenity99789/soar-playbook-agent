import textwrap

# -------------------------------------------------
# SOAR MERMAID DIAGRAM ENGINE
# -------------------------------------------------

def generate_soar_mermaid(playbook: dict) -> str:
    """
    Converts a structured SOAR playbook JSON into a
    professional, horizontal Mermaid diagram.
    """

    blocks = playbook.get("blocks", [])
    decisions = playbook.get("decision_points", [])

    # Group blocks by category (SOAR-style lanes)
    lanes = {
        "Enrichment": [],
        "Analysis": [],
        "Decision": [],
        "Containment": [],
        "Notification": [],
        "Governance": []
    }

    for b in blocks:
        cat = b.get("category", "Analysis")
        if cat not in lanes:
            cat = "Analysis"
        lanes[cat].append(b)

    mermaid = []
    mermaid.append("flowchart LR")
    mermaid.append("%% === SOAR EXECUTION FLOW ===")

    # -------------------------------------------------
    # STYLE DEFINITIONS (REAL SOAR LOOK)
    # -------------------------------------------------
    mermaid.extend([
        "classDef enrichment fill:#2563eb,color:#ffffff,stroke:#1e40af,stroke-width:1px;",
        "classDef analysis fill:#0ea5e9,color:#ffffff,stroke:#0369a1,stroke-width:1px;",
        "classDef decision fill:#f59e0b,color:#000000,stroke:#b45309,stroke-width:1px;",
        "classDef containment fill:#dc2626,color:#ffffff,stroke:#7f1d1d,stroke-width:1px;",
        "classDef notification fill:#16a34a,color:#ffffff,stroke:#065f46,stroke-width:1px;",
        "classDef governance fill:#7c3aed,color:#ffffff,stroke:#4c1d95,stroke-width:1px;",
    ])

    # -------------------------------------------------
    # CREATE SUBGRAPHS (LANES)
    # -------------------------------------------------
    node_ids = {}

    for lane, items in lanes.items():
        if not items:
            continue

        mermaid.append(f"subgraph {lane}")
        mermaid.append("direction LR")

        for b in items:
            node_id = b["id"].replace("-", "_")
            label = b["name"]
            node_ids[b["id"]] = node_id

            shape = "[" + label + "]"
            if b["category"] == "Decision":
                shape = "{" + label + "}"

            mermaid.append(f'{node_id}{shape}')

        mermaid.append("end")

    # -------------------------------------------------
    # CONNECTIONS (DEPENDENCIES)
    # -------------------------------------------------
    for b in blocks:
        src = node_ids.get(b["id"])
        for dep in b.get("depends_on", []):
            dst = node_ids.get(dep)
            if src and dst:
                mermaid.append(f"{dst} --> {src}")

    # -------------------------------------------------
    # DECISION BRANCHES
    # -------------------------------------------------
    for d in decisions:
        q = d["question"]
        q_id = q.replace(" ", "_").replace("?", "")
        yes_id = d["yes_path"].replace("-", "_")
        no_id = d["no_path"].replace("-", "_")

        mermaid.append(f'{q_id}{{"{q}"}}:::decision')
        mermaid.append(f"{q_id} -->|Yes| {yes_id}")
        mermaid.append(f"{q_id} -->|No| {no_id}")

    # -------------------------------------------------
    # APPLY STYLES
    # -------------------------------------------------
    for lane, items in lanes.items():
        for b in items:
            nid = node_ids[b["id"]]
            cls = lane.lower()
            mermaid.append(f"class {nid} {cls}")

    return textwrap.dedent("\n".join(mermaid))
