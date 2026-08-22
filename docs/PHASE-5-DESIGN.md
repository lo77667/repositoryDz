# Phase 5 design

## Provider order

The chain uses explicit provider slots in this order:

| Order | Provider | Configuration | Default model |
|---|---|---|---|
| 1 | Gemini | `LLM_API_KEY`, optional `LLM_BASE_URL`, optional `LLM_MODEL` | `gemini-3-flash-preview` |
| 2 | Groq | `LLM_FALLBACK_API_KEY`, optional `LLM_FALLBACK_BASE_URL`, optional `LLM_FALLBACK_MODEL` | `openai/gpt-oss-20b` |
| 3 | Mistral | `LLM_SECONDARY_API_KEY`, optional `LLM_SECONDARY_BASE_URL`, optional `LLM_SECONDARY_MODEL` | `mistral-small-latest` |

The first configured provider is attempted first. Missing keys are skipped without failing the run. A provider that returns an HTTP error, timeout, malformed structured response, unsafe HTML, JavaScript error, page exception, network request, or failed primary click is recorded as rejected and the next provider is tried.

## Shared generation contract

Every provider uses the same OpenAI-compatible chat-completions contract and requests a JSON object containing an `html` string. The existing generation prompt, static safety gate, isolated Chromium gate, and maximum of two repairs per provider are reused. A provider is accepted only after the generated artifact passes both static and browser checks.

## Failure behavior

The chain never retries one provider indefinitely. Each configured provider gets one initial request plus at most two repair requests. After all configured providers are rejected or unavailable, the workflow creates the deterministic Phase 4 placeholder, runs the same gates again, and publishes it only if it passes. The Telegram message names the actual provider or `deterministic-fallback`; no success message claims LLM generation when fallback was used.

## Security and cost boundary

All provider keys are GitHub Actions secrets and are never committed or printed. Provider URLs and model names are variables or documented defaults. The workflow remains manual-only. This avoids silently multiplying provider costs and allows the operator to review a single run before enabling a later schedule.

## Acceptance criteria

The stage is accepted when local tests prove failover and no-provider safety, the workflow YAML passes validation, a real manual run completes with either an accepted provider or a gated deterministic fallback, the product URL returns HTTP 200, the published HTML passes static and browser gates, and Telegram receives a truthful status message.
