# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2024 IfcOpenShell Contributors
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

"""Tests for case-insensitive schema name handling and IFC2X3-specific entities."""

import pytest
import ifcopenshell
import ifcopenshell.api.project


class TestSchemaCaseInsensitivity:
    """Test that schema names are handled case-insensitively."""

    def test_create_file_with_lowercase_schema(self):
        """Schema names in lowercase should work identically to uppercase."""
        # These should all work identically
        file_upper = ifcopenshell.api.project.create_file(version="IFC4X1")
        file_lower = ifcopenshell.api.project.create_file(version="ifc4x1")
        file_mixed = ifcopenshell.api.project.create_file(version="Ifc4x1")

        # All should produce valid IFC4X1 files
        assert file_upper.schema == "IFC4X1"
        assert file_lower.schema == "IFC4X1"
        assert file_mixed.schema == "IFC4X1"

    def test_create_file_with_lowercase_ifc2x3(self):
        """IFC2X3 schema should work with various case combinations."""
        file_upper = ifcopenshell.api.project.create_file(version="IFC2X3")
        file_lower = ifcopenshell.api.project.create_file(version="ifc2x3")
        file_mixed = ifcopenshell.api.project.create_file(version="Ifc2x3")

        assert file_upper.schema == "IFC2X3"
        assert file_lower.schema == "IFC2X3"
        assert file_mixed.schema == "IFC2X3"

    def test_create_file_with_lowercase_ifc4(self):
        """IFC4 schema should work with various case combinations."""
        file_upper = ifcopenshell.api.project.create_file(version="IFC4")
        file_lower = ifcopenshell.api.project.create_file(version="ifc4")

        assert file_upper.schema == "IFC4"
        assert file_lower.schema == "IFC4"


class TestIfc2X3SpecificEntities:
    """Test IFC2X3-specific entities like Ifc2DCompositeCurve and IfcBezierCurve."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.file = ifcopenshell.api.project.create_file(version="IFC2X3")

    def test_ifc2d_composite_curve_exists(self):
        """Ifc2DCompositeCurve should exist in IFC2X3 schema."""
        # Create control points for a simple segment
        p1 = self.file.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0))
        p2 = self.file.create_entity("IfcCartesianPoint", Coordinates=(1.0, 0.0))
        p3 = self.file.create_entity("IfcCartesianPoint", Coordinates=(1.0, 1.0))

        # Create a polyline as the parent curve for a segment
        polyline = self.file.create_entity("IfcPolyline", Points=[p1, p2, p3])

        # Create a composite curve segment
        segment = self.file.create_entity(
            "IfcCompositeCurveSegment",
            Transition="CONTINUOUS",
            SameSense=True,
            ParentCurve=polyline,
        )

        # Create Ifc2DCompositeCurve (IFC2X3 only)
        composite_2d = self.file.create_entity(
            "Ifc2DCompositeCurve", Segments=[segment], SelfIntersect=False
        )

        assert composite_2d is not None
        assert composite_2d.is_a("Ifc2DCompositeCurve")
        assert composite_2d.is_a("IfcCompositeCurve")
        assert composite_2d.is_a("IfcBoundedCurve")
        assert composite_2d.is_a("IfcCurve")

    def test_ifc_bezier_curve_exists(self):
        """IfcBezierCurve should exist in IFC2X3 schema."""
        # Create control points for a cubic Bezier curve
        p1 = self.file.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
        p2 = self.file.create_entity("IfcCartesianPoint", Coordinates=(1.0, 2.0, 0.0))
        p3 = self.file.create_entity("IfcCartesianPoint", Coordinates=(2.0, 2.0, 0.0))
        p4 = self.file.create_entity("IfcCartesianPoint", Coordinates=(3.0, 0.0, 0.0))

        # Create IfcBezierCurve (IFC2X3 only)
        bezier = self.file.create_entity(
            "IfcBezierCurve",
            Degree=3,
            ControlPointsList=[p1, p2, p3, p4],
            CurveForm="UNSPECIFIED",
            ClosedCurve=False,
            SelfIntersect=False,
        )

        assert bezier is not None
        assert bezier.is_a("IfcBezierCurve")
        assert bezier.is_a("IfcBSplineCurve")
        assert bezier.is_a("IfcBoundedCurve")
        assert bezier.is_a("IfcCurve")
        assert bezier.Degree == 3
        assert len(bezier.ControlPointsList) == 4

    def test_ifc_rational_bezier_curve_exists(self):
        """IfcRationalBezierCurve should exist in IFC2X3 schema."""
        # Create control points for a rational Bezier curve
        p1 = self.file.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
        p2 = self.file.create_entity("IfcCartesianPoint", Coordinates=(1.0, 1.0, 0.0))
        p3 = self.file.create_entity("IfcCartesianPoint", Coordinates=(2.0, 0.0, 0.0))

        # Create IfcRationalBezierCurve (IFC2X3 only)
        rational_bezier = self.file.create_entity(
            "IfcRationalBezierCurve",
            Degree=2,
            ControlPointsList=[p1, p2, p3],
            CurveForm="UNSPECIFIED",
            ClosedCurve=False,
            SelfIntersect=False,
            Weights=[1.0, 2.0, 1.0],  # Higher weight in middle for a rounder curve
        )

        assert rational_bezier is not None
        assert rational_bezier.is_a("IfcRationalBezierCurve")
        assert rational_bezier.is_a("IfcBezierCurve")
        assert rational_bezier.is_a("IfcBSplineCurve")
        assert len(rational_bezier.Weights) == 3


class TestIfc4DoesNotHaveLegacyEntities:
    """Test that IFC4+ schemas do not have deprecated IFC2X3 entities."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.file = ifcopenshell.api.project.create_file(version="IFC4")

    def test_ifc2d_composite_curve_not_in_ifc4(self):
        """Ifc2DCompositeCurve should NOT exist in IFC4 schema."""
        with pytest.raises(Exception):
            # This should fail because Ifc2DCompositeCurve doesn't exist in IFC4
            self.file.create_entity(
                "Ifc2DCompositeCurve", Segments=[], SelfIntersect=False
            )

    def test_ifc_bezier_curve_not_in_ifc4(self):
        """IfcBezierCurve should NOT exist in IFC4 schema (replaced by IfcBSplineCurveWithKnots)."""
        with pytest.raises(Exception):
            p1 = self.file.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
            p2 = self.file.create_entity("IfcCartesianPoint", Coordinates=(1.0, 1.0, 0.0))
            # This should fail because IfcBezierCurve doesn't exist in IFC4
            self.file.create_entity(
                "IfcBezierCurve",
                Degree=1,
                ControlPointsList=[p1, p2],
                CurveForm="UNSPECIFIED",
                ClosedCurve=False,
                SelfIntersect=False,
            )


class TestEntityCaseInsensitivity:
    """Test that entity names are handled case-insensitively."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.file = ifcopenshell.api.project.create_file(version="IFC4")

    def test_entity_declaration_case_insensitive(self):
        """Entity lookups should be case-insensitive."""
        # Create an entity using different case variations
        wall = self.file.create_entity("IfcWall")

        # is_a() should work case-insensitively
        assert wall.is_a("IFCWALL")
        assert wall.is_a("ifcwall")
        assert wall.is_a("IfcWall")
        assert wall.is_a("IFCELEMENT")
        assert wall.is_a("ifcelement")

    def test_by_type_case_insensitive(self):
        """by_type() should work with various case combinations."""
        self.file.create_entity("IfcWall")
        self.file.create_entity("IfcWall")

        # All should return the same results
        walls_upper = self.file.by_type("IFCWALL")
        walls_lower = self.file.by_type("ifcwall")
        walls_mixed = self.file.by_type("IfcWall")

        assert len(walls_upper) == 2
        assert len(walls_lower) == 2
        assert len(walls_mixed) == 2
