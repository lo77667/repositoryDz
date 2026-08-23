#!/usr/bin/env python3
"""Verify the static catalog in isolated Chromium."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from analytics_policy import is_allowed_analytics_url
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_catalog_browser.py index.html")
    path = Path(sys.argv[1]).resolve()
    if not path.exists():
        raise SystemExit(f"Catalog does not exist: {path}")
    console_errors: list[str] = []
    page_errors: list[str] = []
    network_requests: list[str] = []
    analytics_requests: list[str] = []
    result: dict[str, object] = {
        "path": str(path),
        "console_errors": console_errors,
        "page_errors": page_errors,
        "network_requests": network_requests,
        "analytics_requests": analytics_requests,
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", headless=True, args=["--no-sandbox", "--disable-gpu"])
        page = browser.new_page()
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda exception: page_errors.append(str(exception)))

        def record_request(event):
            if event.resource_type == "document":
                return
            if is_allowed_analytics_url(event.url):
                analytics_requests.append(event.url)
            else:
                network_requests.append(event.url)

        page.on("request", record_request)
        try:
            page.goto(path.as_uri(), wait_until="load", timeout=15_000)
            page.wait_for_timeout(500)
            cards = page.locator("article.card")
            links = page.locator("a.open")
            result["cards"] = cards.count()
            result["links"] = links.count()
            result["title"] = page.title()
            if cards.count() < 1 or links.count() != cards.count():
                raise AssertionError("catalog cards and links are not aligned")
            if not page.locator("h1").is_visible():
                raise AssertionError("catalog heading is not visible")
            links.first.click(timeout=5_000)
            page.wait_for_timeout(250)
            result["clicked_first_product"] = True
        except (PlaywrightTimeoutError, AssertionError) as exc:
            result["failure"] = str(exc)
        finally:
            browser.close()
    print(json.dumps(result, ensure_ascii=False))
    if console_errors or page_errors or network_requests or result.get("failure"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
