"""Isolated screenshot capture for URLs using a headless browser."""

import logging
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

_LOG_FILE = Path("log.txt")
_logger: logging.Logger | None = None


def _get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        _logger = logging.getLogger("sitesniper.screenshot")
        _logger.setLevel(logging.DEBUG)
        if not _logger.handlers:
            fh = logging.FileHandler(_LOG_FILE, mode="a", encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            )
            _logger.addHandler(fh)
    return _logger


def _same_netloc(url: str, entry_netloc: str) -> bool:
    """Return True if url has the same netloc as entry (e.g. same domain)."""
    parsed = urlparse(url)
    if not parsed.scheme or parsed.scheme not in ("http", "https"):
        return False
    return parsed.netloc.lower() == entry_netloc.lower()


async def get_same_domain_links_async(url: str) -> list[str]:
    """Load the page at url and return absolute URLs of same-domain links (deduplicated).

    Skips javascript:, mailto:, and non-http(s) links. The entry url is not included.
    """
    log = _get_logger()
    parsed = urlparse(url)
    if not parsed.netloc:
        return []
    entry_netloc = parsed.netloc.lower()
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            log.debug("get_same_domain_links goto url=%s", url)
            await page.goto(url, wait_until="domcontentloaded")
            # Get all absolute hrefs from the page
            raw_hrefs: list[str] = await page.evaluate(
                "() => Array.from(document.querySelectorAll('a[href]')).map(a => a.href)"
            )
            seen: set[str] = set()
            result: list[str] = []
            base = f"{parsed.scheme or 'https'}://{parsed.netloc}"
            for href in raw_hrefs:
                if not href or not href.strip():
                    continue
                # Resolve relative URLs (e.g. //example.com/path)
                absolute = urljoin(base, href.strip())
                parsed_link = urlparse(absolute)
                if parsed_link.scheme not in ("http", "https"):
                    continue
                if not _same_netloc(absolute, entry_netloc):
                    continue
                if absolute in seen:
                    continue
                seen.add(absolute)
                result.append(absolute)
            log.debug("get_same_domain_links found %d links for %s", len(result), url)
            return result
        finally:
            await browser.close()


async def capture_screenshot_async(
    url: str,
    path: Path | None = None,
    full_page: bool = False,
) -> Path | bytes:
    """Take a screenshot of a URL (async; safe to use inside asyncio).

    Args:
        url: The URL to capture (e.g. "https://example.com").
        path: If set, save the image to this path and return it; otherwise return PNG bytes.
        full_page: If True, capture the full scrollable page; otherwise viewport only.

    Returns:
        The path where the screenshot was saved, or the screenshot as PNG bytes if path is None.

    Raises:
        playwright._impl._api_types.Error: On navigation or screenshot failure.
    """
    log = _get_logger()
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            log.debug("goto start url=%s", url)
            await page.goto(url, wait_until="domcontentloaded")
            log.debug("goto ok url=%s", url)
            if path is not None:
                path = Path(path)
                path.parent.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=str(path), full_page=full_page)
                return path
            return await page.screenshot(full_page=full_page)
        except Exception as e:
            log.exception("goto or screenshot failed url=%s: %s", url, e)
            raise
        finally:
            await browser.close()


def capture_screenshot(
    url: str,
    path: Path | None = None,
    full_page: bool = False,
) -> Path | bytes:
    """Take a screenshot of a URL.

    Args:
        url: The URL to capture (e.g. "https://example.com").
        path: If set, save the image to this path and return it; otherwise return PNG bytes.
        full_page: If True, capture the full scrollable page; otherwise viewport only.

    Returns:
        The path where the screenshot was saved, or the screenshot as PNG bytes if path is None.

    Raises:
        playwright._impl._api_types.Error: On navigation or screenshot failure.
    """
    log = _get_logger()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            log.debug("goto start url=%s", url)
            page.goto(url, wait_until="domcontentloaded")
            log.debug("goto ok url=%s", url)
            if path is not None:
                path = Path(path)
                path.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(path), full_page=full_page)
                return path
            return page.screenshot(full_page=full_page)
        except Exception as e:
            log.exception("goto or screenshot failed url=%s: %s", url, e)
            raise
        finally:
            browser.close()
