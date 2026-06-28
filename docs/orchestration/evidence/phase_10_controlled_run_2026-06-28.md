# Phase 10 Controlled Run Evidence Package

Status: completed evidence artifact  
Project: MOEX Bot + FlowiseAI  
Phase: Phase 10  
Lane: flowiseai_pm_orchestration  
Evidence date: 2026-06-28

This file records the PM L2 final evidence package for the Phase 10 FlowiseAI controlled validation run.

Scope boundary:

- GitHub/repo remains the Source of Truth.
- Server remains Applied State only.
- Flowise is treated as execution surface only.
- This artifact does not approve production deployment.
- This artifact does not record a MOEX Bot server apply.
- No secrets are included.

## PM L2 final evidence package

```yaml
pm_l2_final_evidence_package:
  package_id: "phase-10-evidence-package-hardening-controlled-run-001-20260628-final"
  package_version: 1
  project: "MOEX Bot + FlowiseAI"
  phase: "Phase 10"
  lane: "flowiseai_pm_orchestration"
  task_id: "flowiseai_hardening_controlled_run_001"
  created_at: "2026-06-28T11:11:53Z"
  execution_mode: "browser_chatgpt_github_direct"

  authority_boundary:
    merge_authority: "PM_L2_ONLY"
    direct_main_write_allowed: false
    server_apply_authority: "not_used"
    runtime_allowed: "controlled_flowise_execution_only"
    production_deployment_allowed: false
    secrets_allowed_in_chat: false

  verdict:
    status: "completed"
    clean_operational_loop: "yes"
    reason: "Flowise AgentFlow V2 controlled validation run completed, PM L3 validation passed, and external runtime evidence capture resolved execution/hash blockers."

  request_identity:
    handoff_id: "FLOWISEAI-HARDENING-CONTROLLED-RUN-001-2026-06-28"
    task_id: "flowiseai_hardening_controlled_run_001"
    correlation_id: "corr-flowiseai-hardening-controlled-run-001-20260628"
    request_id: "flowise-run-request-hardening-controlled-run-001-20260628"
    result_id: "flowise-run-result-hardening-controlled-run-001-20260628"
    idempotency_key: "flowiseai-hardening-controlled-run-001-20260628"

  execution_identity:
    execution_id: "04c5238e-ab3a-4390-bd89-9cd137ced7e8"
    correlation_id: "corr-flowiseai-hardening-controlled-run-001-20260628"
    idempotency_key: "flowiseai-hardening-controlled-run-001-20260628"

  runtime_evidence:
    runtime_surface: "Flowise AgentFlow V2"
    flowise_version: "3.1.2"
    runtime_observed: true
    runtime_status: "succeeded"
    execution_id: "04c5238e-ab3a-4390-bd89-9cd137ced7e8"
    execution_state: "FINISHED"
    session_id: "31ae2315-ca6c-4e9b-a4d5-6b06ce9fc05f"
    execution_started_at: "2026-06-28 11:10:29"
    execution_completed_at: "2026-06-28 11:10:39"
    executionData_length: 196079
    executionData_sha256: "740fdc6c144ce93b5e6340e36c7de4aa82bae5983957492a1daad8ea1da5c8e4"
    runtime_logs_ref: "not_captured"
    evidence_capture_source: "user-provided server command output"

  graph_evidence:
    graph_id: "c45d7111-43d9-4ffa-a888-5f1ca1ade781"
    graph_name: "Phase 10 MVP PM Orchestration Loop"
    graph_kind: "agentflow_v2"
    graph_type: "AGENTFLOW"
    graph_flowData_length: 40220
    graph_updatedDate: "2026-06-28 11:10:13"
    graph_flowData_sha256: "6b217ffe57774473f841baef4a470d93227f5cf48814ec46b45d5323cd9282ff"
    graph_snapshot_ref: "Flowise DB flowData hash captured externally"
    graph_capture_method: "server_sqlite_read_only_hash_capture"
    captured_at: "2026-06-28T11:11:53Z"

  flowise_run_request_summary:
    request_id: "flowise-run-request-hardening-controlled-run-001-20260628"
    correlation_id: "corr-flowiseai-hardening-controlled-run-001-20260628"
    idempotency_key: "flowiseai-hardening-controlled-run-001-20260628"
    task_id: "flowiseai_hardening_controlled_run_001"
    source_role: "PM_L3_DELIVERY_VALIDATION_OWNER"
    target_flow:
      flow_kind: "agentflow_v2"
      graph_id: "c45d7111-43d9-4ffa-a888-5f1ca1ade781"
      graph_name: "Phase 10 MVP PM Orchestration Loop"
    authority_boundary:
      merge_authority: "PM_L2_ONLY"
      direct_main_write_allowed: false
      server_apply_allowed: false
      deployment_allowed: false
      runtime_modification_allowed: false
      production_graph_change_allowed: false
      secrets_allowed: false

  flowise_run_result_summary:
    result_id: "flowise-run-result-hardening-controlled-run-001-20260628"
    request_id: "flowise-run-request-hardening-controlled-run-001-20260628"
    correlation_id: "corr-flowiseai-hardening-controlled-run-001-20260628"
    idempotency_key: "flowiseai-hardening-controlled-run-001-20260628"
    status: "succeeded"
    outcome: "completed"
    output_type: "validation_report"
    output_summary: "SUBCHAT_VALIDATION executed through Flowise AgentFlow V2; PM L3 validation passed; remaining external evidence blockers resolved by server-side hash capture."

  role_execution_summary:
    assigned_role: "SUBCHAT_VALIDATION"
    source_role: "PM_L3_DELIVERY_VALIDATION_OWNER"
    role_task_status: "completed"
    outputs_created:
      - "validation_report"
      - "pm_l3_validation"
      - "pm_l2_evidence_package"
    changed_files:
      - "none"

  role_chain:
    expected_loop: "PM_L2_PHASE_OWNER -> PM_L3_DELIVERY_VALIDATION_OWNER -> Flowise AgentFlow V2 -> SUBCHAT_VALIDATION -> PM L3 validation -> PM L2 evidence package"
    observed_tokens:
      PM_L2_PHASE_OWNER: 28
      PM_L3_DELIVERY_VALIDATION_OWNER: 148
      SUBCHAT_VALIDATION: 158
      correlation_id: 79
      request_id: 79
      result_id: 66
    stale_token_SUBCHAT_IMPLEMENTATION: "not_found_in_safe_token_scan"

  blockers:
    - blocker_code: "none"
      severity: "none"
      message: "No remaining blockers after external runtime evidence capture."
      evidence_ref: "execution_id, graph_flowData_sha256, executionData_sha256"

  resolved_blockers:
    - "external_runtime_evidence_capture_required"
    - "runtime_execution_id_capture_required"
    - "executionData_sha256_capture_required"
    - "graph_snapshot_hash_capture_required"

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
    verdict: "pass"
    validated_at: "2026-06-28T11:10:39Z"
    validator_role: "PM_L3_DELIVERY_VALIDATION_OWNER"
    scope_check: "pass"
    evidence_completeness_check: "pass_after_external_capture"
    correlation_check: "pass"
    blocker_check: "pass"
    secrets_check: "pass"
    structured_agent_fields_resolved: true
    stale_implementation_role_absent: true
    no_forbidden_claims: true
    unresolved_templates_absent: true
    notes: "Runtime hashes were captured externally after Flowise final node reported capture-required blockers."

  pm_l2_final_verdict:
    verdict: "approved"
    reviewed_at: "2026-06-28T11:11:53Z"
    reviewer_role: "PM_L2_PHASE_OWNER"
    deployment_readiness_claim: "not_claimed"
    pm_l2_deployment_approved: false
    notes: "Controlled operational loop accepted as clean. No production deployment or server apply approved."

  rejected_claims:
    - claim: "production deployment readiness"
      rejection_reason: "not_claimed"
      evidence_ref: "forbidden_scope_flags.production_deployment_performed=false"
    - claim: "server apply completed"
      rejection_reason: "not_claimed"
      evidence_ref: "forbidden_scope_flags.server_apply_performed=false"
    - claim: "direct main write completed"
      rejection_reason: "not_claimed"
      evidence_ref: "forbidden_scope_flags.direct_main_write_performed=false"

  no_secrets:
    secrets_included: false
    secret_sources_checked:
      - "prompts"
      - "request_summary"
      - "result_summary"
      - "runtime_evidence"
      - "graph_evidence"
      - "logs_refs"
    redaction_notes: "No secrets or credentials recorded in this evidence package."

  source_of_truth_boundary:
    github_repo: "Source of Truth"
    server: "Applied State only"
    flowise: "execution surface only"

  final_status: "accepted_by_PM_L2"
```

## External runtime evidence captured

```text
=== PHASE 10 CONTROLLED RUN EXTERNAL EVIDENCE CAPTURE ===
DATE=2026-06-28T11:11:53+00:00
GRAPH_ID=c45d7111-43d9-4ffa-a888-5f1ca1ade781
EXECUTION_ID=04c5238e-ab3a-4390-bd89-9cd137ced7e8
=== GRAPH METADATA ===
c45d7111-43d9-4ffa-a888-5f1ca1ade781|Phase 10 MVP PM Orchestration Loop|AGENTFLOW|40220|2026-06-28 11:10:13
=== GRAPH_FLOWDATA_SHA256 ===
6b217ffe57774473f841baef4a470d93227f5cf48814ec46b45d5323cd9282ff
=== EXECUTION METADATA ===
04c5238e-ab3a-4390-bd89-9cd137ced7e8|FINISHED|c45d7111-43d9-4ffa-a888-5f1ca1ade781|31ae2315-ca6c-4e9b-a4d5-6b06ce9fc05f|196079|2026-06-28 11:10:29|2026-06-28 11:10:39
=== EXECUTIONDATA_SHA256 ===
740fdc6c144ce93b5e6340e36c7de4aa82bae5983957492a1daad8ea1da5c8e4
=== SAFE TOKEN SCAN ===
     28 PM_L2_PHASE_OWNER
    148 PM_L3_DELIVERY_VALIDATION_OWNER
    158 SUBCHAT_VALIDATION
     79 corr-flowiseai-hardening-controlled-run-001-20260628
      3 executionData_sha256_capture_required
      3 external_runtime_evidence_capture_required
     79 flowise-run-request-hardening-controlled-run-001-20260628
     66 flowise-run-result-hardening-controlled-run-001-20260628
      3 graph_snapshot_hash_capture_required
      3 runtime_execution_id_capture_required
```

## Notes

The capture-required tokens remain visible in executionData because the Flowise final node correctly emitted them before external capture. They are recorded above as resolved blockers after server-side evidence capture.
