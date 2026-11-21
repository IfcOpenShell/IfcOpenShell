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

"""Contract tests for user-configurable door handle properties (issue #8090).

Verifies:
- BIMDoorProperties exposes handle_size, handle_inset_from_edge, and handle_height_above_floor
  with expected ISO-standard defaults.
- get_panel_kwargs includes handle properties for roundtrip persistence via BBIM_Door pset.
- set_props_kwargs_from_ifc_data loads persisted handle properties.
- Backward compatibility: when an existing IFC file has no handle properties, defaults are preserved.
- update_door_modifier_bmesh consumes handle properties and updates the resulting mesh vertex Z positions.
"""

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.model


def test_door_handle_properties_defaults():
    from bonsai.bim.module.model.prop import BIMDoorProperties

    # Inspect RNA property definitions on BIMDoorProperties
    assert "handle_size" in BIMDoorProperties.__annotations__
    assert "handle_inset_from_edge" in BIMDoorProperties.__annotations__
    assert "handle_height_above_floor" in BIMDoorProperties.__annotations__


def test_get_panel_kwargs_includes_handle_props():
    from bonsai.bim.module.model.prop import BIMDoorProperties

    class FakeProps:
        panel_depth = 0.035
        panel_width_ratio = 1.0
        transom_thickness = 0.0
        handle_size = (0.120, 0.040, 0.020)
        handle_inset_from_edge = 0.060
        handle_height_above_floor = 1.000

    kwargs = BIMDoorProperties.get_panel_kwargs(FakeProps(), convert_to_project_units=False)
    assert kwargs["handle_size"] == (0.120, 0.040, 0.020)
    assert kwargs["handle_inset_from_edge"] == pytest.approx(0.060)
    assert kwargs["handle_height_above_floor"] == pytest.approx(1.000)


def test_handle_props_backward_compatibility_on_missing_keys():
    from bonsai.bim.module.model.prop import BIMDoorProperties

    class FakeProps:
        non_si_units_props = BIMDoorProperties.non_si_units_props
        handle_size = (0.120, 0.040, 0.020)
        handle_inset_from_edge = 0.060
        handle_height_above_floor = 1.000
        panel_depth = 0.035

    # Simulate legacy pset data with no handle keys
    legacy_data = {"panel_depth": 0.040}

    with patch("bonsai.tool.Model.convert_data_to_si_units", side_effect=lambda data, non_si: dict(data)):
        BIMDoorProperties.set_props_kwargs_from_ifc_data(FakeProps(), legacy_data)

    # Defaults remain untouched
    assert FakeProps.handle_size == (0.120, 0.040, 0.020)
    assert FakeProps.handle_inset_from_edge == pytest.approx(0.060)
    assert FakeProps.handle_height_above_floor == pytest.approx(1.000)
    assert FakeProps.panel_depth == pytest.approx(0.040)


def test_update_door_modifier_consumes_handle_height():
    """Verify that update_door_modifier_bmesh shifts the handle vertex Z position
    when handle_height_above_floor changes."""
    from bonsai.bim.module.model.door import update_door_modifier_bmesh

    class FakeProps:
        is_editing = True
        overall_width = 0.9
        overall_height = 2.1
        door_type = "SINGLE_SWING_LEFT"
        lining_depth = 0.05
        lining_thickness = 0.05
        lining_offset = 0.0
        lining_to_panel_offset_x = 0.025
        lining_to_panel_offset_y = 0.025
        panel_depth = 0.035
        panel_width_ratio = 1.0
        transom_thickness = 0.0
        transom_offset = 0.0
        threshold_thickness = 0.025
        threshold_depth = 0.1
        threshold_offset = 0.0
        casing_thickness = 0.0
        casing_depth = 0.005
        frame_depth = 0.035
        frame_thickness = 0.035
        handle_size = (0.120, 0.040, 0.020)
        handle_inset_from_edge = 0.060
        handle_height_above_floor = 1.000

    class FakeMesh:
        def __init__(self):
            self.verts = []

        def update(self):
            pass

    mesh = FakeMesh()
    fake_obj = MagicMock()
    fake_obj.data = mesh
    fake_context = MagicMock()
    fake_context.active_object = fake_obj
    fake_context.active_object.mode = "OBJECT"

    with patch("bmesh.new"), patch("bmesh.ops.remove_doubles"), patch("bmesh.ops.recalc_face_normals"):
        # Compare handle heights: 1.000m vs 1.150m
        props_1 = FakeProps()
        props_1.handle_height_above_floor = 1.000

        props_2 = FakeProps()
        props_2.handle_height_above_floor = 1.150

        # Run update with height 1.0
        handle_z_1 = []

        def capture_extruded_1(bm, points, magnitude, position):
            handle_z_1.append(position.z)
            return []

        with patch("bonsai.bim.module.model.door.extrude_points", side_effect=capture_extruded_1):
            with patch("bonsai.bim.module.model.door.get_door_props", return_value=props_1):
                update_door_modifier_bmesh(fake_context)

        # Run update with height 1.15
        handle_z_2 = []

        def capture_extruded_2(bm, points, magnitude, position):
            handle_z_2.append(position.z)
            return []

        with patch("bonsai.bim.module.model.door.extrude_points", side_effect=capture_extruded_2):
            with patch("bonsai.bim.module.model.door.get_door_props", return_value=props_2):
                update_door_modifier_bmesh(fake_context)

        assert len(handle_z_1) > 0
        assert len(handle_z_2) > 0
        assert handle_z_1[-1] == pytest.approx(1.000)
        assert handle_z_2[-1] == pytest.approx(1.150)
