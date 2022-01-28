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

import blenderbim.bim.helper
from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.attribute.data import AttributesData, MaterialAttributesData


def draw_ui(context, layout, obj_type, attributes):
    obj = context.active_object if obj_type == "Object" else context.active_object.active_material
    oprops = obj.BIMObjectProperties
    props = obj.BIMAttributeProperties

    if props.is_editing_attributes:
        row = layout.row(align=True)
        op = row.operator("bim.edit_attributes", icon="CHECKMARK", text="Save Attributes")
        op.obj_type = obj_type
        op.obj = obj.name
        op = row.operator("bim.disable_editing_attributes", icon="CANCEL", text="")
        op.obj_type = obj_type
        op.obj = obj.name

        blenderbim.bim.helper.draw_attributes(props.attributes, layout, copy_operator="bim.copy_attribute_to_selection")
    else:
        row = layout.row()
        op = row.operator("bim.enable_editing_attributes", icon="GREASEPENCIL", text="Edit")
        op.obj_type = obj_type
        op.obj = obj.name

        for attribute in attributes:
            row = layout.row(align=True)
            row.label(text=attribute["name"])
            row.label(text=attribute["value"])

    # TODO: reimplement, see #1222
    # if "IfcSite/" in context.active_object.name or "IfcBuilding/" in context.active_object.name:
    #    self.draw_addresses_ui()


class BIM_PT_object_attributes(Panel):
    bl_label = "IFC Attributes"
    bl_idname = "BIM_PT_object_attributes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_object_metadata"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        if not IfcStore.get_element(context.active_object.BIMObjectProperties.ifc_definition_id):
            return False
        return bool(context.active_object.BIMObjectProperties.ifc_definition_id)

    def draw(self, context):
        if not AttributesData.is_loaded:
            AttributesData.load()
        draw_ui(context, self.layout, "Object", AttributesData.data["attributes"])


class BIM_PT_material_attributes(Panel):
    bl_label = "IFC Material Attributes"
    bl_idname = "BIM_PT_material_attributes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        if not IfcStore.get_file():
            return False
        try:
            return bool(context.active_object.active_material.BIMObjectProperties.ifc_definition_id)
        except:
            return False

    def draw(self, context):
        if not MaterialAttributesData.is_loaded:
            MaterialAttributesData.load()
        draw_ui(context, self.layout, "Material", MaterialAttributesData.data["attributes"])
