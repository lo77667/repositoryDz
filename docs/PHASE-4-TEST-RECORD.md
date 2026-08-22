# Phase 4 test record

## Local contract and safety tests

The local mock provider first returned an unsafe candidate containing an external URL and `fetch`. The generator rejected it with the static safety gate, passed the exact failure reasons into the repair prompt, and accepted the corrected candidate on attempt 2. The configured limit remained two repairs, for three total candidates maximum.

A second isolated mock run returned three invalid candidates. The orchestrator stopped after exactly three attempts with an explicit `rejected` result. The deterministic fallback builder then created a safe placeholder. Both the static gate and the isolated Chromium browser gate passed for the fallback: zero console errors, zero page errors, zero network requests, exactly one visible primary control, and a successful click.

The workflow YAML, Python source files, and provider-neutral configuration passed local syntax checks. The provider key never appears in repository files or diagnostic output.

## Real GitHub Actions run

The first real run for `2026-w37` completed safely in `fallback` mode. It published a placeholder because the LLM candidate was not accepted or available in that run; it did not publish unverified generated code. The fallback URL returned HTTP 200 and passed the same static and browser gates.

After the diagnostic improvement, the second real run was executed for `2026-w38` in [GitHub Actions run 32605209546](https://github.com/lo77667/repositoryDz/actions/runs/32605209546). It completed successfully in `generated` mode, confirming that the configured LLM provider returned a candidate accepted by the safety gate and the isolated browser gate.

The selected backlog idea was `generate-001`, **ناقد صفحة الدفع**. The run created `products/weekly/2026-w38/index.html`, marked the idea `built` with `built_period: 2026-w38`, pushed commit `966a1cea349cc18cdafcd54b36326a7920e00812`, waited for GitHub Pages, and sent the successful Telegram notification.

The public artifact is:

`https://lo77667.github.io/repositoryDz/products/weekly/2026-w38/`

The URL returned HTTP 200, the live content matched the main-branch artifact byte-for-byte, and GitHub Pages reported `built` with no error. The artifact is 5,366 bytes and contains exactly one `data-factory-action="primary"` control.

## Live interaction review

The public page loaded in Arabic RTL and displayed seven checkout-quality questions. Clicking **تحليل صفحة الدفع** rendered a live `0%` result, the status **تحتاج إلى تحسين**, and an actionable recommendation list. The browser interaction completed without a visible error.

## Scope and limitations

Phase 4 now has a manual-only LLM workflow with a strict safety gate, bounded repair loop, isolated browser verification, and deterministic fallback. It does not yet add weekly scheduling for LLM generation; that remains intentionally deferred until the manual path has been reviewed. The non-blocking Node.js 20 deprecation annotation from GitHub-hosted actions remains a maintenance note.
