from __future__ import annotations

import copy

from .models import JsonDict, SchemaValidationError
from .schema_validation import validate_pm_l3_decision


_DECISION_STATUS_BY_TYPE = {
    "route_next_role": "routed",
    "accept_role_output": "accepted",
    "reject_role_output": "rejected",
    "request_correction": "correction_requested",
    "raise_blocker": "blocked",
    "return_to_pm_l2": "returned_to_pm_l2",
    "complete_phase_step": "phase_step_completed",
}

_ARTIFACT_TYPE_BY_DECISION_TYPE = {
    "route_next_role": "role_task_request",
    "accept_role_output": "role_output_acceptance",
    "reject_role_output": "role_output_rejection",
    "request_correction": "correction_request",
    "raise_blocker": "blocker_escalation",
    "return_to_pm_l2": "pm_l2_return_package_request",
    "complete_phase_step": "phase_step_completion_record",
}

_REQUIRED_NEXT_ROLE_DECISIONS = {"route_next_role", "request_correction"}


class PMDecisionRoutingError(SchemaValidationError):
    """Raised when a PM L3 decision is schema-valid but not routeable."""


def _decision_error(message: str, decision: JsonDict, *, details: JsonDict | None = None) -> None:
    merged_details: JsonDict = {"decision_type": decision.get("decision_type")}
    if details:
        merged_details.update(details)
    raise PMDecisionRoutingError(message, merged_details)


def _require_decision_semantics(decision: JsonDict) -> None:
    decision_type = str(decision["decision_type"])
    routing = decision["routing_target"]
    acceptance = decision["acceptance_details"]
    rejection = decision["rejection_details"]
    blocker_details = decision["blocker_details"]

    if decision_type in _REQUIRED_NEXT_ROLE_DECISIONS:
        if not decision.get("next_role"):
            _decision_error("next_role is required for this PM L3 decision type", decision)
        if not isinstance(decision.get("next_task"), dict):
            _decision_error("next_task object is required for this PM L3 decision type", decision)
        if routing.get("target_queue") not in {"browser_chat", "n8n_role_task_queue"}:
            _decision_error(
                "routeable decisions must target a role execution queue",
                decision,
                details={"target_queue": routing.get("target_queue")},
            )
        if routing.get("handoff_required") is not True:
            _decision_error("handoff_required must be true for routed role work", decision)

    if decision_type == "accept_role_output":
        if acceptance.get("accepted") is not True or not acceptance.get("criteria_met"):
            _decision_error("accept_role_output requires accepted=true and criteria_met evidence", decision)
        if routing.get("target_queue") != "none":
            _decision_error("accept_role_output must not directly route another queue", decision)

    if decision_type == "reject_role_output":
        if rejection.get("rejected") is not True or not rejection.get("reasons"):
            _decision_error("reject_role_output requires rejected=true and rejection reasons", decision)
        if routing.get("target_queue") != "none":
            _decision_error("reject_role_output must not directly route another queue", decision)

    if decision_type == "raise_blocker":
        if blocker_details.get("blocked") is not True or not blocker_details.get("blockers"):
            _decision_error("raise_blocker requires blocked=true and at least one blocker", decision)
        if routing.get("target_queue") != "none":
            _decision_error("raise_blocker must not directly route another queue", decision)

    if decision_type == "return_to_pm_l2":
        if routing.get("target_queue") != "pm_l2_return":
            _decision_error("return_to_pm_l2 must target pm_l2_return", decision)
        if routing.get("handoff_required") is not True:
            _decision_error("return_to_pm_l2 requires a handoff artifact", decision)

    if decision_type == "complete_phase_step":
        if acceptance.get("accepted") is not True or not acceptance.get("criteria_met"):
            _decision_error("complete_phase_step requires accepted=true and criteria_met evidence", decision)
        if routing.get("target_queue") != "none":
            _decision_error("complete_phase_step must not directly route another queue", decision)


def build_pm_l3_next_step_artifact(decision: JsonDict) -> JsonDict:
    """Build a deterministic next-step artifact for one PM L3 decision.

    The artifact is repository-local data only. It does not execute GitHub,
    server, deployment, model, Flowise, or runtime-smoke side effects.
    """

    validated = validate_pm_l3_decision(decision)
    _require_decision_semantics(validated)
    decision_type = str(validated["decision_type"])
    routing = validated["routing_target"]

    artifact: JsonDict = {
        "artifact_type": _ARTIFACT_TYPE_BY_DECISION_TYPE[decision_type],
        "decision_id": validated["decision_id"],
        "phase_run_id": validated["phase_run_id"],
        "decision_type": decision_type,
        "status": _DECISION_STATUS_BY_TYPE[decision_type],
        "target_role": routing.get("target_role"),
        "target_queue": routing.get("target_queue"),
        "handoff_required": routing.get("handoff_required"),
        "next_role": validated.get("next_role"),
        "next_task": copy.deepcopy(validated.get("next_task")),
        "acceptance_details": copy.deepcopy(validated["acceptance_details"]),
        "rejection_details": copy.deepcopy(validated["rejection_details"]),
        "blocker_details": copy.deepcopy(validated["blocker_details"]),
        "created_at": validated["created_at"],
        "side_effects": {
            "github_mutation_executed": False,
            "server_apply_executed": False,
            "deployment_executed": False,
            "runtime_smoke_executed": False,
        },
    }

    if decision_type == "route_next_role":
        artifact["next_action"] = "create_or_persist_role_task"
    elif decision_type == "request_correction":
        artifact["next_action"] = "route_correction_task"
    elif decision_type == "return_to_pm_l2":
        artifact["next_action"] = "generate_pm_l2_handoff"
    elif decision_type == "complete_phase_step":
        artifact["next_action"] = "record_phase_step_completion"
    elif decision_type == "raise_blocker":
        artifact["next_action"] = "record_blocker_and_stop"
    else:
        artifact["next_action"] = "record_decision"

    return artifact


def route_pm_l3_decision(decision: JsonDict) -> JsonDict:
    """Interpret a PM L3 decision and return deterministic routing output."""

    artifact = build_pm_l3_next_step_artifact(decision)
    return {
        "routing_status": artifact["status"],
        "decision_id": artifact["decision_id"],
        "decision_type": artifact["decision_type"],
        "next_action": artifact["next_action"],
        "target_role": artifact["target_role"],
        "target_queue": artifact["target_queue"],
        "handoff_required": artifact["handoff_required"],
        "next_step_artifact": artifact,
    }
