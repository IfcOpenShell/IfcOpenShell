# Ifc5D - IFC costing utility
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Ifc5D.
#
# Ifc5D is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ifc5D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Ifc5D.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

from typing import Optional

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.drawing
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.element
import pytest

import ifc5d.qto


class TestAnnotationBoundaryQuantities:
    """Space areas copied from boundary annotations assigned with IfcRelAssignsToProduct (#8570)."""

    def setup_method(self):
        self.setup_file()

    def setup_file(self, length_prefix: Optional[str] = None):
        f = self.file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="Test")
        units = [
            f.createIfcSIUnit(None, "LENGTHUNIT", length_prefix, "METRE"),
            f.createIfcSIUnit(None, "AREAUNIT", None, "SQUARE_METRE"),
        ]
        ifcopenshell.api.unit.assign_unit(f, units=units)
        plan = ifcopenshell.api.context.add_context(f, context_type="Plan")
        self.annotation_context = ifcopenshell.api.context.add_context(
            f, context_type="Plan", context_identifier="Annotation", target_view="PLAN_VIEW", parent=plan
        )
        self.space = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSpace", name="Space")

    def add_boundary_annotation(self, items) -> ifcopenshell.entity_instance:
        f = self.file
        annotation = ifcopenshell.api.root.create_entity(f, ifc_class="IfcAnnotation")
        rep = f.createIfcShapeRepresentation(self.annotation_context, "Annotation", "Annotation2D", items)
        annotation.Representation = f.createIfcProductDefinitionShape(None, None, [rep])
        ifcopenshell.api.drawing.assign_product(f, relating_product=self.space, related_object=annotation)
        return annotation

    def create_rectangle_curve(self, size_x: float, size_y: float) -> ifcopenshell.entity_instance:
        # The closed IfcIndexedPolyCurve pattern Bonsai writes for annotations.
        f = self.file
        points = f.createIfcCartesianPointList2D(((0.0, 0.0), (size_x, 0.0), (size_x, size_y), (0.0, size_y)))
        segments = [f.createIfcLineIndex((i, i % 4 + 1)) for i in range(1, 5)]
        return f.createIfcIndexedPolyCurve(points, segments)

    def quantify(self) -> ifc5d.qto.ResultsDict:
        rules = ifc5d.qto.rules["IFC4QtoBaseQuantitiesAnnotation"]
        return ifc5d.qto.quantify(self.file, {self.space}, rules)

    def test_closed_polycurve_boundary(self):
        f = self.file
        curve_set = f.createIfcGeometricCurveSet([self.create_rectangle_curve(4.0, 3.0)])
        self.add_boundary_annotation([curve_set])
        results = self.quantify()
        assert results[self.space]["Qto_SpaceBaseQuantities"] == {"GrossFloorArea": pytest.approx(12.0)}

    def test_fill_area_with_inner_boundary(self):
        f = self.file
        outer = f.createIfcPolyline(
            [f.createIfcCartesianPoint(p) for p in ((0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0))]
        )
        fill_area = f.createIfcAnnotationFillArea(outer, [self.create_rectangle_curve(2.0, 3.0)])
        self.add_boundary_annotation([fill_area])
        results = self.quantify()
        assert results[self.space]["Qto_SpaceBaseQuantities"] == {"GrossFloorArea": pytest.approx(94.0)}

    def test_open_polyline_is_ignored(self):
        f = self.file
        polyline = f.createIfcPolyline([f.createIfcCartesianPoint(p) for p in ((0.0, 0.0), (4.0, 0.0), (4.0, 3.0))])
        self.add_boundary_annotation([f.createIfcGeometricCurveSet([polyline])])
        assert self.quantify() == {}

    def test_space_without_boundary_annotation_is_not_quantified(self):
        assert self.quantify() == {}

    def test_multiple_boundary_annotations_are_summed(self):
        f = self.file
        self.add_boundary_annotation([f.createIfcGeometricCurveSet([self.create_rectangle_curve(4.0, 3.0)])])
        self.add_boundary_annotation([f.createIfcGeometricCurveSet([self.create_rectangle_curve(2.0, 1.0)])])
        results = self.quantify()
        assert results[self.space]["Qto_SpaceBaseQuantities"] == {"GrossFloorArea": pytest.approx(14.0)}

    def test_millimetre_project_units(self):
        self.setup_file(length_prefix="MILLI")
        f = self.file
        curve_set = f.createIfcGeometricCurveSet([self.create_rectangle_curve(4000.0, 3000.0)])
        self.add_boundary_annotation([curve_set])
        results = self.quantify()
        assert results[self.space]["Qto_SpaceBaseQuantities"] == {"GrossFloorArea": pytest.approx(12.0)}

    def test_quantities_are_written_to_the_file(self):
        f = self.file
        self.add_boundary_annotation([f.createIfcGeometricCurveSet([self.create_rectangle_curve(4.0, 3.0)])])
        ifc5d.qto.edit_qtos(f, self.quantify())
        qto = ifcopenshell.util.element.get_pset(self.space, "Qto_SpaceBaseQuantities")
        assert qto["GrossFloorArea"] == pytest.approx(12.0)
