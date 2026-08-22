# Phase 2 automation research

## Verified GitHub behavior

The GitHub Actions documentation confirms that workflows can be triggered by repository events, a schedule, or manual `workflow_dispatch` execution. The workflow syntax documentation confirms that `schedule` uses five-field POSIX cron syntax, runs on the latest commit of the default branch, and supports a minimum interval of five minutes. Scheduled runs use UTC by default; a timezone can be supplied when needed.

For this project, the weekly workflow will use one explicit `schedule` entry and `workflow_dispatch` together. The schedule will run every Monday at 09:00 UTC, while `workflow_dispatch` will provide safe manual verification. The workflow will operate on the default `main` branch and use a narrow `permissions` block.

The relevant official references are:

1. https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows — Events that trigger workflows.
2. https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax — Workflow syntax for GitHub Actions.
3. https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site — Configuring a publishing source for GitHub Pages.

## Phase 2 design decision

The weekly build remains Tier A and deterministic. It will select one entry from a versioned local pool using an ISO week-derived index, generate a self-contained `index.html` under `products/weekly/<week-slug>/`, validate the result, commit only if the path is new, push to `main`, wait for Pages to build, and send a Telegram message with the published URL. A manual run will use the same deterministic selection for the current ISO week, so verification does not create an unbounded number of duplicate products.

The weekly workflow will not call an LLM, will not use external APIs except the Telegram notification endpoint, will not overwrite the Phase 1 product, and will not introduce Manus hosting or deployment.
