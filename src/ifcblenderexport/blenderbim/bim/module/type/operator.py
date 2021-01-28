import bpy
import ifcopenshell.util.schema
import blenderbim.bim.module.type.assign_type as assign_type
import blenderbim.bim.module.type.unassign_type as unassign_type
import blenderbim.bim.module.type.get_related_objects as get_related_objects
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.type.data import Data


class AssignType(bpy.types.Operator):
    bl_idname = "bim.assign_type"
    bl_label = "Assign Type"
    relating_type: bpy.props.StringProperty()
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_object = bpy.data.objects.get(self.related_object) if self.related_object else bpy.context.active_object
        props = related_object.BIMObjectProperties
        relating_type = bpy.data.objects.get(self.relating_type) if self.relating_type else props.relating_type
        if not relating_type or not relating_type.BIMObjectProperties.ifc_definition_id:
            return {"FINISHED"}
        assign_type.Usecase(
            self.file,
            {
                "related_object": self.file.by_id(props.ifc_definition_id),
                "relating_type": self.file.by_id(relating_type.BIMObjectProperties.ifc_definition_id),
            },
        ).execute()
        Data.load(props.ifc_definition_id)
        bpy.ops.bim.disable_editing_type(obj=related_object.name)
        return {"FINISHED"}


class UnassignType(bpy.types.Operator):
    bl_idname = "bim.unassign_type"
    bl_label = "Unassign Type"
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_object = bpy.data.objects.get(self.related_object) if self.related_object else bpy.context.active_object
        props = related_object.BIMObjectProperties
        unassign_type.Usecase(
            self.file,
            {
                "related_object": self.file.by_id(props.ifc_definition_id),
            },
        ).execute()
        Data.load(props.ifc_definition_id)
        return {"FINISHED"}


class EnableEditingType(bpy.types.Operator):
    bl_idname = "bim.enable_editing_type"
    bl_label = "Enable Editing Type"

    def execute(self, context):
        bpy.context.active_object.BIMObjectProperties.relating_type = None
        bpy.context.active_object.BIMObjectProperties.is_editing_type = True
        return {"FINISHED"}


class DisableEditingType(bpy.types.Operator):
    bl_idname = "bim.disable_editing_type"
    bl_label = "Disable Editing Type"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        obj.BIMObjectProperties.is_editing_type = False
        return {"FINISHED"}


class SelectSimilarType(bpy.types.Operator):
    bl_idname = "bim.select_similar_type"
    bl_label = "Select Similar Type"
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_object = bpy.data.objects.get(self.related_object) if self.related_object else bpy.context.active_object
        props = related_object.BIMObjectProperties
        product = self.file.by_id(props.ifc_definition_id)
        declaration = IfcStore.get_schema().declaration_by_name(product.is_a())
        if ifcopenshell.util.schema.is_a(declaration, "IfcElementType"):
            related_objects = get_related_objects.Usecase(self.file, {
                "relating_type": self.file.by_id(props.ifc_definition_id)
            }).execute()
        else:
            related_objects = get_related_objects.Usecase(self.file, {
                "related_object": self.file.by_id(props.ifc_definition_id)
            }).execute()
        for obj in bpy.context.visible_objects:
            if obj.BIMObjectProperties.ifc_definition_id in related_objects:
                obj.select_set(True)
        return {"FINISHED"}
