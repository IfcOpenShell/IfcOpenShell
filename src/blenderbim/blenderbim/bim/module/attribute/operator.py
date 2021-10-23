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
import json
import ifcopenshell
import ifcopenshell.api
import blenderbim.bim.helper
import blenderbim.bim.handler
import blenderbim.tool as tool
import blenderbim.core.attribute as core
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.attribute.data import Data


class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class EnableEditingAttributes(bpy.types.Operator):
    bl_idname = "bim.enable_editing_attributes"
    bl_label = "Enable Editing Attributes"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        if self.obj_type == "Object":
            obj = bpy.data.objects.get(self.obj)
        elif self.obj_type == "Material":
            obj = bpy.data.materials.get(self.obj)
        oprops = obj.BIMObjectProperties
        props = obj.BIMAttributeProperties
        props.attributes.clear()
        if oprops.ifc_definition_id not in Data.products:
            Data.load(IfcStore.get_file(), oprops.ifc_definition_id)
        blenderbim.bim.helper.import_attributes2(tool.Ifc.get().by_id(oprops.ifc_definition_id), props.attributes)
        props.is_editing_attributes = True
        return {"FINISHED"}


class DisableEditingAttributes(bpy.types.Operator):
    bl_idname = "bim.disable_editing_attributes"
    bl_label = "Disable Editing Attributes"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        if self.obj_type == "Object":
            obj = bpy.data.objects.get(self.obj)
        elif self.obj_type == "Material":
            obj = bpy.data.materials.get(self.obj)
        props = obj.BIMAttributeProperties
        props.is_editing_attributes = False
        return {"FINISHED"}


class EditAttributes(bpy.types.Operator):
    bl_idname = "bim.edit_attributes"
    bl_label = "Edit Attributes"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        if self.obj_type == "Object":
            obj = bpy.data.objects.get(self.obj)
        elif self.obj_type == "Material":
            obj = bpy.data.materials.get(self.obj)
        oprops = obj.BIMObjectProperties
        props = obj.BIMAttributeProperties
        attributes = {}
        for attribute in Data.products[oprops.ifc_definition_id]:
            blender_attribute = props.attributes.get(attribute["name"])
            if not blender_attribute:
                continue
            if attribute["is_optional"] and blender_attribute.is_null:
                attributes[attribute["name"]] = None
            elif attribute["type"] == "string":
                attributes[attribute["name"]] = blender_attribute.string_value
            elif attribute["type"] == "list":
                values = blender_attribute.string_value[1:-1].split(", ")
                if attribute["list_type"] == "float":
                    values = [float(v) for v in values]
                elif attribute["list_type"] == "integer":
                    values = [int(v) for v in values]
                attributes[attribute["name"]] = values
            elif attribute["type"] == "integer":
                attributes[attribute["name"]] = blender_attribute.int_value
            elif attribute["type"] == "float":
                attributes[attribute["name"]] = blender_attribute.float_value
            elif attribute["type"] == "enum":
                attributes[attribute["name"]] = blender_attribute.enum_value
        product = self.file.by_id(oprops.ifc_definition_id)
        ifcopenshell.api.run("attribute.edit_attributes", self.file, **{"product": product, "attributes": attributes})
        Data.load(IfcStore.get_file(), oprops.ifc_definition_id)
        bpy.ops.bim.disable_editing_attributes(obj=obj.name, obj_type=self.obj_type)
        return {"FINISHED"}


class GenerateGlobalId(bpy.types.Operator):
    bl_idname = "bim.generate_global_id"
    bl_label = "Regenerate GlobalId"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        index = context.active_object.BIMAttributeProperties.attributes.find("GlobalId")
        if index >= 0:
            global_id = context.active_object.BIMAttributeProperties.attributes[index]
        else:
            global_id = context.active_object.BIMAttributeProperties.attributes.add()
        global_id.name = "GlobalId"
        global_id.data_type = "string"
        global_id.string_value = ifcopenshell.guid.new()
        return {"FINISHED"}


class CopyAttributeToSelection(bpy.types.Operator, Operator):
    bl_idname = "bim.copy_attribute_to_selection"
    bl_label = "Copy Attribute To Selection"
    attribute_name: bpy.props.StringProperty()

    def _execute(self, context):
        value = context.active_object.BIMAttributeProperties.attributes.get(self.attribute_name).get_value()
        for obj in context.selected_objects:
            core.copy_attribute_to_selection(tool.Ifc, name=self.attribute_name, value=value, obj=obj)
