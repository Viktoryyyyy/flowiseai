# Credentials Policy

## Repository rule

Secrets, tokens, API keys, private URLs, private endpoints, credentials, and live deployment data are forbidden in this repository.

This applies to:

- documentation;
- schemas;
- Flowise skeleton descriptors;
- State API contracts;
- CI configuration;
- tests;
- reports and audit evidence copied into repository files.

## Allowed placeholders

Only non-sensitive placeholders may be used:

- `<REDACTED>`
- `<SECRET_FROM_ENV>`
- `${ENV_VAR_NAME}`

Placeholders must not contain real values or partial real values.

## Redaction rules

Reports and audit evidence must redact sensitive data before repository storage.

Required redaction behavior:

1. Replace sensitive value with `<REDACTED>`.
2. Preserve non-sensitive context needed for review.
3. Record redaction state as `redacted` when redaction occurred.
4. Use `no_secret_payload` only when the payload contains no sensitive value.

## CI expectations

CI must check repository artifacts for likely secret values and live runtime data. CI may mention sensitive categories as policy terms, but must not include real values.

## Incident response

If a sensitive value is found:

1. Stop the current role task.
2. Report a blocker with exact file path and redacted evidence.
3. Remove the sensitive value from repository history according to owner-approved remediation.
4. Rotate the affected value outside the repository when applicable.
5. Resume only after PM L2 approves the corrected scope.
