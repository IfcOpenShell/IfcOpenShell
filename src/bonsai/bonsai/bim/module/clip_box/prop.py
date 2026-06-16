# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

from typing import TYPE_CHECKING

import bpy
from bpy.types import PropertyGroup

import bonsai.tool as tool
from bonsai.bim.prop import ObjProperty


class BIMClipBoxProperties(PropertyGroup):
    """Per-object marker for a clip-box host empty.

    The host empty's ``matrix_world`` is the single source of truth for
    the clip box's pose and dimensions: translation = box centre,
    rotation = box orientation, per-axis scale = world half-extents. The
    visible cube comes from the empty's CUBE display.

    Only ``is_clip_box`` lives here; visibility (``enabled``) and overlay
    (``show_caps``) are global per-file and live on the Scene PG.
    """

    is_clip_box: bpy.props.BoolProperty(
        default=False,
        description="True when this empty was created as a clip-box host. Internal flag; not user-edited.",
    )

    if TYPE_CHECKING:
        is_clip_box: bool


def update_active_clip_box_index(self, context):
    tool.ClipBox.schedule_refresh()
    tool.ClipBox.select_active_clip_box(context)


def update_show_caps(self, context):
    tool.ClipBox.schedule_refresh()


def update_enabled(self, context):
    tool.ClipBox.schedule_refresh()


class BIMSceneClipBoxProperties(PropertyGroup):
    """Scene-level registry of clip boxes in this file.

    Multiple boxes may exist; ``active_clip_box_index`` selects which one
    drives the viewport clip at any time. ``enabled`` and ``show_caps``
    are global because the user's intent ("hide everything outside the
    box", "draw cap overlays") applies file-wide, not per box.

    ``enabled`` is intentionally not persisted to the project pset:
    opening a fresh IFC should never silently hide geometry behind a
    remembered toggle. Selecting any clip-box empty in the viewport
    re-arms it (see :meth:`tool.ClipBox._sync_active_to_selection`).
    """

    clip_boxes: bpy.props.CollectionProperty(type=ObjProperty)
    active_clip_box_index: bpy.props.IntProperty(
        default=0,
        min=0,
        update=update_active_clip_box_index,
        description="Index of the clip box currently driving the viewport clip planes",
    )
    enabled: bpy.props.BoolProperty(
        name="Enabled",
        default=False,
        update=update_enabled,
        description="When enabled, the active clip box hides all viewport geometry outside its 6 faces",
    )
    show_caps: bpy.props.BoolProperty(
        name="Show Caps",
        default=True,
        update=update_show_caps,
        description=(
            "Draw filled cross-section caps where IFC product geometry "
            "crosses the active clip planes. Disable for performance on "
            "very heavy scenes"
        ),
    )

    if TYPE_CHECKING:
        active_clip_box_index: int
        enabled: bool
        show_caps: bool
