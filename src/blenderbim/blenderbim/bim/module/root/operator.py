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
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.schema
import ifcopenshell.util.element
import blenderbim.bim.handler
import blenderbim.core.geometry
import blenderbim.core.material
import blenderbim.core.spatial
import blenderbim.core.style
import blenderbim.core.type
import blenderbim.core.root as core
import blenderbim.tool as tool
from ifcopenshell.api.void.data import Data as VoidData
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.helper import get_enum_items


class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class EnableReassignClass(bpy.types.Operator):
    bl_idname = "bim.enable_reassign_class"
    bl_label = "Enable Reassign IFC Class"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        self.file = IfcStore.get_file()
        ifc_class = obj.name.split("/")[0]
        context.active_object.BIMObjectProperties.is_reassigning_class = True
        ifc_products = [
            "IfcElement",
            "IfcElementType",
            "IfcSpatialElement",
            "IfcGroup",
            "IfcStructural",
            "IfcPositioningElement",
            "IfcContext",
            "IfcAnnotation",
            "IfcRelSpaceBoundary",
        ]
        for ifc_product in ifc_products:
            if ifcopenshell.util.schema.is_a(IfcStore.get_schema().declaration_by_name(ifc_class), ifc_product):
                context.scene.BIMRootProperties.ifc_product = ifc_product
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        context.scene.BIMRootProperties.ifc_class = element.is_a()
        if hasattr(element, "PredefinedType") and element.PredefinedType:
            context.scene.BIMRootProperties.ifc_predefined_type = element.PredefinedType
        return {"FINISHED"}


class DisableReassignClass(bpy.types.Operator):
    bl_idname = "bim.disable_reassign_class"
    bl_label = "Disable Reassign IFC Class"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.active_object.BIMObjectProperties.is_reassigning_class = False
        return {"FINISHED"}


class ReassignClass(bpy.types.Operator):
    bl_idname = "bim.reassign_class"
    bl_label = "Reassign IFC Class"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        objects = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        self.file = IfcStore.get_file()
        predefined_type = context.scene.BIMRootProperties.ifc_predefined_type
        if predefined_type == "USERDEFINED":
            predefined_type = context.scene.BIMRootProperties.ifc_userdefined_type
        for obj in objects:
            product = ifcopenshell.api.run(
                "root.reassign_class",
                self.file,
                **{
                    "product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
                    "ifc_class": context.scene.BIMRootProperties.ifc_class,
                    "predefined_type": predefined_type,
                },
            )
            obj.name = "{}/{}".format(product.is_a(), getattr(product, "Name", "None"))
            IfcStore.link_element(product, obj)
            obj.BIMObjectProperties.is_reassigning_class = False
        return {"FINISHED"}


class AssignClass(bpy.types.Operator, Operator):
    bl_idname = "bim.assign_class"
    bl_label = "Assign IFC Class"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Assign the IFC Class to the selected object"
    obj: bpy.props.StringProperty()
    ifc_class: bpy.props.StringProperty()
    predefined_type: bpy.props.StringProperty()
    userdefined_type: bpy.props.StringProperty()
    context_id: bpy.props.IntProperty()
    should_add_representation: bpy.props.BoolProperty(default=True)
    ifc_representation_class: bpy.props.StringProperty()

    def _execute(self, context):
        props = context.scene.BIMRootProperties
        objects = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        ifc_class = self.ifc_class or props.ifc_class
        predefined_type = self.userdefined_type if self.predefined_type == "USERDEFINED" else self.predefined_type
        ifc_context = self.context_id
        if not ifc_context and get_enum_items(props, "contexts", context):
            ifc_context = int(props.contexts or "0") or None
        if ifc_context:
            ifc_context = tool.Ifc.get().by_id(ifc_context)
        active_object = context.active_object
        for obj in objects:
            core.assign_class(
                tool.Ifc,
                tool.Collector,
                tool.Root,
                obj=obj,
                ifc_class=ifc_class,
                predefined_type=predefined_type,
                should_add_representation=self.should_add_representation,
                context=ifc_context,
                ifc_representation_class=self.ifc_representation_class,
            )
        context.view_layer.objects.active = active_object


class UnlinkObject(bpy.types.Operator):
    bl_idname = "bim.unlink_object"
    bl_label = "Unlink Object"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        if self.obj:
            objects = [bpy.data.objects.get(self.obj)]
        else:
            objects = context.selected_objects
        for obj in objects:
            if obj.BIMObjectProperties.ifc_definition_id:
                IfcStore.unlink_element(obj=obj)
            for material_slot in obj.material_slots:
                if material_slot.material:
                    blenderbim.core.style.unlink_style(tool.Ifc, tool.Style, obj=material_slot.material)
                    blenderbim.core.material.unlink_material(tool.Ifc, obj=material_slot.material)
            if "Ifc" in obj.name and "/" in obj.name:
                obj.name = "/".join(obj.name.split("/")[1:])
        return {"FINISHED"}


class CopyClass(bpy.types.Operator, Operator):
    bl_idname = "bim.copy_class"
    bl_label = "Copy Class"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def _execute(self, context):
        objects = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        for obj in objects:
            core.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=obj)
        blenderbim.bim.handler.purge_module_data()
