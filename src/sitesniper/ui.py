import asyncio
from pathlib import Path

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import Frame, TextArea
from PIL import Image, ImageDraw

from urllib.parse import urlparse

from sitesniper.screenshot import (
    capture_screenshot_async,
    get_same_domain_links_async,
)

# One char per 2x2 block: dark -> light (full, lower half, upper half, space)
_BLOCK_CHARS = ("\u2588", "\u2584", "\u2580", " ")


def _image_to_block_art(path: Path, cols: int = 78, rows: int = 10) -> str:
    """Convert an image file to terminal block-art (grayscale, 4 shades)."""
    img = Image.open(path).convert("RGB")
    w, h = img.size
    # Target 2x2 pixels per character
    target_w, target_h = cols * 2, rows * 2
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    pixels = img.load()
    lines = []
    for row in range(rows):
        line_chars = []
        for col in range(cols):
            # 2x2 block: (r0,c0), (r0,c1), (r1,c0), (r1,c1)
            r0, r1 = row * 2, row * 2 + 1
            c0, c1 = col * 2, col * 2 + 1
            total = 0
            for r in (r0, r1):
                for c in (c0, c1):
                    total += sum(pixels[c, r]) / 3
            avg = total / 4  # 0..255
            idx = min(3, int(avg / 64))  # 0->full, 1->lower, 2->upper, 3->space
            line_chars.append(_BLOCK_CHARS[idx])
        lines.append("".join(line_chars))
    return "\n".join(lines)
from rich.console import Group
from rich.layout import Layout as RichLayout
from rich.panel import Panel
from rich.text import Text
from rich_pixels import Pixels


def _welcome_image() -> Pixels:
    """Build a small welcome image for the screenshot area (Rich-compatible)."""
    width, height = 320, 120
    img = Image.new("RGB", (width, height), color=(30, 35, 45))
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, width - 10, height - 10], outline=(70, 130, 180), width=2)
    draw.rectangle([15, 15, width - 15, height - 15], outline=(50, 90, 130), width=1)
    try:
        draw.text((width // 2 - 50, height // 2 - 20), "SiteSniper", fill=(135, 206, 250))
        draw.text((width // 2 - 35, height // 2 + 5), "Welcome", fill=(176, 196, 222))
    except Exception:
        pass
    return Pixels.from_image(img)


def _url_input_container():
    """One-line URL input field (single line tall)."""
    return TextArea(
        height=1,
        multiline=False,
        wrap_lines=False,
        prompt="URL: ",
    )


# Base directory for scrape output (frontpage + same-domain links).
DATA_DIR = Path("data")


def build_app(
    depth: int = 1,
    max_pages: int = 10,
    status: str = "Ready",
) -> Application:
    """Build prompt_toolkit Application with working one-line URL input and status."""
    url_field = _url_input_container()
    default_message = "Screenshots will appear here. Enter a URL and press Enter to capture."
    state: dict[str, str] = {"status": status, "main_text": default_message}

    main_area = Window(
        content=FormattedTextControl(text=lambda: state["main_text"]),
        height=10,
    )
    controls_row = VSplit(
        [
            url_field,
            Window(width=1, char="|"),
            Window(
                content=FormattedTextControl(
                    text=f"Depth: {depth} (1–3)  |  Max pages: {max_pages}",
                ),
                height=1,
            ),
        ],
        height=1,
    )
    status_row = Window(
        content=FormattedTextControl(text=lambda: state["status"]),
        height=1,
    )

    root = HSplit(
        [
            Frame(main_area, title="Screenshot", style="bg:default fg:blue"),
            Frame(controls_row, title="Controls", style="dim"),
            Frame(status_row, title="Status", style="green"),
        ],
    )

    kb = KeyBindings()

    @kb.add("c-c")
    @kb.add("c-q")
    def _(event):
        event.app.exit()

    @kb.add("enter")
    def _on_enter(event):
        if not event.app.layout.has_focus(url_field):
            return
        url = url_field.buffer.text.strip()
        if not url:
            state["status"] = "Enter a URL and press Enter to capture."
            event.app.invalidate()
            return
        state["status"] = "Finding same-domain links..."
        event.app.invalidate()
        app = event.app
        cap_max = max_pages

        async def _do_capture():
            links = await get_same_domain_links_async(url)
            # Frontpage first, then same-domain links, up to max_pages
            urls_to_capture = [url] + [u for u in links if u != url][: cap_max - 1]
            urls_to_capture = urls_to_capture[:cap_max]
            netloc = urlparse(url).netloc or "unknown"
            safe_dir = netloc.replace(":", "_")
            output_dir = DATA_DIR / safe_dir
            output_dir.mkdir(parents=True, exist_ok=True)
            paths: list[Path] = []
            for i, page_url in enumerate(urls_to_capture):
                state["status"] = f"Capturing {i + 1}/{len(urls_to_capture)}: {page_url[:50]}..."
                app.invalidate()
                path = await capture_screenshot_async(
                    page_url, path=output_dir / f"{i}.png"
                )
                if isinstance(path, Path):
                    paths.append(path)
            if paths:
                state["status"] = f"Saved {len(paths)} to {output_dir}"
                state["main_text"] = _image_to_block_art(paths[-1])
            else:
                state["status"] = "No pages captured."
            app.invalidate()

        loop = getattr(app, "loop", None) or asyncio.get_running_loop()
        asyncio.ensure_future(_do_capture(), loop=loop)

    return Application(
        layout=Layout(root, focused_element=url_field),
        key_bindings=kb,
        full_screen=True,
    )


def build_live_renderable(
    url: str,
    depth: int,
    max_pages: int,
    status: str,
):
    """Return a Rich renderable (Layout) for Live display: image area, controls, status."""
    layout = RichLayout()
    layout.split_column(
        RichLayout(name="main"),
        RichLayout(name="bottom"),
    )
    layout["bottom"].split_column(
        RichLayout(name="controls"),
        RichLayout(name="status"),
    )
    layout["main"].update(
        Panel(
            Group(
                _welcome_image(),
                Text("\nScreenshots will appear here", style="dim"),
            ),
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
