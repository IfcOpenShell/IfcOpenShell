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
from . import ui, prop, operator

classes = (
    operator.AddProposedProp,
    operator.AddPset,
    operator.AddQto,
    operator.CopyPropertyToSelection,
    operator.DisablePsetEditing,
    operator.EditPset,
    operator.EnablePsetEditing,
    operator.RemovePset,
    operator.SavePsetAsTemplate,
    operator.TogglePsetExpansion,
    operator.UnsharePset,
    operator.BIM_OT_add_property_to_edit,
    operator.BIM_OT_remove_property_to_edit,
    operator.BIM_OT_clear_list,
    operator.BIM_OT_rename_parameters,
    operator.BIM_OT_add_edit_custom_property,
    operator.BIM_OT_bulk_remove_psets,
    prop.IfcPropertyEnumeratedValue,
    prop.IfcProperty,
    prop.PsetProperties,
    prop.RenameProperties,
    prop.AddEditProperties,
    prop.DeletePsets,
    prop.GlobalPsetProperties,
    ui.BIM_PT_object_psets,
    ui.BIM_PT_object_qtos,
    ui.BIM_PT_material_psets,
    ui.BIM_PT_material_set_psets,
    ui.BIM_PT_material_set_item_psets,
    ui.BIM_PT_task_qtos,
    ui.BIM_PT_resource_qtos,
    ui.BIM_PT_resource_psets,
    ui.BIM_PT_group_psets,
    ui.BIM_PT_group_qtos,
    ui.BIM_PT_profile_psets,
    ui.BIM_PT_work_schedule_psets,
    ui.BIM_PT_bulk_property_editor,
    ui.BIM_PT_rename_parameters,
    ui.BIM_PT_add_edit_custom_properties,
    ui.BIM_PT_delete_psets,
)


def register():
    bpy.types.Object.PsetProperties = bpy.props.PointerProperty(type=prop.PsetProperties)
    bpy.types.Scene.MaterialPsetProperties = bpy.props.PointerProperty(type=prop.PsetProperties)
    bpy.types.Object.MaterialSetPsetProperties = bpy.props.PointerProperty(type=prop.PsetProperties)
    bpy.types.Object.MaterialSetItemPsetProperties = bpy.props.PointerProperty(type=prop.PsetProperties)
    bpy.types.Scene.TaskPsetProperties = bpy.props.PointerProperty(type=prop.PsetProperties)
    bpy.types.Scene.ResourcePsetProperties = bpy.props.PointerProperty(type=prop.PsetProperties)
    bpy.types.Scene.GroupPsetProperties = bpy.props.PointerProperty(type=prop.PsetProperties)
    bpy.types.Scene.ProfilePsetProperties = bpy.props.PointerProperty(type=prop.PsetProperties)
    bpy.types.Scene.WorkSchedulePsetProperties = bpy.props.PointerProperty(type=prop.PsetProperties)
    bpy.types.Scene.RenameProperties = bpy.props.CollectionProperty(type=prop.RenameProperties)
    bpy.types.Scene.AddEditProperties = bpy.props.CollectionProperty(type=prop.AddEditProperties)
    bpy.types.Scene.DeletePsets = bpy.props.CollectionProperty(type=prop.DeletePsets)
    bpy.types.Scene.GlobalPsetProperties = bpy.props.PointerProperty(type=prop.GlobalPsetProperties)


def unregister():
    del bpy.types.Object.PsetProperties
    del bpy.types.Scene.MaterialPsetProperties
    del bpy.types.Object.MaterialSetPsetProperties
    del bpy.types.Object.MaterialSetItemPsetProperties
    del bpy.types.Scene.TaskPsetProperties
    del bpy.types.Scene.ResourcePsetProperties
    del bpy.types.Scene.GroupPsetProperties
    del bpy.types.Scene.ProfilePsetProperties
    del bpy.types.Scene.WorkSchedulePsetProperties
    del bpy.types.Scene.RenameProperties
    del bpy.types.Scene.AddEditProperties
    del bpy.types.Scene.DeletePsets
    del bpy.types.Scene.GlobalPsetProperties
