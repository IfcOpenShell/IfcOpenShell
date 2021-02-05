import bpy
from bpy.types import Operator
from bpy.props import FloatProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


def add_object(self, context):
    verts = [
        Vector((0, 0, 0)),
        Vector((0, self.width, 0)),
        Vector((self.length, self.width, 0)),
        Vector((self.length, 0, 0)),
    ]
    edges = []
    faces = [[0, 1, 2, 3]]

    mesh = bpy.data.meshes.new(name="Dumb Slab")
    mesh.from_pydata(verts, edges, faces)
    obj = object_data_add(context, mesh, operator=self)
    modifier = obj.modifiers.new("Slab Depth", "SOLIDIFY")
    modifier.use_even_offset = True
    modifier.offset = 1
    modifier.thickness = self.depth
    obj.name = "Slab"


class BIM_OT_add_object(Operator, AddObjectHelper):
    bl_idname = "mesh.add_slab"
    bl_label = "Dumb Slab"
    bl_options = {"REGISTER", "UNDO"}

    length: FloatProperty(name="Length", default=2)
    width: FloatProperty(name="Width", default=2)
    depth: FloatProperty(name="Depth", default=0.2)

    def execute(self, context):
        add_object(self, context)
        return {"FINISHED"}


def add_object_button(self, context):
    self.layout.operator(BIM_OT_add_object.bl_idname, icon="PLUGIN")
