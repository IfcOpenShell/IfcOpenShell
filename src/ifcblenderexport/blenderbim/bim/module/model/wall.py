import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty, FloatProperty, BoolProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


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
    obj = object_data_add(context, mesh, operator=self)
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
    obj.name = "IfcWall/Dumb Wall"
    attribute = obj.BIMObjectProperties.attributes.add()
    attribute.name = "PredefinedType"
    attribute.string_value = "STANDARD"


class BIM_OT_add_object(Operator, AddObjectHelper):
    bl_idname = "mesh.add_wall"
    bl_label = "Dumb Wall"
    bl_options = {"REGISTER", "UNDO"}

    height: FloatProperty(name="Height", default=3)
    length: FloatProperty(name="Length", default=1)
    width: FloatProperty(name="Width", default=0.2)
    use_plane: BoolProperty(name="Use Plane", default=False)

    def execute(self, context):
        add_object(self, context)
        return {"FINISHED"}


def add_object_button(self, context):
    self.layout.operator(BIM_OT_add_object.bl_idname, icon="PLUGIN")
