import bpy
import ifcopenshell
import ifcopenshell.util.type
from blenderbim.bim.ifc import IfcStore
from mathutils import Vector


class AddTypeInstance(bpy.types.Operator):
    bl_idname = "bim.add_type_instance"
    bl_label = "Add Type Instance"

    def execute(self, context):
        tprops = context.scene.BIMTypeProperties
        if not tprops.ifc_class or not tprops.relating_type:
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
        context.view_layer.active_layer_collection.collection.objects.link(obj)
        self.file = IfcStore.get_file()
        instance_class = ifcopenshell.util.type.get_applicable_entities(tprops.ifc_class, self.file.schema)[0]
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class=instance_class)
        bpy.ops.bim.assign_type(relating_type=int(tprops.relating_type), related_object=obj.name)
        return {"FINISHED"}
