# Phase 8 Contract Artifacts

Status: implemented as repository contract artifacts  
Project: MOEX Bot + FlowiseAI  
Lane: flowiseai_pm_orchestration  
Execution mode: browser_chatgpt_github_direct

## Goal

Phase 8 converts the accepted Phase 7 contract layer into repository artifacts and validation tests.

The package is data-contract only. It does not implement Flowise runtime behavior, server deployment, production graph changes, secrets, or any direct `main` mutation authority.

## Artifacts

| Path | Purpose |
|---|---|
| `contracts/flowise/flowise_run_request.schema.json` | JSON Schema for a fail-closed Flowise execution request envelope. |
| `contracts/flowise/flowise_run_result.schema.json` | JSON Schema for a Flowise execution result envelope. |
| `contracts/pm/pm_l3_task_envelope.schema.json` | JSON Schema for the PM L3 task envelope passed into execution or validation. |
| `contracts/taxonomy/status_taxonomy.yaml` | Registry of request, result, and PM task statuses. |
| `contracts/taxonomy/blocker_taxonomy.yaml` | Registry of blocking failure categories and forbidden-action mappings. |
| `contracts/correlation/correlation_model.md` | Correlation and idempotency rules across envelope, request, and result. |
| `tests/contracts/test_phase_8_flowise_contracts.py` | Contract validation tests for Phase 8 artifacts. |

## Contract boundaries

The schemas intentionally encode the Phase 7 authority boundary:

- `direct_main_write_allowed` is always `false`;
- merge authority is `PM_L2_ONLY`;
- server apply is not allowed;
- deployment is not allowed;
- Flowise runtime modification is not allowed;
- production graph changes are not allowed;
- secrets are not allowed.

## Status and blocker consistency

Blocked and failed statuses must carry blocker evidence.

Known blocker codes are maintained in `contracts/taxonomy/blocker_taxonomy.yaml`. Status rules are maintained in `contracts/taxonomy/status_taxonomy.yaml`.

## Correlation

A single `correlation_id` ties the PM L3 task envelope to the Flowise request and result. The result must also echo `request_id` and `idempotency_key`.

## Validation

The Phase 8 test file validates:

- JSON Schema validity;
- minimal valid examples;
- required fields;
- enum values;
- authority boundary constraints;
- correlation echo rules;
- status and blocker consistency;
- forbidden Phase 7 action classes remain blocked.

## Explicitly not performed

- server changes;
- deployment;
- Flowise runtime modification;
- production graph changes;
- secret handling;
- direct write to `main`;
- merge without PM L2 authority;
- Phase 3, 4, 5, or 6 architecture changes.
