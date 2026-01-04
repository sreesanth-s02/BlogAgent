def build_html(
    title: str,
    paragraphs: list[str],
    image_url: str | None = None,
    position: str = "top"
) -> str:
    html = f"<h1>{title}</h1>"

    if image_url and position == "top":
        html += (
            f'<img src="{image_url}" '
            'style="max-width:100%;height:auto;margin:20px 0;" />'
        )

    for p in paragraphs:
        html += f"<p>{p}</p>"

    if image_url and position == "bottom":
        html += (
            f'<img src="{image_url}" '
            'style="max-width:100%;height:auto;margin:20px 0;" />'
        )

    return html
