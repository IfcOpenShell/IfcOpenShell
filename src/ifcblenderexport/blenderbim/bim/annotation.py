import bpy
import os
from mathutils import Vector

class Annotator:

    @staticmethod
    def get_svg_text_size(size):
        sizes = {
            '1.8': '2.97',
            '2.5': '4.13',
            '3.5': '5.78',
            '5.0': '8.25',
            '7.0': '11.55',
        }
        return float(sizes[str(size)])

    @staticmethod
    def add_text(related_element=None):
        curve = bpy.data.curves.new(type='FONT', name='Plan/Annotation/PLAN_VIEW/Text')
        curve.body = 'TEXT'
        obj = bpy.data.objects.new('IfcAnnotation/Text', curve)
        obj.matrix_world = bpy.context.scene.camera.matrix_world
        if related_element is None:
            location, co2 = Annotator.get_placeholder_coords()
        else:
            obj.data.BIMTextProperties.related_element = related_element
            location = related_element.location
        obj.location = location
        obj.hide_render = True
        font = bpy.data.fonts.get('OpenGost TypeB TT')
        if not font:
            font = bpy.data.fonts.load(os.path.join(
                bpy.context.scene.BIMProperties.data_dir, 'fonts', 'OpenGost Type B TT.ttf'))
            font.name = 'OpenGost Type B TT'
        obj.data.font = font
        obj.data.BIMTextProperties.font_size = '2.5'
        collection = bpy.context.scene.camera.users_collection[0]
        collection.objects.link(obj)
        Annotator.resize_text(obj)
        return obj

    @staticmethod
    def resize_text(text_obj):
        camera = None
        for obj in text_obj.users_collection[0].objects:
            if isinstance(obj.data, bpy.types.Camera):
                camera = obj
                break
        if not camera:
            return
        # This is a magic number for OpenGost
        font_size = 1.6 / 1000
        font_size *= float(text_obj.data.BIMTextProperties.font_size)
        font_size *= float(camera.data.BIMCameraProperties.diagram_scale.split(':')[1])
        text_obj.data.size = font_size

    @staticmethod
    def add_line_to_annotation(obj):
        co1, co2 = Annotator.get_placeholder_coords()
        if isinstance(obj.data, bpy.types.Mesh):
            obj.data.vertices.add(2)
            obj.data.vertices[-2].co = co1
            obj.data.vertices[-1].co = co2
            obj.data.edges.add(1)
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
            data = bpy.data.meshes.new('Plan/Annotation/PLAN_VIEW/' + name)
        elif data_type == 'curve':
            data = bpy.data.curves.new('Plan/Annotation/PLAN_VIEW/' + name, type='CURVE')
            data.dimensions = '3D'
            data.resolution_u = 2
        obj = bpy.data.objects.new('IfcAnnotation/' + name, data)
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
