from graphviz import Digraph


def generate_soar_svg(playbook_blocks):
    """
    Generates an enterprise-grade SOAR execution flow diagram as SVG.
    """

    dot = Digraph(format="svg")
    dot.attr(rankdir="TB", bgcolor="white")

    # Styles
    styles = {
        "process": {
            "shape": "box",
            "style": "filled,rounded",
            "fillcolor": "#2563eb",  # blue
            "fontcolor": "white",
        },
        "decision": {
            "shape": "diamond",
            "style": "filled",
            "fillcolor": "#f59e0b",  # amber
            "fontcolor": "black",
        },
        "auto": {
            "shape": "box",
            "style": "filled,rounded",
            "fillcolor": "#dc2626",  # red
            "fontcolor": "white",
        },
        "human": {
            "shape": "box",
            "style": "filled,rounded",
            "fillcolor": "#7c3aed",  # purple
            "fontcolor": "white",
        },
        "evidence": {
            "shape": "box",
            "style": "filled,rounded",
            "fillcolor": "#0ea5e9",  # cyan
            "fontcolor": "white",
        },
        "notify": {
            "shape": "box",
            "style": "filled,rounded",
            "fillcolor": "#16a34a",  # green
            "fontcolor": "white",
        },
    }

    # Core flow
    dot.node("validate", "Alert Validation & Enrichment", **styles["process"])
    dot.node("ti", "Threat Intelligence Lookup", **styles["process"])
    dot.node("decision", "Threat Confirmed?", **styles["decision"])

    dot.edge("validate", "ti")
    dot.edge("ti", "decision")

    # Yes path
    dot.node("auto", "Auto Containment", **styles["auto"])
    dot.node("block", "Isolate Host / Block IP", **styles["auto"])
    dot.node("evidence", "Preserve Evidence", **styles["evidence"])
    dot.node("notify", "Notify IR Team", **styles["notify"])

    dot.edge("decision", "auto", label="Yes")
    dot.edge("auto", "block")
    dot.edge("block", "evidence")
    dot.edge("evidence", "notify")

    # Uncertain path
    dot.node("review", "Human Review", **styles["human"])
    dot.node("soc", "SOC Analyst Decision", **styles["human"])

    dot.edge("decision", "review", label="Uncertain")
    dot.edge("review", "soc")

    return dot
