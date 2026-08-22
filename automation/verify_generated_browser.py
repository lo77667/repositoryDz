#!/usr/bin/env python3
"""Run the generated HTML in an isolated headless Chromium browser."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_generated_browser.py path/to/index.html")
    path = Path(sys.argv[1]).resolve()
    if not path.exists():
        raise SystemExit(f"Candidate does not exist: {path}")

    console_errors: list[str] = []
    page_errors: list[str] = []
    requests: list[str] = []
    result: dict[str, object] = {"path": str(path), "console_errors": console_errors, "page_errors": page_errors, "network_requests": requests}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", headless=True, args=["--no-sandbox", "--disable-gpu"])
        page = browser.new_page()
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda exception: page_errors.append(str(exception)))
        page.on("request", lambda request: requests.append(request.url) if request.resource_type not in {"document"} else None)
        try:
            page.goto(path.as_uri(), wait_until="load", timeout=15_000)
            page.wait_for_timeout(250)
            primary = page.locator('[data-factory-action="primary"]')
            count = primary.count()
            result["primary_controls"] = count
            if count != 1:
                raise AssertionError(f"expected exactly one primary control, found {count}")
            if not primary.is_visible():
                raise AssertionError("primary control is not visible")
            primary.click(timeout=5_000)
            page.wait_for_timeout(250)
            result["clicked"] = True
            result["title"] = page.title()
        except (PlaywrightTimeoutError, AssertionError) as exc:
            result["failure"] = str(exc)
        finally:
            browser.close()

    print(json.dumps(result, ensure_ascii=False))
    if console_errors or page_errors or requests or result.get("failure"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
