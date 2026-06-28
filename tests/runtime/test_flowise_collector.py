from __future__ import annotations

import json
import pathlib

import httpx
from jsonschema import Draft202012Validator

from universal_role_runner.flowise_collector import collect_flowise_response


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REQUEST_SCHEMA = REPO_ROOT / "contracts" / "collector" / "flowise_collector_request.schema.json"
RESULT_SCHEMA = REPO_ROOT / "contracts" / "collector" / "flowise_collector_result.schema.json"


def _request(**overrides):
    payload = {
        "contract_version": "1.0.0",
        "correlation_id": "phase-13-test-001",
        "graph_id": "graph-123",
        "base_url": "http://flowise.local",
        "question": "Return a PM L2 structured result.",
    }
    payload.update(overrides)
    return payload


def _schema(path: pathlib.Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_collector_schemas_validate_against_draft_2020_12():
    for path in (REQUEST_SCHEMA, RESULT_SCHEMA):
        schema = _schema(path)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        Draft202012Validator.check_schema(schema)


def test_minimal_request_and_success_result_validate_against_schemas():
    request_schema = _schema(REQUEST_SCHEMA)
    result_schema = _schema(RESULT_SCHEMA)
    request = _request()

    Draft202012Validator(request_schema).validate(request)

    def handler(http_request: httpx.Request) -> httpx.Response:
        assert str(http_request.url) == "http://flowise.local/api/v1/prediction/graph-123"
        body = json.loads(http_request.content.decode("utf-8"))
        assert body["question"] == request["question"]
        assert body["overrideConfig"]["sessionId"] == request["correlation_id"]
        assert body["streaming"] is False
        return httpx.Response(
            200,
            json={
                "chatId": "chat-001",
                "id": "result-001",
                "text": '{"status":"pass","evidence":["mock"]}',
            },
        )

    result = collect_flowise_response(request, client=_client(handler))

    Draft202012Validator(result_schema).validate(result)
    assert result["normalized_status"] == "success"
    assert result["blocker_code"] == "none"
    assert result["correlation_id"] == request["correlation_id"]
    assert result["graph_id"] == request["graph_id"]
    assert result["role_output"] == {"status": "pass", "evidence": ["mock"]}
    assert result["metadata"]["github_mutation_performed"] is False
    assert result["metadata"]["server_apply_performed"] is False


def test_collector_uses_flowise_base_url_from_environment(monkeypatch):
    monkeypatch.setenv("FLOWISE_BASE_URL", "http://127.0.0.1:3000/")

    def handler(http_request: httpx.Request) -> httpx.Response:
        assert str(http_request.url) == "http://127.0.0.1:3000/api/v1/prediction/graph-123"
        return httpx.Response(200, json={"text": "plain role output"})

    request = _request()
    request.pop("base_url")

    result = collect_flowise_response(request, client=_client(handler))

    assert result["normalized_status"] == "success"
    assert result["role_output"] == {"text": "plain role output"}


def test_collector_supports_runtime_graph_identifier_and_form_payload():
    def handler(http_request: httpx.Request) -> httpx.Response:
        assert str(http_request.url) == "http://flowise.local/api/v1/prediction/runtime-graph-abc"
        body = json.loads(http_request.content.decode("utf-8"))
        assert body["form"] == {"task": "run"}
        assert "question" not in body
        return httpx.Response(200, json={"role_output": {"status": "ok"}})

    request = _request(runtime_graph_id="runtime-graph-abc", form={"task": "run"})
    request.pop("graph_id")
    request.pop("question")

    result = collect_flowise_response(request, client=_client(handler))

    assert result["graph_id"] == "runtime-graph-abc"
    assert result["role_output"] == {"status": "ok"}


def test_collector_classifies_missing_base_url_as_request_validation_failure(monkeypatch):
    monkeypatch.delenv("FLOWISE_BASE_URL", raising=False)
    request = _request()
    request.pop("base_url")

    result = collect_flowise_response(request)

    assert result["normalized_status"] == "blocked"
    assert result["blocker_code"] == "request_validation_failure"
    assert result["raw_status"]["http_status"] is None


def test_collector_classifies_connection_failure():
    def handler(http_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    result = collect_flowise_response(_request(), client=_client(handler))

    assert result["normalized_status"] == "blocked"
    assert result["blocker_code"] == "connection_failure"
    assert result["raw_status"]["ok"] is False


def test_collector_classifies_auth_failure_without_printing_secret(monkeypatch):
    monkeypatch.setenv("FLOWISE_API_KEY", "sk-test-secret-value")

    def handler(http_request: httpx.Request) -> httpx.Response:
        assert http_request.headers["Authorization"] == "Bearer sk-test-secret-value"
        return httpx.Response(401, text="invalid token sk-test-secret-value")

    result = collect_flowise_response(_request(), client=_client(handler))

    assert result["normalized_status"] == "blocked"
    assert result["blocker_code"] == "auth_failure"
    assert result["raw_status"]["http_status"] == 401
    assert "sk-test-secret-value" not in json.dumps(result)


def test_collector_classifies_non_json_2xx_as_schema_failure():
    def handler(http_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not-json")

    result = collect_flowise_response(_request(), client=_client(handler))

    assert result["normalized_status"] == "failed"
    assert result["blocker_code"] == "schema_failure"
    assert result["raw_status"]["http_status"] == 200


def test_collector_classifies_runtime_failure():
    def handler(http_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="node failed")

    result = collect_flowise_response(_request(), client=_client(handler))

    assert result["normalized_status"] == "failed"
    assert result["blocker_code"] == "runtime_failure"
    assert result["raw_status"]["http_status"] == 500
