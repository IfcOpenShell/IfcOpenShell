# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from . import ui, prop, operator

classes = (
    operator.AddPset,
    operator.AddQto,
    operator.CopyPropertyToSelection,
    operator.DisablePsetEditing,
    operator.EditPset,
    operator.EnablePsetEditing,
    operator.GuessQuantity,
    operator.GuessAllQuantities,
    operator.RemovePset,
    operator.TogglePsetExpansion,
    operator.BIM_OT_add_property_to_edit,
    operator.BIM_OT_remove_property_to_edit,
    operator.BIM_OT_clear_list,
    operator.BIM_OT_rename_parameters,
    operator.BIM_OT_add_edit_custom_property,
    operator.BIM_OT_bulk_remove_psets,
    prop.IfcPropertyEnumeratedValue,
    prop.IfcProperty,
    prop.PsetProperties,
    prop.MaterialPsetProperties,
    prop.TaskPsetProperties,
    prop.ResourcePsetProperties,
    prop.ProfilePsetProperties,
    prop.WorkSchedulePsetProperties,
    prop.RenameProperties,
    prop.AddEditProperties,
    prop.DeletePsets,
    ui.BIM_PT_object_psets,
    ui.BIM_PT_object_qtos,
    ui.BIM_PT_material_psets,
    ui.BIM_PT_task_qtos,
    ui.BIM_PT_resource_qtos,
    ui.BIM_PT_resource_psets,
    ui.BIM_PT_profile_psets,
    ui.BIM_PT_work_schedule_psets,
    ui.BIM_PT_bulk_property_editor,
    ui.BIM_PT_rename_parameters,
    ui.BIM_PT_add_edit_custom_properties,
    ui.BIM_PT_delete_psets,
)


def register():
    bpy.types.Object.PsetProperties = bpy.props.PointerProperty(type=prop.PsetProperties)
    bpy.types.Material.PsetProperties = bpy.props.PointerProperty(type=prop.MaterialPsetProperties)
    bpy.types.Scene.TaskPsetProperties = bpy.props.PointerProperty(type=prop.TaskPsetProperties)
    bpy.types.Scene.ResourcePsetProperties = bpy.props.PointerProperty(type=prop.ResourcePsetProperties)
    bpy.types.Scene.ProfilePsetProperties = bpy.props.PointerProperty(type=prop.ProfilePsetProperties)
    bpy.types.Scene.WorkSchedulePsetProperties = bpy.props.PointerProperty(type=prop.WorkSchedulePsetProperties)
    bpy.types.Scene.RenameProperties = bpy.props.CollectionProperty(type=prop.RenameProperties)
    bpy.types.Scene.AddEditProperties = bpy.props.CollectionProperty(type=prop.AddEditProperties)
    bpy.types.Scene.DeletePsets = bpy.props.CollectionProperty(type=prop.DeletePsets)


def unregister():
    del bpy.types.Object.PsetProperties
    del bpy.types.Material.PsetProperties
    del bpy.types.Scene.TaskPsetProperties
    del bpy.types.Scene.ResourcePsetProperties
    del bpy.types.Scene.ProfilePsetProperties
    del bpy.types.Scene.WorkSchedulePsetProperties
    del bpy.types.Scene.RenameProperties
    del bpy.types.Scene.AddEditProperties
    del bpy.types.Scene.DeletePsets
