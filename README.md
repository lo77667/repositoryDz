# Autonomous Weekly Micro-Product Factory

This repository is the foundation for a phone-operated, zero-budget factory that can ship small static micro-products through GitHub Actions. The system is designed around three separated layers: an idea backlog, deterministic or generated builds, and publication plus notification.

## Current state

> **Phase 8 — hardening and scale: complete.**

The repository is public, phone-operable, and remains hosted only on GitHub Pages. The weekly Tier A path, the manually triggered LLM provider chain, the public Arabic idea intake, the catalog, and the lifecycle workflow are now protected by centralized artifact-safety rules, shared publish concurrency, stale-main refusal, verified action SHAs, and a confirmed-only retirement/revisit path. No deployment to Manus was used or configured.

## Phase gates

Each phase is a gate. The next phase must not begin until the current phase has been reviewed and tested successfully.

| Phase | Scope | State |
|---|---|---|
| 0 | Public repository, Pages readiness, and manual Telegram test plumbing | Complete |
| 1 | One manually built Tier A product, end to end | Complete |
| 2 | Weekly automation for the first template | Complete |
| 3 | Backlog expansion and additional deterministic templates | Complete |
| 4 | LLM generation behind an automated verification gate | Complete — manual rollout |
| 5 | LLM provider fallback chain | Complete — real Gemini-to-Groq failover proven |
| 6 | Catalog and lightweight analytics | Complete — Tier A and LLM paths, public browser proof |
| 7 | Public idea intake and feedback-informed prioritization | Complete — real issue triage and Telegram proof |
| 8 | Hardening and scale | Complete — security, lifecycle, concurrency, and failure proof |

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

The end-to-end verification selected **بطاقات القرار** with `template:visual-toy` for `2026-w36`. The resulting product is available at [https://lo77667.github.io/repositoryDz/products/weekly/2026-w36/](https://lo77667.github.io/repositoryDz/products/weekly/2026-w36/) and the successful run is [32602565367](https://github.com/lo77667/repositoryDz/actions/runs/32602565367). Full details are in [`docs/PHASE-3-TEST-RECORD.md`](docs/PHASE-3-TEST-RECORD.md).

## Phase 4 LLM generation

The manual-only workflow [`Phase 4 — LLM generation behind verification gate`](.github/workflows/phase-4-llm-gated-factory.yml) selects an idea whose strategy is `generate`, requests one structured HTML candidate from an OpenAI-compatible provider, and never publishes the candidate directly. It applies a static safety gate, an isolated Chromium browser gate, and at most two repair attempts. A rejected or unavailable candidate is replaced by a deterministic safe placeholder and reported as `fallback`.

The provider configuration is externalized to `LLM_API_KEY` as a repository secret, with optional `LLM_BASE_URL` and `LLM_MODEL` variables. The documented default is Google Gemini's OpenAI-compatible endpoint with `gemini-3-flash-preview`. Provider research and official references are in [`docs/PHASE-4-PROVIDER-RESEARCH.md`](docs/PHASE-4-PROVIDER-RESEARCH.md), while the design contract is in [`docs/PHASE-4-DESIGN.md`](docs/PHASE-4-DESIGN.md).

The successful real rollout was [run 32605209546](https://github.com/lo77667/repositoryDz/actions/runs/32605209546). It selected **ناقد صفحة الدفع**, accepted the result in `generated` mode, passed static and isolated-browser verification, published [the 2026-w38 product](https://lo77667.github.io/repositoryDz/products/weekly/2026-w38/), returned HTTP 200, and sent a Telegram notification. The live primary action rendered a `0%` result and recommendations. The full record is in [`docs/PHASE-4-TEST-RECORD.md`](docs/PHASE-4-TEST-RECORD.md).

The first real rollout was intentionally retained as evidence of the safe fallback path: it published `2026-w37` in `fallback` mode after the candidate was not accepted or available. It still passed every safety and browser gate. The full Phase 5 record is in [`docs/PHASE-5-TEST-RECORD.md`](docs/PHASE-5-TEST-RECORD.md). LLM scheduling remains manual-only.

## Phase 5 provider fallback chain

The chain is implemented in [`automation/provider_chain.py`](automation/provider_chain.py) and uses Gemini first, Groq second, and Mistral third when configured. Missing providers are skipped, provider exceptions move immediately to the next slot, and each provider receives one initial request plus at most two repair attempts. Groq uses its documented OpenAI-compatible endpoint and a provider-specific JSON contract; its free-tier request budget is capped to remain below the observed 8,000-token-per-minute limit.

The required real proof is [run 32608059785](https://github.com/lo77667/repositoryDz/actions/runs/32608059785): Gemini was intentionally forced to fail, Groq returned an accepted candidate, the generated product passed both gates, Telegram reported `provider=groq` and `mode=generated`, and [the 2026-w43 product](https://lo77667.github.io/repositoryDz/products/weekly/2026-w43/) returned HTTP 200. The public product was also interacted with successfully. Earlier fallback-only attempts and their corrections are recorded in the test record; they are not counted as multi-provider proof.

## Phase 6 catalog and lightweight analytics

The root [catalog](https://lo77667.github.io/repositoryDz/) is generated by [`automation/build_catalog.py`](automation/build_catalog.py) into `index.html` and `catalog.json`. It lists every committed product with its title, pitch, period, category, and internal link. The weekly and LLM workflows rebuild it after each successful product publication and verify both the product URL and the catalog URL before sending Telegram.

The trusted post-processing step [`automation/instrument_analytics.py`](automation/instrument_analytics.py) adds one invisible CounterAPI pixel per published page. The static and Chromium gates allow only the exact CounterAPI host, path, namespace, action, and key pattern; all other external URLs and network-capable APIs remain blocked. CounterAPI's official documentation states that its public counter needs no account, key, or authentication and describes the privacy handling; the design and evidence are in [`docs/PHASE-6-DESIGN.md`](docs/PHASE-6-DESIGN.md) and [`docs/PHASE-6-TEST-RECORD.md`](docs/PHASE-6-TEST-RECORD.md).

The real Tier A verification was [run 32609912761](https://github.com/lo77667/repositoryDz/actions/runs/32609912761), which published [2026-w44](https://lo77667.github.io/repositoryDz/products/weekly/2026-w44/) and grew the catalog to 12 products. The real LLM verification was [run 32610019306](https://github.com/lo77667/repositoryDz/actions/runs/32610019306), which accepted Gemini output for `2026-w45`, published [مرتب أسباب الاسترجاع](https://lo77667.github.io/repositoryDz/products/weekly/2026-w45/), and grew the catalog to 13 products. Both runs passed the final static and isolated-browser gates, Pages returned HTTP 200, and Telegram success steps completed.

## Phase 7 public idea intake and feedback-informed prioritization

The public Arabic [GitHub Issue Form](.github/ISSUE_TEMPLATE/product-idea.yml) collects a structured product title, problem, pitch, audience, strategy hint, evidence of need, optional constraints, and explicit no-secret/no-personal-data confirmations. The form is public by design, and its contents are treated as public data. Blank issues remain available for existing technical reports, while the Phase 7 workflow processes only issues carrying `idea:submitted` or issues selected manually.

The deterministic triage tool [`automation/triage_idea.py`](automation/triage_idea.py) validates field presence and length, rejects secret-like patterns, links, HTML execution elements, and network APIs, normalizes Arabic text for comparison, and compares the proposal against the committed backlog. It returns `ready-for-review`, `needs-info`, `duplicate`, or `rejected`, with an explainable score out of 100. It never writes to `ideas/backlog.json` and never executes issue text.

The workflow [`Phase 7 — public idea intake triage`](.github/workflows/phase-7-idea-intake.yml) updates one marked review comment, applies the status label, and sends a Telegram notification. It has `contents: read` and `issues: write` only; it has no `git push`, no product build, and no publication path. `idea:accepted` remains a human decision.

The real successful case was [Issue #1](https://github.com/lo77667/repositoryDz/issues/1) and [run 32610704529](https://github.com/lo77667/repositoryDz/actions/runs/32610704529): **مراجع وضوح عرض الشحن** received `ready-for-review` with `94/100`, a `template:text-tool` suggestion, and an `ecommerce` category. The negative cases were [run 32610788025](https://github.com/lo77667/repositoryDz/actions/runs/32610788025) for missing information, [run 32610788444](https://github.com/lo77667/repositoryDz/actions/runs/32610788444) for a duplicate, and [run 32610788924](https://github.com/lo77667/repositoryDz/actions/runs/32610788924) for unsafe content. All four workflows succeeded, Telegram steps completed, and the backlog SHA remained unchanged. Full evidence is in [`docs/PHASE-7-DESIGN.md`](docs/PHASE-7-DESIGN.md) and [`docs/PHASE-7-TEST-RECORD.md`](docs/PHASE-7-TEST-RECORD.md).

## Phase 8 hardening and scale

Phase 8 adds the shared [`automation/security_policy.py`](automation/security_policy.py) rules and regression tests used by the generated-HTML and Tier A validators. They reject network-capable browser APIs, dangerous markup, inline event handlers, redirects, external frames, data HTML URLs, and credential-like literals. The approved CounterAPI pixel remains the only external exception after the final instrumentation gate. The local regression suite and the existing products, catalog, and browser gates passed after the change.

The lifecycle tool [`automation/manage_lifecycle.py`](automation/manage_lifecycle.py) supports only validated `retired`, `revisit`, and `backlog` transitions with a reason, optional internal replacement path, history, and atomic backlog writes. It never deletes a published artifact or overwrites its URL. The manual [`Phase 8 — product lifecycle management`](.github/workflows/phase-8-lifecycle.yml) workflow requires `confirm=true`, uses the shared publish lock, refuses stale `main`, rebuilds and verifies the catalog, waits for Pages, and notifies Telegram.

The weekly and LLM publishing workflows now share `repositoryDz-publish-main`, reject a stale push after fetching `origin/main`, and no longer export the unnecessary provider model output. Active third-party actions are pinned to verified SHAs, and the repository Actions policy now reports `sha_pinning_required=true`. The non-blocking Node.js 20 deprecation annotation remains a GitHub runner maintenance note; it did not block any run.

Real evidence includes [Tier A run 32611679734](https://github.com/lo77667/repositoryDz/actions/runs/32611679734) for `2026-w46`, [LLM run 32611883144](https://github.com/lo77667/repositoryDz/actions/runs/32611883144) for `2026-w47`, the intentionally rejected no-confirm lifecycle run [32612039113](https://github.com/lo77667/repositoryDz/actions/runs/32612039113), the confirmed retirement run [32612061452](https://github.com/lo77667/repositoryDz/actions/runs/32612061452), and the post-pinning guard [32612331756](https://github.com/lo77667/repositoryDz/actions/runs/32612331756). The public catalog and original retired product remained reachable, while the replacement path also loaded successfully. The full record is in [`docs/PHASE-8-TEST-RECORD.md`](docs/PHASE-8-TEST-RECORD.md).

## Diversity hardening — deterministic idea rotation

The generate picker now reads the last four active weekly entries from [`catalog.json`](catalog.json) and avoids their recent categories and shapes whenever an alternative exists. The rule applies only to the exact `generate` strategy; deterministic Tier A template selection is unchanged. A missing or invalid catalog, or a backlog with no outside alternative, triggers a safe fallback to the original candidate set rather than failing the factory.

Backlog records now carry a `shape` such as `checker`, `converter`, `comparator`, `game`, `generator`, or `planner`. Four new generate candidates were added outside the repeated ecommerce cluster: services/comparator, design/game, content/generator, and wellbeing/planner. The implementation and contract are in [`docs/DIVERSITY-HARDENING-DESIGN.md`](docs/DIVERSITY-HARDENING-DESIGN.md), and the test record is in [`docs/DIVERSITY-HARDENING-TEST-RECORD.md`](docs/DIVERSITY-HARDENING-TEST-RECORD.md).

The real [2026-w48 run](https://github.com/lo77667/repositoryDz/actions/runs/32612951967) selected `generate-010` as `services/comparator`, breaking both the recent ecommerce cluster and the recent checker/sorter/converter shape cluster. The selected artifact passed all product and catalog gates and Telegram, but the provider chain used the safe deterministic fallback because Groq had reached its free TPM limit; this is recorded honestly and is not counted as a successful LLM generation.

## Prompt hardening for generated HTML

The generator now places five critical non-negotiable rules at the beginning of `SYSTEM_PROMPT` and a self-check reminder at the end. The rules require a complete document from `<!DOCTYPE html>` through `</html>`, Arabic `lang="ar" dir="rtl"`, zero inline `on*` event handlers, exactly one `data-factory-action="primary"`, and fully offline execution. This is a prompt-only change; provider ordering, JSON contracts, token caps, and safety gates remain unchanged.

The baseline [w48 run](https://github.com/lo77667/repositoryDz/actions/runs/32612951967) had Gemini reject twice and Groq reject twice before deterministic fallback. After hardening, [w49](https://github.com/lo77667/repositoryDz/actions/runs/32614004936) had Gemini reject once for an incomplete document and Groq accept on its first attempt, while [w50](https://github.com/lo77667/repositoryDz/actions/runs/32614120217) had Gemini accept on its first attempt. Both generated products passed static and Chromium gates, Pages, catalog, and Telegram; the w50 product was also interacted with on the public URL. Two weeks are evidence of direction, not statistical proof, so the repair-focused prompt and further shape-specific instructions remain deferred pending more observations. Full evidence is in [`docs/PROMPT-HARDENING-TEST-RECORD.md`](docs/PROMPT-HARDENING-TEST-RECORD.md), with the public browser notes in [`docs/PROMPT-HARDENING-PUBLIC-FINDINGS.md`](docs/PROMPT-HARDENING-PUBLIC-FINDINGS.md).

## Weekly period idempotency guard

The weekly Tier A workflow now checks the target period before `pick_idea.py`. If an unscheduled/manual run leaves the period empty and the current period is already published, the workflow exits successfully without selecting an idea, changing the backlog, rebuilding the catalog, or overwriting the artifact, and sends an `already-published` Telegram notice. If a manual run explicitly requests an already-published period, it fails clearly before picker and sends the normal failure notice. The original overwrite refusal in [`automation/build_weekly_product.py`](automation/build_weekly_product.py) remains as a final defense.

The original collision was [run 32719459833](https://github.com/lo77667/repositoryDz/actions/runs/32719459833), where the scheduled run targeted already-used `2026-w35` and correctly refused to replace a different product. The real no-op verification [run 32767321437](https://github.com/lo77667/repositoryDz/actions/runs/32767321437) succeeded before picker and sent the already-published notification. The explicit manual-reuse verification [run 32767380959](https://github.com/lo77667/repositoryDz/actions/runs/32767380959) rejected the period before picker and sent a failure notification. The full record is in [`docs/WEEKLY-PERIOD-GUARD-TEST-RECORD.md`](docs/WEEKLY-PERIOD-GUARD-TEST-RECORD.md).

**The weekly period guard checkpoint is complete. Phase 9 has not started.**

## Defect repair record

A full audit identified and repaired the confirmed implementation defects without deleting any product, template, backlog idea, workflow, or historical record. The LLM workflow now runs the same weekly-period idempotency guard before the picker as the Tier A workflow: a blank-period dispatch for an already published period is a successful no-op, while an explicit reused period fails before any picker or provider call. The provider chain and deterministic fallback also refuse to overwrite an existing artifact as defense in depth.

Period handling is centralized in [`automation/period_utils.py`](automation/period_utils.py) and validates real ISO weeks, including years that do or do not contain week 53. Replacement metadata is canonicalized by [`automation/replacement_utils.py`](automation/replacement_utils.py); `index.html` and directory forms resolve to the catalog directory form, the weekly root is rejected, and catalog validation now checks that every local product or replacement target exists on disk. Generated and deterministic validators now require one complete HTML document and reject protocol-relative external URLs. The builder safely serializes idea JSON and escapes titles before embedding them in HTML.

The three deterministic templates and their existing products now expose exactly one primary-action marker. The two historical LLM products that contained inline handlers were minimally repaired by moving the same functions to `addEventListener`; their text, layout, and behavior were retained. A legacy backlog record now links the already published `2026-w35` artifact to an administrable idea identity without rebuilding or replacing that page. Browser verification opens every catalog product and replacement link, and Playwright is installed from the pinned [`automation/browser-requirements.txt`](automation/browser-requirements.txt) manifest.

The implementation was pushed in commits [`5ccfd48`](https://github.com/lo77667/repositoryDz/commit/5ccfd48) and [`ccd17a8`](https://github.com/lo77667/repositoryDz/commit/ccd17a8). The expanded local regression suite, YAML checks, Python compilation, static validators, full catalog rebuild comparison, and Chromium matrix passed. Real LLM guard evidence is [no-op run 32774375830](https://github.com/lo77667/repositoryDz/actions/runs/32774375830), which skipped picker/providers/build/publish and completed the already-published Telegram notification, and [manual collision run 32774533800](https://github.com/lo77667/repositoryDz/actions/runs/32774533800), which failed at the guard, skipped picker/providers/publish, and completed the failure notification. The detailed record remains in [`docs/WEEKLY-PERIOD-GUARD-TEST-RECORD.md`](docs/WEEKLY-PERIOD-GUARD-TEST-RECORD.md).

Branch protection is not changed by this repair because the current design intentionally permits the trusted GitHub Actions publisher to commit to `main`; the workflows retain stale-main refusal, shared publish concurrency, SHA-pinned actions, and least-privilege permissions where applicable. Enabling pull-request-only protection would be a separate operational policy decision and is not silently imposed here.
