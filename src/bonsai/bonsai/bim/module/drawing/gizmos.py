# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Maxim Vasilyev <qwiglydee@gmail.com>
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
from bpy import types
from mathutils import Vector
from mathutils import geometry
from bpy_extras import view3d_utils
from bonsai.bim.module.drawing.shaders import DotsGizmoShader, ExtrusionGuidesShader
from ifcopenshell.util.unit import si_conversions


"""Gizmos under the hood

## Transforms:

source/blender/windowmanager/gizmo/WM_gizmo_types.h
matrix_basis -- "Transformation of this gizmo." = placement in scene
matrix_offset -- "Custom offset from origin." = local transforms according to state/value
matrix_space -- "The space this gizmo is being modified in." used by some gizmos for undefined purposes
matrix_world -- final matrix, scaled according to viewport zoom and custom scale_basis

source/blender/windowmanager/gizmo/intern/wm_gizmo.c:WM_gizmo_calc_matrix_final_params
final = space @ (autoscale * (basis @ offset))
final = space @ (basis @ offset) -- if gizmo.use_draw_scale == False
final = space @ ((autoscale * basis) @ offset) -- if gizmo.use_draw_offset_scale

source/blender/windowmanager/gizmo/intern/wm_gizmo.c:wm_gizmo_calculate_scale
autoscale = gizmo.scale_basis * magic(preferences, matrix_space, matrix_basis, context.region_data)
magic -- making 1.0 to match preferences.view.gizmo_size pixels (75 by default)


## Selection

select_id -- apparently, id of a selectable part
test_select -- expected to return id of selection, doesn't seem to work
draw_select -- fake-draw of selection geometry for gpu-side cursor tracking

"""


# some geometries for Gizmo.custom_shape shaders

CUBE = (
    (+1, +1, +1),
    (-1, +1, +1),
    (+1, -1, +1),  # top
    (+1, -1, +1),
    (-1, +1, +1),
    (-1, -1, +1),
    (+1, +1, +1),
    (+1, -1, +1),
    (+1, +1, -1),  # right
    (+1, +1, -1),
    (+1, -1, +1),
    (+1, -1, -1),
    (+1, +1, +1),
    (+1, +1, -1),
    (-1, +1, +1),  # back
    (-1, +1, +1),
    (+1, +1, -1),
    (-1, +1, -1),
    (-1, -1, -1),
    (-1, +1, -1),
    (+1, -1, -1),  # bot
    (+1, -1, -1),
    (-1, +1, -1),
    (+1, +1, -1),
    (-1, -1, -1),
    (-1, -1, +1),
    (-1, +1, -1),  # left
    (-1, +1, -1),
    (-1, -1, +1),
    (-1, +1, +1),
    (-1, -1, -1),
    (+1, -1, -1),
    (-1, -1, +1),  # front
    (-1, -1, +1),
    (+1, -1, -1),
    (+1, -1, +1),
)

DISC = (
    (0.0, 0.0, 0.0),
    (1.0, 0.0, 0),
    (0.8660254037844387, 0.49999999999999994, 0),
    (0.0, 0.0, 0.0),
    (0.8660254037844387, 0.49999999999999994, 0),
    (0.5000000000000001, 0.8660254037844386, 0),
    (0.0, 0.0, 0.0),
    (0.5000000000000001, 0.8660254037844386, 0),
    (6.123233995736766e-17, 1.0, 0),
    (0.0, 0.0, 0.0),
    (6.123233995736766e-17, 1.0, 0),
    (-0.4999999999999998, 0.8660254037844387, 0),
    (0.0, 0.0, 0.0),
    (-0.4999999999999998, 0.8660254037844387, 0),
    (-0.8660254037844385, 0.5000000000000003, 0),
    (0.0, 0.0, 0.0),
    (-0.8660254037844385, 0.5000000000000003, 0),
    (-1.0, 1.2246467991473532e-16, 0),
    (0.0, 0.0, 0.0),
    (-1.0, 1.2246467991473532e-16, 0),
    (-0.8660254037844388, -0.4999999999999997, 0),
    (0.0, 0.0, 0.0),
    (-0.8660254037844388, -0.4999999999999997, 0),
    (-0.5000000000000004, -0.8660254037844384, 0),
    (0.0, 0.0, 0.0),
    (-0.5000000000000004, -0.8660254037844384, 0),
    (-1.8369701987210297e-16, -1.0, 0),
    (0.0, 0.0, 0.0),
    (-1.8369701987210297e-16, -1.0, 0),
    (0.49999999999999933, -0.866025403784439, 0),
    (0.0, 0.0, 0.0),
    (0.49999999999999933, -0.866025403784439, 0),
    (0.8660254037844384, -0.5000000000000004, 0),
    (0.0, 0.0, 0.0),
    (0.8660254037844384, -0.5000000000000004, 0),
    (1.0, 0.0, 0),
)

X3DISC = (
    (0.0, 0.0, 0.0),
    (1.0, 0.0, 0),
    (0.8660254037844387, 0.49999999999999994, 0),
    (0.0, 0.0, 0.0),
    (0.8660254037844387, 0.49999999999999994, 0),
    (0.5000000000000001, 0.8660254037844386, 0),
    (0.0, 0.0, 0.0),
    (0.5000000000000001, 0.8660254037844386, 0),
    (6.123233995736766e-17, 1.0, 0),
    (0.0, 0.0, 0.0),
    (6.123233995736766e-17, 1.0, 0),
    (-0.4999999999999998, 0.8660254037844387, 0),
    (0.0, 0.0, 0.0),
    (-0.4999999999999998, 0.8660254037844387, 0),
    (-0.8660254037844385, 0.5000000000000003, 0),
    (0.0, 0.0, 0.0),
    (-0.8660254037844385, 0.5000000000000003, 0),
    (-1.0, 1.2246467991473532e-16, 0),
    (0.0, 0.0, 0.0),
    (-1.0, 1.2246467991473532e-16, 0),
    (-0.8660254037844388, -0.4999999999999997, 0),
    (0.0, 0.0, 0.0),
    (-0.8660254037844388, -0.4999999999999997, 0),
    (-0.5000000000000004, -0.8660254037844384, 0),
    (0.0, 0.0, 0.0),
    (-0.5000000000000004, -0.8660254037844384, 0),
    (-1.8369701987210297e-16, -1.0, 0),
    (0.0, 0.0, 0.0),
    (-1.8369701987210297e-16, -1.0, 0),
    (0.49999999999999933, -0.866025403784439, 0),
    (0.0, 0.0, 0.0),
    (0.49999999999999933, -0.866025403784439, 0),
    (0.8660254037844384, -0.5000000000000004, 0),
    (0.0, 0.0, 0.0),
    (0.8660254037844384, -0.5000000000000004, 0),
    (1.0, 0.0, 0),
    (0.0, 0.0, 0.0),
    (0, 1.0, 0.0),
    (0, 0.8660254037844387, 0.49999999999999994),
    (0.0, 0.0, 0.0),
    (0, 0.8660254037844387, 0.49999999999999994),
    (0, 0.5000000000000001, 0.8660254037844386),
    (0.0, 0.0, 0.0),
    (0, 0.5000000000000001, 0.8660254037844386),
    (0, 6.123233995736766e-17, 1.0),
    (0.0, 0.0, 0.0),
    (0, 6.123233995736766e-17, 1.0),
    (0, -0.4999999999999998, 0.8660254037844387),
    (0.0, 0.0, 0.0),
    (0, -0.4999999999999998, 0.8660254037844387),
    (0, -0.8660254037844385, 0.5000000000000003),
    (0.0, 0.0, 0.0),
    (0, -0.8660254037844385, 0.5000000000000003),
    (0, -1.0, 1.2246467991473532e-16),
    (0.0, 0.0, 0.0),
    (0, -1.0, 1.2246467991473532e-16),
    (0, -0.8660254037844388, -0.4999999999999997),
    (0.0, 0.0, 0.0),
    (0, -0.8660254037844388, -0.4999999999999997),
    (0, -0.5000000000000004, -0.8660254037844384),
    (0.0, 0.0, 0.0),
    (0, -0.5000000000000004, -0.8660254037844384),
    (0, -1.8369701987210297e-16, -1.0),
    (0.0, 0.0, 0.0),
    (0, -1.8369701987210297e-16, -1.0),
    (0, 0.49999999999999933, -0.866025403784439),
    (0.0, 0.0, 0.0),
    (0, 0.49999999999999933, -0.866025403784439),
    (0, 0.8660254037844384, -0.5000000000000004),
    (0.0, 0.0, 0.0),
    (0, 0.8660254037844384, -0.5000000000000004),
    (0, 1.0, 0.0),
    (0.0, 0.0, 0.0),
    (0.0, 0, 1.0),
    (0.49999999999999994, 0, 0.8660254037844387),
    (0.0, 0.0, 0.0),
    (0.49999999999999994, 0, 0.8660254037844387),
    (0.8660254037844386, 0, 0.5000000000000001),
    (0.0, 0.0, 0.0),
    (0.8660254037844386, 0, 0.5000000000000001),
    (1.0, 0, 6.123233995736766e-17),
    (0.0, 0.0, 0.0),
    (1.0, 0, 6.123233995736766e-17),
    (0.8660254037844387, 0, -0.4999999999999998),
    (0.0, 0.0, 0.0),
    (0.8660254037844387, 0, -0.4999999999999998),
    (0.5000000000000003, 0, -0.8660254037844385),
    (0.0, 0.0, 0.0),
    (0.5000000000000003, 0, -0.8660254037844385),
    (1.2246467991473532e-16, 0, -1.0),
    (0.0, 0.0, 0.0),
    (1.2246467991473532e-16, 0, -1.0),
    (-0.4999999999999997, 0, -0.8660254037844388),
    (0.0, 0.0, 0.0),
    (-0.4999999999999997, 0, -0.8660254037844388),
    (-0.8660254037844384, 0, -0.5000000000000004),
    (0.0, 0.0, 0.0),
    (-0.8660254037844384, 0, -0.5000000000000004),
    (-1.0, 0, -1.8369701987210297e-16),
    (0.0, 0.0, 0.0),
    (-1.0, 0, -1.8369701987210297e-16),
    (-0.866025403784439, 0, 0.49999999999999933),
    (0.0, 0.0, 0.0),
    (-0.866025403784439, 0, 0.49999999999999933),
    (-0.5000000000000004, 0, 0.8660254037844384),
    (0.0, 0.0, 0.0),
    (-0.5000000000000004, 0, 0.8660254037844384),
    (0.0, 0, 1.0),
)


class CustomGizmo:
    # FIXME: highliting/selection doesnt work
    def draw_very_custom_shape(self, ctx, custom_shape, select_id=None):
        # create shader and batch
        shader_wrapper, batch = custom_shape
        shader = shader_wrapper.get_shader()

        # setup params
        shader.bind()
        if select_id is not None:
            gpu.select.load_id(select_id)
        else:
            if self.is_highlight:
                color = (*self.color_highlight, self.alpha_highlight)
            else:
                color = (*self.color, self.alpha)
            shader.uniform_float("color", color)
            shader_wrapper.glenable()
        shader_wrapper.uniform_region(ctx)

        # using `with` block to make sure matrix multiplication
        # won't affect other shaders
        with gpu.matrix.push_pop():
            # using matrix_world seems to be unaffected by matrix_offset
            # therefore we use basis @ offset
            matrix = self.matrix_basis @ self.matrix_offset
            gpu.matrix.multiply_matrix(matrix)
            batch.draw(shader)

        gpu.state.blend_set("NONE")


class OffsetHandle:
    """Handling mouse to offset gizmo from base along Z axis"""

    # FIXME: works a bit weird for rotated objects

    def invoke(self, ctx, event):
        self.init_value = self.target_get_value("offset") / self.scale_value
        coordz = self.project_mouse(ctx, event)
        if coordz is None:
            return {"CANCELLED"}
        self.init_coordz = coordz
        return {"RUNNING_MODAL"}

    def modal(self, ctx, event, tweak):
        coordz = self.project_mouse(ctx, event)
        if coordz is None:
            return {"CANCELLED"}
        delta = coordz - self.init_coordz
        if "PRECISE" in tweak:
            delta /= 10.0
        value = max(0, self.init_value + delta)
        value *= self.scale_value
        # ctx.area.header_text_set(f"coords: {self.init_coordz} - {coordz}, delta: {delta}, value: {value}")
        ctx.area.header_text_set(f"Depth: {value}")
        self.target_set_value("offset", value)
        return {"RUNNING_MODAL"}

    def project_mouse(self, ctx, event):
        """Projecting mouse coords to local axis Z"""
        # logic from source/blender/editors/gizmo_library/gizmo_types/arrow3d_gizmo.c:gizmo_arrow_modal

        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        region = ctx.region
        region3d = ctx.region_data
        ray_orig = view3d_utils.region_2d_to_origin_3d(region, region3d, mouse)
        ray_norm = view3d_utils.region_2d_to_vector_3d(region, region3d, mouse)

        # 'arrow' origin and direction
        base = Vector((0, 0, 0))
        axis = Vector((0, 0, 1))

        # projection of the arrow to a plane, perpendicular to view ray
        axis_proj = axis - ray_norm * axis.dot(ray_norm)

        # intersection of the axis with the plane through view origin perpendicular to the arrow projection
        coords = geometry.intersect_line_plane(base, axis, ray_orig, axis_proj)

        return coords.z

    def exit(self, ctx, cancel):
        if cancel:
            self.target_set_value("offset", self.init_value)
        else:
            self.group.update(ctx)


class UglyDotGizmo(OffsetHandle, types.Gizmo):
    """three orthogonal circles"""

    bl_idname = "BIM_GT_uglydot_3d"
    bl_target_properties = ({"id": "offset", "type": "FLOAT", "array_length": 1},)

    __slots__ = (
        "scale_value",
        "custom_shape",
        "init_value",
        "init_coordz",
    )

    def setup(self):
        self.custom_shape = self.new_custom_shape(type="TRIS", verts=X3DISC)

    def refresh(self):
        offset = self.target_get_value("offset") / self.scale_value
        self.matrix_offset.translation.z = offset  # z-shift

    def draw(self, ctx):
        self.refresh()
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, ctx, select_id):
        self.refresh()
        self.draw_custom_shape(self.custom_shape, select_id=select_id)


# TODO: dead code?
class DotGizmo(CustomGizmo, OffsetHandle, types.Gizmo):
    """Single dot viewport-aligned"""

    # FIXME: make it selectable
    bl_idname = "BIM_GT_dot_2d"
    bl_target_properties = ({"id": "offset", "type": "FLOAT", "array_length": 1},)

    __slots__ = (
        "scale_value",
        "custom_shape",
    )

    def setup(self):
        shader = DotsGizmoShader()
        self.custom_shape = shader, shader.batch(pos=((0, 0, 0),)), shader.prog
        self.use_draw_scale = False

    def refresh(self):
        offset = self.target_get_value("offset") / self.scale_value
        self.matrix_offset.translation.z = offset  # z-shifted

    def draw(self, ctx):
        self.refresh()
        self.draw_very_custom_shape(ctx, self.custom_shape)

    def draw_select(self, ctx, select_id):
        self.refresh()
        self.draw_very_custom_shape(ctx, self.custom_shape, select_id=select_id)


class ExtrusionGuidesGizmo(CustomGizmo, types.Gizmo):
    """Extrusion guides

    Noninteractive gizmo to indicate extrusion depth and planes.
    Draws main segment and orthogonal cross at endpoints.
    """

    bl_idname = "BIM_GT_extrusion_guides"
    bl_target_properties = ({"id": "depth", "type": "FLOAT", "array_length": 1},)

    __slots__ = ("scale_value", "custom_shape")

    def setup(self):
        """setup `custom_shape`"""
        shader_wrapper = ExtrusionGuidesShader()
        verts = [Vector((0, 0, 0)), Vector((0, 0, 1))]
        verts, edges = shader_wrapper.process_geometry(verts)
        self.custom_shape = shader_wrapper, shader_wrapper.batch(
            pos=verts,
            indices=edges,
        )

    def draw(self, ctx):
        self.refresh()
        self.draw_very_custom_shape(ctx, self.custom_shape)

    def refresh(self):
        depth = self.target_get_value("depth") / self.scale_value
        self.matrix_offset.col[2][2] = depth  # z-scaled


# TODO: dead code?
class DimensionLabelGizmo(types.Gizmo):
    """Text label for a dimension"""

    # does not work properly, fonts are totally screwed up

    bl_idname = "BIM_GT_dimension_label"
    bl_target_properties = ({"id": "value", "type": "FLOAT", "array_length": 1},)

    __slots__ = "text_label"

    def setup(self):
        pass

    def refresh(self, ctx):
        value = self.target_get_value("value")
        self.matrix_offset.translation.z = value * 0.5
        unit_system = ctx.scene.unit_settings.system
        self.text_label = bpy.utils.units.to_string(unit_system, "LENGTH", value, 3, split_unit=False)

    def draw(self, ctx):
        self.refresh(ctx)
        self.draw_text(ctx)

    def draw_text(self, ctx):
        font_id = 0
        font_size = 16
        dpi = ctx.preferences.system.dpi

        # pos = self.matrix_world @ Vector((0, 0, 0, 1))
        # pos = Vector((0, 0, 0.5))
        # region = ctx.region
        # region3d = ctx.region_data
        # pos = view3d_utils.location_3d_to_region_2d(region, region3d, pos)

        # text = self.text_label

        blf.size(font_id, font_size, dpi)
        blf.position(font_id, 0, 0, 0)
        blf.color(font_id, *self.color, self.alpha)
        blf.draw(font_id, "ABC")


class ExtrusionWidget(types.GizmoGroup):
    bl_idname = "bim.extrusion_widget"
    bl_label = "Extrusion Gizmos"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT", "SHOW_MODAL_ALL"}

    @classmethod
    def poll(cls, ctx):
        obj = ctx.object
        return (
            obj
            and obj.type == "MESH"
            and obj.data.BIMMeshProperties.ifc_parameters.get("IfcExtrudedAreaSolid/Depth") is not None
        )

    def setup(self, ctx):
        target = ctx.object
        prop = target.data.BIMMeshProperties.ifc_parameters.get("IfcExtrudedAreaSolid/Depth")

        basis = target.matrix_world.normalized()
        theme = ctx.preferences.themes[0].user_interface
        scale_value = self.get_scale_value(ctx.scene.unit_settings.system, ctx.scene.unit_settings.length_unit)

        # setup handle
        gz = self.handle = self.gizmos.new("BIM_GT_uglydot_3d")
        gz.matrix_basis = basis
        gz.scale_basis = 0.1
        gz.color = gz.color_highlight = tuple(theme.gizmo_primary)
        gz.alpha = 0.5
        gz.alpha_highlight = 1.0
        gz.use_draw_modal = True
        gz.target_set_prop("offset", prop, "value")
        gz.scale_value = scale_value

        # setup guides
        gz = self.guides = self.gizmos.new("BIM_GT_extrusion_guides")
        gz.matrix_basis = basis
        gz.color = gz.color_highlight = tuple(theme.gizmo_secondary)
        gz.alpha = gz.alpha_highlight = 0.75
        gz.use_draw_modal = True
        gz.target_set_prop("depth", prop, "value")
        gz.scale_value = scale_value

        # gz = self.label = self.gizmos.new('GIZMO_GT_dimension_label')
        # gz.matrix_basis = basis
        # gz.color = tuple(theme.gizmo_secondary)
        # gz.alpha = 0.5
        # gz.use_draw_modal = True
        # gz.target_set_prop('value', target.demo, 'depth')

    def refresh(self, ctx):
        """updating gizmos"""
        target = ctx.object
        basis = target.matrix_world.normalized()
        self.handle.matrix_basis = basis
        self.guides.matrix_basis = basis

    def update(self, ctx):
        """updating object"""
        bpy.ops.bim.update_parametric_representation()
        target = ctx.object
        prop = target.data.BIMMeshProperties.ifc_parameters.get("IfcExtrudedAreaSolid/Depth")
        self.handle.target_set_prop("offset", prop, "value")
        self.guides.target_set_prop("depth", prop, "value")

    @staticmethod
    def get_scale_value(system, length_unit):
        scale_value = 1
        if system == "METRIC":
            if length_unit == "KILOMETERS":
                scale_value /= 1000
            elif length_unit == "CENTIMETERS":
                scale_value *= 100
            elif length_unit == "MILLIMETERS":
                scale_value *= 1000
            elif length_unit == "MICROMETERS":
                scale_value *= 1000000
        elif system == "IMPERIAL":
            if length_unit == "MILES":
                scale_value /= si_conversions["mile"]
            elif length_unit == "FEET":
                scale_value /= si_conversions["foot"]
            elif length_unit == "INCHES":
                scale_value /= si_conversions["inch"]
            elif length_unit == "THOU":
                scale_value /= si_conversions["thou"]
        return scale_value
