import bpy
import ifcopenshell.util.schema
import ifcopenshell.util.type
import blenderbim.bim.module.type.assign_type as assign_type
import blenderbim.bim.module.type.unassign_type as unassign_type
import blenderbim.bim.module.type.get_related_objects as get_related_objects
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.type.data import Data
from blenderbim.bim.module.type.prop import getIfcTypes, getAvailableTypes, updateTypeInstanceIfcClass
from mathutils import Vector


class AssignType(bpy.types.Operator):
    bl_idname = "bim.assign_type"
    bl_label = "Assign Type"
    relating_type: bpy.props.IntProperty()
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        relating_type = self.relating_type or int(context.active_object.BIMTypeProperties.relating_type)
        related_objects = (
            [bpy.data.objects.get(self.related_object)] if self.related_object else bpy.context.selected_objects
        )
        for related_object in related_objects:
            oprops = related_object.BIMObjectProperties
            assign_type.Usecase(
                self.file,
                {
                    "related_object": self.file.by_id(oprops.ifc_definition_id),
                    "relating_type": self.file.by_id(relating_type),
                },
            ).execute()
            Data.load(oprops.ifc_definition_id)
            if self.file.by_id(relating_type).RepresentationMaps:
                bpy.ops.bim.map_representations(product_id=oprops.ifc_definition_id, type_product_id=relating_type)

        bpy.ops.bim.disable_editing_type(obj=related_object.name)
        return {"FINISHED"}


class UnassignType(bpy.types.Operator):
    bl_idname = "bim.unassign_type"
    bl_label = "Unassign Type"
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_objects = (
            [bpy.data.objects.get(self.related_object)] if self.related_object else bpy.context.selected_objects
        )
        for related_object in related_objects:
            oprops = related_object.BIMObjectProperties
            unassign_type.Usecase(
                self.file,
                {
                    "related_object": self.file.by_id(oprops.ifc_definition_id),
                },
            ).execute()
            Data.load(oprops.ifc_definition_id)
        return {"FINISHED"}


class EnableEditingType(bpy.types.Operator):
    bl_idname = "bim.enable_editing_type"
    bl_label = "Enable Editing Type"

    def execute(self, context):
        bpy.context.active_object.BIMTypeProperties.is_editing_type = True
        return {"FINISHED"}


class DisableEditingType(bpy.types.Operator):
    bl_idname = "bim.disable_editing_type"
    bl_label = "Disable Editing Type"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        obj.BIMTypeProperties.is_editing_type = False
        return {"FINISHED"}


class SelectSimilarType(bpy.types.Operator):
    bl_idname = "bim.select_similar_type"
    bl_label = "Select Similar Type"
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_object = bpy.data.objects.get(self.related_object) if self.related_object else bpy.context.active_object
        oprops = related_object.BIMObjectProperties
        product = self.file.by_id(oprops.ifc_definition_id)
        declaration = IfcStore.get_schema().declaration_by_name(product.is_a())
        if ifcopenshell.util.schema.is_a(declaration, "IfcElementType"):
            related_objects = get_related_objects.Usecase(
                self.file, {"relating_type": self.file.by_id(oprops.ifc_definition_id)}
            ).execute()
        else:
            related_objects = get_related_objects.Usecase(
                self.file, {"related_object": self.file.by_id(oprops.ifc_definition_id)}
            ).execute()
        for obj in bpy.context.visible_objects:
            if obj.BIMObjectProperties.ifc_definition_id in related_objects:
                obj.select_set(True)
        return {"FINISHED"}


class AddTypeInstance(bpy.types.Operator):
    bl_idname = "bim.add_type_instance"
    bl_label = "Add Type Instance"
    ifc_class: bpy.props.EnumProperty(items=getIfcTypes, name="IFC Class", update=updateTypeInstanceIfcClass)
    relating_type: bpy.props.EnumProperty(items=getAvailableTypes, name="Relating Type")

    def execute(self, context):
        if not self.ifc_class or not self.relating_type:
            return {"FINISHED"}
        # A cube
        verts = [
            Vector((-1, -1, -1)),
            Vector((-1, -1, 1)),
            Vector((-1, 1, -1)),
            Vector((-1, 1, 1)),
            Vector((1, -1, -1)),
            Vector((1, -1, 1)),
            Vector((1, 1, -1)),
            Vector((1, 1, 1)),
        ]
        edges = []
        faces = [
            [0, 2, 3, 1],
            [2, 3, 7, 6],
            [4, 5, 7, 6],
            [0, 1, 5, 4],
            [1, 3, 7, 5],
        ]
        mesh = bpy.data.meshes.new(name="Instance")
        mesh.from_pydata(verts, edges, faces)
        obj = bpy.data.objects.new("Instance", mesh)
        obj.location = context.scene.cursor.location
        context.view_layer.active_layer_collection.collection.objects.link(obj)
        self.file = IfcStore.get_file()
        instance_class = ifcopenshell.util.type.get_applicable_entities(self.ifc_class, self.file.schema)[0]
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class=instance_class)
        bpy.ops.bim.assign_type(relating_type=int(self.relating_type), related_object=obj.name)
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
