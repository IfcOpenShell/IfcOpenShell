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


class AssignClass(bpy.types.Operator):
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

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        objects = [bpy.data.objects.get(self.obj)] if self.obj else context.selected_objects
        self.file = IfcStore.get_file()
        if not self.ifc_class:
            self.ifc_class = context.scene.BIMRootProperties.ifc_class
        self.declaration = IfcStore.get_schema().declaration_by_name(self.ifc_class)
        if self.predefined_type == "USERDEFINED":
            self.predefined_type = self.userdefined_type
        for obj in objects:
            self.assign_class(context, obj)
        return {"FINISHED"}

    def assign_class(self, context, obj):
        if obj.BIMObjectProperties.ifc_definition_id:
            return
        product = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            **{
                "ifc_class": self.ifc_class,
                "predefined_type": self.predefined_type or None,
                "name": obj.name,
            },
        )
        obj.name = "{}/{}".format(product.is_a(), obj.name)
        IfcStore.link_element(product, obj)

        if self.should_add_representation:
            ifc_context = self.context_id or int(context.scene.BIMProperties.contexts or "0") or None
            if ifc_context:
                ifc_context = tool.Ifc.get().by_id(ifc_context)
            blenderbim.core.geometry.add_representation(
                tool.Ifc,
                tool.Geometry,
                tool.Style,
                tool.Surveyor,
                obj=obj,
                context=ifc_context,
                ifc_representation_class=self.ifc_representation_class,
                profile_set_usage=None,
            )

        if product.is_a("IfcElementType"):
            tool.Collector.assign(obj)
        elif product.is_a("IfcOpeningElement"):
            obj.display_type = "WIRE"
            tool.Collector.assign(obj)
        elif (
            product.is_a("IfcSpatialElement")
            or product.is_a("IfcSpatialStructureElement")
            or product.is_a("IfcProject")
            or product.is_a("IfcContext")
        ):
            self.place_in_spatial_collection(obj, context)
        elif product.is_a("IfcStructuralItem"):
            if product.is_a("IfcStructuralMember"):
                self.place_in_structural_items_collection(obj, context, structural_collection="Members")
            elif product.is_a("IfcStructuralConnection"):
                self.place_in_structural_items_collection(obj, context, structural_collection="Connections")
        else:
            self.assign_potential_spatial_container(obj)
        context.view_layer.objects.active = obj

    def place_in_spatial_collection(self, obj, context):
        for collection in obj.users_collection:
            if collection.name == obj.name:
                return
        parent_collection = None
        for collection in obj.users_collection:
            collection.objects.unlink(obj)
            if "Ifc" in collection.name:
                parent_collection = collection
        collection = bpy.data.collections.new(obj.name)
        collection.objects.link(obj)
        if parent_collection:
            parent_collection.children.link(collection)
            blenderbim.core.aggregate.assign_object(
                tool.Ifc,
                tool.Aggregate,
                tool.Collector,
                relating_obj=bpy.data.objects.get(parent_collection.name),
                related_obj=obj,
            )
        else:
            context.scene.collection.children.link(collection)

    def place_in_structural_items_collection(self, obj, context, structural_collection):
        for project in [c for c in context.view_layer.layer_collection.children if "IfcProject" in c.name]:
            if not [c for c in project.children if "StructuralItems" in c.name]:
                members = bpy.data.collections.new("Members")
                connections = bpy.data.collections.new("Connections")
                items = bpy.data.collections.new("StructuralItems")
                items.children.link(members)
                items.children.link(connections)
                project.collection.children.link(items)

            for coll in [c for c in project.children if "StructuralItems" in c.name]:
                for collection in [c for c in coll.children if structural_collection in c.name]:
                    for user_collection in obj.users_collection:
                        user_collection.objects.unlink(obj)
                    collection.collection.objects.link(obj)
                    break
                break
            break

    def assign_potential_spatial_container(self, obj):
        for collection in obj.users_collection:
            if "Ifc" not in collection.name or collection.name == obj.name:
                continue
            spatial_obj = bpy.data.objects.get(collection.name)
            if spatial_obj and spatial_obj.BIMObjectProperties.ifc_definition_id:
                element = self.file.by_id(spatial_obj.BIMObjectProperties.ifc_definition_id)
                if self.file.schema != "IFC2X3" and not element.is_a("IfcSpatialElement"):
                    continue
                elif self.file.schema == "IFC2X3" and not element.is_a("IfcSpatialStructureElement"):
                    continue
                blenderbim.core.spatial.assign_container(
                    tool.Ifc,
                    tool.Collector,
                    tool.Spatial,
                    structure_obj=spatial_obj,
                    element_obj=obj,
                )
                break


class UnassignClass(bpy.types.Operator):
    bl_idname = "bim.unassign_class"
    bl_label = "Unassign IFC Class"
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
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            product = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            self.remove_voids(product, obj)
            IfcStore.unlink_element(product, obj)
            if product.is_a("IfcGridAxis"):
                ifcopenshell.api.run("grid.remove_grid_axis", self.file, **{"axis": product})
            elif product.is_a("IfcGrid"):
                grid_collection = bpy.data.collections.get(obj.name)
                for axis_collection in grid_collection.children:
                    for axis_obj in axis_collection.objects:
                        bpy.ops.bim.unassign_class(obj=axis_obj.name)
            else:
                ifcopenshell.api.run("root.remove_product", self.file, **{"product": product})
            if "/" in obj.name and obj.name[0:3] == "Ifc":
                obj.name = "/".join(obj.name.split("/")[1:])
            if obj.data and obj.data.name == "Void":
                bpy.data.objects.remove(obj)
        return {"FINISHED"}

    def remove_voids(self, product, obj):
        if product.id() not in VoidData.products:
            VoidData.load(self.file, product.id())
        for opening_id in VoidData.products[product.id()]:
            bpy.ops.bim.remove_opening(opening_id=opening_id, obj=obj.name)


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
