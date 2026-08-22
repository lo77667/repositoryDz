# Autonomous Weekly Micro-Product Factory

This repository is the foundation for a phone-operated, zero-budget factory that can ship small static micro-products through GitHub Actions. The system is designed around three separated layers: an idea backlog, deterministic or generated builds, and publication plus notification.

## Current state

> **Phase 0 — Foundation: in progress.**

The repository is public and ready for GitHub Actions configuration. The Phase 0 workflow is intentionally limited to a manually triggered Telegram plumbing test. No product site is created in this phase, and no deployment to Manus is used or configured.

The Telegram test requires two GitHub Actions secrets, `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. Secrets are never stored in this repository. The workflow will report a clear failure if either secret is missing and will send a minimal test message only after the operator manually starts the workflow.

## Phase gates

Each phase is a gate. The next phase must not begin until the current phase has been reviewed and tested successfully.

| Phase | Scope | State |
|---|---|---|
| 0 | Public repository, Pages readiness, and manual Telegram test plumbing | In progress |
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
