# Autonomous Weekly Micro-Product Factory

This repository is the foundation for a phone-operated, zero-budget factory that can ship small static micro-products through GitHub Actions. The system is designed around three separated layers: an idea backlog, deterministic or generated builds, and publication plus notification.

## Current state

> **Phase 0 — Foundation: complete.**

The repository is public, the Phase 0 workflow is present on `main`, and the workflow was manually dispatched for verification. No product site was created in this phase, and no deployment to Manus was used or configured.

The Telegram test requires two GitHub Actions secrets, `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. Secrets are never stored in this repository. After the secrets were added, the manual verification succeeded. GitHub Pages is configured from the `main` branch and the root folder. No product site was created in this phase, and no deployment to Manus was used or configured.

## Phase gates

Each phase is a gate. The next phase must not begin until the current phase has been reviewed and tested successfully.

| Phase | Scope | State |
|---|---|---|
| 0 | Public repository, Pages readiness, and manual Telegram test plumbing | Complete |
| 1 | One manually built Tier A product, end to end | Not started |
| 2 | Weekly automation for the first template | Not started |
| 3 | Backlog expansion and additional deterministic templates | Not started |
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
