from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text


def build_live_renderable(
    url: str,
    depth: int,
    max_pages: int,
    status: str,
):
    """Return a Rich renderable (Layout) for Live display: image area, controls, status."""
    layout = Layout()
    layout.split_column(
        Layout(name="main"),
        Layout(name="bottom"),
    )
    layout["bottom"].split_column(
        Layout(name="controls"),
        Layout(name="status"),
    )
    layout["main"].update(
        Panel(
            "Screenshots will appear here",
            title="Screenshot",
            border_style="blue",
        )
    )
    controls_text = Text()
    controls_text.append("URL: ", style="bold")
    controls_text.append(url or "(none)")
    controls_text.append("  |  Depth: ", style="bold")
    controls_text.append(f"{depth} (1–3)")
    controls_text.append("  |  Max pages: ", style="bold")
    controls_text.append(str(max_pages))
    layout["controls"].update(Panel(controls_text, title="Controls", border_style="dim"))
    layout["status"].update(Panel(Text(status), title="Status", border_style="green"))
    return layout


def build_layout_text(
    url: str,
    depth: int,
    max_pages: int,
    status: str,
) -> str:
    """Return a single string with placeholders for image area, url, depth, max_pages, status."""
    return f"""┌─ Screenshot ─────────────────────────┐
│ [image area]                    │
└─────────────────────────────────┘

URL:   {url}
Depth: {depth}
Max:   {max_pages}
Status: {status}
"""
