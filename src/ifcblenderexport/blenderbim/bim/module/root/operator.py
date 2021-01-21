import bpy
import numpy as np
import ifcopenshell
import ifcopenshell.util.schema
import blenderbim.bim.module.root.create_product as create_product
import blenderbim.bim.module.root.remove_product as remove_product
import blenderbim.bim.module.root.reassign_class as reassign_class
from blenderbim.bim.ifc import IfcStore


class EnableReassignClass(bpy.types.Operator):
    bl_idname = "bim.enable_reassign_class"
    bl_label = "Enable Reassign IFC Class"

    def execute(self, context):
        obj = bpy.context.active_object
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
                bpy.context.scene.BIMProperties.ifc_product = ifc_product
        bpy.context.scene.BIMProperties.ifc_class = obj.name.split("/")[0]
        predefined_type = obj.BIMObjectProperties.attributes.get("PredefinedType")
        if predefined_type:
            bpy.context.scene.BIMProperties.ifc_predefined_type = predefined_type.string_value
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

    def execute(self, context):
        obj = bpy.context.active_object
        self.file = IfcStore.get_file()
        predefined_type = bpy.context.scene.BIMProperties.ifc_predefined_type
        if predefined_type == "USERDEFINED":
            predefined_type = bpy.context.scene.BIMProperties.ifc_userdefined_type
        product = reassign_class.Usecase(
            self.file,
            {
                "product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
                "ifc_class": bpy.context.scene.BIMProperties.ifc_class,
                "predefined_type": predefined_type,
            },
        ).execute()
        obj.name = "{}/{}".format(product.is_a(), "/".join(obj.name.split("/")[1:]))
        obj.BIMObjectProperties.ifc_definition_id = int(product.id())
        bpy.context.active_object.BIMObjectProperties.is_reassigning_class = False
        return {"FINISHED"}


class AssignClass(bpy.types.Operator):
    bl_idname = "bim.assign_class"
    bl_label = "Assign IFC Class"
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
            if obj.data:
                for material in obj.data.materials:
                    if not material.BIMMaterialProperties.ifc_style_id:
                        bpy.ops.bim.add_style(material=material.name)
            self.assign_class(obj)
        return {"FINISHED"}

    def assign_class(self, obj):
        if obj.BIMObjectProperties.ifc_definition_id:
            return
        product = create_product.Usecase(
            self.file,
            {
                "ifc_class": self.ifc_class,
                "predefined_type": self.predefined_type,
                "name": obj.name,
            },
        ).execute()
        obj.name = "{}/{}".format(product.is_a(), obj.name)
        obj.BIMObjectProperties.ifc_definition_id = int(product.id())

        if obj.data:
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
        else:
            bpy.context.scene.collection.children.link(collection)

    def assign_potential_spatial_container(self, obj):
        for collection in obj.users_collection:
            if "Ifc" not in collection.name or collection.name == obj.name:
                continue
            bpy.ops.bim.assign_container(relating_structure=collection.name, related_element=obj.name)
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
            usecase = remove_product.Usecase(
                self.file,
                {"product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)},
            )
            usecase.execute()
            obj.BIMObjectProperties.ifc_definition_id = 0
            if "/" in obj.name and obj.name[0:3] == "Ifc":
                obj.name = "/".join(obj.name.split("/")[1:])
        return {"FINISHED"}
