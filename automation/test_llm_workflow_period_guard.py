#!/usr/bin/env python3
"""Static regression checks for the LLM workflow period guard."""

from __future__ import annotations

from pathlib import Path

workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/phase-4-llm-gated-factory.yml").read_text(encoding="utf-8")
guard_position = workflow.index("- name: Guard weekly period before picking an idea")
pick_position = workflow.index("- name: Pick one generate idea")
assert guard_position < pick_position
assert "id: period_guard" in workflow
assert "python3 automation/guard_weekly_period.py --period" in workflow
assert "python3 automation/guard_weekly_period.py" in workflow
assert "if: ${{ steps.period_guard.outputs.decision == 'proceed' }}" in workflow
assert "- name: Send already-published notification" in workflow
assert "steps.period_guard.outputs.decision == 'already_published'" in workflow
assert "- name: Send failure notification" in workflow
assert "- name: Commit and push the accepted artifact and backlog state\n        if: ${{ steps.period_guard.outputs.decision == 'proceed' }}" in workflow
assert "- name: Wait for the published Pages path\n        if: ${{ steps.period_guard.outputs.decision == 'proceed' }}" in workflow

print("LLM workflow period guard tests passed")
