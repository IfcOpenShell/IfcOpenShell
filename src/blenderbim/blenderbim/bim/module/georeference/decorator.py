import math
import blf
import gpu
import bmesh
import blenderbim.tool as tool
from bpy.types import SpaceView3D
from mathutils import Vector, Matrix
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import location_3d_to_region_2d

class GeoVizDecorator():
    is_installed = False
    handlers = []
    end2 = Vector()
    @classmethod
    def install(cls, context):
        if cls.is_installed:
            cls.uninstall(context)
        handler = cls()
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_text, (context,), "WINDOW", "POST_PIXEL"))
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_arrows, (context,), "WINDOW", "POST_VIEW"))
        cls.is_installed = True

    @classmethod
    def uninstall(cls, context):
        while cls.handlers:
            handler = cls.handlers.pop()
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
        self.addon_prefs = context.preferences.addons["blenderbim"].preferences
        special_elements_color = self.addon_prefs.decorator_color_special
        
        # Coordinates
        font_id = 0
        blf.size(font_id, 15)
        blf.color(font_id, *special_elements_color)

        text_offset = 50  # Offset to the right of the arrow

        values = [
            f"E: {context.scene.BIMGeoreferenceProperties.coordinate_operation[0].string_value}",
            f"N: {context.scene.BIMGeoreferenceProperties.coordinate_operation[1].string_value}",
            f"H: {context.scene.BIMGeoreferenceProperties.coordinate_operation[2].string_value}",
        ]

        p = Vector((0, 1, 0))  # Position at the end of the first arrow

        coords_2d = location_3d_to_region_2d(context.region, context.region_data, p)

        if coords_2d:
            for i, value in enumerate(values):
                blf.position(font_id, coords_2d[0] + text_offset, coords_2d[1] -20 - i * 20, 0)
                blf.draw(font_id, value)
        
        
        pos1 = Vector((0,0,0))
        
        font_id = 0
        blf.size(font_id, 20)
        blf.color(font_id, *special_elements_color)

        coords_2d = location_3d_to_region_2d(context.region, context.region_data, pos1)

        if coords_2d:
            blf.position(font_id, coords_2d[0], coords_2d[1], 0)
            blf.draw(font_id, f"Angle: {bpy.context.scene.BIMGeoreferenceProperties.grid_north_angle}")


        #Project North Text
        pos2 = Vector((-0.1, 1, 0))
        
        font_id = 0
        blf.size(font_id, 10)
        blf.color(font_id, *special_elements_color)

        coords_2d = location_3d_to_region_2d(context.region, context.region_data, pos2)

        if coords_2d:
            blf.position(font_id, coords_2d[0], coords_2d[1], 0)
            blf.draw(font_id, f"PROJECT NORTH")

        
        #Grid North Text
        pos2 = self.end2
        
        font_id = 0
        blf.size(font_id, 10)
        blf.color(font_id, *special_elements_color)

        coords_2d = location_3d_to_region_2d(context.region, context.region_data, pos2)

        if coords_2d:
            blf.position(font_id, coords_2d[0], coords_2d[1], 0)
            blf.draw(font_id, f"GRID NORTH")


    def draw_arrows(self, context):
        self.addon_prefs = context.preferences.addons["blenderbim"].preferences
        special_elements_color = self.addon_prefs.decorator_color_special

        gpu.state.point_size_set(6)
        gpu.state.blend_set("ALPHA")

        self.line_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        self.line_shader.bind()
        self.line_shader.uniform_float("viewportSize", (context.region.width, context.region.height))
        self.line_shader.uniform_float("lineWidth", 2.0)

        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        # Main line of the first arrow
        start = Vector((0, 0, 0))
        end = Vector((0, 1, 0))
        arrow_vertices = [start, end]

        # Arrowhead of the first arrow
        arrow_size = 0.2
        direction = (end - start).normalized()
        perpendicular = direction.cross(Vector((0, 0, 1)))

        arrowhead1 = end - direction * arrow_size + perpendicular * arrow_size * 0.5
        arrowhead2 = end - direction * arrow_size - perpendicular * arrow_size * 0.5

        arrow_vertices.extend([end, arrowhead1, end, arrowhead2])
        arrow_indices = [(0, 1), (2, 3), (4, 5)]

        self.draw_batch("LINES", arrow_vertices, special_elements_color, arrow_indices)

        # Second arrow rotated counterclockwise
        value = int(context.scene.BIMGeoreferenceProperties.grid_north_angle)
        angle = math.radians(value)
        rotation_matrix = Matrix.Rotation(-angle, 4, 'Z')

        start2 = Vector((0, 0, 0))
        self.end2 = Vector((0, 1, 0)) @ rotation_matrix
        arrow_vertices2 = [start2, self.end2]

        direction2 = (self.end2 - start2).normalized()
        perpendicular2 = direction2.cross(Vector((0, 0, 1)))

        arrowhead3 = self.end2 - direction2 * arrow_size + perpendicular2 * arrow_size * 0.5
        arrowhead4 = self.end2 - direction2 * arrow_size - perpendicular2 * arrow_size * 0.5

        arrow_vertices2.extend([self.end2, arrowhead3, self.end2, arrowhead4])
        arrow_indices2 = [(0, 1), (2, 3), (4, 5)]

        self.draw_batch("LINES", arrow_vertices2, special_elements_color, arrow_indices2)

        # Draw the angle arc
        self.draw_arc(context, start, math.pi / 2, math.pi / 2 - angle, num_segments=32, radius=0.2)
        
        
    def draw_arc(self, context, center, start_angle, end_angle, num_segments=32, radius=0.5):
        arc_vertices = []
        arc_indices = []

        for i in range(num_segments + 1):
            t = i / num_segments
            current_angle = start_angle + t * (start_angle - end_angle)
            point = Vector((math.cos(current_angle), math.sin(current_angle), 0)) * radius + center
            arc_vertices.append(point)
            if i > 0:
                arc_indices.append((i - 1, i))

        self.draw_batch("LINES", arc_vertices, self.addon_prefs.decorator_color_special, arc_indices)

