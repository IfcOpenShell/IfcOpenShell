# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Maxim Vasilyev <qwiglydee@gmail.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import os
import blenderbim.tool as tool
from mathutils import Vector


class Annotator:
    @staticmethod
    def get_svg_text_size(size):
        sizes = {
            "1.8": "2.97",
            "2.5": "4.13",
            "3.5": "5.78",
            "5.0": "8.25",
            "7.0": "11.55",
        }
        return float(sizes[str(size)])

    @staticmethod
    def add_text(related_element=None):
        curve = bpy.data.curves.new(type="FONT", name="Text")
        curve.body = "TEXT"
        obj = bpy.data.objects.new("Text", curve)
        obj.matrix_world = bpy.context.scene.camera.matrix_world
        if related_element is None:
            location, _, _, _ = Annotator.get_placeholder_coords(bpy.context)
        else:
            obj.data.BIMTextProperties.related_element = related_element
            location = related_element.location
        obj.location = location
        obj.hide_render = True
        font = bpy.data.fonts.get("OpenGost TypeB TT")
        if not font:
            font = bpy.data.fonts.load(
                os.path.join(bpy.context.scene.BIMProperties.data_dir, "fonts", "OpenGost Type B TT.ttf")
            )
            font.name = "OpenGost Type B TT"
        obj.data.font = font
        obj.data.BIMTextProperties.font_size = "2.5"
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

        if camera.data.BIMCameraProperties.diagram_scale == "CUSTOM":
            human_scale, fraction = camera.data.BIMCameraProperties.custom_diagram_scale.split("|")
        else:
            human_scale, fraction = camera.data.BIMCameraProperties.diagram_scale.split("|")
        numerator, denominator = fraction.split("/")
        font_size /= float(numerator) / float(denominator)

        text_obj.data.size = font_size

    @staticmethod
    def add_line_to_annotation(obj, co1=None, co2=None):
        if co1 is None:
            co1, co2, _, _ = Annotator.get_placeholder_coords()
        co1 = obj.matrix_world.inverted() @ co1
        co2 = obj.matrix_world.inverted() @ co2
        if isinstance(obj.data, bpy.types.Mesh):
            obj.data.vertices.add(2)
            obj.data.vertices[-2].co = co1
            obj.data.vertices[-1].co = co2
            obj.data.edges.add(1)
            obj.data.edges[-1].vertices = (obj.data.vertices[-2].index, obj.data.vertices[-1].index)
        if isinstance(obj.data, bpy.types.Curve):
            polyline = obj.data.splines.new("POLY")
            polyline.points.add(1)
            polyline.points[-2].co = list(co1) + [1]
            polyline.points[-1].co = list(co2) + [1]
        return obj

    @staticmethod
    def add_plane_to_annotation(obj):
        co1, co2, co3, co4 = Annotator.get_placeholder_coords()
        co1 = obj.matrix_world.inverted() @ co1  # bot left
        co2 = obj.matrix_world.inverted() @ co2  # top left
        co3 = obj.matrix_world.inverted() @ co3  # bot right
        co4 = obj.matrix_world.inverted() @ co4  # top right

        obj.data.vertices.add(4)
        v1 = obj.data.vertices[-4]
        v2 = obj.data.vertices[-3]
        v3 = obj.data.vertices[-2]
        v4 = obj.data.vertices[-1]
        v1.co = co4
        v2.co = co2
        v3.co = co1
        v4.co = co3

        obj.data.edges.add(4)
        e1 = obj.data.edges[-4]
        e2 = obj.data.edges[-3]
        e3 = obj.data.edges[-2]
        e4 = obj.data.edges[-1]
        e1.vertices = (v1.index, v2.index)
        e2.vertices = (v2.index, v3.index)
        e3.vertices = (v3.index, v4.index)
        e4.vertices = (v4.index, v1.index)

        obj.data.loops.add(4)
        l1 = obj.data.loops[-4]
        l2 = obj.data.loops[-3]
        l3 = obj.data.loops[-2]
        l4 = obj.data.loops[-1]
        l1.vertex_index = v1.index
        l1.edge_index = e1.index
        l2.vertex_index = v2.index
        l2.edge_index = e2.index
        l3.vertex_index = v3.index
        l3.edge_index = e3.index
        l4.vertex_index = v4.index
        l4.edge_index = e4.index

        obj.data.polygons.add(1)
        p1 = obj.data.polygons[-1]
        p1.vertices = (v1.index, v2.index, v3.index, v4.index)
        p1.loop_start = l1.index
        p1.loop_total = 4
        return obj

    @staticmethod
    def get_annotation_obj(drawing, object_type, data_type):
        camera = tool.Ifc.get_object(drawing)
        co1, _, _, _ = Annotator.get_placeholder_coords(camera)
        matrix_world = camera.matrix_world.copy()
        matrix_world[0][3] = co1.x
        matrix_world[1][3] = co1.y
        matrix_world[2][3] = co1.z
        collection = camera.users_collection[0]
        if object_type == "TEXT":
            obj = bpy.data.objects.new(object_type, None)
            obj.matrix_world = matrix_world
            collection.objects.link(obj)
            return obj
        elif object_type in ("TEXT_LEADER", "SECTION_LEVEL"):
            data = bpy.data.curves.new(object_type, type="CURVE")
            data.dimensions = "3D"
            data.resolution_u = 2
            obj = bpy.data.objects.new(object_type, data)
            obj.matrix_world = matrix_world
            collection.objects.link(obj)
            return obj
        if object_type != "ANGLE":
            for obj in collection.objects:
                element = tool.Ifc.get_entity(obj)
                if element and element.ObjectType == object_type:
                    return obj
        if data_type == "mesh":
            data = bpy.data.meshes.new(object_type)
        elif data_type == "curve":
            data = bpy.data.curves.new(object_type, type="CURVE")
            data.dimensions = "3D"
            data.resolution_u = 2
        obj = bpy.data.objects.new(object_type, data)
        obj.matrix_world = matrix_world
        collection.objects.link(obj)
        return obj

    @staticmethod
    def get_placeholder_coords(camera=None):
        if not camera:
            camera = bpy.context.scene.camera
        z_offset = camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        if bpy.context.scene.render.resolution_x > bpy.context.scene.render.resolution_y:
            y = (
                camera.data.ortho_scale
                * (bpy.context.scene.render.resolution_y / bpy.context.scene.render.resolution_x)
                / 4
            )
        else:
            y = camera.data.ortho_scale / 4
        y_offset = camera.matrix_world.to_quaternion() @ Vector((0, y, 0))
        x_offset = camera.matrix_world.to_quaternion() @ Vector((y / 2, 0, 0))
        return (
            camera.location + z_offset,
            camera.location + z_offset + y_offset,
            camera.location + z_offset + x_offset,
            camera.location + z_offset + x_offset + y_offset,
        )
