# Phase 4 design

## Scope

Phase 4 adds Tier B generation behind a strict automated gate. A selected `generate` idea is sent to an OpenAI-compatible provider, which must return one JSON object containing one complete HTML document. The candidate is never published directly.

## Provider configuration

The GitHub Actions workflow reads the provider configuration from repository secrets and variables:

| Name | Type | Purpose |
|---|---|---|
| `LLM_API_KEY` | Actions secret | Provider credential; never logged or committed |
| `LLM_BASE_URL` | Actions variable | OpenAI-compatible base URL; defaults to Google's documented Gemini endpoint in the workflow documentation |
| `LLM_MODEL` | Actions variable | Provider model identifier; defaults to `gemini-3-flash-preview` in the workflow documentation |

The code is provider-neutral and does not embed a credential. The default model is chosen for short code generation and structured output; the live account's model access and quota remain authoritative.

## Generation contract

The model receives the idea title, pitch, audience, and constraints. It must return JSON with an `html` string. The HTML must be a standalone Arabic RTL document with inline CSS and JavaScript only, no external resources, no network calls, no credentials, no backend assumptions, and exactly one primary interactive control marked `data-factory-action="primary"`.

## Verification gate

The candidate passes only if all gates pass:

1. The JSON response is parseable and contains only the required HTML field.
2. The HTML has the required language and direction, a title, a visible body, inline assets only, and no blocked network APIs or external URLs.
3. The inline JavaScript passes a syntax check.
4. A headless browser loads the file within a timeout with no console errors or page exceptions.
5. The primary control exists, is visible, and responds to a click without an exception.
6. The page makes no network request during loading or interaction.

## Repair loop and fallback

The initial candidate is verified, then up to two repair attempts are allowed, for three total candidates. Each repair prompt includes the exact verification failures and the previous candidate. If all attempts fail, the workflow must not publish the candidate. It will fall back to a deterministic Tier A template and notify Telegram that the fallback was used. If fallback also fails, the workflow fails and sends a failure message with the run URL.

## Security boundary

Generated HTML is treated as untrusted code. It is written to a temporary workspace, inspected statically, and opened only as a local file in an isolated headless browser. It is not executed in the repository's build process, and it is not copied to a public product path until every gate is green. The generated artifact cannot use external network calls or credentials.

## Initial rollout

The Phase 4 workflow will be manually triggered first. A live run requires the operator to add a provider key and configuration. Until that bootstrap is complete, local mock-provider tests prove the parser, repair loop, gate, and fallback behavior without fabricating a successful provider run.
