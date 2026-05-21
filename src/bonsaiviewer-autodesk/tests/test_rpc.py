"""Tests for the JSON-RPC host (``bonsaiviewer_autodesk.rpc``)."""

from __future__ import annotations

import io
import json

from bonsaiviewer_autodesk.rpc import (
    JSONRPC_INTERNAL_ERROR,
    JSONRPC_INVALID_PARAMS,
    JSONRPC_INVALID_REQUEST,
    JSONRPC_METHOD_NOT_FOUND,
    JSONRPC_PARSE_ERROR,
    JsonRpcHost,
    RpcError,
)


def run(line: str, handlers: dict | None = None) -> tuple[list[dict], str]:
    """Drive a ``JsonRpcHost`` over in-memory streams.

    Returns ``(responses, stderr_text)`` where ``responses`` is the parsed
    JSON written to stdout, one element per line.
    """
    out = io.StringIO()
    err = io.StringIO()
    JsonRpcHost(
        handlers or {},
        stdin=io.StringIO(line),
        stdout=out,
        stderr=err,
    ).run()
    responses = [json.loads(piece) for piece in out.getvalue().splitlines() if piece]
    return responses, err.getvalue()


def test_parse_error_for_invalid_json():
    responses, _ = run("this is not json\n")
    assert responses[0]["error"]["code"] == JSONRPC_PARSE_ERROR
    assert responses[0]["id"] is None


def test_request_must_be_a_json_object():
    responses, _ = run("[1, 2, 3]\n")
    assert responses[0]["error"]["code"] == JSONRPC_INVALID_REQUEST


def test_wrong_jsonrpc_version_keeps_id():
    responses, _ = run('{"jsonrpc": "1.0", "id": 7, "method": "go"}\n')
    assert responses[0]["error"]["code"] == JSONRPC_INVALID_REQUEST
    assert responses[0]["id"] == 7


def test_missing_method_string():
    responses, _ = run('{"jsonrpc": "2.0", "id": 1}\n')
    assert responses[0]["error"]["code"] == JSONRPC_INVALID_REQUEST


def test_params_must_be_object_or_array():
    responses, _ = run('{"jsonrpc": "2.0", "id": 1, "method": "go", "params": 5}\n')
    assert responses[0]["error"]["code"] == JSONRPC_INVALID_PARAMS


def test_unknown_method():
    responses, _ = run('{"jsonrpc": "2.0", "id": 1, "method": "nope"}\n')
    assert responses[0]["error"]["code"] == JSONRPC_METHOD_NOT_FOUND


def test_successful_result_round_trip():
    responses, _ = run(
        '{"jsonrpc": "2.0", "id": 42, "method": "echo", "params": {"x": 1}}\n',
        {"echo": lambda params: params},
    )
    assert responses == [{"jsonrpc": "2.0", "id": 42, "result": {"x": 1}}]


def test_rpc_error_is_forwarded_with_code_and_data():
    def handler(_params):
        raise RpcError(JSONRPC_INTERNAL_ERROR, "boom", data={"detail": "x"})

    responses, _ = run(
        '{"jsonrpc": "2.0", "id": 1, "method": "go"}\n',
        {"go": handler},
    )
    assert responses[0]["error"] == {
        "code": JSONRPC_INTERNAL_ERROR,
        "message": "boom",
        "data": {"detail": "x"},
    }


def test_unexpected_exception_becomes_internal_error():
    def handler(_params):
        raise ValueError("kaboom")

    responses, stderr = run(
        '{"jsonrpc": "2.0", "id": 1, "method": "go"}\n',
        {"go": handler},
    )
    assert responses[0]["error"]["code"] == JSONRPC_INTERNAL_ERROR
    assert responses[0]["error"]["message"] == "kaboom"
    assert "Traceback" in stderr


def test_notification_runs_handler_but_writes_no_response():
    calls: list[int] = []
    responses, _ = run(
        '{"jsonrpc": "2.0", "method": "go"}\n',
        {"go": lambda _params: calls.append(1)},
    )
    assert calls == [1]
    assert responses == []


def test_blank_lines_skipped_and_requests_processed_in_order():
    line = (
        '{"jsonrpc": "2.0", "id": 1, "method": "go"}\n'
        "\n"
        "   \n"
        '{"jsonrpc": "2.0", "id": 2, "method": "go"}\n'
    )
    responses, _ = run(line, {"go": lambda _params: "ok"})
    assert [r["id"] for r in responses] == [1, 2]
