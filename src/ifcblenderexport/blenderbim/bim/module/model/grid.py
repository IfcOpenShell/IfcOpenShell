import bpy
import math
from bpy.types import Operator
from bpy.props import FloatVectorProperty, FloatProperty, IntProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector

def add_object(self, context):
    obj = object_data_add(context, None, operator=self)
    obj.name = 'IfcGrid/Grid'
    name = obj.name.split('/')[1]

    default_collection = obj.users_collection[0]
    default_collection.objects.unlink(obj)

    collection = bpy.data.collections.new('IfcGrid/' + name)
    bpy.context.view_layer.active_layer_collection.collection.children.link(collection)
    collection.objects.link(obj)

    axes_collection = bpy.data.collections.new('UAxes')
    collection.children.link(axes_collection)
    for i in range(0, self.total_u):
        verts = [Vector((-2, i*self.u_spacing, 0)), Vector((((self.total_v-1)*self.v_spacing)+2, i*self.u_spacing, 0))]
        edges = [[0, 1]]
        faces = []
        mesh = bpy.data.meshes.new(name="Grid Axis")
        mesh.from_pydata(verts, edges, faces)
        obj = object_data_add(context, mesh, operator=self)
        tag = chr(ord('A')+i)
        obj.name = 'IfcGridAxis/' + tag
        default_collection.objects.unlink(obj)
        axes_collection.objects.link(obj)
        attribute = obj.BIMObjectProperties.attributes.add()
        attribute.name = 'AxisTag'
        attribute.string_value = tag

    axes_collection = bpy.data.collections.new('VAxes')
    collection.children.link(axes_collection)
    for i in range(0, self.total_v):
        verts = [Vector((i*self.v_spacing, -2, 0)), Vector((i*self.v_spacing, ((self.total_u-1)*self.u_spacing)+2, 0))]
        edges = [[0, 1]]
        faces = []
        mesh = bpy.data.meshes.new(name="Grid Axis")
        mesh.from_pydata(verts, edges, faces)
        obj = object_data_add(context, mesh, operator=self)
        tag = str(i+1).zfill(2)
        obj.name = 'IfcGridAxis/' + tag
        default_collection.objects.unlink(obj)
        axes_collection.objects.link(obj)
        attribute = obj.BIMObjectProperties.attributes.add()
        attribute.name = 'AxisTag'
        attribute.string_value = tag



class BIM_OT_add_object(Operator, AddObjectHelper):
    bl_idname = "mesh.add_grid"
    bl_label = "Grid"
    bl_options = {'REGISTER', 'UNDO'}

    u_spacing: FloatProperty(name='U Spacing', default=10)
    total_u: IntProperty(name='Number of U Grids', default=3)
    v_spacing: FloatProperty(name='V Spacing', default=10)
    total_v: IntProperty(name='Number of V Grids', default=3)

    def execute(self, context):
        add_object(self, context)
        return {'FINISHED'}


def add_object_button(self, context):
    self.layout.operator(
        BIM_OT_add_object.bl_idname,
        icon='PLUGIN')
