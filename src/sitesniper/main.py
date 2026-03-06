from sitesniper.ui import build_app


def main() -> None:
    app = build_app(depth=1, max_pages=10, status="Ready")
    app.run()
