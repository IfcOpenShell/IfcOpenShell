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

import bpy
from bpy.app.handlers import persistent

import bonsai.tool as tool

from . import operator, prop, ui

classes = (
    operator.LinkReference,
    operator.UnlinkReference,
    operator.LoadLinkedReference,
    operator.UnloadLinkedReference,
    operator.RefreshLinkedReference,
    operator.SelectLinkedReferenceHandle,
    operator.ToggleLinkedReferenceVisibility,
    prop.LinkedReferenceLink,
    prop.BIMLinkedReferenceProperties,
    ui.BIM_UL_linked_references,
    ui.BIM_PT_linked_references,
)


@persistent
def _on_load_post(filepath):
    tool.LinkedReference.reset_timer()


def register():
    bpy.types.Scene.BIMLinkedReferenceProperties = bpy.props.PointerProperty(type=prop.BIMLinkedReferenceProperties)
    if _on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load_post)


def unregister():
    tool.LinkedReference.cancel_timer()
    if _on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load_post)
    del bpy.types.Scene.BIMLinkedReferenceProperties
