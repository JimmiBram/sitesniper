# CLI Skeleton Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a bare minimum CLI skeleton for SiteSniper: Rich-based TUI with URL input, status, depth dropdown, max-pages input, and placeholder image area—no crawler or scraper logic yet.

**Architecture:** Single entry point `poetry run sniper` starts the app. A main module runs the Rich Live display with a layout: top = image area (placeholder), bottom = controls row (URL input, depth select, max pages) and status row. Dependencies: `rich` only. Package lives under `src/sitesniper/`.

**Tech Stack:** Python 3.14+, Poetry, Rich (Console/Live/Panel/Input/Select).

---

## Task 1: Project script and package layout

**Files:**
- Modify: `pyproject.toml`
- Create: `src/sitesniper/__init__.py`
- Create: `src/sitesniper/main.py`

**Step 1: Add Poetry script, rich dependency, and pytest**

In `pyproject.toml`:
- Add `rich` to `dependencies`.
- Add dev dependency so Task 2 tests run: `[tool.poetry.group.dev.dependencies]` with `pytest = "^8.0"`.
- Add section:

```toml
[tool.poetry.scripts]
sniper = "sitesniper.main:main"
```

**Step 2: Create package and stub main**

- Create `src/sitesniper/__init__.py` (can be empty or `"""SiteSniper - console website screenshot scraper."""`).
- Create `src/sitesniper/main.py` with a `main()` that prints a single line and exits (e.g. `print("SiteSniper CLI")`).

**Step 3: Verify script runs**

Run: `poetry install` then `poetry run sniper`
Expected: Output "SiteSniper CLI" (or equivalent) and exit.

**Step 4: Commit**

```bash
git add pyproject.toml src/sitesniper/__init__.py src/sitesniper/main.py
git commit -m "chore: add sniper script and package layout"
```

---

## Task 2: Rich Live skeleton with layout

**Files:**
- Create: `src/sitesniper/ui.py`
- Modify: `src/sitesniper/main.py`

**Step 1: Write the failing test**

Create `tests/test_ui.py`:

```python
from sitesniper.ui import build_layout_text

def test_build_layout_includes_image_area_and_controls():
    text = build_layout_text(url="", depth=1, max_pages=10, status="Ready")
    assert "image" in text.lower() or "screenshot" in text.lower()
    assert "Ready" in text
    assert "1" in text
    assert "10" in text
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_ui.py -v`
Expected: FAIL (e.g. module/function not found).

**Step 3: Implement minimal layout**

- In `src/sitesniper/ui.py`: define `build_layout_text(url: str, depth: int, max_pages: int, status: str) -> str` that returns a single string containing placeholders for: image area, url, depth, max_pages, status (e.g. a simple multi-line string or Rich renderable rendered to string for testing).
- In `src/sitesniper/main.py`: call `build_layout_text` with defaults and print it, then exit (no Live loop yet).

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_ui.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add src/sitesniper/ui.py src/sitesniper/main.py tests/test_ui.py
git commit -m "feat: add layout text builder for CLI skeleton"
```

---

## Task 3: Run CLI with Rich Live and placeholder panels

**Files:**
- Modify: `src/sitesniper/ui.py`
- Modify: `src/sitesniper/main.py`

**Step 1: Implement Live UI with panels**

- In `ui.py`: build a Rich layout (e.g. `Layout`) with:
  - Top: main panel for “image area” (placeholder text like “Screenshots will appear here”).
  - Bottom: two rows — (1) controls: URL placeholder, depth 1–3 placeholder, max pages placeholder; (2) status line.
- Expose a function that returns this layout (or a `Group`/renderable) for a given state (url, depth, max_pages, status).

**Step 2: Run with Live in main**

- In `main.py`: use `rich.console.Live(ui_renderable, refresh_per_second=4)` and `live.start()`, then sleep a few seconds (e.g. 3), then `live.stop()`. No input handling yet—just display.

**Step 3: Manual verification**

Run: `poetry run sniper`
Expected: TUI appears for a few seconds with image area and controls/status placeholders, then exits.

**Step 4: Commit**

```bash
git add src/sitesniper/ui.py src/sitesniper/main.py
git commit -m "feat: run CLI with Rich Live and placeholder panels"
```

---

## Out of scope (later)

- URL validation and scraper/crawler logic.
- Real input fields (e.g. `rich` input widget or `prompt`) and event loop.
- Saving screenshots to `/Data/Scrapes`.

---

## Execution Handoff

Plan complete and saved to `docs/plans/2025-03-06-cli-skeleton.md`.

**Two execution options:**

1. **Subagent-Driven (this session)** – I dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Parallel Session (separate)** – Open a new session with executing-plans and run the plan task-by-task with checkpoints.

Which approach?
