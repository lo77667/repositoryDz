# Autonomous Weekly Micro-Product Factory

This repository is the foundation for a phone-operated, zero-budget factory that can ship small static micro-products through GitHub Actions. The system is designed around three separated layers: an idea backlog, deterministic or generated builds, and publication plus notification.

## Current state

> **Phase 3 — Expanded idea layer and deterministic templates: complete.**

The repository is public, the first manually built Tier A product is live, the weekly heartbeat is active, and Phase 3 now provides a versioned idea backlog plus four deterministic Tier A templates. The weekly workflow selects a not-yet-built idea, renders the matching template, validates it, pushes it to `main`, waits for GitHub Pages, and notifies Telegram. No deployment to Manus was used or configured.

## Phase gates

Each phase is a gate. The next phase must not begin until the current phase has been reviewed and tested successfully.

| Phase | Scope | State |
|---|---|---|
| 0 | Public repository, Pages readiness, and manual Telegram test plumbing | Complete |
| 1 | One manually built Tier A product, end to end | Complete |
| 2 | Weekly automation for the first template | Complete |
| 3 | Backlog expansion and additional deterministic templates | Complete |
| 4 | LLM generation behind an automated verification gate | Not started |
| 5 | LLM provider fallback chain | Not started |
| 6 | Catalog and lightweight analytics | Not started |
| 7 | Public idea intake and feedback-informed prioritization | Not started |
| 8 | Hardening and scale | Not started |

## Operating constraints

The project must remain zero-budget, phone-operable, and based on a public GitHub repository. Credentials belong only in GitHub Actions Secrets. Weekly runs must not require a manual intervention after bootstrap. This repository does not use Manus for hosting or publication.

## Phase 0 audit record

| Check | Result | Evidence |
|---|---|---|
| Repository visibility | Passed | `lo77667/repositoryDz` is public |
| Main branch content | Passed | Commit `79e7743a410162e6bd5d0967fdb414e1f7ff3f36` |
| Workflow discovery | Passed | `Phase 0 — Telegram plumbing test` is active |
| Manual workflow execution | Passed | Run [32600240785](https://github.com/lo77667/repositoryDz/actions/runs/32600240785) completed successfully after both secrets were added |
| GitHub Pages configuration | Passed | Status `built`; source is `main` and `/`; URL: https://lo77667.github.io/repositoryDz/ |
| Manus publication | Intentionally not used | Outside the approved scope |

## Phase 1 product

**شرارة منتج** is available at [https://lo77667.github.io/repositoryDz/products/idea-mashup/](https://lo77667.github.io/repositoryDz/products/idea-mashup/). It generates an initial product hypothesis from a hand-authored audience, problem, format, and differentiator. It supports generation, clipboard copy, reset, and local browser persistence without an account or external connection.

## Phase 1 audit record

| Check | Result | Evidence |
|---|---|---|
| Manual artifact build | Passed | Commit `e4447b23c764b641985ffe0cfc4d91fd0315b448` |
| Static validation | Passed | Required controls, inline JavaScript syntax, no external dependencies or network APIs |
| Public Pages path | Passed | HTTP 200 after Pages build reached `built` |
| Browser interaction | Passed | Generate, copy, reset, and refresh persistence tested on the live URL |
| Launch notification | Passed | [Telegram workflow run 32600921582](https://github.com/lo77667/repositoryDz/actions/runs/32600921582) |
| Manus publication | Intentionally not used | Outside the approved scope |

## Phase 2 automation

The active workflow [Phase 2 — weekly factory heartbeat](.github/workflows/phase-2-weekly-factory.yml) runs every Monday at 09:00 UTC and can also be started manually with an optional `YYYY-wNN` period. It uses the local deterministic builder and validator, so it requires no LLM and no paid provider. Each period is placed under `products/weekly/YYYY-wNN/`, and an existing different artifact is never overwritten.

The successful verification run [32602071976](https://github.com/lo77667/repositoryDz/actions/runs/32602071976) created [the 2026-w35 product](https://lo77667.github.io/repositoryDz/products/weekly/2026-w35/), verified its public HTTP 200 response, and sent a Telegram success notification. The full audit is in [docs/PHASE-2-TEST-RECORD.md](docs/PHASE-2-TEST-RECORD.md). The runner displayed a non-blocking Node.js 20 deprecation annotation for pinned third-party actions; this is recorded for future dependency maintenance.

## Phase 3 expansion

The versioned backlog is stored in [`ideas/backlog.json`](ideas/backlog.json). It contains the required idea metadata, strategy tags, statuses, difficulty, and category fields. The picker in [`automation/pick_idea.py`](automation/pick_idea.py) selects only `backlog` ideas, uses a stable period-based hash, and marks the selected record as `built` with its period.

The deterministic template library now includes the original idea mashup plus [`templates/converter.html`](templates/converter.html), [`templates/visual-toy.html`](templates/visual-toy.html), and [`templates/text-tool.html`](templates/text-tool.html). The validator adapts its required interaction checks to the selected strategy and uses only standard Python libraries on the GitHub runner.

The end-to-end verification selected **بطاقات القرار** with `template:visual-toy` for `2026-w36`. The resulting product is available at [https://lo77667.github.io/repositoryDz/products/weekly/2026-w36/](https://lo77667.github.io/repositoryDz/products/weekly/2026-w36/) and the successful run is [32602565367](https://github.com/lo77667/repositoryDz/actions/runs/32602565367). Full details are in [`docs/PHASE-3-TEST-RECORD.md`](docs/PHASE-3-TEST-RECORD.md). Phase 4, LLM generation, remains not started.
