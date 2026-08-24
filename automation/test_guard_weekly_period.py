#!/usr/bin/env python3
"""Deterministic tests for the weekly period guard."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("guard_weekly_period.py")


def run(*args: str, output: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if output:
        env["GITHUB_OUTPUT"] = str(output)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    output = root / "github-output.txt"
    fresh = run("--period", "2099-w01", "--products-root", str(root / "weekly"), output=output)
    assert fresh.returncode == 0, fresh.stderr
    assert "proceed" in output.read_text(encoding="utf-8")

    for invalid_period in ("2026-w00", "2026-w54", "2026-w99"):
        invalid = run("--period", invalid_period, "--products-root", str(root / "weekly"))
        assert invalid.returncode != 0
        assert "ISO week" in invalid.stderr

    existing = root / "weekly" / "2099-w02" / "index.html"
    existing.parent.mkdir(parents=True)
    existing.write_text("<!DOCTYPE html>", encoding="utf-8")

    scheduled_like = run("--products-root", str(root / "weekly"), output=output)
    # The process date is not 2099-w02, so test the no-op branch with a helper-like
    # current-period override through an explicit temporary invocation below.
    assert scheduled_like.returncode == 0

    no_op = run("--period", "2099-w02", "--products-root", str(root / "weekly"))
    assert no_op.returncode != 0, "explicit manual reuse must be rejected"
    assert "already published" in no_op.stderr

    # Exercise the scheduled/no-input branch by creating today's ISO period.
    from datetime import date
    iso = date.today().isocalendar()
    today_period = f"{iso.year}-w{iso.week:02d}"
    today_path = root / "weekly" / today_period / "index.html"
    today_path.parent.mkdir(parents=True, exist_ok=True)
    today_path.write_text("<!DOCTYPE html>", encoding="utf-8")
    scheduled = run("--products-root", str(root / "weekly"), output=output)
    assert scheduled.returncode == 0, scheduled.stderr
    assert "already_published" in output.read_text(encoding="utf-8")
    assert "no-op" in scheduled.stdout

print("weekly period guard tests passed")
