import bpy
import bmesh
from bpy.types import Operator
from bpy.props import FloatVectorProperty, FloatProperty, IntProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


def add_object(self, context):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=self.size)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    mesh = bpy.data.meshes.new(name="Dumb Opening")
    bm.to_mesh(mesh)
    bm.free()
    obj = object_data_add(context, mesh, operator=self)
    obj.name = "IfcOpening/Dumb Opening"
    obj.display_type = "WIRE"
    attribute = obj.BIMObjectProperties.attributes.add()
    attribute.name = "PredefinedType"
    attribute.string_value = "OPENING"


class BIM_OT_add_object(Operator, AddObjectHelper):
    bl_idname = "mesh.add_opening"
    bl_label = "Dumb Opening"
    bl_options = {"REGISTER", "UNDO"}

    size: FloatProperty(name="Size", default=2)

    def execute(self, context):
        add_object(self, context)
        return {"FINISHED"}


def add_object_button(self, context):
    self.layout.operator(BIM_OT_add_object.bl_idname, icon="PLUGIN")
