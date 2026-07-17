# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell
import ifcopenshell.guid

import ifcpatch
import test.bootstrap


def add_context(f: ifcopenshell.file) -> ifcopenshell.entity_instance:
    origin = f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    return f.createIfcGeometricRepresentationContext(None, "Model", 3, 1.0e-05, origin, None)


def add_wall_with_curve(f: ifcopenshell.file, context, coords) -> ifcopenshell.entity_instance:
    wall = f.create_entity("IfcWall", ifcopenshell.guid.new())
    points = [f.createIfcCartesianPoint(c) for c in coords]
    polyline = f.createIfcPolyline(points)
    rep = f.createIfcShapeRepresentation(context, "Body", "Curve2D", [polyline])
    wall.Representation = f.createIfcProductDefinitionShape(None, None, [rep])
    return wall


def curve_of(wall: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    return wall.Representation.Representations[0].Items[0]


class TestOptimise(test.bootstrap.IFC4):
    def test_folding_value_identical_non_rooted_entities(self):
        # Two polylines built from separate but value-identical points.
        context = add_context(self.file)
        coords = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 0.0)]
        wall1 = add_wall_with_curve(self.file, context, coords)
        wall2 = add_wall_with_curve(self.file, context, coords)
        assert curve_of(wall1) != curve_of(wall2)

        output = ifcpatch.execute({"file": self.file, "recipe": "Optimise", "arguments": []})

        assert len(output.by_type("IfcPolyline")) == 1

        walls_after = output.by_type("IfcWall")
        assert len(walls_after) == 2
        assert curve_of(walls_after[0]) == curve_of(walls_after[1])

    def test_distinct_values_are_not_folded(self):
        context = add_context(self.file)
        wall1 = add_wall_with_curve(self.file, context, [(0.0, 0.0), (1.0, 0.0)])
        wall2 = add_wall_with_curve(self.file, context, [(0.0, 0.0), (2.0, 0.0)])
        assert curve_of(wall1) != curve_of(wall2)

        output = ifcpatch.execute({"file": self.file, "recipe": "Optimise", "arguments": []})

        assert len(output.by_type("IfcPolyline")) == 2
        walls_after = output.by_type("IfcWall")
        assert curve_of(walls_after[0]) != curve_of(walls_after[1])
