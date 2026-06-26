# FlowiseAI PM Orchestration Bootstrap v1

Repository: `Viktoryyyyy/flowiseai`

This repository contains the bootstrap-v1 contract and skeleton layer for the MOEX Bot PM orchestration model. It is intended to coordinate PM L1, PM L2, PM L3, and Sub-chat execution through explicit task, handoff, role-output, audit, Flowise skeleton, State API contract, security, and CI artifacts.

Bootstrap v1 status:

- contract and skeleton foundation only;
- no Flowise runtime deployment;
- no State API implementation;
- no server apply;
- no trading strategy implementation.

## Purpose

The system defines a GitHub-first orchestration layer for controlled PM delivery:

1. PM L1 preserves the user-facing objective and route.
2. PM L2 owns phase authority, scope, merge authority, and server-apply decisions.
3. PM L3 owns delivery decomposition, Sub-chat dispatch, evidence validation, and blocker classification.
4. Sub-chats execute one assigned role task inside the approved scope and return normalized reports.

## Core directories

- `00_CORE_CONSTITUTION/` — repository principles and authority rules.
- `docs/` — bootstrap and architecture documentation.
- `contracts/schemas/` — JSON Schema Draft 2020-12 contracts.
- `contracts/bindings/` — role, lane, mode, and validator bindings.
- `flowise/` — Flowise-compatible skeleton descriptors with no runtime deployment claim.
- `state_api/runtime_stub/` — State API contract stub with no implemented service.
- `security/` — repository credentials and redaction policy.
- `ci/` — CI validation scope documentation.
- `tests/contract/` — contract-only validation tests.

## Delivery model

GitHub is the Source of Truth. Implementation is PR-first:

- work starts from `main`;
- implementation uses the lane branch `integration/flowiseai-bootstrap-v1`;
- direct writes to `main` are not allowed;
- PM L2 retains merge authority;
- CI evidence supports review but is not merge approval.

## Security and runtime boundaries

Secrets, tokens, API keys, credentials, private URLs, private endpoints, and live deployment data are not allowed in this repository. Runtime configuration must be supplied outside the repository if a later phase explicitly authorizes runtime work.

This bootstrap does not deploy Flowise and does not implement the State API. The files in `flowise/` and `state_api/runtime_stub/` are descriptors and contracts only.
