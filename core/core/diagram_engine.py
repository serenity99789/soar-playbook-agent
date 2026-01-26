def generate_soar_svg(blocks):
    """
    Generates a professional, color-coded SOAR execution flow SVG.
    This is STATIC (deterministic) and leadership-safe.
    """

    y = 20
    step_gap = 90
    svg_elements = []

    def box(x, y, w, h, text, color, text_color="white"):
        return f"""
        <rect x="{x}" y="{y}" rx="8" ry="8" width="{w}" height="{h}"
              style="fill:{color};stroke:#333;stroke-width:1.5"/>
        <text x="{x + w/2}" y="{y + h/2 + 5}"
              text-anchor="middle"
              font-size="14"
              fill="{text_color}"
              font-family="Arial, Helvetica, sans-serif">
            {text}
        </text>
        """

    def arrow(x1, y1, x2, y2):
        return f"""
        <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"
              stroke="#333" stroke-width="2"
              marker-end="url(#arrow)"/>
        """

    svg_elements.append("""
    <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10"
                refX="6" refY="3"
                orient="auto">
            <path d="M0,0 L0,6 L9,3 z" fill="#333"/>
        </marker>
    </defs>
    """)

    x_center = 300
    prev_y = None

    for i, block in enumerate(blocks):
        title = block["title"]

        if "contain" in title.lower():
            color = "#d32f2f"   # red
        elif "review" in title.lower():
            color = "#7b1fa2"   # purple
        elif "notify" in title.lower():
            color = "#2e7d32"   # green
        elif "intelligence" in title.lower():
            color = "#1976d2"   # blue
        else:
            color = "#455a64"   # neutral

        svg_elements.append(box(x_center - 150, y, 300, 55, title, color))

        if prev_y is not None:
            svg_elements.append(
                arrow(
                    x_center,
                    prev_y + 55,
                    x_center,
                    y
                )
            )

        prev_y = y
        y += step_gap

    svg = f"""
    <svg width="600" height="{y + 40}" viewBox="0 0 600 {y + 40}"
         xmlns="http://www.w3.org/2000/svg">
        {''.join(svg_elements)}
    </svg>
    """

    return svg
