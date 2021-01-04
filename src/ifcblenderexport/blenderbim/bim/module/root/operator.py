import bpy
import numpy as np
import ifcopenshell
import blenderbim.bim.module.root.assign_class as assign_class
import blenderbim.bim.module.geometry.add_representation as add_representation
import blenderbim.bim.module.geometry.assign_styles as assign_styles
import blenderbim.bim.module.geometry.assign_representation as assign_representation
import blenderbim.bim.module.geometry.add_object_placement as add_object_placement
from blenderbim.bim.ifc import IfcStore

# from blenderbim.bim.module.geometry.data import Data


class ReassignClass(bpy.types.Operator):
    bl_idname = "bim.reassign_class"
    bl_label = "Reassign IFC Class"

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


class AssignClass(bpy.types.Operator):
    bl_idname = "bim.assign_class"
    bl_label = "Assign IFC Class"
    object_name: bpy.props.StringProperty()

    def execute(self, context):
        objects = [bpy.data.objects.get(self.object_name)] if self.object_name else bpy.context.selected_objects
        self.file = IfcStore.get_file()
        for obj in objects:
            if obj.BIMObjectProperties.ifc_definition_id:
                continue
            usecase = assign_class.Usecase(
                self.file,
                {
                    "ifc_class": bpy.context.scene.BIMProperties.ifc_class,
                    "predefined_type": bpy.context.scene.BIMProperties.ifc_predefined_type,
                    "name": obj.name,
                },
            )
            product = usecase.execute()

            usecase = add_object_placement.Usecase(
                self.file,
                {
                    "product": product,
                    "matrix": np.array(obj.matrix_world),
                },
            )
            result = usecase.execute()

            if obj.data:
                usecase = add_representation.Usecase(
                    self.file,
                    {
                        "context": self.file.by_id(int(bpy.context.scene.BIMProperties.contexts)),
                        "geometry": obj.data,
                        "total_items": max(1, len(obj.material_slots)),
                    },
                )
                representation = usecase.execute()

                usecase = assign_styles.Usecase(
                    self.file,
                    {
                        "shape_representation": representation,
                        "styles": [
                            self.file.by_id(s.material.BIMMaterialProperties.ifc_style_id)
                            for s in obj.material_slots
                            if s.material
                        ],
                    },
                )
                usecase.execute()

                usecase = assign_representation.Usecase(
                    self.file, {"product": product, "representation": representation}
                )
                usecase.execute()

            obj.name = "{}/{}".format(bpy.context.scene.BIMProperties.ifc_class, obj.name)
            obj.BIMObjectProperties.ifc_definition_id = int(result.id())
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
        if self.object_name:
            objects = [bpy.data.objects.get(self.object_name)]
        else:
            objects = bpy.context.selected_objects
        for obj in objects:
            existing_class = None
            if "/" in obj.name and obj.name[0:3] == "Ifc":
                obj.name = "/".join(obj.name.split("/")[1:])
        return {"FINISHED"}
