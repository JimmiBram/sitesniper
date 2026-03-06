from sitesniper.ui import build_layout_text


def main() -> None:
    text = build_layout_text(url="", depth=1, max_pages=10, status="Ready")
    print(text)
