from __future__ import annotations

import json
import sys
import traceback
from typing import Any, Callable, TextIO


JSONRPC_PARSE_ERROR = -32700
JSONRPC_INVALID_REQUEST = -32600
JSONRPC_METHOD_NOT_FOUND = -32601
JSONRPC_INVALID_PARAMS = -32602
JSONRPC_INTERNAL_ERROR = -32603


class RpcError(Exception):
    def __init__(self, code: int, message: str, data: Any | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


Handler = Callable[[Any], Any]


class JsonRpcHost:
    def __init__(
        self,
        handlers: dict[str, Handler],
        *,
        stdin: TextIO = sys.stdin,
        stdout: TextIO = sys.stdout,
        stderr: TextIO = sys.stderr,
    ) -> None:
        self.handlers = handlers
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def run(self) -> int:
        for line in self.stdin:
            line = line.strip()
            if not line:
                continue
            self._handle_line(line)
        return 0

    def _handle_line(self, line: str) -> None:
        message_id: Any = None
        try:
            try:
                message = json.loads(line)
            except json.JSONDecodeError as exc:
                self._respond_error(None, JSONRPC_PARSE_ERROR, f"Parse error: {exc}")
                return

            if not isinstance(message, dict):
                self._respond_error(None, JSONRPC_INVALID_REQUEST, "Request must be a JSON object")
                return
            if message.get("jsonrpc") != "2.0":
                self._respond_error(message.get("id"), JSONRPC_INVALID_REQUEST, "Missing or wrong 'jsonrpc' version")
                return

            message_id = message.get("id")
            method = message.get("method")
            if not isinstance(method, str):
                self._respond_error(message_id, JSONRPC_INVALID_REQUEST, "Missing 'method' string")
                return

            params = message.get("params", None)
            if params is not None and not isinstance(params, (dict, list)):
                self._respond_error(message_id, JSONRPC_INVALID_PARAMS, "'params' must be a JSON object or array")
                return

            handler = self.handlers.get(method)
            if handler is None:
                self._respond_error(message_id, JSONRPC_METHOD_NOT_FOUND, f"Unknown method '{method}'")
                return

            try:
                result = handler(params)
            except RpcError as exc:
                self._respond_error(message_id, exc.code, exc.message, exc.data)
                return
            except Exception as exc:
                print(f"Handler '{method}' raised: {exc}", file=self.stderr)
                traceback.print_exc(file=self.stderr)
                self._respond_error(message_id, JSONRPC_INTERNAL_ERROR, str(exc))
                return

            if message_id is not None:
                self._respond_result(message_id, result)
        except Exception as exc:
            print(f"Unhandled host error: {exc}", file=self.stderr)
            traceback.print_exc(file=self.stderr)
            self._respond_error(message_id, JSONRPC_INTERNAL_ERROR, str(exc))

    def _respond_result(self, message_id: Any, result: Any) -> None:
        self._write({"jsonrpc": "2.0", "id": message_id, "result": result})

    def _respond_error(self, message_id: Any, code: int, message: str, data: Any | None = None) -> None:
        error: dict[str, Any] = {"code": code, "message": message}
        if data is not None:
            error["data"] = data
        self._write({"jsonrpc": "2.0", "id": message_id, "error": error})

    def _write(self, payload: dict[str, Any]) -> None:
        line = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        self.stdout.write(line + "\n")
        self.stdout.flush()
