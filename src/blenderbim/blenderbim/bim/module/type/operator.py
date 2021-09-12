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
import ifcopenshell.util.schema
import ifcopenshell.util.type
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.type.data import Data
from ifcopenshell.api.geometry.data import Data as GeometryData
from ifcopenshell.api.material.data import Data as MaterialData


class AssignType(bpy.types.Operator):
    bl_idname = "bim.assign_type"
    bl_label = "Assign Type"
    bl_options = {"REGISTER", "UNDO"}
    relating_type: bpy.props.IntProperty()
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        relating_type = self.relating_type or int(context.active_object.BIMTypeProperties.relating_type)
        related_objects = (
            [bpy.data.objects.get(self.related_object)]
            if self.related_object
            else context.selected_objects or [context.active_object]
        )
        for related_object in related_objects:
            oprops = related_object.BIMObjectProperties
            ifcopenshell.api.run(
                "type.assign_type",
                self.file,
                **{
                    "related_object": self.file.by_id(oprops.ifc_definition_id),
                    "relating_type": self.file.by_id(relating_type),
                },
            )
            Data.load(IfcStore.get_file(), oprops.ifc_definition_id)
            GeometryData.load(IfcStore.get_file(), oprops.ifc_definition_id)
            MaterialData.load(IfcStore.get_file(), oprops.ifc_definition_id)
            representation_ids = GeometryData.products[oprops.ifc_definition_id]
            if not representation_ids:
                pass  # TODO: clear geometry? Make void? Make none type?
            has_switched = False
            for representation_id in representation_ids:
                representation = GeometryData.representations[representation_id]
                if representation["ContextOfItems"]["ContextIdentifier"] == "Body":
                    bpy.ops.bim.switch_representation(
                        obj=related_object.name, ifc_definition_id=representation_id, should_switch_all_meshes=False
                    )
                    has_switched = True
            if not has_switched and representation_ids:
                bpy.ops.bim.switch_representation(
                    obj=related_object.name, ifc_definition_id=representation_id, should_switch_all_meshes=False
                )

        bpy.ops.bim.disable_editing_type(obj=related_object.name)
        MaterialData.load(self.file)
        return {"FINISHED"}


class UnassignType(bpy.types.Operator):
    bl_idname = "bim.unassign_type"
    bl_label = "Unassign Type"
    bl_options = {"REGISTER", "UNDO"}
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        related_objects = (
            [bpy.data.objects.get(self.related_object)] if self.related_object else context.selected_objects
        )
        for related_object in related_objects:
            oprops = related_object.BIMObjectProperties
            ifcopenshell.api.run(
                "type.unassign_type",
                self.file,
                **{
                    "related_object": self.file.by_id(oprops.ifc_definition_id),
                },
            )
            Data.load(IfcStore.get_file(), oprops.ifc_definition_id)
        return {"FINISHED"}


class EnableEditingType(bpy.types.Operator):
    bl_idname = "bim.enable_editing_type"
    bl_label = "Enable Editing Type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.active_object.BIMTypeProperties.is_editing_type = True
        return {"FINISHED"}


class DisableEditingType(bpy.types.Operator):
    bl_idname = "bim.disable_editing_type"
    bl_label = "Disable Editing Type"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        obj.BIMTypeProperties.is_editing_type = False
        return {"FINISHED"}


class SelectType(bpy.types.Operator):
    bl_idname = "bim.select_type"
    bl_label = "Select Type"
    bl_options = {"REGISTER", "UNDO"}
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_object = bpy.data.objects.get(self.related_object, context.active_object)
        oprops = related_object.BIMObjectProperties
        element_type = ifcopenshell.util.element.get_type(self.file.by_id(oprops.ifc_definition_id))
        if element_type is not None:
            obj = IfcStore.get_element(element_type.GlobalId)
            context.view_layer.objects.active = obj
            obj.select_set(True)
        return {"FINISHED"}


class SelectSimilarType(bpy.types.Operator):
    bl_idname = "bim.select_similar_type"
    bl_label = "Select Similar Type"
    bl_options = {"REGISTER", "UNDO"}
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_object = bpy.data.objects.get(self.related_object) if self.related_object else context.active_object
        oprops = related_object.BIMObjectProperties
        product = self.file.by_id(oprops.ifc_definition_id)
        declaration = IfcStore.get_schema().declaration_by_name(product.is_a())
        if ifcopenshell.util.schema.is_a(declaration, "IfcElementType"):
            related_objects = ifcopenshell.api.run(
                "type.get_related_objects", self.file, **{"relating_type": self.file.by_id(oprops.ifc_definition_id)}
            )
        else:
            related_objects = ifcopenshell.api.run(
                "type.get_related_objects", self.file, **{"related_object": self.file.by_id(oprops.ifc_definition_id)}
            )
        for obj in context.visible_objects:
            if obj.BIMObjectProperties.ifc_definition_id in related_objects:
                obj.select_set(True)
        return {"FINISHED"}


class SelectTypeObjects(bpy.types.Operator):
    bl_idname = "bim.select_type_objects"
    bl_label = "Select Type Objects"
    bl_options = {"REGISTER", "UNDO"}
    relating_type: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        relating_type = bpy.data.objects.get(self.relating_type) if self.relating_type else context.active_object
        oprops = relating_type.BIMObjectProperties
        related_objects = Data.types[oprops.ifc_definition_id]
        for obj in context.visible_objects:
            if obj.BIMObjectProperties.ifc_definition_id in related_objects:
                obj.select_set(True)
        return {"FINISHED"}
