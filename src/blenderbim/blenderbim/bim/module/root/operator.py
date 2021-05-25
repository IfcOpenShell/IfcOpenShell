import bpy
import numpy as np
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.schema
import ifcopenshell.util.element
from ifcopenshell.api.geometry.data import Data as GeometryData
from ifcopenshell.api.void.data import Data as VoidData
from blenderbim.bim.ifc import IfcStore


class EnableReassignClass(bpy.types.Operator):
    bl_idname = "bim.enable_reassign_class"
    bl_label = "Enable Reassign IFC Class"

    def execute(self, context):
        obj = bpy.context.active_object
        self.file = IfcStore.get_file()
        ifc_class = obj.name.split("/")[0]
        bpy.context.active_object.BIMObjectProperties.is_reassigning_class = True
        ifc_products = [
            "IfcElement",
            "IfcElementType",
            "IfcSpatialElement",
            "IfcGroup",
            "IfcStructural",
            "IfcPositioningElement",
            "IfcContext",
            "IfcAnnotation",
        ]
        for ifc_product in ifc_products:
            if ifcopenshell.util.schema.is_a(IfcStore.get_schema().declaration_by_name(ifc_class), ifc_product):
                bpy.context.scene.BIMRootProperties.ifc_product = ifc_product
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        bpy.context.scene.BIMRootProperties.ifc_class = element.is_a()
        if hasattr(element, "PredefinedType") and element.PredefinedType:
            bpy.context.scene.BIMRootProperties.ifc_predefined_type = element.PredefinedType
        return {"FINISHED"}


class DisableReassignClass(bpy.types.Operator):
    bl_idname = "bim.disable_reassign_class"
    bl_label = "Disable Reassign IFC Class"

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.is_reassigning_class = False
        return {"FINISHED"}


class ReassignClass(bpy.types.Operator):
    bl_idname = "bim.reassign_class"
    bl_label = "Reassign IFC Class"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        objects = [bpy.data.objects.get(self.obj)] if self.obj else bpy.context.selected_objects
        self.file = IfcStore.get_file()
        predefined_type = bpy.context.scene.BIMRootProperties.ifc_predefined_type
        if predefined_type == "USERDEFINED":
            predefined_type = bpy.context.scene.BIMRootProperties.ifc_userdefined_type
        for obj in objects:
            product = ifcopenshell.api.run(
                "root.reassign_class",
                self.file,
                **{
                    "product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
                    "ifc_class": bpy.context.scene.BIMRootProperties.ifc_class,
                    "predefined_type": predefined_type,
                },
            )
            obj.name = "{}/{}".format(product.is_a(), "/".join(obj.name.split("/")[1:]))
            IfcStore.link_element(product, obj)
            obj.BIMObjectProperties.is_reassigning_class = False
        return {"FINISHED"}


class AssignClass(bpy.types.Operator):
    bl_idname = "bim.assign_class"
    bl_label = "Assign IFC Class"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    ifc_class: bpy.props.StringProperty()
    predefined_type: bpy.props.StringProperty()
    userdefined_type: bpy.props.StringProperty()
    context_id: bpy.props.IntProperty()

    def execute(self, context):
        objects = [bpy.data.objects.get(self.obj)] if self.obj else bpy.context.selected_objects
        self.file = IfcStore.get_file()
        self.declaration = IfcStore.get_schema().declaration_by_name(self.ifc_class)
        if self.predefined_type == "USERDEFINED":
            self.predefined_type = self.ifc_userdefined_type
        elif self.predefined_type == "":
            predefined_type = None
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
                "predefined_type": self.predefined_type,
                "name": obj.name,
            },
        )
        obj.name = "{}/{}".format(product.is_a(), obj.name)
        IfcStore.link_element(product, obj)

        bpy.ops.bim.add_representation(obj=obj.name, context_id=self.context_id)

        if product.is_a("IfcElementType"):
            self.place_in_types_collection(obj)
        elif (
            product.is_a("IfcSpatialElement")
            or product.is_a("IfcSpatialStructureElement")
            or product.is_a("IfcProject")
            or product.is_a("IfcContext")
        ):
            self.place_in_spatial_collection(obj)
        else:
            self.assign_potential_spatial_container(obj)
        context.view_layer.objects.active = obj

    def place_in_types_collection(self, obj):
        for project in [c for c in bpy.context.view_layer.layer_collection.children if "IfcProject" in c.name]:
            if not [c for c in project.children if "Types" in c.name]:
                types = bpy.data.collections.new("Types")
                project.collection.children.link(types)
            for collection in [c for c in project.children if "Types" in c.name]:
                for user_collection in obj.users_collection:
                    user_collection.objects.unlink(obj)
                collection.collection.objects.link(obj)
                break
            break

    def place_in_spatial_collection(self, obj):
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
            bpy.ops.bim.assign_object(related_object=obj.name, relating_object=parent_collection.name)
        else:
            bpy.context.scene.collection.children.link(collection)

    def assign_potential_spatial_container(self, obj):
        for collection in obj.users_collection:
            if "Ifc" not in collection.name or collection.name == obj.name:
                continue
            spatial_obj = bpy.data.objects.get(collection.name)
            if spatial_obj and spatial_obj.BIMObjectProperties.ifc_definition_id:
                bpy.ops.bim.assign_container(
                    relating_structure=spatial_obj.BIMObjectProperties.ifc_definition_id, related_element=obj.name
                )
                break


class UnassignClass(bpy.types.Operator):
    bl_idname = "bim.unassign_class"
    bl_label = "Unassign IFC Class"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        if self.obj:
            objects = [bpy.data.objects.get(self.obj)]
        else:
            objects = bpy.context.selected_objects
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
    obj: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        if self.obj:
            objects = [bpy.data.objects.get(self.obj)]
        else:
            objects = bpy.context.selected_objects
        for obj in objects:
            if obj.BIMObjectProperties.ifc_definition_id:
                IfcStore.unlink_element(obj=obj)
            if "Ifc" in obj.name and "/" in obj.name:
                obj.name = "/".join(obj.name.split("/")[1:])
        return {"FINISHED"}


class CopyClass(bpy.types.Operator):
    bl_idname = "bim.copy_class"
    bl_label = "Copy Class"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        if self.obj:
            objects = [bpy.data.objects.get(self.obj)]
        else:
            objects = bpy.context.selected_objects
        for obj in objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            result = ifcopenshell.api.run(
                "root.copy_class", self.file, **{"product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)}
            )
            IfcStore.link_element(result, obj)
            relating_type = ifcopenshell.util.element.get_type(result)
            if relating_type and relating_type.RepresentationMaps:
                bpy.ops.bim.assign_type(relating_type=relating_type.id(), related_object=obj.name)
            else:
                bpy.ops.bim.add_representation(obj=obj.name)
        return {"FINISHED"}
