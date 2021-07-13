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
            else bpy.context.selected_objects or [bpy.context.active_object]
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
            [bpy.data.objects.get(self.related_object)] if self.related_object else bpy.context.selected_objects
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
        bpy.context.active_object.BIMTypeProperties.is_editing_type = True
        return {"FINISHED"}


class DisableEditingType(bpy.types.Operator):
    bl_idname = "bim.disable_editing_type"
    bl_label = "Disable Editing Type"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        obj.BIMTypeProperties.is_editing_type = False
        return {"FINISHED"}


class SelectSimilarType(bpy.types.Operator):
    bl_idname = "bim.select_similar_type"
    bl_label = "Select Similar Type"
    bl_options = {"REGISTER", "UNDO"}
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_object = bpy.data.objects.get(self.related_object) if self.related_object else bpy.context.active_object
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
        for obj in bpy.context.visible_objects:
            if obj.BIMObjectProperties.ifc_definition_id in related_objects:
                obj.select_set(True)
        return {"FINISHED"}
