# Phase 5 provider research

## Groq alternative

The official Groq rate-limit documentation states that limits are measured in requests per minute, requests per day, tokens per minute, tokens per day, and separate input/output token dimensions where configured. It states that limits apply at the organization level, that exact limits depend on the account, and that the API returns HTTP 429 when a limit is exceeded. The page lists a Free Plan Limits table and explains that the exact current limits should be checked in the account limits page.

The Phase 5 chain will therefore classify HTTP 429, timeouts, network errors, authentication errors, and malformed responses as provider failures, record only a redacted reason, and try the next configured provider once. It will not retry the same failed provider indefinitely.

## Configuration decision

Provider order will be explicit and secret-backed rather than inferred from public model catalogs. Each provider has a key, base URL, and model. The first provider is the current Gemini configuration; the second provider is Groq-compatible and can be enabled by adding its key and model. If a provider is not configured, the chain skips it. The final deterministic fallback remains the last safety boundary.

The existing Phase 4 static and isolated-browser gates are reused unchanged after every provider response. A provider is considered successful only when its candidate passes those gates, not merely when the HTTP call returns 200.

## References

1. GroqDocs, Rate Limits: https://console.groq.com/docs/rate-limits
2. GroqDocs, OpenAI Compatibility: https://console.groq.com/docs/openai
3. Google Gemini, OpenAI compatibility: https://ai.google.dev/gemini-api/docs/openai
4. Google Gemini, Rate limits: https://ai.google.dev/gemini-api/docs/rate-limits
The official Groq OpenAI-compatibility page documents the base URL `https://api.groq.com/openai/v1` and says the OpenAI client can be configured with a Groq API key. It also lists unsupported OpenAI fields that must not be sent, including `logprobs`, `logit_bias`, and `top_logprobs`; the chain will send only the common chat-completions fields needed by the existing generator.

The official Mistral usage-and-limits page states that **Free mode** lets an organization create API keys and use included monthly usage within the limits shown on its Limits page. It distinguishes this from pay-as-you-go usage beyond the included amount. Mistral is therefore suitable as an optional second provider when the operator has enabled its free mode, but the chain will skip it when its key is absent.

Additional reference: https://docs.mistral.ai/admin/billing-usage/usage-limits
The official Groq structured-output documentation distinguishes strict and best-effort modes. It lists `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, and `openai/gpt-oss-safeguard-20b` as supporting structured outputs with best-effort mode and recommends JSON Object Mode for other models. The Phase 5 chain will default the Groq fallback to `openai/gpt-oss-20b` when configured, use the same JSON schema request, and still require the local parsing and HTML gates because provider schema compliance is not itself a publication approval.

Additional reference: https://console.groq.com/docs/structured-outputs
