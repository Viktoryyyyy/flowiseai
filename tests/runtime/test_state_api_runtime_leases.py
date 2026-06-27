from __future__ import annotations

import pytest

from state_api.runtime.errors import LeaseError, RuntimeValidationError

from conftest import sample_task


def test_claim_creates_exclusive_finite_lease_without_state_transition(operations) -> None:
    operations.create_task(sample_task("task-lease"), idempotency_key="idem-lease-create")
    claim = operations.claim_next_task(
        lane="flowiseai_pm_orchestration",
        claimant_role="SUBCHAT_IMPLEMENTATION",
        claimant_id="worker-a",
        idempotency_key="idem-lease-claim-a",
    )
    lease = claim["lease"]
    assert lease["exclusive"] is True
    assert lease["runtime_claim"] is False
    assert lease["lease_duration_seconds"] == 600
    assert operations.read_task("task-lease")["task"]["lifecycle_state"] == "created"

    blocked_claim = operations.claim_next_task(
        lane="flowiseai_pm_orchestration",
        claimant_role="SUBCHAT_IMPLEMENTATION",
        claimant_id="worker-b",
        idempotency_key="idem-lease-claim-b",
    )
    assert blocked_claim["lease"] is None


def test_renew_and_release_task_lease(operations) -> None:
    operations.create_task(sample_task("task-renew"), idempotency_key="idem-renew-create")
    claim = operations.claim_next_task(
        lane="flowiseai_pm_orchestration",
        claimant_role="SUBCHAT_IMPLEMENTATION",
        claimant_id="worker-a",
        idempotency_key="idem-renew-claim",
    )
    lease_id = claim["lease"]["lease_id"]

    renewed = operations.renew_task_lease(
        lease_id,
        claimant_id="worker-a",
        lease_duration_seconds=1200,
        idempotency_key="idem-renew",
    )
    assert renewed["lease"]["lease_state"] == "renewed"
    assert renewed["lease"]["lease_duration_seconds"] == 1200

    released = operations.release_task_lease(
        lease_id,
        claimant_id="worker-a",
        idempotency_key="idem-release",
    )
    assert released["lease"]["lease_state"] == "released"

    with pytest.raises(LeaseError):
        operations.renew_task_lease(
            lease_id,
            claimant_id="worker-a",
            idempotency_key="idem-renew-after-release",
        )


def test_expired_lease_allows_new_claim(operations, clock) -> None:
    operations.create_task(sample_task("task-expiry"), idempotency_key="idem-expiry-create")
    first = operations.claim_next_task(
        lane="flowiseai_pm_orchestration",
        claimant_role="SUBCHAT_IMPLEMENTATION",
        claimant_id="worker-a",
        lease_duration_seconds=1,
        idempotency_key="idem-expiry-claim-a",
    )
    assert first["lease"]["task_id"] == "task-expiry"

    clock.advance(2)

    second = operations.claim_next_task(
        lane="flowiseai_pm_orchestration",
        claimant_role="SUBCHAT_IMPLEMENTATION",
        claimant_id="worker-b",
        idempotency_key="idem-expiry-claim-b",
    )
    assert second["lease"]["task_id"] == "task-expiry"
    assert operations.repository.get_lease(first["lease"]["lease_id"])["lease_state"] == "expired"


def test_lease_duration_has_configured_maximum(operations) -> None:
    operations.create_task(sample_task("task-max-lease"), idempotency_key="idem-max-lease-create")
    with pytest.raises(RuntimeValidationError):
        operations.claim_next_task(
            lane="flowiseai_pm_orchestration",
            claimant_role="SUBCHAT_IMPLEMENTATION",
            claimant_id="worker-a",
            lease_duration_seconds=3601,
            idempotency_key="idem-max-lease-claim",
        )
