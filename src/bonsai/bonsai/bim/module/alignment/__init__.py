# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
from bpy.app.handlers import persistent
from . import ui, prop, operator


@persistent
def on_undo_redo(scene):
    """Handler called after undo/redo to sync PI Editor with IFC.

    When Blender undoes, both Blender properties and IFC state may change.
    This handler syncs the PI Editor to reflect the current IFC state:
    - If the active alignment still exists, extracts PI data from IFC segments
    - If the alignment was deleted/invalidated, clears the PI Editor
    - Rebuilds display_rows to match the synced state
    """
    if not hasattr(scene, "SaikeiAlignmentProperties"):
        return
    props = scene.SaikeiAlignmentProperties
    # Sync PI Editor from IFC to ensure consistency after undo/redo
    operator.sync_pis_from_ifc(props)


classes = (
    # Property groups (must be registered before classes that use them)
    prop.AlignmentPI,
    prop.AlignmentSegmentItem,
    prop.AlignmentDisplayRow,
    prop.SaikeiAlignmentProperties,
    # UILists
    ui.SAIKEI_UL_alignment_pis,
    operator.ImportAlignmentCSV,
    # Operators - PI Management
    operator.SAIKEI_OT_add_pi,
    operator.SAIKEI_OT_remove_pi,
    operator.SAIKEI_OT_pick_pi_from_viewport,
    operator.SAIKEI_OT_recalculate_pis,
    operator.SAIKEI_OT_clear_pis,
    # Operators - Creation
    operator.SAIKEI_OT_create_alignment,
    operator.SAIKEI_OT_create_alignment_by_pi,
    operator.SAIKEI_OT_import_alignment_csv,
    # Operators - Stationing
    operator.SAIKEI_OT_add_stationing_referent,
    operator.SAIKEI_OT_name_segments,
    # UI Panels
    ui.SAIKEI_PT_horizontal_alignment,
    ui.SAIKEI_PT_alignment_creation,
    ui.SAIKEI_PT_pi_editor,
    ui.SAIKEI_PT_alignment_stationing,
)


def menu_func_import(self, context):
    self.layout.operator(operator.ImportAlignmentCSV.bl_idname, text="Alignment (.csv)")


def register():
    bpy.types.Scene.SaikeiAlignmentProperties = bpy.props.PointerProperty(type=prop.SaikeiAlignmentProperties)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.app.handlers.undo_post.append(on_undo_redo)
    bpy.app.handlers.redo_post.append(on_undo_redo)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    # Unregister handlers
    if on_undo_redo in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.remove(on_undo_redo)
    if on_undo_redo in bpy.app.handlers.redo_post:
        bpy.app.handlers.redo_post.remove(on_undo_redo)
    del bpy.types.Scene.SaikeiAlignmentProperties
