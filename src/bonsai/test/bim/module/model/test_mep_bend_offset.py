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

import json
from math import radians

import bpy
import ifcopenshell.util.element
import pytest
from mathutils import Matrix

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc

pytestmark = pytest.mark.model


class TestMEPAddBendOffsetOutOfBendPlane(NewIfc):
    def _select_perpendicular_segments(self, offset: float, roll: float = 0.0):
        root_props = tool.Root.get_root_props()
        root_props.ifc_product = "IfcElementType"
        root_props.ifc_class = "IfcDuctSegmentType"
        root_props.representation_template = "FLOW_SEGMENT_RECTANGULAR"
        bpy.ops.bim.add_element()
        model_props = tool.Model.get_model_props()
        model_props.ifc_class = "IfcDuctSegmentType"
        model_props.relating_type_id = str(tool.Ifc.get().by_type("IfcDuctSegmentType")[0].id())
        model_props.extrusion_depth = 5.0
        bpy.ops.bim.add_occurrence()
        start = bpy.context.active_object
        bpy.ops.bim.add_occurrence()
        end = bpy.context.active_object
        end.rotation_euler[2] += radians(90)
        bpy.context.view_layer.update()
        end.matrix_world.translation = (6, 1, start.matrix_world.translation.z + offset)
        for obj in (start, end):
            obj.matrix_world = obj.matrix_world @ Matrix.Rotation(radians(roll), 4, "Z")
        bpy.context.view_layer.update()
        start.select_set(True)
        end.select_set(True)

    def test_float_noise_offset_still_gets_a_bend(self):
        self._select_perpendicular_segments(offset=0.00005)
        bpy.ops.bim.mep_add_bend()
        assert len(tool.Ifc.get().by_type("IfcDuctFitting")) == 1

    def test_float_noise_offset_keeps_the_lateral_axis(self):
        self._select_perpendicular_segments(offset=0.00005, roll=90)
        bpy.ops.bim.mep_add_bend()
        fitting_type = tool.Ifc.get().by_type("IfcDuctFittingType")[0]
        data = json.loads(ifcopenshell.util.element.get_pset(fitting_type, "BBIM_Fitting", "Data"))
        assert data["lateral_axis"] == 1

    def test_real_offset_is_rejected_as_a_double_bend(self):
        self._select_perpendicular_segments(offset=0.001)
        with pytest.raises(
            RuntimeError, match="Detected an offset of -0.001 along the local axis Y when lateral axis is X"
        ):
            bpy.ops.bim.mep_add_bend()
        assert not tool.Ifc.get().by_type("IfcDuctFitting")
