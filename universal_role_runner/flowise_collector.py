from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx


RESULT_VERSION = "1.0.0"
REQUEST_VERSION = "1.0.0"

SECRET_MARKERS = (
    "authorization",
    "bearer ",
    "token",
    "api_key",
    "apikey",
    "password",
    "secret",
)


@dataclass(frozen=True)
class CollectorConfig:
    base_url: str
    graph_id: str
    timeout_seconds: float


class CollectorRequestError(ValueError):
    pass


def _redact(value: Any) -> Any:
    """Return a representation that is safe for reports and chat output."""

    if value is None:
        return None
    text = str(value)
    lowered = text.lower()
    if any(marker in lowered for marker in SECRET_MARKERS):
        return "[REDACTED]"
    return text[:500]


def _graph_id(request: dict[str, Any]) -> str:
    value = request.get("graph_id") or request.get("runtime_graph_id")
    if not isinstance(value, str) or not value.strip():
        raise CollectorRequestError("graph_id or runtime_graph_id is required")
    return value.strip()


def _base_url(request: dict[str, Any]) -> str:
    value = request.get("base_url") or os.getenv("FLOWISE_BASE_URL")
    if not isinstance(value, str) or not value.strip():
        raise CollectorRequestError("base_url is required or FLOWISE_BASE_URL must be set")
    return value.strip().rstrip("/")


def _timeout_seconds(request: dict[str, Any]) -> float:
    value = request.get("timeout_seconds", 30)
    try:
        timeout = float(value)
    except (TypeError, ValueError) as exc:
        raise CollectorRequestError("timeout_seconds must be numeric") from exc
    if timeout < 1 or timeout > 120:
        raise CollectorRequestError("timeout_seconds must be between 1 and 120")
    return timeout


def _validate_request(request: dict[str, Any]) -> CollectorConfig:
    if not isinstance(request, dict):
        raise CollectorRequestError("request must be a JSON object")

    if request.get("contract_version") != REQUEST_VERSION:
        raise CollectorRequestError("contract_version must be 1.0.0")

    correlation_id = request.get("correlation_id")
    if not isinstance(correlation_id, str) or not correlation_id.strip():
        raise CollectorRequestError("correlation_id is required")

    has_question = isinstance(request.get("question"), str) and bool(request["question"].strip())
    has_form = isinstance(request.get("form"), dict)
    if not has_question and not has_form:
        raise CollectorRequestError("question or form is required")

    return CollectorConfig(
        base_url=_base_url(request),
        graph_id=_graph_id(request),
        timeout_seconds=_timeout_seconds(request),
    )


def _headers_from_environment() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}

    bearer_token = os.getenv("FLOWISE_API_KEY") or os.getenv("FLOWISE_ACCESS_TOKEN")
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    custom_name = os.getenv("FLOWISE_AUTH_HEADER_NAME")
    custom_value = os.getenv("FLOWISE_AUTH_HEADER_VALUE")
    if custom_name and custom_value:
        headers[custom_name] = custom_value

    return headers


def _prediction_payload(request: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {"streaming": False}

    if isinstance(request.get("question"), str) and request["question"].strip():
        payload["question"] = request["question"]

    if isinstance(request.get("form"), dict):
        payload["form"] = request["form"]

    if isinstance(request.get("override_config"), dict):
        payload["overrideConfig"] = dict(request["override_config"])
    else:
        payload["overrideConfig"] = {}

    payload["overrideConfig"].setdefault("sessionId", request["correlation_id"])

    if isinstance(request.get("history"), list):
        payload["history"] = request["history"]

    if isinstance(request.get("uploads"), list):
        payload["uploads"] = request["uploads"]

    return payload


def _endpoint(base_url: str, graph_id: str) -> str:
    return f"{base_url}/api/v1/prediction/{quote(graph_id, safe='')}"


def _extract_role_output(response_json: Any) -> Any:
    if not isinstance(response_json, dict):
        return response_json

    for key in ("role_output", "output", "structured_output"):
        if key in response_json:
            return response_json[key]

    text = response_json.get("text")
    if isinstance(text, str):
        stripped = text.strip()
        if stripped:
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                return {"text": text}

    return response_json


def _result(
    *,
    request: dict[str, Any],
    graph_id: str | None,
    raw_ok: bool,
    http_status: int | None,
    normalized_status: str,
    blocker_code: str,
    role_output: Any,
    evidence_summary: list[str],
    error_type: str | None = None,
    error_message: str | None = None,
    request_id: str | None = None,
    result_id: str | None = None,
) -> dict[str, Any]:
    correlation_id = request.get("correlation_id")
    if not isinstance(correlation_id, str) or not correlation_id:
        correlation_id = "unknown"

    return {
        "collector_result_version": RESULT_VERSION,
        "correlation_id": correlation_id,
        "graph_id": graph_id or "unknown",
        "request_id": request_id,
        "result_id": result_id,
        "raw_status": {
            "ok": raw_ok,
            "http_status": http_status,
            "error_type": error_type,
            "error_message": _redact(error_message),
        },
        "normalized_status": normalized_status,
        "blocker_code": blocker_code,
        "role_output": role_output,
        "evidence_summary": evidence_summary,
        "metadata": {
            "collector": "universal_role_runner.flowise_collector",
            "github_mutation_performed": False,
            "server_apply_performed": False,
        },
    }


def _failure_for_http_status(status_code: int) -> tuple[str, str]:
    if status_code in (401, 403):
        return "blocked", "auth_failure"
    return "failed", "runtime_failure"


def collect_flowise_response(
    request: dict[str, Any],
    *,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Call Flowise Prediction API and return a normalized collector result.

    The collector is intentionally limited to Flowise runtime calls. It never
    performs GitHub mutation, merge, or server apply.
    """

    try:
        config = _validate_request(request)
    except CollectorRequestError as exc:
        return _result(
            request=request if isinstance(request, dict) else {},
            graph_id=None,
            raw_ok=False,
            http_status=None,
            normalized_status="blocked",
            blocker_code="request_validation_failure",
            role_output=None,
            evidence_summary=["request validation failed before Flowise call"],
            error_type="request_validation_failure",
            error_message=str(exc),
        )

    url = _endpoint(config.base_url, config.graph_id)
    payload = _prediction_payload(request)
    headers = _headers_from_environment()

    close_client = client is None
    active_client = client or httpx.Client(timeout=config.timeout_seconds)

    try:
        response = active_client.post(
            url,
            json=payload,
            headers=headers,
            timeout=config.timeout_seconds,
        )
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.NetworkError) as exc:
        return _result(
            request=request,
            graph_id=config.graph_id,
            raw_ok=False,
            http_status=None,
            normalized_status="blocked",
            blocker_code="connection_failure",
            role_output=None,
            evidence_summary=[
                "Flowise runtime call attempted",
                "no GitHub mutation performed",
                "no server apply performed",
            ],
            error_type=exc.__class__.__name__,
            error_message=str(exc),
        )
    except httpx.HTTPError as exc:
        return _result(
            request=request,
            graph_id=config.graph_id,
            raw_ok=False,
            http_status=None,
            normalized_status="blocked",
            blocker_code="connection_failure",
            role_output=None,
            evidence_summary=["Flowise HTTP client failed before response was available"],
            error_type=exc.__class__.__name__,
            error_message=str(exc),
        )
    finally:
        if close_client:
            active_client.close()

    if response.status_code < 200 or response.status_code >= 300:
        normalized_status, blocker_code = _failure_for_http_status(response.status_code)
        return _result(
            request=request,
            graph_id=config.graph_id,
            raw_ok=False,
            http_status=response.status_code,
            normalized_status=normalized_status,
            blocker_code=blocker_code,
            role_output=None,
            evidence_summary=[
                f"Flowise runtime returned HTTP {response.status_code}",
                "correlation_id preserved",
                "no GitHub mutation performed",
                "no server apply performed",
            ],
            error_type="http_status_error",
            error_message=response.text[:500],
        )

    try:
        response_json = response.json()
    except ValueError as exc:
        return _result(
            request=request,
            graph_id=config.graph_id,
            raw_ok=False,
            http_status=response.status_code,
            normalized_status="failed",
            blocker_code="schema_failure",
            role_output=None,
            evidence_summary=["Flowise response was not valid JSON"],
            error_type=exc.__class__.__name__,
            error_message=str(exc),
        )

    role_output = _extract_role_output(response_json)
    request_id = None
    result_id = None
    if isinstance(response_json, dict):
        request_id = response_json.get("chatId") or response_json.get("requestId")
        result_id = response_json.get("id") or response_json.get("resultId")

    return _result(
        request=request,
        graph_id=config.graph_id,
        raw_ok=True,
        http_status=response.status_code,
        normalized_status="success",
        blocker_code="none",
        role_output=role_output,
        evidence_summary=[
            "Flowise Prediction API returned 2xx JSON response",
            "correlation_id preserved",
            "role_output normalized",
            "no GitHub mutation performed",
            "no server apply performed",
        ],
        request_id=request_id,
        result_id=result_id,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one controlled Flowise collector request.")
    parser.add_argument("request_json", help="Path to FlowiseCollectorRequest JSON file.")
    args = parser.parse_args(argv)

    with open(args.request_json, "r", encoding="utf-8") as handle:
        request = json.load(handle)

    result = collect_flowise_response(request)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")

    return 0 if result["normalized_status"] == "success" else 2


if __name__ == "__main__":
    raise SystemExit(main())
