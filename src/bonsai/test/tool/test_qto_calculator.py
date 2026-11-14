# This file was generated with the assistance of an AI coding tool.

import bpy
import pytest
from mathutils import Matrix

from bonsai.bim.module.qto.calculator import get_outer_surface_area
from test.bim.bootstrap import NewFile


class TestGetOuterSurfaceArea(NewFile):
    @pytest.mark.parametrize("size, expected", [((4, 2, 1), 12.0), ((1, 2, 3), 18.0)])
    def test_top_and_bottom_along_local_z_are_excluded(self, size, expected):
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj = bpy.context.active_object
        obj.data.transform(Matrix.Diagonal((*size, 1.0)))
        assert get_outer_surface_area(obj) == pytest.approx(expected)
