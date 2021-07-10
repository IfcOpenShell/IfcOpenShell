import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element
import ifcopenshell.util.representation
from . import wall, slab, column
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.pset.data import Data as PsetData
from mathutils import Vector


class AddTypeInstance(bpy.types.Operator):
    bl_idname = "bim.add_type_instance"
    bl_label = "Add Type Instance"
    bl_options = {"REGISTER", "UNDO"}
    ifc_class: bpy.props.StringProperty()
    relating_type: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        tprops = context.scene.BIMTypeProperties
        ifc_class = self.ifc_class or tprops.ifc_class
        relating_type = self.relating_type or tprops.relating_type
        if not ifc_class or not relating_type:
            return {"FINISHED"}
        self.file = IfcStore.get_file()
        instance_class = ifcopenshell.util.type.get_applicable_entities(ifc_class, self.file.schema)[0]
        if ifc_class == "IfcWallType":
            obj = wall.DumbWallGenerator(self.file.by_id(int(relating_type))).generate()
            if obj:
                return {"FINISHED"}
        elif ifc_class == "IfcSlabType":
            obj = slab.DumbSlabGenerator(self.file.by_id(int(relating_type))).generate()
            if obj:
                return {"FINISHED"}
        elif ifc_class == "IfcColumnType":
            obj = column.DumbColumnGenerator(self.file.by_id(int(relating_type))).generate()
            if obj:
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
            [0, 2, 6, 4],
        ]
        mesh = bpy.data.meshes.new(name="Instance")
        mesh.from_pydata(verts, edges, faces)
        obj = bpy.data.objects.new("Instance", mesh)
        obj.location = context.scene.cursor.location
        collection = bpy.context.view_layer.active_layer_collection.collection
        collection.objects.link(obj)
        collection_obj = bpy.data.objects.get(collection.name)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class=instance_class)
        bpy.ops.bim.assign_type(relating_type=int(tprops.relating_type), related_object=obj.name)
        if collection_obj and collection_obj.BIMObjectProperties.ifc_definition_id:
            obj.location[2] = collection_obj.location[2] - min([v[2] for v in obj.bound_box])
        return {"FINISHED"}


def generate_box(usecase_path, ifc_file, settings):
    box_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Box", "MODEL_VIEW")
    if not box_context:
        return
    obj = settings["blender_object"]
    if 0 in list(obj.dimensions):
        return
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    old_box = ifcopenshell.util.representation.get_representation(product, "Model", "Box", "MODEL_VIEW")
    if settings["context"].ContextType == "Model" and getattr(settings["context"], "ContextIdentifier") == "Body":
        if old_box:
            bpy.ops.bim.remove_representation(representation_id=old_box.id(), obj=obj.name)

        new_settings = settings.copy()
        new_settings["context"] = box_context
        new_box = ifcopenshell.api.run(
            "geometry.add_representation", ifc_file, should_run_listeners=False, **new_settings
        )
        ifcopenshell.api.run(
            "geometry.assign_representation",
            ifc_file,
            should_run_listeners=False,
            **{"product": product, "representation": new_box}
        )

def regenerate_profile_usage(usecase_path, ifc_file, settings):
    elements = []
    if ifc_file.schema == "IFC2X3":
        for rel in ifc_file.get_inverse(settings["usage"]):
            if not rel.is_a("IfcRelAssociatesMaterial"):
                continue
            for element in rel.RelatedObjects:
                elements.append(element)
    else:
        for rel in settings["usage"].AssociatedTo:
            for element in rel.RelatedObjects:
                elements.append(element)

    for element in elements:
        obj = IfcStore.get_element(element.id())
        if not obj:
            continue
        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if representation:
            bpy.ops.bim.switch_representation(obj=obj.name, ifc_definition_id=representation.id(), should_reload=True)
