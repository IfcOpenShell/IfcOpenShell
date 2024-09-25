# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import blf
import gpu
import bmesh
import ifcopenshell
import bonsai.tool as tool
from math import radians
from bpy.types import SpaceView3D
from mathutils import Vector, Matrix
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import location_3d_to_region_2d
from bonsai.bim.module.georeference.data import GeoreferenceData


class GeoreferenceDecorator:
    is_installed = False
    handlers = []

    @classmethod
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_text, (context,), "WINDOW", "POST_PIXEL"))
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_geometry, (context,), "WINDOW", "POST_VIEW"))
        cls.is_installed = True

    @classmethod
    def uninstall(cls):
        for handler in cls.handlers:
            try:
                SpaceView3D.draw_handler_remove(handler, "WINDOW")
            except ValueError:
                pass
        cls.is_installed = False

    def draw_batch(self, shader_type, content_pos, color, indices=None):
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

    def draw_text(self, context):
        if not GeoreferenceData.is_loaded:
            GeoreferenceData.load()

        self.calculate_angles(context)
        props = context.scene.BIMGeoreferenceProperties
        e, n, h = [round(float(o), 7) for o in props.model_origin.split(",")]
        if (operation := GeoreferenceData.data["coordinate_operation"]) and (scale := operation.get("Scale", None)):
            e *= scale
            n *= scale
            h *= scale

        self.addon_prefs = tool.Blender.get_addon_preferences()

        self.font_id = 0
        blf.size(self.font_id, 12)
        color = self.addon_prefs.decorations_colour
        blf.color(self.font_id, *color)
        blf.enable(self.font_id, blf.SHADOW)
        blf.shadow(self.font_id, 6, 0, 0, 0, 1)

        if props.has_blender_offset:
            text = "Blender Origin"
            text += f"\nBlender Coordinates ({GeoreferenceData.data['local_unit_symbol']}) X: 0, Y: 0, Z: 0"
        else:
            text = "IFC Local Origin"
        text += f"\nLocal Coordinates ({GeoreferenceData.data['local_unit_symbol']}) X: {props.blender_offset_x}, Y: {props.blender_offset_y}, Z: {props.blender_offset_z}"
        if GeoreferenceData.data["projected_crs"]:
            text += f"\nMap Coordinates ({GeoreferenceData.data['map_unit_symbol']}) E: {e}, N: {n}, H: {h}"
        self.draw_text_at_position(context, text, Vector((0, -0.1, 0)))

        angle = Matrix.Rotation(radians(self.pn_angle), 4, "Z")
        p = angle @ Vector((0, 1.55, 0))
        self.draw_text_at_position(context, "Project North", p)

        if not tool.Cad.is_x(self.pn_angle, 0):
            arc_start = Vector((0, 1.05, 0))
            angle_half = Matrix.Rotation(radians(self.pn_angle / 2), 4, "Z")
            arc_mid = angle_half @ arc_start
            self.draw_text_at_position(context, f"{self.pn_angle}deg", arc_mid)

        if GeoreferenceData.data["coordinate_operation"]:
            angle = Matrix.Rotation(radians(self.gn_angle), 4, "Z")
            grid_north_p = angle @ Vector((0, 1.05, 0))
            self.draw_text_at_position(context, "Grid North", grid_north_p)

            arc_start = Vector((0, 0.55, 0))
            angle_half = Matrix.Rotation(radians(self.gn_angle / 2), 4, "Z")
            arc_mid = angle_half @ arc_start
            self.draw_text_at_position(context, f"{self.gn_angle}deg", arc_mid)

        if GeoreferenceData.data["true_north"]:
            angle = Matrix.Rotation(radians(self.tn_angle), 4, "Z")
            grid_north_p = angle @ Vector((0, 0.8, 0))
            self.draw_text_at_position(context, "True North", grid_north_p)

            arc_start = Vector((0, 0.3, 0))
            angle_half = Matrix.Rotation(radians(self.tn_angle / 2), 4, "Z")
            arc_mid = angle_half @ arc_start
            self.draw_text_at_position(context, f"{self.tn_angle}deg", arc_mid)

        if (wcs := GeoreferenceData.data["world_coordinate_system"]) and wcs["has_transformation"]:
            text = "WCS"
            if props.has_blender_offset:
                text += f"\nBlender Coordinates ({GeoreferenceData.data['local_unit_symbol']}) X: {wcs['blender_x']}, Y: {wcs['blender_y']}, Z: {wcs['blender_z']}"
            text += f"\nLocal Coordinates ({GeoreferenceData.data['local_unit_symbol']}) X: {wcs['x']}, Y: {wcs['y']}, Z: {wcs['z']}"
            if operation := GeoreferenceData.data["coordinate_operation"]:
                e = operation.get("Eastings")
                n = operation.get("Northings")
                h = operation.get("OrthogonalHeight")
                text += f"\nMap Coordinates ({GeoreferenceData.data['map_unit_symbol']}) E: {e}, N: {n}, H: {h}"

            if wcs["blender_location"].length < 1000:
                position = wcs["blender_location"].copy()
            else:
                position = wcs["blender_location"].normalized() * 3
                text += "\n(Warning: Actual XYZ Not Shown)"
            position -= Vector((0, 0.1, 0))

            self.draw_text_at_position(context, text, position)

        if props.has_blender_offset:
            text = "IFC Local Origin"
            x = GeoreferenceData.data["local_origin"]["x"]
            y = GeoreferenceData.data["local_origin"]["y"]
            z = GeoreferenceData.data["local_origin"]["z"]
            location = GeoreferenceData.data["local_origin"]["location"]
            text += f"\nBlender Coordinates ({GeoreferenceData.data['local_unit_symbol']}) X: {x}, Y: {y}, Z: {z}"
            text += f"\nLocal Coordinates ({GeoreferenceData.data['local_unit_symbol']}) X: 0, Y: 0, Z: 0"
            if GeoreferenceData.data["projected_crs"]:
                e, n, h = GeoreferenceData.data["local_origin"]["enh"]
                text += f"\nMap Coordinates ({GeoreferenceData.data['map_unit_symbol']}) E: {e}, N: {n}, H: {h}"
            if location.length > 1000:
                location = location.normalized() * 3
                text += "\n(Warning: Actual XYZ Not Shown)"
            self.draw_text_at_position(context, text, location)
        blf.disable(self.font_id, blf.SHADOW)

    def draw_text_at_position(self, context, text, position):
        coords_2d = location_3d_to_region_2d(context.region, context.region_data, position)
        if not coords_2d:
            return
        for i, line in enumerate(text.split("\n")):
            w, h = blf.dimensions(self.font_id, line)
            co = coords_2d.copy()
            co -= Vector((w * 0.5, 15 * i))
            blf.position(self.font_id, co[0], co[1], 0)
            blf.draw(self.font_id, line)

    def draw_geometry(self, context):
        if not GeoreferenceData.is_loaded:
            GeoreferenceData.load()

        self.calculate_angles(context)

        self.addon_prefs = tool.Blender.get_addon_preferences()
        decorator_color = self.addon_prefs.decorations_colour
        decorator_color_special = self.addon_prefs.decorator_color_special
        decorator_color_selected = self.addon_prefs.decorator_color_selected
        decorator_color_error = self.addon_prefs.decorator_color_error

        gpu.state.blend_set("ALPHA")

        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()  # required to be able to change uniforms of the shader
        # POLYLINE_UNIFORM_COLOR specific uniforms
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))

        # general shader
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        # A crosshair to emphasize the coordinate system, in case they have grids turned off
        self.line_shader.uniform_float("lineWidth", 2.0)
        verts = [Vector((0, -1.25, 0)), Vector((0, 1.25, 0)), Vector((-1.25, 0, 0)), Vector((1.25, 0, 0))]
        edges = [[0, 1], [2, 3]]
        self.draw_batch("LINES", verts, decorator_color, edges)
        self.line_shader.uniform_float("lineWidth", 5.0)

        # A point at the origin to emphasize its significance as a Blender origin
        points = [Vector((0, 0, 0))]
        gpu.state.point_size_set(10)
        self.draw_batch("POINTS", points, decorator_color_selected)

        # A project north arrow always exists
        angle = Matrix.Rotation(radians(self.pn_angle), 4, "Z")
        points = [angle @ Vector((0, 1.5, 0))]
        gpu.state.point_size_set(4)
        self.draw_batch("POINTS", points, decorator_color_selected)

        verts = [Vector((0, 0, 0)), angle @ Vector((0, 1.5, 0))]
        edges = [[0, 1]]
        self.draw_batch("LINES", verts, decorator_color_selected, edges)

        verts = [Vector((0, 1.5, 0)), Vector((-0.15, 1.35, 0)), Vector((0.15, 1.35, 0))]
        edges = [[0, 1], [0, 2]]
        verts = [angle @ v for v in verts]
        self.draw_batch("LINES", verts, decorator_color_selected, edges)

        self.line_shader.uniform_float("lineWidth", 2.0)

        # If we have a Blender offset, project north may not be up
        if not tool.Cad.is_x(self.pn_angle, 0):
            arc_start = Vector((0, 1, 0))
            arc_end = angle @ arc_start
            angle_half = Matrix.Rotation(radians(self.pn_angle / 2), 4, "Z")
            arc_mid = angle_half @ arc_start
            arc_segments = tool.Cad.create_arc_segments(
                pts=[arc_start, arc_mid, arc_end], num_verts=12, make_edges=True
            )
            verts, edges = arc_segments
            self.draw_batch("LINES", verts, decorator_color_selected, edges)

        if GeoreferenceData.data["coordinate_operation"]:
            points = [Vector((0, 0, 0)), Vector((0, 1, 0))]
            angle = Matrix.Rotation(radians(self.gn_angle), 4, "Z")
            points = [angle @ v for v in points]
            self.draw_batch("POINTS", points, decorator_color_special)

            verts = [Vector((0, 0, 0)), Vector((0, 1, 0))]
            edges = [[0, 1]]
            angle = Matrix.Rotation(radians(self.gn_angle), 4, "Z")
            verts = [angle @ v for v in verts]
            self.draw_batch("LINES", verts, decorator_color_special, edges)

            verts = [Vector((0, 1, 0)), Vector((-0.15, 0.85, 0)), Vector((0.15, 0.85, 0))]
            edges = [[0, 1], [0, 2]]
            verts = [angle @ v for v in verts]
            self.line_shader.uniform_float("lineWidth", 5.0)
            self.draw_batch("LINES", verts, decorator_color_special, edges)
            self.line_shader.uniform_float("lineWidth", 2.0)

            arc_start = Vector((0, 0.5, 0))
            arc_end = angle @ arc_start
            angle_half = Matrix.Rotation(radians(self.gn_angle / 2), 4, "Z")
            arc_mid = angle_half @ arc_start
            arc_segments = tool.Cad.create_arc_segments(
                pts=[arc_start, arc_mid, arc_end], num_verts=12, make_edges=True
            )
            verts, edges = arc_segments
            self.draw_batch("LINES", verts, decorator_color_special, edges)

        if GeoreferenceData.data["true_north"]:
            points = [Vector((0, 0, 0)), Vector((0, 0.75, 0))]
            angle = Matrix.Rotation(radians(self.tn_angle), 4, "Z")
            points = [angle @ v for v in points]
            self.draw_batch("POINTS", points, decorator_color_special)

            verts = [Vector((0, 0, 0)), Vector((0, 0.75, 0))]
            edges = [[0, 1]]
            angle = Matrix.Rotation(radians(self.tn_angle), 4, "Z")
            verts = [angle @ v for v in verts]
            self.draw_batch("LINES", verts, decorator_color_special, edges)

            verts = [Vector((0, 0.75, 0)), Vector((-0.15, 0.6, 0)), Vector((0.15, 0.6, 0))]
            edges = [[0, 1], [0, 2]]
            verts = [angle @ v for v in verts]
            self.line_shader.uniform_float("lineWidth", 5.0)
            self.draw_batch("LINES", verts, decorator_color_special, edges)
            self.line_shader.uniform_float("lineWidth", 2.0)

            arc_start = Vector((0, 0.25, 0))
            arc_end = angle @ arc_start
            angle_half = Matrix.Rotation(radians(self.tn_angle / 2), 4, "Z")
            arc_mid = angle_half @ arc_start
            arc_segments = tool.Cad.create_arc_segments(
                pts=[arc_start, arc_mid, arc_end], num_verts=12, make_edges=True
            )
            verts, edges = arc_segments
            self.draw_batch("LINES", verts, decorator_color_special, edges)

        if (wcs := GeoreferenceData.data["world_coordinate_system"]) and wcs["has_transformation"]:
            if wcs["blender_location"].length < 1000:
                verts = [Vector((0, 0, 0)), wcs["blender_location"]]
                edges = [[0, 1]]
                self.draw_batch("LINES", verts, decorator_color_special, edges)
                self.draw_batch("POINTS", verts[1:], decorator_color_special)
            else:
                location = wcs["blender_location"].normalized()
                edges = [[0, 1]]
                verts = [Vector((0, 0, 0)), location * 3]
                self.draw_batch("LINES", verts, decorator_color_special, edges)
                self.draw_dashed_line(location * 3, location * 6, decorator_color_error)

        props = context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            location = GeoreferenceData.data["local_origin"]["location"]
            if location.length < 1000:
                verts = [Vector((0, 0, 0)), location]
                edges = [[0, 1]]
                self.draw_batch("LINES", verts, decorator_color_special, edges)
                self.draw_batch("POINTS", verts[1:], decorator_color_special)
            else:
                location = location.normalized()
                edges = [[0, 1]]
                verts = [Vector((0, 0, 0)), location * 3]
                self.draw_batch("LINES", verts, decorator_color_special, edges)
                self.draw_dashed_line(location * 3, location * 6, decorator_color_error)

    def draw_dashed_line(self, start, end, colour):
        direction = (end - start).normalized()
        distance = (end - start).length
        current_distance = Vector((0, 0, 0))
        gap = 0.05 * direction
        dash = 0.1 * direction
        points = [start]
        while current_distance.length < distance:
            points.append(start + current_distance + dash)
            points.append(start + current_distance + dash + gap)
            current_distance += gap + dash
        points.pop()

        edges = [[i, i + 1] for i in range(0, len(points), 2)]
        verts = points
        self.draw_batch("LINES", verts, colour, edges)

    def calculate_angles(self, context):
        self.pn_angle = 0.0
        self.gn_angle = float(GeoreferenceData.data["map_derived_angle"] or 0)
        self.tn_angle = float(GeoreferenceData.data["true_derived_angle"] or 0)

        props = context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset:
            blender_angle = ifcopenshell.util.geolocation.xaxis2angle(
                float(props.blender_x_axis_abscissa), float(props.blender_x_axis_ordinate)
            )
            self.pn_angle += blender_angle
            self.gn_angle += blender_angle
            self.tn_angle += blender_angle
            self.pn_angle = tool.Cad.normalise_angle(self.pn_angle)
            self.gn_angle = tool.Cad.normalise_angle(self.gn_angle)
            self.tn_angle = tool.Cad.normalise_angle(self.tn_angle)
