from __future__ import annotations

import sys

from bonsaiviewer_autodesk.connector import AutodeskConnector
from bonsaiviewer_autodesk.rpc import JsonRpcHost
from bonsaiviewer_autodesk.ui import ensure_tk_app


def main() -> int:
    ensure_tk_app()
    connector = AutodeskConnector()
    host = JsonRpcHost(connector.handlers(), stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    return host.run()


if __name__ == "__main__":
    raise SystemExit(main())
