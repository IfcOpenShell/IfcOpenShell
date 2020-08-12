import bpy
import math
from bpy.types import Operator
from bpy.props import FloatVectorProperty, FloatProperty, IntProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector

def add_object(self, context):
    # Window lining profile
    verts = [
        Vector((0, 0, 0)),
        Vector((0, -self.depth, 0)),
        Vector((.04, -self.depth, 0)),
        Vector((.04, 0, 0)),
    ]
    edges = []
    faces = [[0, 1, 2, 3]]
    mesh = bpy.data.meshes.new(name="Dumb Window Profile")
    mesh.from_pydata(verts, edges, faces)
    obj = object_data_add(context, mesh, operator=self)
    bpy.ops.object.convert(target='CURVE')

    # Window lining sweep
    verts = [
        Vector((0, 0, 0)),
        Vector((0, self.overall_height, 0)),
        Vector((self.overall_width, self.overall_height, 0)),
        Vector((self.overall_width, 0, 0)),
    ]
    edges = [[0, 1], [1, 2], [2, 3]]
    faces = []
    mesh = bpy.data.meshes.new(name="Dumb Window")
    mesh.from_pydata(verts, edges, faces)
    obj2 = object_data_add(context, mesh, operator=self)
    bpy.ops.object.convert(target='CURVE')
    obj2.data.splines[0].use_cyclic_u = True

    obj2.data.dimensions = '2D'
    obj2.data.bevel_object = obj

    obj2.rotation_euler[0] = math.pi/2
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.transform_apply(location=False)
    bpy.data.objects.remove(obj, do_unlink=True)

    # Window panel
    verts = [
        Vector((.04, (self.depth/2)+.005, .04)),
        Vector((.04, (self.depth/2)-.005, .04)),
        Vector((self.overall_width-.04, (self.depth/2)-.005, .04)),
        Vector((self.overall_width-.04, (self.depth/2)+.005, .04)),
    ]
    edges = []
    faces = [[0, 1, 2, 3]]
    mesh = bpy.data.meshes.new(name="Dumb Window Panel")
    mesh.from_pydata(verts, edges, faces)
    obj3 = object_data_add(context, mesh, operator=self)
    modifier = obj3.modifiers.new('Panel Height', 'SOLIDIFY')
    modifier.offset = 1
    modifier.thickness = self.overall_height-.08
    bpy.ops.object.convert(target='MESH')

    ctx = bpy.context.copy()
    ctx['active_object'] = obj2
    ctx['selected_editable_objects'] = [obj2, obj3]
    bpy.ops.object.join(ctx)

    # Window Opening
    verts = [
        Vector((0, -.1, 0)),
        Vector((0, self.depth+.1, 0)),
        Vector((self.overall_width, self.depth+.1, 0)),
        Vector((self.overall_width, -.1, 0)),
    ]
    edges = []
    faces = [[0, 1, 2, 3]]
    mesh = bpy.data.meshes.new(name="Dumb Window Opening")
    mesh.from_pydata(verts, edges, faces)
    obj4 = object_data_add(context, mesh, operator=self)
    modifier = obj4.modifiers.new('Panel Height', 'SOLIDIFY')
    modifier.offset = -1
    modifier.thickness = self.overall_height
    bpy.ops.object.convert(target='MESH')
    obj4.display_type = 'WIRE'
    obj4.parent = obj2
    obj4.matrix_parent_inverse = obj2.matrix_world.inverted()
    obj4.hide_render = True
    obj4.name = 'IfcOpeningElement/Dumb Window Opening'
    attribute = obj4.BIMObjectProperties.attributes.add()
    attribute.name = 'PredefinedType'
    attribute.string_value = 'OPENING'

    obj2.name = 'IfcWindow/Dumb Window'
    attribute = obj2.BIMObjectProperties.attributes.add()
    attribute.name = 'PredefinedType'
    attribute.string_value = 'WINDOW'


class BIM_OT_add_object(Operator, AddObjectHelper):
    bl_idname = "mesh.add_window"
    bl_label = "Dumb Window"
    bl_options = {'REGISTER', 'UNDO'}

    overall_width: FloatProperty(name='Overall Width', default=.7)
    overall_height: FloatProperty(name='Overall Height', default=1)
    depth: FloatProperty(name='Depth', default=.1)

    def execute(self, context):
        add_object(self, context)
        return {'FINISHED'}


def add_object_button(self, context):
    self.layout.operator(
        BIM_OT_add_object.bl_idname,
        icon='PLUGIN')
