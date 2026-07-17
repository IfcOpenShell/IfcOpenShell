# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Union

import bpy

import bonsai.tool as tool

_timer_callback: Union[Callable[[], Union[float, None]], None] = None
# Last known on-disk state of the active IFC file: (path, st_mtime_ns, st_size).
_snapshot: Union[tuple[str, int, int], None] = None
# A change seen on the previous poll that we are waiting to stabilise,
# so we never reload a file an external tool is still writing.
_pending_change: Union[tuple[str, int, int], None] = None
_is_prompt_active = False


class FileWatcher:
    """Watch the loaded IFC file for external modifications.

    When enabled, a ``bpy.app.timers`` poll compares the file's mtime and
    size on disk against a snapshot taken at load/save time. On a change it
    either asks the user to reload (default) or reloads silently ("viewer
    mode"), always via the view-preserving ``tool.Project.reload_ifc_file``.
    """

    @classmethod
    def is_enabled(cls) -> bool:
        return bool(tool.Blender.get_addon_preferences().watch_ifc_enabled)

    @classmethod
    def get_mode(cls) -> str:
        return tool.Blender.get_addon_preferences().watch_ifc_mode

    @classmethod
    def get_interval_seconds(cls) -> float:
        seconds = tool.Blender.get_addon_preferences().watch_ifc_interval_seconds
        return max(1.0, float(seconds))

    @classmethod
    def get_active_ifc_path(cls) -> Union[Path, None]:
        props = tool.Blender.get_bim_props()
        if not props.ifc_file:
            return None
        return tool.Blender.ensure_blender_path_is_abs(Path(props.ifc_file))

    @classmethod
    def is_eligible(cls) -> bool:
        return cls.is_enabled() and tool.Ifc.get() is not None and cls.get_active_ifc_path() is not None

    @classmethod
    def stat_file(cls, path: Path) -> Union[tuple[int, int], None]:
        try:
            stat = path.stat()
        except OSError:
            # The file may be missing mid-replace by an external tool.
            # Report nothing and check again on the next poll.
            return None
        return stat.st_mtime_ns, stat.st_size

    @classmethod
    def take_snapshot(cls) -> None:
        """Record the current on-disk state as the baseline for change detection."""
        global _snapshot, _pending_change
        _pending_change = None
        path = cls.get_active_ifc_path()
        stat = cls.stat_file(path) if path is not None else None
        _snapshot = None if path is None or stat is None else (path.as_posix(), *stat)

    @classmethod
    def set_prompt_active(cls, active: bool) -> None:
        global _is_prompt_active
        _is_prompt_active = active

    @classmethod
    def cancel_timer(cls) -> None:
        global _timer_callback
        if _timer_callback is not None and bpy.app.timers.is_registered(_timer_callback):
            bpy.app.timers.unregister(_timer_callback)
        _timer_callback = None

    @classmethod
    def reset_timer(cls) -> None:
        cls.cancel_timer()
        cls.take_snapshot()
        if not cls.is_eligible():
            return

        def on_timer() -> Union[float, None]:
            cls._on_timer_expired()
            # Reschedule by returning the next interval rather than calling
            # reset_timer(), which would unregister this timer from within
            # its own callback and corrupt Blender's timer registry (see the
            # matching comment in tool.Autosave.reset_timer).
            return cls.get_interval_seconds() if cls.is_eligible() else None

        global _timer_callback
        _timer_callback = on_timer
        bpy.app.timers.register(on_timer, first_interval=cls.get_interval_seconds())

    @classmethod
    def _on_timer_expired(cls) -> None:
        global _snapshot, _pending_change
        if _is_prompt_active or not cls.is_eligible():
            return
        path = cls.get_active_ifc_path()
        assert path is not None
        if _snapshot is None or _snapshot[0] != path.as_posix():
            # First poll for this file (or the active path changed).
            cls.take_snapshot()
            return
        stat = cls.stat_file(path)
        if stat is None:
            return
        current = (path.as_posix(), *stat)
        if current == _snapshot:
            _pending_change = None
            return
        if _pending_change != current:
            # A change was detected, but wait until two consecutive polls
            # agree so we never reload a half-written file.
            _pending_change = current
            return
        _snapshot = current
        _pending_change = None
        cls._handle_external_change()

    @classmethod
    def _handle_external_change(cls) -> None:
        props = tool.Blender.get_bim_props()
        if cls.get_mode() == "AUTO" and not props.is_dirty:
            try:
                bpy.ops.bim.reload_project("EXEC_DEFAULT")
            except Exception as error:
                print(f"Bonsai: automatic reload after external file change failed: {error}")
            return
        # PROMPT mode, or AUTO with unsaved changes: never discard the user's
        # work silently, always ask first.
        cls.set_prompt_active(True)
        try:
            bpy.ops.bim.file_changed_reload_prompt("INVOKE_DEFAULT")
        except Exception as error:
            # Not re-raised: an exception would also unregister the timer.
            cls.set_prompt_active(False)
            print(f"Bonsai: failed to show external file change prompt: {error}")
