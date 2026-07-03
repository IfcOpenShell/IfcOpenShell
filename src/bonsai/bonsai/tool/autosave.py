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

import logging
import os
from pathlib import Path
from typing import Callable, Union

import bpy

import bonsai.tool as tool
from bonsai.bim import export_ifc
from bonsai.bim.module.model import preview_base


AUTOSAVING_SUFFIX = "_autosaving.ifc"
AUTOSAVED_SUFFIX = "_autosaved.ifc"

_timer_callback: Union[Callable[[], None], None] = None


class Autosave:
    @classmethod
    def get_paths(cls, ifc_path: Union[str, Path]) -> tuple[Path, Path, Path]:
        path = Path(ifc_path)
        stem = path.stem if path.suffix.lower() == ".ifc" else path.name
        parent = path.parent
        main_path = path if path.suffix.lower() == ".ifc" else parent / f"{stem}.ifc"
        autosaving_path = parent / f"{stem}{AUTOSAVING_SUFFIX}"
        autosaved_path = parent / f"{stem}{AUTOSAVED_SUFFIX}"
        return main_path, autosaving_path, autosaved_path

    @classmethod
    def get_active_ifc_path(cls) -> Union[Path, None]:
        props = tool.Blender.get_bim_props()
        if not props.ifc_file:
            return None
        path = tool.Blender.ensure_blender_path_is_abs(Path(props.ifc_file))
        if path.suffix.lower() != ".ifc":
            return None
        return path

    @classmethod
    def is_enabled(cls) -> bool:
        return bool(tool.Blender.get_addon_preferences().autosave_enabled)

    @classmethod
    def get_interval_seconds(cls) -> float:
        minutes = tool.Blender.get_addon_preferences().autosave_interval_minutes
        return max(1.0, float(minutes) * 60.0)

    @classmethod
    def is_eligible(cls) -> bool:
        return cls.is_enabled() and tool.Ifc.get() is not None and cls.get_active_ifc_path() is not None

    @classmethod
    def cancel_timer(cls) -> None:
        global _timer_callback
        if _timer_callback is not None and bpy.app.timers.is_registered(_timer_callback):
            bpy.app.timers.unregister(_timer_callback)
        _timer_callback = None

    @classmethod
    def reset_timer(cls) -> None:
        cls.cancel_timer()
        if not cls.is_eligible():
            return

        def on_timer() -> None:
            cls._on_timer_expired()
            return None

        global _timer_callback
        _timer_callback = on_timer
        bpy.app.timers.register(on_timer, first_interval=cls.get_interval_seconds())

    @classmethod
    def _on_timer_expired(cls) -> None:
        if not cls.is_eligible():
            return

        prefs = tool.Blender.get_addon_preferences()
        bim_props = tool.Blender.get_bim_props()

        if bim_props.is_dirty:
            if prefs.autosave_mode == "PROMPT":
                bpy.ops.bim.autosave_prompt("INVOKE_DEFAULT")
            elif prefs.autosave_mode == "BACKUP":
                try:
                    cls.perform_backup(bpy.context)
                except Exception as error:
                    print(f"Bonsai: autosave backup failed: {error}")
        cls.reset_timer()

    @classmethod
    def perform_backup(cls, context: bpy.types.Context) -> None:
        ifc_path = cls.get_active_ifc_path()
        if ifc_path is None:
            return

        _, autosaving_path, autosaved_path = cls.get_paths(ifc_path)
        autosaving_path.parent.mkdir(parents=True, exist_ok=True)

        tool.Parametric.commit_pending_edits()
        preview_base.discard_pending_previews(context.scene)

        logger = logging.getLogger("ExportIFC")
        output_file = autosaving_path.as_posix().replace("\\", "/")
        settings = export_ifc.IfcExportSettings.factory(context, output_file, logger)
        export_ifc.IfcExporter(settings).export()

        try:
            os.replace(autosaving_path, autosaved_path)
        except OSError:
            if autosaving_path.is_file():
                autosaving_path.unlink(missing_ok=True)
            raise

    @classmethod
    def get_newer_autosaved_path(cls, ifc_path: Union[str, Path]) -> Union[str, None]:
        path = Path(ifc_path)
        if path.suffix.lower() != ".ifc" or not path.is_file():
            return None

        _, _, autosaved_path = cls.get_paths(path)
        if not autosaved_path.is_file():
            return None
        if autosaved_path.stat().st_mtime > path.stat().st_mtime:
            return autosaved_path.as_posix().replace("\\", "/")
        return None
