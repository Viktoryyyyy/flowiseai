from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UniversalRoleRunnerConfig:
    """Local/dev runner boundary configuration.

    Phase 2E is intentionally repository-local. Every external execution flag
    remains false; GitHub execution requests are validated artifacts only.
    """

    project: str = "MOEX Bot"
    execution_mode: str = "browser_chatgpt_github_direct"
    claimant_role: str = "UNIVERSAL_ROLE_RUNNER"
    claimant_id: str = "local-dev-runner"
    default_lease_duration_seconds: int | None = None
    allow_github_mutation_execution: bool = False
    allow_server_apply: bool = False
    allow_deployment: bool = False
    allow_runtime_smoke: bool = False
    allow_secrets: bool = False
    allow_private_endpoints: bool = False
