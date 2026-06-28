# Phase 10 Evidence Package Template

Status: MVP repository artifact  
Project: MOEX Bot + FlowiseAI  
Phase: Phase 10  
Lane: flowiseai_pm_orchestration

This template is the PM L2 evidence package structure for Phase 10+ Flowise-assisted PM orchestration loops.

It records evidence only. It does not grant merge, runtime, server apply, or deployment authority.

## Required YAML template

```yaml
pm_l2_evidence_package:
  package_id: phase-10-evidence-package-<id>
  package_version: 1
  project: MOEX Bot + FlowiseAI
  phase: Phase 10
  lane: flowiseai_pm_orchestration
  task_id: <task id>
  created_at: <ISO-8601 timestamp>

  authority_boundary:
    merge_authority: PM_L2_ONLY
    direct_main_write_allowed: false
    server_apply_authority: PM_L2_ONLY_OR_EXPLICIT_PM_L2_TASK
    runtime_allowed: false
    production_deployment_allowed: false
    secrets_allowed_in_chat: false

  execution_identity:
    # Mandatory for Phase 10+ production-grade runtime validation.
    execution_id: <execution id>
    correlation_id: corr-<id>
    idempotency_key: <stable replay key>

  runtime_evidence:
    runtime_surface: Flowise AgentFlow V2
    runtime_url: <redacted-or-not_captured>
    runtime_observed: true | false
    execution_started_at: <ISO-8601 timestamp-or-not_captured>
    execution_completed_at: <ISO-8601 timestamp-or-not_captured>
    execution_id: <same execution id>
    runtime_logs_ref: <redacted-ref-or-not_captured>
    runtime_status: succeeded | blocked | failed | cancelled | not_checked

  graph_evidence:
    graph_id: <flowise graph id>
    graph_name: <human readable graph name>
    graph_kind: agentflow_v2
    graph_export_sha256: <sha256-or-not_captured>
    graph_snapshot_ref: <repo path, artifact ref, or not_captured>
    graph_capture_method: ui_export | api_export | manual_inventory | not_captured
    captured_at: <ISO-8601 timestamp-or-not_captured>

  flowise_run_request_summary:
    request_id: flowise-run-request-<id>
    correlation_id: corr-<id>
    idempotency_key: <stable replay key>
    task_id: <task id>
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

  flowise_run_result_summary:
    result_id: flowise-run-result-<id>
    request_id: flowise-run-request-<id>
    correlation_id: corr-<id>
    idempotency_key: <stable replay key>
    status: succeeded | blocked | failed | cancelled
    outcome: completed | blocked | failed | no_op
    output_type: implementation_report | validation_report | pm_l3_evidence_package | none
    output_summary: <short summary>

  role_execution_summary:
    assigned_role: <role id>
    role_task_status: completed | blocked | failed | cancelled
    outputs_created:
      - <artifact or none>
    changed_files:
      - <path or none>

  blockers:
    # Required even when empty.
    - blocker_code: <code>
      severity: blocking | warning
      message: <message>
      evidence_ref: <ref-or-none>

  forbidden_scope_flags:
    runtime_action_performed: false
    server_apply_performed: false
    n8n_action_performed: false
    direct_main_write_performed: false
    merge_performed: false
    production_deployment_performed: false
    production_graph_change_performed: false
    forbidden_files_changed: false
    secrets_exposed: false

  pm_l3_validation:
    verdict: pass | conditional_pass | fail
    validated_at: <ISO-8601 timestamp>
    validator_role: PM_L3_DELIVERY_VALIDATION_OWNER
    scope_check: pass | fail
    evidence_completeness_check: pass | fail
    correlation_check: pass | fail
    blocker_check: pass | fail
    secrets_check: pass | fail
    notes: <short notes>

  pm_l2_final_verdict:
    # Must be recorded only after pm_l3_validation.verdict exists.
    verdict: approved | rejected | needs_fix | not_reviewed
    reviewed_at: <ISO-8601 timestamp-or-not_reviewed>
    reviewer_role: PM_L2_PHASE_OWNER
    deployment_readiness_claim: not_claimed | claimed_ready | rejected
    pm_l2_deployment_approved: false
    notes: <short notes>

  rejected_claims:
    # Explicitly record unsupported model/runtime/server/deployment claims.
    - claim: <claim text>
      rejection_reason: missing_external_evidence | missing_pm_l2_authority | scope_violation | secret_boundary | other
      evidence_ref: <ref-or-none>

  no_secrets:
    secrets_included: false
    secret_sources_checked:
      - prompts
      - request_summary
      - result_summary
      - runtime_evidence
      - graph_evidence
      - logs_refs
    redaction_notes: <notes-or-none>
```

## Runtime evidence fields

Runtime evidence must identify what was observed and what was not observed. `not_checked` and `not_captured` are valid evidence values when runtime proof was not collected. Unsupported claims must not be inferred from missing runtime evidence.

## Graph evidence fields

Graph evidence must include `graph_id` and `graph_name`. Export or snapshot proof is required when claiming that a graph was frozen or reviewed. If export is unavailable, write `not_captured`.

## FlowiseRunRequest summary fields

The request summary must include `request_id`, `correlation_id`, `idempotency_key`, `task_id`, `target_flow.graph_id`, and `target_flow.graph_name`.

## FlowiseRunResult summary fields

The result summary must echo `request_id`, `correlation_id`, and `idempotency_key`. It must include status, outcome, output type, blockers, and forbidden-scope flags.

## Mandatory execution_id

`execution_id` is mandatory for Phase 10+ production-grade runtime validation. A package missing `execution_id` must be rejected or marked `needs_fix`.

## Blocker list

The `blockers` field is required even when there are no blockers. In that case it must be an empty list:

```yaml
blockers: []
```

## PM L3 and PM L2 verdict order

PM L3 validation verdict must exist before PM L2 final verdict. PM L2 final verdict must not be used to backfill missing PM L3 validation.

## Rejected claims

The `rejected_claims` section is required when the model, Flowise result, server output, or role report claims an action that is unsupported by evidence or outside authority.

Examples:

- deployment readiness without PM L2 approval;
- merge performed without merge evidence;
- server apply performed without server output;
- runtime validation completed without `execution_id`;
- graph export captured without graph export proof.

## No secrets

The package must explicitly state that no secrets are included. If any secret appears in the source material, the package must fail closed and reference only a redacted evidence location.
