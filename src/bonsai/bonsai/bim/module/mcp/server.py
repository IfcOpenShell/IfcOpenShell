# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

# The socket handling is adapted from the Blender MCP add-on
# (https://projects.blender.org/lab/blender_mcp, mcp_to_blender_server.py),
# Copyright 2026 Blender Authors, GPL-3.0-or-later.

"""Non-blocking TCP server that answers ifcmcp tool calls about the open IFC model.

``ifcmcp --bonsai`` connects once per tool call and sends a JSON request ending
in a null byte: ``{"type": "tool", "name": "ifc_summary", "args": {}}``. The
reply is ``{"status": "ok", "result": ...}`` or ``{"status": "error",
"message": ...}``, also ending in a null byte. A timer polls the socket on
Blender's main thread, so the model is never touched from another thread.

Only the tools that change nothing are served.
"""

from __future__ import annotations

import json
import socket
import time
from typing import Any, NamedTuple, Optional

import bpy

import bonsai.tool as tool

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9877

# Seconds between polls while requests are arriving, and once idle.
_INTERVAL_ACTIVE = 0.05
_INTERVAL_IDLE = 0.5
# Seconds without a request before polling slows to the idle rate.
_IDLE_DELAY = 5.0
_MAX_REQUEST_BYTES = 10 * 1024 * 1024
_LISTEN_BACKLOG = 5
_RECV_BUFFER_SIZE = 65536
# Seconds before a client that has not sent a complete request is closed.
_CLIENT_TIMEOUT = 10.0
# Seconds to keep writing a reply before giving up on the client.
_SEND_TIMEOUT = 30.0


class _Client:
    __slots__ = ("conn", "buffer", "deadline")

    def __init__(self, conn: socket.socket) -> None:
        self.conn = conn
        self.buffer = bytearray()
        self.deadline = time.monotonic() + _CLIENT_TIMEOUT


class _PendingWrite(NamedTuple):
    conn: socket.socket
    data: memoryview
    deadline: float


class _State:
    sock: Optional[socket.socket] = None
    clients: list[_Client] = []
    pending_writes: list[_PendingWrite] = []
    last_request: float = 0.0


def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    """Run one ifcmcp read-only tool on the model open in Bonsai."""
    from ifcmcp.core import IfcSession
    from ifcmcp.server import READ_ONLY_TOOLS

    if request.get("type") != "tool":
        return {"status": "error", "message": f"Unknown request type: {request.get('type')!r}"}
    name = request.get("name")
    if name not in READ_ONLY_TOOLS:
        return {"status": "error", "message": f"{name} is not available from Bonsai, which serves only read-only tools"}
    model = tool.Ifc.get()
    if model is None:
        return {"status": "error", "message": "No IFC project is open in Bonsai"}
    session = IfcSession(model=model, model_path=tool.Ifc.get_path() or None)
    try:
        result = session.dispatch(name, request.get("args") or {})
    except Exception as e:
        return {"status": "error", "message": str(e) or type(e).__name__}
    return {"status": "ok", "result": result}


def _encode(response: dict[str, Any]) -> bytes:
    return (json.dumps(response) + "\0").encode("utf-8")


def _close(conn: socket.socket) -> None:
    try:
        conn.close()
    except OSError:
        pass


# Never use `sendall` on these non-blocking sockets: it raises as soon as the
# kernel send buffer fills and leaves the client a truncated reply. Write what
# the socket takes now and the rest on later polls.
def _send_partial(conn: socket.socket, data: memoryview) -> memoryview:
    while data:
        try:
            sent = conn.send(data)
        except BlockingIOError:
            break
        except OSError:
            return memoryview(b"")
        data = data[sent:]
    return data


def _reply_and_close(conn: socket.socket, response: dict[str, Any]) -> None:
    data = _send_partial(conn, memoryview(_encode(response)))
    if data:
        _State.pending_writes.append(_PendingWrite(conn, data, time.monotonic() + _SEND_TIMEOUT))
    else:
        _close(conn)


def _flush_pending_writes() -> None:
    pending = []
    for write in _State.pending_writes:
        data = _send_partial(write.conn, write.data)
        if data and time.monotonic() < write.deadline:
            pending.append(write._replace(data=data))
        else:
            _close(write.conn)
    _State.pending_writes = pending


def _accept_clients() -> None:
    while _State.sock is not None:
        try:
            conn, _ = _State.sock.accept()
        except OSError:  # Includes BlockingIOError when none are waiting.
            break
        conn.setblocking(False)
        _State.clients.append(_Client(conn))


def _service_clients() -> bool:
    """Read from every client and answer each complete request. Return whether any was answered."""
    answered = False
    for client in _State.clients[:]:
        if time.monotonic() > client.deadline:
            _State.clients.remove(client)
            _reply_and_close(client.conn, {"status": "error", "message": "Client timed out"})
            continue
        try:
            chunk = client.conn.recv(_RECV_BUFFER_SIZE)
        except BlockingIOError:
            continue
        except OSError:
            chunk = b""
        if not chunk:
            _State.clients.remove(client)
            _close(client.conn)
            continue
        client.buffer.extend(chunk)
        if len(client.buffer) > _MAX_REQUEST_BYTES:
            _State.clients.remove(client)
            _reply_and_close(
                client.conn, {"status": "error", "message": f"Request exceeds {_MAX_REQUEST_BYTES} byte limit"}
            )
            continue
        if b"\0" not in client.buffer:
            continue
        _State.clients.remove(client)
        try:
            request = json.loads(bytes(client.buffer[: client.buffer.index(b"\0")]))
            response = handle_request(request)
        except Exception as e:
            response = {"status": "error", "message": f"{type(e).__name__}: {e}"}
        _reply_and_close(client.conn, response)
        answered = True
    return answered


def poll() -> bool:
    """Accept connections, answer complete requests and finish queued replies.

    Return whether there is still work in progress.
    """
    _flush_pending_writes()
    _accept_clients()
    if _service_clients():
        _State.last_request = time.monotonic()
    return bool(_State.clients or _State.pending_writes)


def _timer() -> Optional[float]:
    if _State.sock is None:
        return None
    busy = poll()
    if busy or time.monotonic() - _State.last_request < _IDLE_DELAY:
        return _INTERVAL_ACTIVE
    return _INTERVAL_IDLE


def start(port: int = DEFAULT_PORT, host: str = DEFAULT_HOST) -> None:
    """Listen on ``host:port`` and poll for requests from a Blender timer.

    Raises ``OSError`` if the port is in use.
    """
    if is_running():
        raise RuntimeError("The MCP bridge is already running")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(False)
        sock.bind((host, port))
        sock.listen(_LISTEN_BACKLOG)
    except OSError:
        sock.close()
        raise
    _State.sock = sock
    _State.last_request = time.monotonic()
    if not bpy.app.timers.is_registered(_timer):
        bpy.app.timers.register(_timer, persistent=True)


def stop() -> None:
    """Close the listening socket and every open connection."""
    sock, _State.sock = _State.sock, None
    if sock is not None:
        _close(sock)
    for client in _State.clients:
        _close(client.conn)
    _State.clients = []
    for write in _State.pending_writes:
        _close(write.conn)
    _State.pending_writes = []
    if bpy.app.timers.is_registered(_timer):
        bpy.app.timers.unregister(_timer)


def is_running() -> bool:
    return _State.sock is not None


def port() -> Optional[int]:
    return _State.sock.getsockname()[1] if _State.sock is not None else None
