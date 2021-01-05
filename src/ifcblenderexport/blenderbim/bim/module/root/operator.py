import bpy
import numpy as np
import ifcopenshell
import blenderbim.bim.module.root.create_product as create_product
import blenderbim.bim.module.root.remove_product as remove_product
import blenderbim.bim.module.root.reassign_class as reassign_class
import blenderbim.bim.module.geometry.add_representation as add_representation
import blenderbim.bim.module.geometry.assign_styles as assign_styles
import blenderbim.bim.module.geometry.assign_representation as assign_representation
import blenderbim.bim.module.geometry.add_object_placement as add_object_placement
import blenderbim.bim.module.spatial.assign_container as assign_container
from blenderbim.bim.ifc import IfcStore


class EnableReassignClass(bpy.types.Operator):
    bl_idname = "bim.enable_reassign_class"
    bl_label = "Enable Reassign IFC Class"

    def execute(self, context):
        obj = bpy.context.active_object
        ifc_class = obj.name.split("/")[0]
        ifc_schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(bpy.context.scene.BIMProperties.export_schema)
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
            if ifcopenshell.util.schema.is_a(ifc_schema.declaration_by_name(ifc_class), ifc_product):
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

    def execute(self, context):
        objects = [bpy.data.objects.get(self.obj)] if self.obj else bpy.context.selected_objects
        self.file = IfcStore.get_file()
        for obj in objects:
            if obj.BIMObjectProperties.ifc_definition_id:
                continue
            if self.predefined_type == "USERDEFINED":
                predefined_type = self.ifc_userdefined_type
            elif self.predefined_type == "":
                predefined_type = None
            else:
                predefined_type = self.predefined_type
            product = create_product.Usecase(
                self.file,
                {
                    "ifc_class": self.ifc_class,
                    "predefined_type": predefined_type,
                    "name": obj.name,
                },
            ).execute()

            add_object_placement.Usecase(
                self.file,
                {
                    "product": product,
                    "matrix": np.array(obj.matrix_world),
                },
            ).execute()

            if obj.data:
                representation = add_representation.Usecase(
                    self.file,
                    {
                        "context": self.file.by_id(int(bpy.context.scene.BIMProperties.contexts)),
                        "geometry": obj.data,
                        "total_items": max(1, len(obj.material_slots)),
                    },
                ).execute()

                assign_styles.Usecase(
                    self.file,
                    {
                        "shape_representation": representation,
                        "styles": [
                            self.file.by_id(s.material.BIMMaterialProperties.ifc_style_id)
                            for s in obj.material_slots
                            if s.material
                        ],
                    },
                ).execute()

                assign_representation.Usecase(
                    self.file, {"product": product, "representation": representation}
                ).execute()

            relating_structure = None
            for collection in obj.users_collection:
                if "Ifc" in collection.name:
                    relating_structure = self.file.by_id(
                        bpy.data.objects.get(collection.name).BIMObjectProperties.ifc_definition_id
                    )
                    break

            if relating_structure:
                assign_container.Usecase(
                    self.file,
                    {
                        "product": product,
                        "relating_structure": relating_structure,
                    },
                ).execute()

            obj.name = "{}/{}".format(product.is_a(), obj.name)
            obj.BIMObjectProperties.ifc_definition_id = int(product.id())
            if bpy.context.scene.BIMProperties.ifc_product == "IfcElementType":
                self.place_in_types_collection(obj)
        return {"FINISHED"}

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


class UnassignClass(bpy.types.Operator):
    bl_idname = "bim.unassign_class"
    bl_label = "Unassign IFC Class"
    object_name: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        if self.object_name:
            objects = [bpy.data.objects.get(self.object_name)]
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
