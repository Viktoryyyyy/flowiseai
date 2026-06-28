# Phase 10 Production Orchestration Loop Design

Status: MVP repository artifact  
Project: MOEX Bot + FlowiseAI  
Phase: Phase 10  
Lane: flowiseai_pm_orchestration

## MVP goal

Phase 10 moves the project from a one-action Flowise smoke pattern to a controlled Flowise-assisted PM orchestration MVP loop.

The MVP goal is to define and validate a repeatable loop:

```text
PM L2 -> PM L3 -> Flowise AgentFlow V2 -> role execution -> PM L3 validation -> PM L2 evidence package
```

The loop must produce repository-owned evidence that can be reviewed before any merge, server apply, runtime modification, or deployment decision.

## Non-goals

Phase 10 WP1 does not:

- deploy anything to production;
- modify Flowise runtime/server configuration;
- modify n8n workflows;
- change existing Phase 8 schemas, contracts, or taxonomies;
- grant merge authority to Flowise, PM L3, or a sub-chat;
- grant server apply authority to Flowise, PM L3, or a sub-chat;
- claim production readiness without PM L2 approval;
- include secrets, tokens, cookies, credentials, or runtime environment values.

## Source of Truth boundary

```text
GitHub / repository = Source of Truth
Flowise AgentFlow V2 = execution surface
Server = Applied State only
n8n / DB = workflow and applied-state evidence only when explicitly used
```

Repository artifacts define accepted structure, evidence fields, and validation gates. Flowise may assist role execution, but Flowise output is not a repository fact until it is captured in a reviewed artifact or PR. Server files and running containers are not architectural proof.

## Controlled loop architecture

### 1. PM L2 phase authority

PM L2 owns the phase decision, approved scope, forbidden scope, branch policy, merge authority, and server/deployment authority.

PM L2 creates or approves a PM L3 task package containing:

- `task_id`;
- lane;
- execution mode;
- approved file/action scope;
- forbidden file/action scope;
- acceptance criteria;
- authority boundary;
- required evidence fields.

### 2. PM L3 delivery and validation ownership

PM L3 decomposes PM L2 scope into exact role tasks. PM L3 must not widen scope or approve merge/deployment unless PM L2 explicitly delegates that authority.

PM L3 sends a FlowiseRunRequest to the Flowise execution surface only after the task envelope is complete.

### 3. Flowise AgentFlow V2 execution surface

Flowise AgentFlow V2 may execute or assist a role-task iteration. It must receive a complete request envelope and must return a result envelope.

Flowise must be treated as an execution surface, not as Source of Truth. A model-generated claim that code was merged, deployed, server-applied, or runtime-validated is rejected unless supported by external evidence and approved authority.

### 4. Role execution

The assigned role executes only the approved task. The role output must state:

- done;
- not done;
- blockers;
- next step;
- changed files or produced artifacts when applicable;
- forbidden actions not performed.

### 5. PM L3 validation gate

PM L3 validates the role output before PM L2 receives a final evidence package. PM L3 checks:

- task alignment;
- approved scope compliance;
- required evidence completeness;
- request/result correlation;
- runtime evidence sufficiency;
- blocker classification;
- forbidden action flags;
- secrets boundary.

If evidence is incomplete, contradictory, or unsupported, the loop fails closed.

### 6. PM L2 final evidence package and authority gate

PM L2 receives the evidence package after PM L3 validation. PM L2 remains the only authority for merge approval, server apply approval, deployment approval, and production-readiness acceptance.

CI passed, Flowise success, or PM L3 pass is evidence only. It is not PM L2 approval.

## FlowiseRunRequest capture model

A Phase 10 request capture must include at minimum:

```yaml
flowise_run_request_summary:
  request_id: flowise-run-request-<id>
  correlation_id: corr-<id>
  idempotency_key: <stable replay key>
  task_id: <pm task id>
  source_role: PM_L3_DELIVERY_VALIDATION_OWNER
  target_flow:
    flow_kind: agentflow_v2
    graph_id: <flowise graph id>
    graph_name: <human readable graph name>
  authority_boundary:
    merge_authority: PM_L2_ONLY
    direct_main_write_allowed: false
    server_apply_allowed: false
    deployment_allowed: false
    runtime_modification_allowed: false
    production_graph_change_allowed: false
    secrets_allowed: false
```

The request summary may omit raw prompts if they contain sensitive values. It must never include secrets.

## FlowiseRunResult capture model

A Phase 10 result capture must include at minimum:

```yaml
flowise_run_result_summary:
  result_id: flowise-run-result-<id>
  request_id: flowise-run-request-<id>
  correlation_id: corr-<id>
  idempotency_key: <same stable replay key>
  status: succeeded | blocked | failed | cancelled
  outcome: completed | blocked | failed | no_op
  output_type: implementation_report | validation_report | pm_l3_evidence_package | none
  blockers: []
  forbidden_scope_flags:
    runtime_action_performed: false
    server_apply_performed: false
    n8n_action_performed: false
    secrets_exposed: false
```

The result must echo the originating request fields: `request_id`, `correlation_id`, and `idempotency_key`.

## Mandatory execution_id rule

For Phase 10+ production-grade runtime validation, every evidence package must include a mandatory `execution_id`.

The `execution_id` identifies one end-to-end loop attempt and binds together:

- PM L3 task envelope;
- FlowiseRunRequest summary;
- FlowiseRunResult summary;
- PM L3 validation verdict;
- PM L2 final verdict.

No Phase 10 runtime evidence package may be accepted as production-grade without `execution_id`.

## Graph ID and graph export/snapshot rule

A runtime evidence package must include:

- `graph_id`;
- `graph_name`;
- `graph_export_sha256` or an explicit `not_captured` value;
- `graph_snapshot_ref` or an explicit `not_captured` value;
- capture timestamp.

If a Flowise graph export is unavailable, the package must state that explicitly. It must not imply that a graph was exported or snapshotted without proof.

## PM L3 validation gate

PM L3 validation must run before PM L2 final verdict.

Required PM L3 verdict values:

```text
pass | conditional_pass | fail
```

A PM L2 final verdict is invalid if PM L3 validation verdict is missing, skipped, or recorded after PM L2 acceptance.

## PM L2 authority gate

The evidence package must distinguish evidence from authority.

PM L2 authority is required for:

- merge approval;
- server apply;
- runtime change;
- production deployment;
- production readiness claim.

A package may say `evidence_collected`. It may not say `deployment_ready` unless PM L2 explicitly approved that claim in the current phase decision.

## Fail-closed blocker handling

The loop fails closed when any of these conditions appears:

- missing `execution_id` for production-grade runtime evidence;
- missing graph identity;
- request/result correlation mismatch;
- missing PM L3 validation verdict;
- PM L2 final verdict recorded before PM L3 validation;
- forbidden scope action flag is true;
- blocker classification is missing;
- evidence contains secrets;
- model-generated deployment/server/merge claim lacks external proof and PM L2 authority.

Fail-closed means the package returns `blocked` or `fail`, not a partial approval.

## Secrets boundary

Secrets must not appear in prompts, Flowise request captures, result captures, evidence packages, docs, tests, PR descriptions, logs copied to chat, or repository artifacts.

Allowed values are structural identifiers, redacted references, and explicit `not_captured` markers.

## Rejection of model-generated deployment claims

Any deployment, runtime, server, merge, or production-readiness claim generated by a model is rejected unless all of the following are present:

1. external evidence tied to an exact commit, PR, workflow run, server output, or runtime capture;
2. PM L3 validation verdict;
3. PM L2 approval for the claimed authority level;
4. no forbidden-scope flags.

## WP sequencing

### WP1 — Repository artifacts

Create this design document, the Phase 10 evidence package template, and deterministic contract tests. No runtime action.

### WP2 — Runtime capability check

Inspect Flowise AgentFlow V2 capability and capture minimal graph/runtime evidence. No production deployment unless separately approved.

### WP3 — Graph hardening

Define and export the minimal AgentFlow V2 graph with stable graph identity, request/result capture points, and fail-closed behavior.

### WP4 — Controlled role execution pilot

Run one controlled PM L3 -> Flowise -> role execution -> PM L3 validation loop and produce a PM L2 evidence package.

### WP5 — PM L2 acceptance and next production decision

PM L2 reviews evidence, decides whether to merge, server-apply, harden runtime, repeat, or stop.
