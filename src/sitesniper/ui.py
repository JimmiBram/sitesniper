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
