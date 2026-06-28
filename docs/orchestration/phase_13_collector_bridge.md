# Phase 13 Collector Bridge

Status: repository implementation package for PR-first validation  
Project: MOEX Bot + FlowiseAI  
Lane: `flowiseai_pm_orchestration`  
Task: `flowiseai_phase_13_collector_bridge`

## Goal

Implement a minimal Collector Bridge:

```text
PM L2 request -> collector -> Flowise AgentFlow V2 -> collector -> normalized result for PM L2
```

The collector is a controlled runtime caller. It does not make architecture or approval decisions.

## Authority boundary

The collector is not a GitHub executor.

It must not:

- create branches, commits, pull requests, merges, or releases;
- apply server changes;
- open ports or change infrastructure;
- print secrets;
- treat Flowise output as automatic PM approval.

PM L2 may consume `FlowiseCollectorResult` as structured evidence only.

## Runtime endpoint

The collector calls the Flowise Prediction API:

```text
POST /api/v1/prediction/:id
```

The runtime base URL is selected in this order:

1. `base_url` from `FlowiseCollectorRequest`;
2. `FLOWISE_BASE_URL` from the environment.

For same-server live runs, the intended base URL is the local Flowise runtime URL after it is verified by PM L2:

```text
http://127.0.0.1:3000
```

For external controlled calls, PM L2 must verify the public Flowise URL before using it.

## Request contract

Schema:

```text
contracts/collector/flowise_collector_request.schema.json
```

Required fields:

- `contract_version`;
- `correlation_id`;
- `graph_id` or `runtime_graph_id`;
- `question` or `form`.

Optional fields:

- `base_url`;
- `override_config`;
- `history`;
- `uploads`;
- `timeout_seconds`;
- `metadata`.

The collector sets `overrideConfig.sessionId` to `correlation_id` when the request does not already set it.

## Result contract

Schema:

```text
contracts/collector/flowise_collector_result.schema.json
```

Required normalized fields:

- `correlation_id`;
- `graph_id`;
- `raw_status`;
- `normalized_status`;
- `blocker_code`;
- `role_output`;
- `evidence_summary`.

Blocker classification:

| Case | `normalized_status` | `blocker_code` |
| --- | --- | --- |
| Invalid request | `blocked` | `request_validation_failure` |
| Timeout/network/client connection failure | `blocked` | `connection_failure` |
| HTTP 401/403 | `blocked` | `auth_failure` |
| HTTP non-2xx runtime response | `failed` | `runtime_failure` |
| 2xx response is not JSON | `failed` | `schema_failure` |
| 2xx JSON response | `success` | `none` |

## Secret handling

Credentials are read only from environment variables when needed:

- `FLOWISE_API_KEY`;
- `FLOWISE_ACCESS_TOKEN`;
- `FLOWISE_AUTH_HEADER_NAME`;
- `FLOWISE_AUTH_HEADER_VALUE`.

Secrets must not be committed, pasted into chat, or printed in collector output.

## Minimal usage

```bash
export FLOWISE_BASE_URL="http://127.0.0.1:3000"
python universal_role_runner/flowise_collector.py request.json
```

Example `request.json` shape:

```json
{
  "contract_version": "1.0.0",
  "correlation_id": "phase-13-live-001",
  "graph_id": "FLOWISE_GRAPH_ID_FROM_UI",
  "question": "Return a structured PM L2 role output for this task.",
  "timeout_seconds": 30
}
```

## Validation

Repository validation is mock-only in this phase.

```bash
python -m pytest tests/runtime/test_flowise_collector.py
```

Live validation is separate and requires PM L2-controlled runtime evidence after PR merge.
