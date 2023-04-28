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

        def callback(name, prop, data):
            if name in ("RefLatitude", "RefLongitude"):
                new = props.attributes.add()
                new.name = name
                new.is_null = data[name] is None
                new.is_optional = True
                new.data_type = "string"
                new.ifc_class = data["type"]
                new.string_value = "" if new.is_null else json.dumps(data[name])

        blenderbim.bim.helper.import_attributes2(
            tool.Ifc.get().by_id(oprops.ifc_definition_id), props.attributes, callback=callback
        )
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


class EditAttributes(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_attributes"
    bl_label = "Edit Attributes"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    obj_type: bpy.props.StringProperty()

    def _execute(self, context):
        self.file = IfcStore.get_file()
        if self.obj_type == "Object":
            obj = bpy.data.objects.get(self.obj)
        elif self.obj_type == "Material":
            obj = bpy.data.materials.get(self.obj)
        props = obj.BIMAttributeProperties
        product = tool.Ifc.get_entity(obj)

        def callback(attributes, prop):
            if prop.name in ("RefLatitude", "RefLongitude"):
                if prop.is_null:
                    attributes[prop.name] = None
                else:
                    try:
                        attributes[prop.name] = json.loads(prop.string_value)
                    except:
                        attributes[prop.name] = None
                return True

        attributes = blenderbim.bim.helper.export_attributes(props.attributes, callback=callback)
        ifcopenshell.api.run("attribute.edit_attributes", self.file, product=product, attributes=attributes)
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
    name: bpy.props.StringProperty()

    def _execute(self, context):
        value = context.active_object.BIMAttributeProperties.attributes.get(self.name).get_value()
        for obj in tool.Blender.get_selected_objects():
            core.copy_attribute_to_selection(tool.Ifc, name=self.name, value=value, obj=obj)
