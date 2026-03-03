# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>, 2026 Michael Yoder <myoder@desertspringscivil.com>
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
    prop.CivilAlignmentProperties,
    # UILists
    ui.CIVIL_UL_alignment_pis,
    operator.ImportAlignmentCSV,
    # Operators - PI Management
    operator.CIVIL_OT_add_pi,
    operator.CIVIL_OT_remove_pi,
    operator.CIVIL_OT_pick_pi_from_viewport,
    operator.CIVIL_OT_recalculate_pis,
    operator.CIVIL_OT_clear_pis,
    # Operators - Creation
    operator.CIVIL_OT_create_alignment_by_pi,
    operator.CIVIL_OT_import_alignment_csv,
    # Operators - Stationing
    operator.CIVIL_OT_add_stationing_referent,
    operator.CIVIL_OT_name_segments,
    # Operators - PI Edit Mode
    operator.CIVIL_OT_enter_pi_edit_mode,
    # UI Panels (appear in Properties sidebar under CIVIL tab)
    ui.CIVIL_PT_alignment_creation,
    ui.CIVIL_PT_pi_editor,
    ui.CIVIL_PT_alignment_stationing,
)


def menu_func_import(self, context):
    self.layout.operator(operator.ImportAlignmentCSV.bl_idname, text="Alignment (.csv)")


def register():
    bpy.types.Scene.CivilAlignmentProperties = bpy.props.PointerProperty(type=prop.CivilAlignmentProperties)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    del bpy.types.Scene.CivilAlignmentProperties
