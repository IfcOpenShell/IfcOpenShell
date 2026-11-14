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

The query tools are served, and the edit tools in ``EDIT_TOOLS``. An edit that
changes the model becomes the undo step of the ``bim.mcp_edit`` operator, which
covers both the IFC change and the objects updated to match it. ``ifc_undo``
and ``ifc_redo`` step through Bonsai's undo history, but only over those steps,
never the user's own. The tools in ``VIEW_TOOLS`` read and change the
selection and the 3D viewport.
"""

from __future__ import annotations

import json
import socket
import time
from typing import Any, NamedTuple, Optional

import bpy

import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore

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


# Tools that change the model, each run as one Bonsai undo step.
EDIT_TOOLS = frozenset({"ifc_edit", "ifc_shape", "ifc_quantify"})
# The operator that runs them, whose class name ends the key of each step it adds.
EDIT_OPERATOR = "McpEdit"
# Tools that only Bonsai has: they read or change the selection and the viewport, never the model.
VIEW_TOOLS = frozenset({"bonsai_selection", "bonsai_select", "bonsai_view", "bonsai_screenshot"})


class _State:
    sock: Optional[socket.socket] = None
    clients: list[_Client] = []
    pending_writes: list[_PendingWrite] = []
    last_request: float = 0.0
    # The transaction of an edit, for bim.mcp_edit to make its undo step, and
    # whether it did, with any error updating Blender to match.
    edit: Optional[Any] = None
    adopted: bool = False
    sync_error: Optional[str] = None


def _session() -> Any:
    from ifcmcp.core import IfcSession

    return IfcSession(model=tool.Ifc.get(), model_path=tool.Ifc.get_path() or None)


def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    """Run one ifcmcp tool on the model open in Bonsai."""
    from ifcmcp.server import READ_ONLY_TOOLS

    if request.get("type") != "tool":
        return {"status": "error", "message": f"Unknown request type: {request.get('type')!r}"}
    name = request.get("name")
    args = request.get("args") or {}
    if name not in READ_ONLY_TOOLS | EDIT_TOOLS | VIEW_TOOLS | {"ifc_undo", "ifc_redo"}:
        return {"status": "error", "message": f"{name} is not available from Bonsai"}
    if tool.Ifc.get() is None:
        return {"status": "error", "message": "No IFC project is open in Bonsai"}
    if name in EDIT_TOOLS:
        return _edit(name, args)
    if name in VIEW_TOOLS:
        return _view(name, args)
    if name == "ifc_undo":
        return _undo()
    if name == "ifc_redo":
        return _redo()
    try:
        result = _session().dispatch(name, args)
    except Exception as e:
        return {"status": "error", "message": str(e) or type(e).__name__}
    return {"status": "ok", "result": result}


def _view(name: str, args: dict[str, Any]) -> dict[str, Any]:
    from bonsai.bim.module.mcp import view

    try:
        if name == "bonsai_selection":
            result = view.selection()
        elif name == "bonsai_select":
            session = _session()
            elements = [session._get_element(i) for i in args.get("element_ids") or []]
            if not elements:
                return {"status": "error", "message": "No element_ids given"}
            result = view.select(elements, frame=args.get("frame", True))
        elif name == "bonsai_view":
            result = view.set_view(direction=args.get("direction", ""), frame=args.get("frame", "selected"))
        else:
            result = view.screenshot()
    except Exception as e:
        return {"status": "error", "message": str(e) or type(e).__name__}
    return {"status": "ok", "result": result}


def _call_operator(operator: Any, *args: Any) -> None:
    """Call an operator from the timer, which runs without a window or screen that undo needs."""
    window = bpy.context.window or next(iter(bpy.context.window_manager.windows), None)
    if window is None:  # Background mode.
        operator(*args)
        return
    with bpy.context.temp_override(window=window, screen=window.screen):
        operator(*args)


def _edit(name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Run an edit, then make what it changed one Bonsai undo step.

    ifcmcp runs the edit in a transaction of its own, rolled back if the edit
    fails. Only an edit that changed the model reaches ``bim.mcp_edit``, so a
    failed call adds no undo step and leaves redo alone.
    """
    model = tool.Ifc.get()
    last = model.history[-1] if model.history else None
    try:
        result = _session().dispatch(name, args)
    except Exception as e:
        return {"status": "error", "message": str(e) or type(e).__name__}
    if not model.history or model.history[-1] is last:
        return {"status": "ok", "result": result}
    _State.edit, _State.adopted, _State.sync_error = model.history[-1], False, None
    try:
        # Undo is off by default for an operator called from Python.
        _call_operator(bpy.ops.bim.mcp_edit, "EXEC_DEFAULT", True)
    except Exception as e:
        _State.sync_error = _State.sync_error or f"{type(e).__name__}: {e}"
    finally:
        transaction, _State.edit = _State.edit, None
    if not _State.adopted:
        # Without an undo step for it, the change could never be undone: revert it.
        model.history.remove(transaction)
        transaction.rollback()
        return {"status": "error", "message": f"Bonsai could not run the edit: {_State.sync_error}"}
    if _State.sync_error:
        return {
            "status": "error",
            "message": f"The edit was made, but Bonsai could not update its objects to match "
            f"({_State.sync_error}). ifc_undo reverts it.",
        }
    return {"status": "ok", "result": result}


def adopt_edit() -> None:
    """Make the pending edit's transaction ``bim.mcp_edit``'s undo step, and update Blender to match."""
    from bonsai.bim.module.mcp import sync

    model = tool.Ifc.get()
    transaction = _State.edit
    assert transaction is not None and model.history and model.history[-1] is transaction
    # Bonsai opened an empty transaction for the operator: the edit's replaces it.
    model.history.pop()
    model.transaction = transaction
    _State.adopted = True
    try:
        sync.apply(model, sync.find_changes(model, transaction.operations))
    except Exception as e:
        _State.sync_error = f"{type(e).__name__}: {e}"


def _is_mcp_step(step: dict[str, Any]) -> bool:
    return step["key"].endswith(EDIT_OPERATOR)


def _history_state() -> dict[str, Any]:
    def count(steps: list) -> int:
        n = 0
        for step in reversed(steps):
            if not _is_mcp_step(step):
                break
            n += 1
        return n

    return {"ok": True, "undo_available": count(IfcStore.history), "redo_available": count(IfcStore.future)}


def _undo() -> dict[str, Any]:
    if not IfcStore.history or not _is_mcp_step(IfcStore.history[-1]):
        return {"status": "error", "message": "Nothing to undo: the last change in Bonsai was not made through MCP."}
    key = IfcStore.history[-1]["key"]
    _call_operator(bpy.ops.ed.undo)
    if any(step["key"] == key for step in IfcStore.history):
        # Blender's last undo step was the user's, not ours: put it back.
        _call_operator(bpy.ops.ed.redo)
        return {
            "status": "error",
            "message": "Nothing to undo: the last step in Bonsai's undo history was not made through MCP.",
        }
    return {"status": "ok", "result": _history_state()}


def _redo() -> dict[str, Any]:
    if not IfcStore.future or not _is_mcp_step(IfcStore.future[-1]):
        return {"status": "error", "message": "Nothing to redo: the next change in Bonsai was not made through MCP."}
    key = IfcStore.future[-1]["key"]
    try:
        _call_operator(bpy.ops.ed.redo)
    except RuntimeError:
        # Blender has nothing to redo: a change made in Bonsai since the undo discarded it.
        return {"status": "error", "message": "Nothing to redo: a change made in Bonsai since the undo discarded it."}
    if not IfcStore.history or IfcStore.history[-1]["key"] != key:
        _call_operator(bpy.ops.ed.undo)
        return {
            "status": "error",
            "message": "Nothing to redo: the next step in Bonsai's undo history was not made through MCP.",
        }
    return {"status": "ok", "result": _history_state()}


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
