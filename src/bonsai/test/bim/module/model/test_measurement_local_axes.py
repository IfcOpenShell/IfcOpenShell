# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

"""Contract tests for PolylineDecorator.calculate_measurement_local_x_y_and_z:
the "Single" measure tool's breakdown of a two-point delta against the active
object's own orientation (issue #4391), on top of the existing global-axis
breakdown (calculate_measurement_x_y_and_z)."""

import math
from types import SimpleNamespace

import bpy
import pytest
from mathutils import Euler, Vector

from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model


def _decorator_with_points(start: Vector, end: Vector):
    from bonsai.bim.module.model.decorator import PolylineDecorator

    decorator = PolylineDecorator.__new__(PolylineDecorator)
    decorator.polyline_points = [
        SimpleNamespace(x=start.x, y=start.y, z=start.z),
        SimpleNamespace(x=end.x, y=end.y, z=end.z),
    ]
    return decorator


def _make_active_object_rotated_about_z(degrees: float):
    bpy.ops.object.add(type="EMPTY")
    obj = bpy.context.active_object
    obj.rotation_euler = Euler((0, 0, math.radians(degrees)), "XYZ")
    bpy.context.view_layer.update()
    return obj


class TestCalculateMeasurementLocalXYAndZ(NewFile):
    def test_no_active_object_returns_none(self):
        bpy.context.view_layer.objects.active = None
        decorator = _decorator_with_points(Vector((0, 0, 0)), Vector((1, 2, 3)))
        axis, center, delta = decorator.calculate_measurement_local_x_y_and_z(bpy.context)
        assert axis is None
        assert center is None
        assert delta is None

    def test_unrotated_active_object_matches_global_so_returns_none(self):
        _make_active_object_rotated_about_z(0)
        decorator = _decorator_with_points(Vector((0, 0, 0)), Vector((1, 2, 3)))
        axis, center, delta = decorator.calculate_measurement_local_x_y_and_z(bpy.context)
        assert axis is None

    def test_90_degree_z_rotation_swaps_x_and_y_components(self):
        # A +90 deg rotation about Z maps local +X -> global +Y and local +Y -> global -X,
        # so the local breakdown of a global (3, 4, 5) delta is (4, -3, 5).
        _make_active_object_rotated_about_z(90)
        start = Vector((0, 0, 0))
        end = Vector((3, 4, 5))
        decorator = _decorator_with_points(start, end)
        axis, center, delta = decorator.calculate_measurement_local_x_y_and_z(bpy.context)

        assert axis is not None and center is not None and delta is not None
        assert delta.x == pytest.approx(4)
        assert delta.y == pytest.approx(-3)
        assert delta.z == pytest.approx(5)

        x_axis, y_axis, z_axis = axis
        assert tuple(x_axis[0]) == pytest.approx(tuple(start))
        # Stairstep segments must land exactly on the measured end point.
        assert tuple(z_axis[1]) == pytest.approx(tuple(end))
        assert (x_axis[1] - x_axis[0]).length == pytest.approx(abs(delta.x))
        assert (y_axis[1] - y_axis[0]).length == pytest.approx(abs(delta.y))
        assert (z_axis[1] - z_axis[0]).length == pytest.approx(abs(delta.z))

    def test_arbitrary_rotation_round_trips_back_to_global_delta(self):
        # Re-projecting the local components back onto world space (via the
        # object's rotation) must reconstruct the original global delta,
        # regardless of the rotation chosen.
        obj = _make_active_object_rotated_about_z(0)
        obj.rotation_euler = Euler((math.radians(20), math.radians(35), math.radians(50)), "XYZ")
        bpy.context.view_layer.update()

        start = Vector((1, -2, 0.5))
        end = Vector((4, 1, 3.5))
        decorator = _decorator_with_points(start, end)
        axis, center, delta = decorator.calculate_measurement_local_x_y_and_z(bpy.context)

        assert delta is not None
        rotation = obj.matrix_world.to_3x3().normalized()
        reconstructed = start + rotation @ delta
        assert tuple(reconstructed) == pytest.approx(tuple(end))

        # Length is preserved (rotation only, no scale), matching what a
        # BIMVision-style local readout should report.
        global_length = (end - start).length
        local_length = math.sqrt(delta.x**2 + delta.y**2 + delta.z**2)
        assert local_length == pytest.approx(global_length)
