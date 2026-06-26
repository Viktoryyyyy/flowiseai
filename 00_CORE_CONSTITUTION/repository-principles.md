# Repository Principles

## GitHub-first Source of Truth

GitHub is the Source of Truth for repository content, architecture contracts, branches, commits, pull requests, and CI evidence.

Server state is Applied State only. Server filesystem content is not architecture proof and must not be used as the primary source for repository design decisions.

## PR-first implementation

Implementation must use a feature branch and PR to `main`.

Rules:

- direct writes to `main` are not allowed;
- branch creation is allowed only inside the approved task scope;
- one branch equals one lane and one task;
- one PR equals one lane and one task;
- PM L2 retains merge authority;
- CI pass is evidence for review and not merge approval.

The bootstrap v1 integration branch is `integration/flowiseai-bootstrap-v1`.

## Branch and lane isolation

Integration work uses the `integration/` branch prefix. A branch must not mix unrelated lanes or hidden cleanup.

## No-secrets policy

Repository artifacts must not contain secrets, tokens, API keys, credentials, private URLs, private endpoints, or live runtime data. Only explicit placeholders such as `<REDACTED>`, `<SECRET_FROM_ENV>`, and `${ENV_VAR_NAME}` may appear.

## No runtime claim policy

Bootstrap artifacts may describe contracts and skeletons. They must not claim a Flowise runtime deployment, a working State API service, production readiness, or a completed runtime smoke.

## Server boundary

Server apply is not part of bootstrap v1. Server state can only be referenced as applied-state evidence in a separately authorized phase.
