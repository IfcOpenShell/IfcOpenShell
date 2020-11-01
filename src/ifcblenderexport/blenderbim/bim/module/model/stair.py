import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty, FloatProperty, IntProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


def add_object(self, context):
    if self.number_of_treads <= 0:
        self.number_of_treads = 1
    verts = [
        Vector((0, 0, 0)),
        Vector((0, self.tread_length, 0)),
        Vector((self.width, self.tread_length, 0)),
        Vector((self.width, 0, 0)),
    ]
    edges = []
    faces = [[0, 1, 2, 3]]

    mesh = bpy.data.meshes.new(name="Dumb Stair")
    mesh.from_pydata(verts, edges, faces)
    obj = object_data_add(context, mesh, operator=self)
    modifier = obj.modifiers.new("Stair Width", "SOLIDIFY")
    modifier.use_even_offset = True
    modifier.offset = 1
    modifier.thickness = self.tread_depth
    modifier = obj.modifiers.new("Stair Treads", "ARRAY")
    modifier.relative_offset_displace[0] = 0
    modifier.relative_offset_displace[1] = 1
    modifier.use_constant_offset = True
    modifier.constant_offset_displace[2] = self.height / self.number_of_treads
    modifier.count = self.number_of_treads
    self.riser_height = self.height / self.number_of_treads
    self.length = self.number_of_treads * self.tread_length
    obj.name = "IfcStairFlight/Dumb Stair"
    attribute = obj.BIMObjectProperties.attributes.add()
    attribute.name = "PredefinedType"
    attribute.string_value = "STRAIGHT"


class BIM_OT_add_object(Operator, AddObjectHelper):
    bl_idname = "mesh.add_stair"
    bl_label = "Dumb Stair"
    bl_options = {"REGISTER", "UNDO"}

    width: FloatProperty(name="Width", default=1.1)
    height: FloatProperty(name="Height", default=1)
    tread_depth: FloatProperty(name="Tread Depth", default=0.2)
    number_of_treads: IntProperty(name="Number of Treads (Goings)", default=6)
    tread_length: FloatProperty(name="Tread Length (Going)", default=0.25)
    riser_height: FloatProperty(name="*Calculated* Riser Height")
    length: FloatProperty(name="*Calculated* Length")

    def execute(self, context):
        add_object(self, context)
        return {"FINISHED"}


def add_object_button(self, context):
    self.layout.operator(BIM_OT_add_object.bl_idname, icon="PLUGIN")
