def render_mermaid_flow(blocks):
    lines = ["flowchart LR"]

    for b in blocks:
        node_shape = {
            "process": "[",
            "action": "[",
            "decision": "{",
        }[b["type"]]

        close_shape = {
            "process": "]",
            "action": "]",
            "decision": "}",
        }[b["type"]]

        lines.append(f'{b["id"]}{node_shape}{b["title"]}{close_shape}')

        if b.get("on_true"):
            lines.append(f'{b["id"]} -->|Yes| {b["on_true"]}')
        if b.get("on_false"):
            lines.append(f'{b["id"]} -->|No| {b["on_false"]}')

    return "\n".join(lines)
