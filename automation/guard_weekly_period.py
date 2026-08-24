#!/usr/bin/env python3
"""Guard weekly publishing against reusing an existing period."""

from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path

from period_utils import require_period


def current_period(today: date) -> str:
    year, week, _ = today.isocalendar()
    return f"{year}-w{week:02d}"


def write_output(values: dict[str, str]) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if not output:
        return
    with open(output, "a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--period", default="", help="Explicit YYYY-wNN period; empty means current ISO week")
    parser.add_argument(
        "--products-root",
        default=str(Path(__file__).resolve().parents[1] / "products/weekly"),
        help="Root directory containing weekly product folders",
    )
    args = parser.parse_args()
    explicit_period = args.period.strip()
    try:
        period = require_period(explicit_period or current_period(date.today()))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    output_path = Path(args.products_root) / period / "index.html"
    if output_path.exists():
        if explicit_period:
            raise SystemExit(
                f"Period {period} is already published at {output_path}; refusing manual reuse."
            )
        values = {
            "period": period,
            "decision": "already_published",
            "path": str(output_path),
            "url": f"https://lo77667.github.io/repositoryDz/products/weekly/{period}/",
        }
        write_output(values)
        print(f"Period {period} is already published; no-op without selecting an idea.")
        return

    values = {
        "period": period,
        "decision": "proceed",
        "path": str(output_path),
        "url": f"https://lo77667.github.io/repositoryDz/products/weekly/{period}/",
    }
    write_output(values)
    print(f"Period {period} is unused; weekly build may proceed.")


if __name__ == "__main__":
    main()
