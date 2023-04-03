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
    def add_text(related_element=None):
        curve = bpy.data.curves.new(type="FONT", name="Text")
        curve.body = "TEXT"
        obj = bpy.data.objects.new("Text", curve)
        obj.matrix_world = bpy.context.scene.camera.matrix_world
        if related_element is None:
            location, _, _, _ = Annotator.get_placeholder_coords(bpy.context)
        else:
            obj.data.BIMAssignedProductProperties.related_element = related_element
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
        # default order = bot left, top left, bot right, top right
        # therefore we redefine the order
        face_verts = [0, 2, 3, 1]

        verts_world_space = Annotator.get_placeholder_coords()
        verts_local = [obj.matrix_world.inverted() @ v for v in verts_world_space]
        bm = tool.Blender.get_bmesh_for_mesh(obj.data, clean=True)
        new_verts = [bm.verts.new(v) for v in verts_local]

        bm.faces.new([new_verts[i] for i in face_verts])
        tool.Blender.apply_bmesh(obj.data, bm, obj)
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
                if element and element.ObjectType == object_type and obj.type == object_type.upper():
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
