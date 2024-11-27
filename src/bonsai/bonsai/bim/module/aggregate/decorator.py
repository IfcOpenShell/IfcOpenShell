# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2024 Bruno Perdigão <contact@brunopo.com>
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

import blf
import bpy
import gpu
import ifcopenshell
import bonsai.tool as tool
from bpy.types import SpaceView3D
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from mathutils import Vector


def transparent_color(color, alpha=0.1):
    color = [i for i in color]
    color[3] = alpha
    return color

class AggregateDecorator:
    is_installed = False
    handlers = []

    @classmethod
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_aggregate, (context,), "WINDOW", "POST_VIEW"))
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.lock_objects, (context,), "WINDOW", "POST_VIEW"))
        cls.is_installed = True

    @classmethod
    def uninstall(cls):
        for handler in cls.handlers:
            try:
                SpaceView3D.draw_handler_remove(handler, "WINDOW")
            except ValueError:
                pass
        cls.is_installed = False


    def dotted_line_shader(self):
        vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")
        vert_out.smooth("FLOAT", "v_ArcLength")

        shader_info = gpu.types.GPUShaderCreateInfo()
        shader_info.push_constant("MAT4", "u_ViewProjectionMatrix")
        shader_info.push_constant("FLOAT", "u_Scale")
        shader_info.vertex_in(0, "VEC3", "position")
        shader_info.vertex_in(1, "FLOAT", "arcLength")
        shader_info.vertex_out(vert_out)
        shader_info.fragment_out(0, "VEC4", "FragColor")
        shader_info.push_constant("VEC4", "color")

        shader_info.vertex_source(
            "void main()"
            "{"
            "  v_ArcLength = arcLength;"
            "  gl_Position = u_ViewProjectionMatrix * vec4(position, 1.0f);"
            "}"
        )

        shader_info.fragment_source(
            "void main()" "{" "  if (step(sin(v_ArcLength * u_Scale), 0.4) == 1) discard;" "  FragColor = color;" "}"
        )

        shader = gpu.shader.create_from_info(shader_info)
        del vert_out
        del shader_info
        return shader

    def draw_custom_batch(self, coords, color):
        shader = self.dotted_line_shader()

        arc_lengths = [0]
        for a, b in zip(coords[:-1], coords[1:]):
            arc_lengths.append(arc_lengths[-1] + (a - b).length)

        batch = batch_for_shader(
            shader,
            "LINE_STRIP",
            {"position": coords, "arcLength": arc_lengths},
        )

        matrix = bpy.context.region_data.perspective_matrix
        shader.uniform_float("color", color)
        shader.uniform_float("u_ViewProjectionMatrix", matrix)
        shader.uniform_float("u_Scale", 25)
        batch.draw(shader)

    def draw_batch(self, shader_type, content_pos, color, indices=None):
        shader = self.line_shader if shader_type == "LINES" else self.shader
        batch = batch_for_shader(shader, shader_type, {"pos": content_pos}, indices=indices)
        shader.uniform_float("color", color)
        batch.draw(shader)

    def create_bounding_box(self, objs):
        # Initialize the bounding box coordinates
        min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
        max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

        # Iterate over the selected objects
        for obj in objs:
            # Get the object's bounding box coordinates
            bbox_world = [obj.matrix_world @ Vector(b) for b in obj.bound_box]
            obj_min = []
            obj_min.append(min([b[0] for b in bbox_world]))
            obj_min.append(min([b[1] for b in bbox_world]))
            obj_min.append(min([b[2] for b in bbox_world]))
            obj_max = []
            obj_max.append(max([b[0] for b in bbox_world]))
            obj_max.append(max([b[1] for b in bbox_world]))
            obj_max.append(max([b[2] for b in bbox_world]))

            # Update the overall bounding box coordinates
            min_x = min(min_x, min(obj_min[0], obj_max[0]))
            min_y = min(min_y, min(obj_min[1], obj_max[1]))
            min_z = min(min_z, min(obj_min[2], obj_max[2]))
            max_x = max(max_x, max(obj_min[0], obj_max[0]))
            max_y = max(max_y, max(obj_min[1], obj_max[1]))
            max_z = max(max_z, max(obj_min[2], obj_max[2]))

        indices = [
            (min_x, min_y, min_z),
            (max_x, min_y, min_z),
            (max_x, max_y, min_z),
            (min_x, max_y, min_z),
            (min_x, min_y, max_z),
            (max_x, min_y, max_z),
            (max_x, max_y, max_z),
            (min_x, max_y, max_z)
        ]

        edges = [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7)
        ]

        return indices, edges

    def draw_aggregate(self, context):
        if context.scene.BIMAggregateProperties.in_aggregate_mode:
            return
        self.addon_prefs = tool.Blender.get_addon_preferences()
        decorator_color_special = self.addon_prefs.decorator_color_special
        decorator_color_selected = self.addon_prefs.decorator_color_selected
        decorator_color_error = self.addon_prefs.decorator_color_error
        decorator_color_unselected = self.addon_prefs.decorator_color_unselected
        decorator_color_background = self.addon_prefs.decorator_color_background
        theme = context.preferences.themes.items()[0][1]
        selected_object_color = (*theme.view_3d.object_active, 1)

        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()
        # POLYLINE_UNIFORM_COLOR specific uniforms
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        aggregates = []
        if not (selected_objects := context.selected_objects):
            return
        for obj in selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not element.is_a("IfcElement"):
                return

            parts = ifcopenshell.util.element.get_parts(element)
            if parts:
                aggregates.append(obj)
                continue

            aggregate = ifcopenshell.util.element.get_aggregate(element)
            if aggregate:
                aggregates.append(tool.Ifc.get_object(aggregate))

        aggregates = set(aggregates)
        for aggregate in aggregates:
            self.line_shader.uniform_float("lineWidth", 1.0)
            color = decorator_color_unselected
            if aggregate in selected_objects:
                color = selected_object_color
            size = aggregate.empty_display_size
            location = aggregate.location
            line_x = (location - Vector((size, 0.0, 0.0)), location + Vector((size, 0.0, 0.0)))
            self.draw_batch("LINES", line_x, color, [(0, 1)])
            line_y = (location - Vector((0.0, size, 0.0)), location + Vector((0.0, size, 0.0)))
            self.draw_batch("LINES", line_y, color, [(0, 1)])
            line_z = (location - Vector((0.0, 0.0, size)), location + Vector((0.0, 0.0, size)))
            self.draw_batch("LINES", line_z, color, [(0, 1)])
            if context.scene.BIMAggregateProperties.in_aggregate_mode:
                return
            parts = ifcopenshell.util.element.get_parts(tool.Ifc.get_entity(aggregate))
            parts_objs = [tool.Ifc.get_object(p) for p in parts]

            for part_obj in parts_objs:
                line = (part_obj.matrix_world.translation, location)
                self.draw_custom_batch(line, decorator_color_unselected)

            indices, edges = self.create_bounding_box(parts_objs)
            self.line_shader.uniform_float("lineWidth", 0.5)
            self.draw_batch("LINES", indices, color, edges)

class AggregateModeDecorator:
    is_installed = False
    handlers = []

    @classmethod
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall()
        handler = cls()
        cls.handlers.append(
            SpaceView3D.draw_handler_add(handler.draw_aggregate_name, (context,), "WINDOW", "POST_PIXEL")
        )
        cls.handlers.append(
            SpaceView3D.draw_handler_add(handler.draw_aggregate_empty, (context,), "WINDOW", "POST_VIEW")
        )
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


    def draw_aggregate_name(self, context):
        region = context.region
        rv3d = region.data
        props = context.scene.BIMAggregateProperties
        aggregate_obj = props.editing_aggregate
        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.font_id = 0
        font_size = tool.Blender.scale_font_size(12)
        blf.size(self.font_id, font_size)
        blf.enable(self.font_id, blf.SHADOW)
        blf.shadow(self.font_id, 6, 0, 0, 0, 1)
        color = self.addon_prefs.decorator_color_selected
        if aggregate_obj in context.selected_objects:
            color = self.addon_prefs.decorator_color_selected
        blf.color(self.font_id, *color)
        text = aggregate_obj.name
        text_coords = view3d_utils.location_3d_to_region_2d(region, rv3d, aggregate_obj.location)
        text_length = blf.dimensions(self.font_id, text)
        text_coords[0] -= (text_length[0] / 2)
        text_coords[1] -= 20
        blf.position(self.font_id, text_coords[0], text_coords[1], 0)

        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        blf.draw(self.font_id, text)

    def draw_aggregate_empty(self, context):
        props = context.scene.BIMAggregateProperties
        aggregate_obj = props.editing_aggregate
        self.addon_prefs = tool.Blender.get_addon_preferences()
        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.line_shader.uniform_float("lineWidth", 2.0)
        color = self.addon_prefs.decorator_color_selected
        theme = context.preferences.themes.items()[0][1]
        selected_object_color = (*theme.view_3d.object_active, 1)
        size = aggregate_obj.empty_display_size
        location = aggregate_obj.location
        line_x = (location - Vector((size, 0.0, 0.0)), location + Vector((size, 0.0, 0.0)))
        self.draw_batch("LINES", line_x, color, [(0, 1)])
        line_y = (location - Vector((0.0, size, 0.0)), location + Vector((0.0, size, 0.0)))
        self.draw_batch("LINES", line_y, color, [(0, 1)])
        line_z = (location - Vector((0.0, 0.0, size)), location + Vector((0.0, 0.0, size)))
        self.draw_batch("LINES", line_z, color, [(0, 1)])
        parts = ifcopenshell.util.element.get_parts(tool.Ifc.get_entity(aggregate_obj))
        if parts:
            for part in parts:
                if part.is_a("IfcElementAssembly"):
                    part_obj = tool.Ifc.get_object(part)
                    self.line_shader.uniform_float("lineWidth", 1.0)
                    size = part_obj.empty_display_size
                    location = part_obj.location
                    color = self.addon_prefs.decorator_color_unselected
                    if part_obj in context.selected_objects:
                        color = selected_object_color
                    line_x = (location - Vector((size, 0.0, 0.0)), location + Vector((size, 0.0, 0.0)))
                    self.draw_batch("LINES", line_x, color, [(0, 1)])
                    line_y = (location - Vector((0.0, size, 0.0)), location + Vector((0.0, size, 0.0)))
                    self.draw_batch("LINES", line_y, color, [(0, 1)])
                    line_z = (location - Vector((0.0, 0.0, size)), location + Vector((0.0, 0.0, size)))
                    self.draw_batch("LINES", line_z, color, [(0, 1)])
                    parts = ifcopenshell.util.element.get_parts(tool.Ifc.get_entity(aggregate_obj))
        
