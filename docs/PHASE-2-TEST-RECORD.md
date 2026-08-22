# Phase 2 test record

## Local verification

The deterministic builder generated `products/weekly/2026-w34/index.html` from the Phase 1 template using an ISO-week period. The generated artifact passed the standard-library validator, the inline JavaScript syntax check, the no-external-dependency check, the no-network-API check, and `git diff --check`.

The first GitHub run exposed one real environment defect: the validator imported BeautifulSoup, which is not installed on a clean GitHub-hosted runner. The validator was rewritten to use Python's standard library only. Local validation passed after the fix, and the corrected commit was pushed.

## End-to-end manual run

The weekly factory was manually run with the explicit period `2026-w35` to avoid waiting for the Monday schedule. Run [32602071976](https://github.com/lo77667/repositoryDz/actions/runs/32602071976) completed successfully.

All job steps passed: checkout of `main`, Python setup, deterministic build, generated-artifact validation, commit and push, Pages reachability check, and Telegram success notification. The run created `products/weekly/2026-w35/index.html` in commit `48b6295299e6404e68eeba082eb3d5140c0ceb2d`.

The published URL returned HTTP 200 and contained the injected weekly payload:

`https://lo77667.github.io/repositoryDz/products/weekly/2026-w35/`

## Schedule and scope review

The workflow is active and contains both a Monday 09:00 UTC schedule and a manual trigger. The manual trigger accepts an optional period in `YYYY-wNN` format. Concurrency prevents overlapping runs from racing on `main`.

Phase 2 remains Tier A and deterministic. It does not call an LLM, does not use a paid service, does not overwrite the Phase 1 artifact, does not add analytics or public idea intake, and does not use Manus for hosting or publication.

The GitHub runner displayed a Node.js 20 deprecation annotation for the pinned checkout and setup actions. It did not affect the successful run and is recorded for a future dependency-maintenance pass.
