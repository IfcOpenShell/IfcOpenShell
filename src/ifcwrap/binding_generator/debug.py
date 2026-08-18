from __future__ import annotations

import os
import sys
import time
from pathlib import Path

_DEBUG_ENABLED = os.environ.get("IFCWRAP_BINDGEN_DEBUG", "").lower() not in {
    "",
    "0",
    "false",
    "no",
}
_START_TIME = time.monotonic()


def debug_enabled() -> bool:
    return _DEBUG_ENABLED


def debug_log(stage: str, message: str) -> None:
    if not _DEBUG_ENABLED:
        return
    elapsed = time.monotonic() - _START_TIME
    sys.stderr.write(f"[bindgen {elapsed:8.2f}s] {stage}: {message}\n")
    sys.stderr.flush()


def debug_path(path: Path | None) -> str:
    if path is None:
        return "<none>"
    try:
        return str(path.resolve())
    except OSError:
        return str(path)
