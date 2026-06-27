from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    """Local/dev runtime configuration only.

    The MVP intentionally avoids secrets, private endpoints, deployment
    coordinates, and production database connection strings.
    """

    sqlite_path: str = ":memory:"
    lease_duration_seconds: int = 600
    max_lease_duration_seconds: int = 3600
    max_attempts: int = 3
    backoff_seconds: int = 60
    auth_mode: str = "local_dev_no_auth"

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        return cls(
            sqlite_path=os.getenv("STATE_API_SQLITE_PATH", ":memory:"),
            lease_duration_seconds=int(os.getenv("STATE_API_LEASE_DURATION_SECONDS", "600")),
            max_lease_duration_seconds=int(os.getenv("STATE_API_MAX_LEASE_DURATION_SECONDS", "3600")),
            max_attempts=int(os.getenv("STATE_API_MAX_ATTEMPTS", "3")),
            backoff_seconds=int(os.getenv("STATE_API_BACKOFF_SECONDS", "60")),
            auth_mode="local_dev_no_auth",
        )
