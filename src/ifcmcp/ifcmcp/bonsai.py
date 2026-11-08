# This file was generated with the assistance of an AI coding tool.
"""Run ifcmcp's tools on the model open in Bonsai.

Bonsai's MCP bridge (Quality and Coordination > Collaboration > MCP Bridge)
listens on a local port. Each tool call opens a connection, sends
``{"type": "tool", "name": ..., "args": {...}}`` as JSON ending in a null
byte, and reads back
``{"status": "ok", "result": ...}`` or ``{"status": "error", "message": ...}``
in the same framing. Bonsai runs the tool with :class:`ifcmcp.core.IfcSession`
on its own model, so the results match those for a file loaded here.
"""

from __future__ import annotations

import inspect
import json
import socket
from typing import Any

from ifcmcp.core import IfcSession, IfcSessionError

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9877
# Long enough for ifc_clash or ifc_validate on a large model.
_TIMEOUT = 300.0


class BonsaiSession:
    """Stands in for :class:`IfcSession`, forwarding each tool call to Bonsai."""

    def __init__(self, port: int = DEFAULT_PORT, host: str = DEFAULT_HOST) -> None:
        self.host = host
        self.port = port

    def call(self, name: str, args: dict[str, Any]) -> Any:
        request = (json.dumps({"type": "tool", "name": name, "args": args}) + "\0").encode()
        try:
            with socket.create_connection((self.host, self.port), timeout=_TIMEOUT) as sock:
                sock.sendall(request)
                buf = bytearray()
                while b"\0" not in buf:
                    chunk = sock.recv(65536)
                    if not chunk:
                        break
                    buf.extend(chunk)
        except ConnectionRefusedError:
            raise IfcSessionError(
                f"Bonsai is not listening on {self.host}:{self.port}. In Bonsai, open the Quality and "
                "Coordination tab, then Collaboration > MCP Bridge, and press Start MCP Bridge."
            ) from None
        except OSError as e:
            raise IfcSessionError(f"Lost the connection to Bonsai on {self.host}:{self.port}: {e}") from None
        if b"\0" not in buf:
            raise IfcSessionError("Bonsai closed the connection before replying")
        reply = json.loads(buf.partition(b"\0")[0])
        if reply.get("status") != "ok":
            raise IfcSessionError(reply.get("message") or "Bonsai reported an error")
        return reply.get("result")

    def __getattr__(self, name: str) -> Any:
        method = getattr(IfcSession, name, None)
        if not name.startswith("ifc_") or method is None:
            raise AttributeError(name)
        signature = inspect.signature(method)

        def forward(*args: Any, **kwargs: Any) -> Any:
            bound = signature.bind(None, *args, **kwargs)
            return self.call(name, {k: v for k, v in bound.arguments.items() if k != "self"})

        return forward
