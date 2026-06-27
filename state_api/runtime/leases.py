from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid

from .models import DEFAULT_LEASE_DURATION_SECONDS, MAX_LEASE_DURATION_SECONDS, STATE_API_SCHEMA_VERSION, JsonDict
from .validation import validate_lease_duration


def parse_utc_iso(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_lease(
    *,
    task_id: str,
    claimant_role: str,
    claimant_id: str,
    claimed_at: str,
    lease_duration_seconds: int | None = None,
    max_lease_duration_seconds: int = MAX_LEASE_DURATION_SECONDS,
    default_lease_duration_seconds: int = DEFAULT_LEASE_DURATION_SECONDS,
) -> JsonDict:
    duration = validate_lease_duration(
        lease_duration_seconds,
        default_lease_duration_seconds,
        max_lease_duration_seconds,
    )
    expires_at = utc_iso(parse_utc_iso(claimed_at) + timedelta(seconds=duration))
    return {
        "lease_id": f"lease-{uuid.uuid4()}",
        "schema_version": STATE_API_SCHEMA_VERSION,
        "task_id": task_id,
        "claimant_role": claimant_role,
        "claimant_id": claimant_id,
        "lease_state": "active",
        "claimed_at": claimed_at,
        "expires_at": expires_at,
        "renewed_at": None,
        "released_at": None,
        "lease_duration_seconds": duration,
        "max_lease_duration_seconds": max_lease_duration_seconds,
        "exclusive": True,
        "runtime_claim": False,
    }


def renew_lease_payload(
    *,
    lease: JsonDict,
    renewed_at: str,
    lease_duration_seconds: int | None = None,
    max_lease_duration_seconds: int = MAX_LEASE_DURATION_SECONDS,
    default_lease_duration_seconds: int = DEFAULT_LEASE_DURATION_SECONDS,
) -> JsonDict:
    duration = validate_lease_duration(
        lease_duration_seconds,
        default_lease_duration_seconds,
        max_lease_duration_seconds,
    )
    lease = dict(lease)
    lease["lease_state"] = "renewed"
    lease["renewed_at"] = renewed_at
    lease["lease_duration_seconds"] = duration
    lease["max_lease_duration_seconds"] = max_lease_duration_seconds
    lease["expires_at"] = utc_iso(parse_utc_iso(renewed_at) + timedelta(seconds=duration))
    return lease


def release_lease_payload(*, lease: JsonDict, released_at: str) -> JsonDict:
    lease = dict(lease)
    lease["lease_state"] = "released"
    lease["released_at"] = released_at
    return lease
