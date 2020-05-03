import bpy
from mathutils import Vector

class Annotator:

    @staticmethod
    def add_text():
        curve = bpy.data.curves.new(type='FONT', name='Text')
        curve.body = 'TEXT'
        obj = bpy.data.objects.new('Text', curve)
        obj.matrix_world = bpy.context.scene.camera.matrix_world
        co1, co2 = Annotator.get_placeholder_coords()
        obj.location = co1
        obj.hide_render = True
        bpy.context.scene.collection.objects.link(obj)
        return obj

    @staticmethod
    def add_line_to_annotation(obj):
        co1, co2 = Annotator.get_placeholder_coords()
        if isinstance(obj.data, bpy.types.Mesh):
            obj.data.vertices.add(2)
            obj.data.vertices[-2].co = co1
            obj.data.vertices[-1].co = co2
            obj.data.edges.add(2)
            obj.data.edges[-1].vertices = (obj.data.vertices[-2].index, obj.data.vertices[-1].index)
        if isinstance(obj.data, bpy.types.Curve):
            polyline = obj.data.splines.new('POLY')
            polyline.points.add(1)
            polyline.points[-2].co = list(co1) + [1]
            polyline.points[-1].co = list(co2) + [1]
        return obj

    @staticmethod
    def get_annotation_obj(name, data_type):
        collection = bpy.context.scene.camera.users_collection[0]
        for obj in collection.objects:
            if name in obj.name:
                return obj
        if data_type == 'mesh':
            data = bpy.data.meshes.new(name)
        elif data_type == 'curve':
            data = bpy.data.curves.new(name, type='CURVE')
            data.dimensions = '3D'
            data.resolution_u = 2
        obj = bpy.data.objects.new(name, data)
        collection.objects.link(obj)
        return obj

    @staticmethod
    def get_placeholder_coords():
        camera = bpy.context.scene.camera
        z_offset = camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        if bpy.context.scene.render.resolution_x > bpy.context.scene.render.resolution_y:
            y = camera.data.ortho_scale * (bpy.context.scene.render.resolution_y / bpy.context.scene.render.resolution_x) / 4
        else:
            y = camera.data.ortho_scale / 4
        y_offset = camera.matrix_world.to_quaternion() @ Vector((0, y, 0))
        return (camera.location + z_offset, camera.location + z_offset + y_offset)
