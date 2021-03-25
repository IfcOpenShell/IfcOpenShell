import bpy
from bpy.types import Operator
from bpy.props import FloatProperty, BoolProperty
from mathutils import Vector
from blenderbim.bim.ifc import IfcStore


def add_object(self, context):
    if self.use_plane:
        verts = [
            Vector((0, 0, 0)),
            Vector((0, 0, self.height)),
            Vector((self.length, 0, self.height)),
            Vector((self.length, 0, 0)),
        ]
        edges = []
        faces = [[0, 1, 2, 3]]
    else:
        verts = [
            Vector((0, 0, 0)),
            Vector((self.length, 0, 0)),
        ]
        edges = [[0, 1]]
        faces = []

    mesh = bpy.data.meshes.new(name="Dumb Wall")
    mesh.from_pydata(verts, edges, faces)
    obj = bpy.data.objects.new("Wall", mesh)
    context.view_layer.active_layer_collection.collection.objects.link(obj)
    if not self.use_plane:
        modifier = obj.modifiers.new("Wall Height", "SCREW")
        modifier.angle = 0
        modifier.screw_offset = self.height
        modifier.use_smooth_shade = False
        modifier.use_normal_calculate = True
        modifier.use_normal_flip = True
        modifier.steps = 1
        modifier.render_steps = 1
    modifier = obj.modifiers.new("Wall Width", "SOLIDIFY")
    modifier.use_even_offset = True
    modifier.thickness = self.width
    obj.name = "Wall"
    if IfcStore.get_file():
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcWall")
    obj.location = context.scene.cursor.location
    return obj


class BIM_OT_add_object(Operator):
    bl_idname = "mesh.add_wall"
    bl_label = "Dumb Wall"

    height: FloatProperty(name="Height", default=3)
    length: FloatProperty(name="Length", default=1)
    width: FloatProperty(name="Width", default=0.2)
    use_plane: BoolProperty(name="Use Plane", default=False)

    def execute(self, context):
        add_object(self, context)
        return {"FINISHED"}


def add_object_button(self, context):
    self.layout.operator(BIM_OT_add_object.bl_idname, icon="PLUGIN")
