# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 IfcOpenShell contributors
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

import math

import pytest

import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.geom
import ifcopenshell.util.shape as subject
import test.bootstrap


class TestElevationHelpers(test.bootstrap.IFC4):
    def get_body_context(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        return ifcopenshell.api.context.add_context(
            self.file,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model,
        )

    def create_shape(self, element):
        settings = ifcopenshell.geom.settings()
        return ifcopenshell.geom.create_shape(settings, element)

    def create_degenerate_wall(self, body):
        # Mirrors the malformed pattern found live in issue #6895's file: an
        # untrimmed IfcLine (an unbounded curve) used directly as a body
        # representation item. Valid IFC never does this; IfcLine is only
        # valid as the basis curve of a bounded (e.g. trimmed) curve.
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        point = self.file.create_entity("IfcCartesianPoint", (0.0, 0.0, 0.0))
        direction = self.file.create_entity("IfcDirection", (0.0, 0.0, 1.0))
        vector = self.file.create_entity("IfcVector", direction, 1000.0)
        line = self.file.create_entity("IfcLine", point, vector)
        geometric_set = self.file.create_entity("IfcGeometricCurveSet", (line,))
        shape_representation = self.file.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=body,
            RepresentationIdentifier="Body",
            RepresentationType="GeometricCurveSet",
            Items=(geometric_set,),
        )
        element.Representation = self.file.create_entity(
            "IfcProductDefinitionShape", Representations=(shape_representation,)
        )
        return element

    def test_valid_wall_elevations_are_unaffected(self):
        body = self.get_body_context()
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        representation = ifcopenshell.api.geometry.add_wall_representation(
            self.file, context=body, length=5, height=3, thickness=0.2
        )
        ifcopenshell.api.geometry.assign_representation(self.file, product=wall, representation=representation)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=wall)

        shape = self.create_shape(wall)
        with _no_warnings():
            bottom = subject.get_shape_bottom_elevation(shape, shape.geometry)
            top = subject.get_shape_top_elevation(shape, shape.geometry)

        assert bottom == pytest.approx(0.0, abs=1e-6)
        assert top == pytest.approx(3.0, abs=1e-6)

        assert subject.get_bottom_elevation(shape.geometry) == pytest.approx(0.0, abs=1e-6)
        assert subject.get_top_elevation(shape.geometry) == pytest.approx(3.0, abs=1e-6)

        assert subject.get_element_bottom_elevation(wall, shape.geometry) == pytest.approx(0.0, abs=1e-6)
        assert subject.get_element_top_elevation(wall, shape.geometry) == pytest.approx(3.0, abs=1e-6)

    def test_degenerate_infinite_line_returns_nan_with_warning(self):
        body = self.get_body_context()
        wall = self.create_degenerate_wall(body)
        shape = self.create_shape(wall)

        with pytest.warns(UserWarning):
            bottom = subject.get_shape_bottom_elevation(shape, shape.geometry)
        with pytest.warns(UserWarning):
            top = subject.get_shape_top_elevation(shape, shape.geometry)
        with pytest.warns(UserWarning):
            local_bottom = subject.get_bottom_elevation(shape.geometry)
        with pytest.warns(UserWarning):
            local_top = subject.get_top_elevation(shape.geometry)
        with pytest.warns(UserWarning):
            element_bottom = subject.get_element_bottom_elevation(wall, shape.geometry)
        with pytest.warns(UserWarning):
            element_top = subject.get_element_top_elevation(wall, shape.geometry)

        for value in (bottom, top, local_bottom, local_top, element_bottom, element_top):
            assert math.isnan(value)

        # Sanity check on the underlying assumption: the degenerate curve
        # really does tessellate to a practically-infinite vertex, not a
        # small or ordinary large number.
        z_values = subject.get_vertices(shape.geometry)[:, 2]
        assert (abs(z_values) >= subject.PRACTICAL_INFINITY).any()


class _no_warnings:
    """Context manager asserting no warnings are raised (avoids importing `warnings` at module level)."""

    def __enter__(self):
        import warnings

        self._cm = warnings.catch_warnings(record=True)
        self._log = self._cm.__enter__()
        warnings.simplefilter("always")
        return self

    def __exit__(self, *exc_info):
        self._cm.__exit__(*exc_info)
        assert not self._log, f"Unexpected warning(s): {[str(w.message) for w in self._log]}"
