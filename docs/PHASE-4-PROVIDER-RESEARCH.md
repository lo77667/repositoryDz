# Phase 4 provider research

## Verified sources

The official Google Gemini OpenAI-compatibility page confirms that Gemini models can be accessed through the OpenAI Python library by changing the API key and base URL. The documented Python example uses `GEMINI_API_KEY`, a base URL under `generativelanguage.googleapis.com/v1beta/openai/`, and a Gemini Flash model through the chat-completions shape.

The official Gemini Developer API pricing page currently presents a Free plan for developers and small projects. Its listed benefits include limited access to certain models, free input and output tokens, Google AI Studio access, and a note that content may be used to improve Google's products. This makes it compatible with the project's zero-budget constraint for a text-only generation experiment, but the exact model access and quotas must remain subject to the live account and documentation.

## Integration decision

Phase 4 will use a provider-neutral OpenAI-compatible client configuration in GitHub Actions. The repository will not store a provider key. The workflow will read `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL` from GitHub Actions Secrets/Variables, allowing the operator to use a no-card free provider without changing application code. The default example will be documented but not embedded as a credential.

The generation prompt will require a single self-contained HTML document with no network calls, no external resources, no forms that submit data, no credentials, no backend assumptions, and a small accessible interaction. The generated output will be rejected before publication if it violates the safety gate.

## References

1. Google AI for Developers, OpenAI compatibility: https://ai.google.dev/gemini-api/docs/openai
2. Google AI for Developers, Gemini Developer API pricing: https://ai.google.dev/gemini-api/docs/pricing
3. Google AI for Developers, Rate limits: https://ai.google.dev/gemini-api/docs/rate-limits
The official rate-limits page states that quotas are measured across requests per minute, tokens per minute, and requests per day, and that limits vary by model and account. It documents `429 RESOURCE_EXHAUSTED` and recommends waiting and retrying or reducing request cost. The Phase 4 workflow will therefore make one small generation request per run and fail safely rather than loop indefinitely.

The official structured-output page confirms that Gemini can generate JSON using a response format with `application/json` and a schema, with a supported subset of JSON Schema including string, object, array, enum, required, and additionalProperties. The generator will request a JSON object containing one `html` string so parsing is explicit before safety validation.

Additional reference: https://ai.google.dev/gemini-api/docs/structured-output
The live built-in model catalog was also checked in the sandbox. It reports `gemini-3-flash-preview` with structured-output support and a current catalog price of $0.50 input / $3 output per million tokens, while the official Google Developer API pricing page separately shows a Free plan with free input and output tokens but limited model access. The workflow therefore keeps provider model and endpoint configurable and treats the provider's live quota as authoritative.

The Phase 4 design deliberately uses one generation request plus at most two repair requests per run. If the provider returns a quota or service error, the workflow does not spin indefinitely; it falls back to a deterministic safe placeholder and reports the mode honestly.
