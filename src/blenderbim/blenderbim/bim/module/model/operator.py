import bpy
import math
import ifcopenshell
import ifcopenshell.util.type
import ifcopenshell.util.unit
import mathutils.geometry
from blenderbim.bim.ifc import IfcStore
from mathutils import Vector


class AddTypeInstance(bpy.types.Operator):
    bl_idname = "bim.add_type_instance"
    bl_label = "Add Type Instance"

    def execute(self, context):
        tprops = context.scene.BIMTypeProperties
        if not tprops.ifc_class or not tprops.relating_type:
            return {"FINISHED"}
        self.file = IfcStore.get_file()
        instance_class = ifcopenshell.util.type.get_applicable_entities(tprops.ifc_class, self.file.schema)[0]
        if instance_class in ["IfcWall", "IfcWallStandardCase"]:
            obj = DumbWallGenerator(self.file.by_id(int(tprops.relating_type))).generate()
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


class DumbWallGenerator:
    def __init__(self, relating_type):
        self.relating_type = relating_type

    def generate(self):
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(IfcStore.get_file())
        thicknesses = []
        for rel in self.relating_type.HasAssociations:
            if rel.is_a("IfcRelAssociatesMaterial"):
                material = rel.RelatingMaterial
                if material.is_a("IfcMaterialLayerSet"):
                    thicknesses = [l.LayerThickness for l in material.MaterialLayers]
                    break
        if not thicknesses:
            return

        self.collection = bpy.context.view_layer.active_layer_collection.collection
        self.collection_obj = bpy.data.objects.get(self.collection.name)
        self.width = sum(thicknesses) * unit_scale
        self.height = 3
        self.length = 1
        self.rotation = 0
        self.location = Vector((0, 0, 0))

        if self.has_sketch():
            return self.derive_from_sketch()
        return self.derive_from_cursor()

    def has_sketch(self):
        return (
            len(bpy.context.scene.grease_pencil.layers) == 1
            and bpy.context.scene.grease_pencil.layers[0].active_frame.strokes
        )

    def derive_from_cursor(self):
        self.location = bpy.context.scene.cursor.location
        if self.collection:
            for sibling_obj in self.collection.objects:
                if not isinstance(sibling_obj.data, bpy.types.Mesh):
                    continue
                if "IfcWall" not in sibling_obj.name:
                    continue
                print("checking sibling", sibling_obj)
                raycast = sibling_obj.closest_point_on_mesh(bpy.context.scene.cursor.location, distance=0.05)
                print(raycast)
                if raycast[0]:
                    print("GOT IT!")
                    print(raycast)
                    # Rotate the wall in the direction of the face normal
                    self.rotation = math.atan2(raycast[2][1], raycast[2][0])
                    break
        self.create_wall()

    def create_wall(self):
        verts = [
            Vector((0, self.width / 2, 0)),
            Vector((0, -self.width / 2, 0)),
            Vector((0, self.width / 2, self.height)),
            Vector((0, -self.width / 2, self.height)),
            Vector((self.length, self.width / 2, 0)),
            Vector((self.length, -self.width / 2, 0)),
            Vector((self.length, self.width / 2, self.height)),
            Vector((self.length, -self.width / 2, self.height)),
        ]
        faces = [
            [1, 3, 2, 0],
            [4, 6, 7, 5],
            [1, 0, 4, 5],
            [3, 7, 6, 2],
            [0, 2, 6, 4],
            [1, 5, 7, 3],
        ]
        mesh = bpy.data.meshes.new(name="Wall")
        mesh.from_pydata(verts, [], faces)
        obj = bpy.data.objects.new("Wall", mesh)
        obj.location = self.location
        obj.rotation_euler[2] = self.rotation
        if self.collection_obj and self.collection_obj.BIMObjectProperties.ifc_definition_id:
            obj.location[2] = self.collection_obj.location[2]
        self.collection.objects.link(obj)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcWall")
        bpy.ops.bim.assign_type(relating_type=self.relating_type.id(), related_object=obj.name)
        return obj
