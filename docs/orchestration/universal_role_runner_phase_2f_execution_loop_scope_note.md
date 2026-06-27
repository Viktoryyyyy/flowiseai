# Phase 2F Branch Fallback Scope Note

Clean branch creation was attempted but blocked by GitHub connector tool safety in the prior Phase 2E P2 fix cycle.

For Phase 2F, the controlled fallback continues to use the existing `flowiseai-pm/universal-role-runner-runtime-phase-2e` branch.

The merge-review boundary is the GitHub compare from current `main` to this branch. At Phase 2F PR creation, that diff must contain only Phase 2F files:

- `universal_role_runner/execution_loop.py`;
- `tests/runtime/test_universal_role_runner_execution_loop.py`;
- `tests/runtime/test_universal_role_runner_execution_loop_error.py`;
- `docs/orchestration/universal_role_runner_phase_2f_execution_loop.md`;
- this scope note.

This is not a direct write to `main` and does not authorize server apply, deployment, or runtime smoke.
