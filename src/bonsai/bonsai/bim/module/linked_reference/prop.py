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

from typing import TYPE_CHECKING

import bpy
from bpy.props import BoolProperty, CollectionProperty, IntProperty, PointerProperty, StringProperty
from bpy.types import PropertyGroup

import bonsai.tool as tool


def update_auto_refresh(self: "BIMLinkedReferenceProperties", context: bpy.types.Context) -> None:
    tool.LinkedReference.reset_timer()


class LinkedReferenceLink(PropertyGroup):
    name: StringProperty(name="Name")
    filepath: StringProperty(
        name="Filepath",
        description="Path to the linked .svg or .dxf file, possibly relative to the active IFC file",
    )
    transformation: StringProperty(
        name="Transformation",
        description="4x4 placement matrix as a flattened comma separated list",
        default="",
    )
    ifc_definition_id: IntProperty(
        name="IFC Definition ID",
        description="STEP ID of the IfcDocumentReference persisting this link. Zero when no IFC project exists",
        default=0,
    )
    anchor: PointerProperty(
        name="Anchor Object",
        description="Empty holding the user placement. Imported geometry is parented to it",
        type=bpy.types.Object,
    )
    is_loaded: BoolProperty(name="Is Loaded", default=False)
    file_mtime: StringProperty(
        name="File Modification Time",
        description="Modification time of the source file at last import, used to detect updates",
        default="",
    )

    if TYPE_CHECKING:
        name: str
        filepath: str
        transformation: str
        ifc_definition_id: int
        anchor: bpy.types.Object | None
        is_loaded: bool
        file_mtime: str


class BIMLinkedReferenceProperties(PropertyGroup):
    references: CollectionProperty(name="Linked References", type=LinkedReferenceLink)
    active_reference_index: IntProperty(name="Active Reference Index")
    auto_refresh: BoolProperty(
        name="Auto Refresh",
        description="Periodically check linked reference files on disk and re-import them when they change",
        default=False,
        update=update_auto_refresh,
    )
    auto_refresh_interval: IntProperty(
        name="Interval (s)",
        description="How often to check linked reference files for changes, in seconds",
        default=5,
        min=1,
        soft_max=3600,
    )

    if TYPE_CHECKING:
        references: bpy.types.bpy_prop_collection_idprop[LinkedReferenceLink]
        active_reference_index: int
        auto_refresh: bool
        auto_refresh_interval: int
