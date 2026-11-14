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

# The viewport screenshot is adapted from the Blender MCP add-on
# (https://projects.blender.org/lab/blender_mcp,
# get_screenshot_of_area_as_image_toolcode.py), Copyright 2026 Blender Authors,
# GPL-3.0-or-later.

"""Tools that show the agent what the user sees in Bonsai, and point the user at elements.

These change the selection and the 3D viewport, never the model.
"""

from __future__ import annotations

import base64
import math
import os
import tempfile
from typing import Any, NamedTuple

import bpy
import ifcopenshell
from mathutils import Euler

import bonsai.tool as tool

# Longest edge of a screenshot, in pixels. Larger images are scaled down by
# the client anyway, and cost the agent more to read.
_SCREENSHOT_MAX_EDGE = 1568
# Elements listed by bonsai_selection; the count is always given.
_SELECTION_LIMIT = 200

_AXES = {"top": "TOP", "bottom": "BOTTOM", "front": "FRONT", "back": "BACK", "left": "LEFT", "right": "RIGHT"}
# Looking down at 35.26 degrees from the front right, like Blender's default view.
_ISO = Euler((math.radians(54.7356), 0.0, math.radians(45.0))).to_quaternion()


class ViewError(Exception):
    pass


class _View3D(NamedTuple):
    window: bpy.types.Window
    area: bpy.types.Area
    region: bpy.types.Region


def _view3d() -> _View3D:
    """The largest 3D viewport in any window."""
    if bpy.app.background:
        raise ViewError("Blender is running without a window, so there is no viewport")
    best = None
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type != "VIEW_3D":
                continue
            region = next((r for r in area.regions if r.type == "WINDOW"), None)
            if region and (best is None or area.width * area.height > best.area.width * best.area.height):
                best = _View3D(window, area, region)
    if best is None:
        raise ViewError("No 3D viewport is open in Bonsai")
    return best


def _describe(element: ifcopenshell.entity_instance) -> dict[str, Any]:
    return {"id": element.id(), "type": element.is_a(), "name": getattr(element, "Name", None)}


def _selected_objects() -> list[bpy.types.Object]:
    # Timers have no window, so context.selected_objects is empty there.
    return [obj for obj in bpy.context.view_layer.objects if obj.select_get()]


def selection() -> dict[str, Any]:
    active = tool.Blender.get_active_object(is_selected=True)
    active_element = tool.Ifc.get_entity(active) if active else None
    elements = sorted((e for obj in _selected_objects() if (e := tool.Ifc.get_entity(obj))), key=lambda e: e.id())
    return {
        "count": len(elements),
        "active": _describe(active_element) if active_element else None,
        "selected": [_describe(e) for e in elements[:_SELECTION_LIMIT]],
    }


def select(elements: list[ifcopenshell.entity_instance], frame: bool = True) -> dict[str, Any]:
    if bpy.context.mode != "OBJECT":
        raise ViewError(f"Bonsai is in {bpy.context.mode.lower().replace('_', ' ')} mode: ask the user to leave it")
    view_layer = bpy.context.view_layer
    # Objects created since the last update are not in the view layer yet.
    view_layer.update()
    found, missing, hidden = [], [], []
    for element in elements:
        obj = tool.Ifc.get_object(element)
        if obj is None or view_layer.objects.get(obj.name) is None:
            missing.append(element.id())
        elif not obj.visible_get():
            hidden.append(element.id())
        else:
            found.append(obj)
    if not found:
        raise ViewError(
            "None of these elements can be selected: "
            + "; ".join(f"{label} {ids}" for label, ids in (("no object", missing), ("hidden", hidden)) if ids)
        )
    for obj in _selected_objects():
        obj.select_set(False)
    for obj in found:
        obj.select_set(True)
    view_layer.objects.active = found[0]
    result: dict[str, Any] = {"selected": [tool.Ifc.get_entity(obj).id() for obj in found]}
    if missing:
        result["no_object"] = missing
    if hidden:
        result["hidden"] = hidden
    if frame:
        result["framed"] = _frame("selected")
    return result


def _frame(what: str) -> bool:
    """Frame the selection or the whole scene. Return False when there is no viewport to frame."""
    try:
        view = _view3d()
    except ViewError:
        return False
    with bpy.context.temp_override(window=view.window, area=view.area, region=view.region):
        if what == "selected":
            bpy.ops.view3d.view_selected()
        else:
            bpy.ops.view3d.view_all()
    return True


def set_view(direction: str = "", frame: str = "selected") -> dict[str, Any]:
    direction = direction.lower()
    if direction and direction != "iso" and direction not in _AXES:
        raise ViewError(f"Unknown direction {direction!r}: use iso, {', '.join(_AXES)} or leave it empty")
    if frame not in ("selected", "all", ""):
        raise ViewError(f"Unknown frame {frame!r}: use selected, all or leave it empty")
    view = _view3d()
    region_3d = view.area.spaces.active.region_3d
    with bpy.context.temp_override(window=view.window, area=view.area, region=view.region):
        if region_3d.view_perspective == "CAMERA":
            region_3d.view_perspective = "PERSP"
        if direction == "iso":
            region_3d.view_rotation = _ISO
            region_3d.view_perspective = "PERSP"
        elif direction:
            bpy.ops.view3d.view_axis(type=_AXES[direction])
        if frame == "selected" and _selected_objects():
            bpy.ops.view3d.view_selected()
        elif frame:
            bpy.ops.view3d.view_all()
    return {"direction": direction or None, "perspective": region_3d.view_perspective.lower()}


def screenshot() -> dict[str, Any]:
    """The largest 3D viewport as the user sees it, as a base64 PNG."""
    view = _view3d()
    with tempfile.TemporaryDirectory(prefix="bonsai_mcp_") as tmpdir:
        path = os.path.join(tmpdir, "viewport.png")
        with bpy.context.temp_override(window=view.window, area=view.area):
            bpy.ops.screen.screenshot_area(filepath=path)
        width, height = _limit_size(path)
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("ascii")
    return {"png_base64": data, "width": width, "height": height}


def _limit_size(path: str) -> tuple[int, int]:
    """Scale the image at ``path`` down in place so its longest edge fits. Return its size."""
    import imbuf

    image = imbuf.load(path)
    try:
        width, height = image.size
        scale = _SCREENSHOT_MAX_EDGE / max(width, height)
        if scale < 1.0:
            width, height = max(1, round(width * scale)), max(1, round(height * scale))
            image.resize((width, height), method="BILINEAR")
            imbuf.write(image, filepath=path)
        return width, height
    finally:
        image.free()
