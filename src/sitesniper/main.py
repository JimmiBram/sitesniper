import time

from rich.live import Live

from sitesniper.ui import build_live_renderable


def main() -> None:
    renderable = build_live_renderable(
        url="", depth=1, max_pages=10, status="Ready"
    )
    with Live(renderable, refresh_per_second=4) as _:
        time.sleep(3)
