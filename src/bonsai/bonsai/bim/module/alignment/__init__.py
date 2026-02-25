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
from . import ui, prop, operator, decorator


classes = (
    # Property groups (must be registered before classes that use them)
    prop.AlignmentPI,
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
    operator.SAIKEI_OT_create_alignment_by_pi,
    operator.SAIKEI_OT_import_alignment_csv,
    # Operators - Stationing
    operator.SAIKEI_OT_add_stationing_referent,
    operator.SAIKEI_OT_name_segments,
    # Operators - PI Edit Mode
    operator.SAIKEI_OT_enter_pi_edit_mode,
    # UI Panels (appear in Properties sidebar under CIVIL tab)
    ui.SAIKEI_PT_alignment_status,
    ui.SAIKEI_PT_alignment_creation,
    ui.SAIKEI_PT_pi_editor,
    ui.SAIKEI_PT_alignment_stationing,
)


def menu_func_import(self, context):
    self.layout.operator(operator.ImportAlignmentCSV.bl_idname, text="Alignment (.csv)")


def register():
    bpy.types.Scene.SaikeiAlignmentProperties = bpy.props.PointerProperty(type=prop.SaikeiAlignmentProperties)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    del bpy.types.Scene.SaikeiAlignmentProperties
