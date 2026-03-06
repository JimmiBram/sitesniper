from sitesniper.ui import build_layout_text


def test_build_layout_includes_image_area_and_controls():
    text = build_layout_text(url="", depth=1, max_pages=10, status="Ready")
    assert "image" in text.lower() or "screenshot" in text.lower()
    assert "Ready" in text
    assert "1" in text
    assert "10" in text
