# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from mathutils import Matrix, Vector

import bonsai.tool as tool
from bonsai.tool.drawing import Drawing
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.drawing


class TestRegenerateStoreyAnnotation(NewFile):
    def test_preserves_reversed_vertex_order_when_storey_elevation_changes(self):
        identity = Matrix.Identity(4)
        fake_shape = SimpleNamespace(geometry=SimpleNamespace())
        # Reversed mark: symbol end at x=-6.0, tail at x=6.0, old elevation y=1.75
        reversed_verts = np.array([[-6.0, 1.75, 0.0], [6.0, 1.75, 0.0]])
        captured_points = []

        class FakeBuilder:
            def __init__(self, _ifc):
                pass

            def polyline(self, pts):
                captured_points.extend(pts)
                return SimpleNamespace()

            def get_representation(self, _context, _items):
                return SimpleNamespace()

        storey = SimpleNamespace(Name="Ground Floor")
        annotation = SimpleNamespace(Name="Ground Floor")
        drawing = SimpleNamespace()
        context = SimpleNamespace()

        with (
            patch.object(
                Drawing,
                "generate_storey_points",
                return_value=(Vector((6.0, 2.0, 0.0)), Vector((-6.0, 2.0, 0.0))),
            ),
            patch.object(Drawing, "get_default_annotation_matrix", return_value=identity),
            patch.object(tool.Ifc, "get_object", side_effect=[SimpleNamespace(), None]),
            patch.object(tool.Ifc, "get", return_value=SimpleNamespace()),
            patch("bonsai.tool.drawing.ifcopenshell.geom.settings", return_value=MagicMock()),
            patch("bonsai.tool.drawing.ifcopenshell.geom.create_shape", return_value=fake_shape),
            patch("bonsai.tool.drawing.ifcopenshell.util.shape.get_shape_matrix", return_value=np.array(identity)),
            patch("bonsai.tool.drawing.ifcopenshell.util.shape.get_vertices", return_value=reversed_verts),
            patch("bonsai.tool.drawing.ifcopenshell.util.representation.get_representation", return_value=None),
            patch("bonsai.tool.drawing.ifcopenshell.util.unit.calculate_unit_scale", return_value=1.0),
            patch("bonsai.tool.drawing.ifcopenshell.api.geometry.assign_representation"),
            patch("bonsai.tool.drawing.ifcopenshell.api.geometry.edit_object_placement"),
            patch("bonsai.tool.drawing.ShapeBuilder", FakeBuilder),
        ):
            Drawing.regenerate_storey_annotation(drawing, annotation, storey, context)

        assert len(captured_points) == 2
        assert tuple(captured_points[0]) == (-6.0, 2.0, 0.0)
        assert tuple(captured_points[1]) == (6.0, 2.0, 0.0)
