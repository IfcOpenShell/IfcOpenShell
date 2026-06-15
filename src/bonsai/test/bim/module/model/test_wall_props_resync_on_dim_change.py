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

"""Pins the contract that the three dimension-mutating wall operators —
``bim.change_extrusion_depth``, ``bim.change_extrusion_x_angle``,
``bim.change_layer_length`` — re-prime ``BIMWallProperties`` from the
post-mutation IFC at the end of ``_execute``.

Without the resync, ``props.height`` / ``props.length`` / ``props.x_angle``
stay at their pre-mutation values; gizmo icons that position from
``props.height`` then sit at the old elevation even though the wall mesh
shows the new one."""

import inspect

import pytest

pytestmark = pytest.mark.wall


def _execute_source(operator_cls):
    return inspect.getsource(operator_cls._execute)


def test_change_extrusion_depth_resyncs_wall_props():
    """Height mutation must re-prime ``BIMWallProperties.height`` so
    gizmo icons positioned from ``props.height`` track the post-mutation
    wall top in the same redraw."""
    from bonsai.bim.module.model.wall import ChangeExtrusionDepth

    assert "_resync_walls_after_mutation" in _execute_source(ChangeExtrusionDepth)


def test_change_extrusion_x_angle_resyncs_wall_props():
    """Slope mutation must re-prime ``BIMWallProperties.x_angle`` so
    slope-driven gizmo positions track the new angle."""
    from bonsai.bim.module.model.wall import ChangeExtrusionXAngle

    assert "_resync_walls_after_mutation" in _execute_source(ChangeExtrusionXAngle)


def test_change_layer_length_resyncs_wall_props():
    """Length mutation must re-prime ``BIMWallProperties.length`` so
    horizontal gizmo X positions track the new axis extent."""
    from bonsai.bim.module.model.wall import ChangeLayerLength

    assert "_resync_walls_after_mutation" in _execute_source(ChangeLayerLength)
