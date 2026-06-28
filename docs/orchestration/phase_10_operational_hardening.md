# Phase 10 MVP Operational Hardening

Status: proposed repository artifact  
Project: MOEX Bot + FlowiseAI  
Phase: Phase 10  
Lane: flowiseai_pm_orchestration

## Purpose

This artifact turns the Phase 10 Flowise-assisted PM orchestration MVP from an ad-hoc runtime result into a repeatable operating procedure.

It does not approve production deployment, server apply, n8n changes, Docker changes, or autonomous merge authority.

## Current MVP evidence baseline

```yaml
phase_10_runtime_baseline:
  graph_id: c45d7111-43d9-4ffa-a888-5f1ca1ade781
  graph_name: Phase 10 MVP PM Orchestration Loop
  runtime_surface: Flowise AgentFlow V2
  current_graph_snapshot_hash: 0d7293faffa7980ae173ad607c08bd3435248151645a288660f18f17d5154e89
  latest_successful_execution_id: a5cad982-0c5c-4f72-8160-65935807dd18
  latest_session_id: 31ae2315-ca6c-4e9b-a4d5-6b06ce9fc05f
  latest_execution_state: FINISHED
  latest_executionData_sha256: 2c4e4a6f6bc1d6b5edca4254a49697eb894254826ea0d8612ed88bf63c3c3992
  latest_executionData_length: 49321
  latest_execution_createdDate: "2026-06-28 09:59:00"
  latest_execution_updatedDate: "2026-06-28 09:59:07"
```

## Accepted result and known deviation

```yaml
phase_10_mvp_result:
  functional_result: pass
  reason:
    - Phase 10 graph reached FINISHED state.
    - Final YAML-compatible output was produced.
    - Runtime metadata was captured from SQLite.
    - Graph snapshot hash was captured.
  procedural_result: deviated
  deviation:
    - multiple debug runs occurred during WP4 fix-and-run.
    - metadata fields were captured externally after the run, not inside the final model output.
```

The deviation does not invalidate the MVP signal. It prevents claiming a clean operational loop until hardening is completed.

## Hardening objective

The next operational target is one reproducible controlled run with no debug reruns and complete evidence capture.

```yaml
hardening_target:
  controlled_run_count: exactly_one
  graph_edit_before_run: false
  graph_edit_after_run: false
  metadata_capture: mandatory
  evidence_capture_method: sqlite_read_only
  runtime_output: YAML-compatible
  authority_boundary: enforced
```

## Required operator sequence

### Step 1. Pre-run baseline

Capture current graph metadata and hash before any new run.

Required fields:

- graph_id
- graph_name
- graph_type
- deployed
- isPublic
- flowData length
- graph flowData SHA256
- execution count for graph before run

### Step 2. One run only

Run the existing graph exactly once with a PM L2 approved test input.

No extra click, retry, rerun, duplicate browser submission, or Flowise API call is allowed without a new PM L2 decision.

### Step 3. Post-run evidence

Capture:

- latest execution_id
- session_id
- execution state
- executionData length
- executionData SHA256
- createdDate
- updatedDate
- post-run graph flowData SHA256
- raw final output capture method
- final YAML validity result

### Step 4. Acceptance decision

PM L2 may accept the run only if:

```yaml
acceptance_criteria:
  exactly_one_new_execution: true
  execution_state: FINISHED
  yaml_output_valid: true
  execution_id_captured: true
  session_id_captured: true
  executionData_sha256_captured: true
  graph_snapshot_hash_captured: true
  graph_hash_changed_without_approved_edit: false
  secrets_exposed: false
  forbidden_mutations_performed: false
```

## Authority boundary

```yaml
authority_boundary:
  merge_authority: PM_L2_ONLY
  direct_main_write_allowed: false
  server_apply_allowed: false
  deployment_allowed: false
  n8n_changes_allowed: false
  docker_restart_down_prune_allowed: false
  infra_changes_allowed: false
  graph_edit_allowed_without_pm_l2: false
  secrets_allowed_in_chat: false
```

## Source of Truth boundary

GitHub repository artifacts define accepted architecture, procedures, and evidence requirements.

Flowise runtime is an execution surface. Server SQLite is an applied-state evidence source. Server filesystem is not architectural proof by itself.

## Non-goals

This hardening step does not:

- deploy the graph to production;
- claim trading readiness;
- connect the graph to MOEX Bot production runtime;
- alter n8n;
- restart Docker;
- change server network or firewall configuration;
- grant Flowise authority to merge or deploy.
