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

import numpy as np
import pytest

import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape
from ifcopenshell.util.shape_builder import ShapeBuilder

import ifcpatch
import test.bootstrap

# All models are authored in millimetres so that the unit conversion is
# exercised, whereas everything IfcOpenShell hands back is in SI units.
STOREY_ELEVATION = 3000.0
# An L shaped room, as would be exported by ArchiCAD as a faceted brep.
L_SHAPE = [(0.0, 0.0), (6000.0, 0.0), (6000.0, 2000.0), (2000.0, 2000.0), (2000.0, 5000.0), (0.0, 5000.0)]
L_SHAPE_AREA = 18.0
# A rectangular room with a column poking through it, i.e. a profile with a void.
RECTANGLE = [(0.0, 0.0), (5000.0, 0.0), (5000.0, 4000.0), (0.0, 4000.0)]
COLUMN = [(1000.0, 1000.0), (1000.0, 2000.0), (2000.0, 2000.0), (2000.0, 1000.0)]
RECTANGLE_AREA = 19.0


class TestFixArchiCADToRevitSpaces(test.bootstrap.IFC4):
    def create_project(self) -> None:
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        self.body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        self.builder = ShapeBuilder(self.file)
        self.storey = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey")
        self.place(self.storey, STOREY_ELEVATION)

    def place(self, element: ifcopenshell.entity_instance, elevation: float, angle: float = 0.0) -> None:
        matrix = np.eye(4)
        matrix[:2, :2] = [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
        matrix[2][3] = elevation
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, matrix=matrix, is_si=False)

    def create_space(self, elevation: float, angle: float = 0.0) -> ifcopenshell.entity_instance:
        space = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSpace")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[space], relating_object=self.storey)
        self.place(space, elevation, angle)
        return space

    def assign_brep(self, space: ifcopenshell.entity_instance, height: float = 2500.0) -> None:
        """Extrude the L shape as a faceted brep, the way ArchiCAD exports spaces"""
        points = [(x, y, 0.0) for x, y in L_SHAPE] + [(x, y, height) for x, y in L_SHAPE]
        total = len(L_SHAPE)
        faces = [list(reversed(range(total))), list(range(total, total * 2))]
        faces += [[i, (i + 1) % total, (i + 1) % total + total, i + total] for i in range(total)]
        brep = self.builder.faceted_brep(points, faces)
        representation = self.builder.get_representation(self.body, [brep], "Brep")
        ifcopenshell.api.geometry.assign_representation(self.file, product=space, representation=representation)

    def assign_extrusion_with_a_void(self, space: ifcopenshell.entity_instance, height: float = 2500.0) -> None:
        outer_curve = self.builder.polyline(RECTANGLE, closed=True)
        inner_curve = self.builder.polyline(COLUMN, closed=True)
        profile = self.builder.profile(outer_curve, inner_curves=[inner_curve])
        extrusion = self.builder.extrude(profile, magnitude=height)
        representation = self.builder.get_representation(self.body, [extrusion], "SweptSolid")
        ifcopenshell.api.geometry.assign_representation(self.file, product=space, representation=representation)

    def run(self) -> None:
        ifcpatch.execute({"file": self.file, "recipe": "FixArchiCADToRevitSpaces", "arguments": []})

    def get_geometry(self, space: ifcopenshell.entity_instance) -> tuple[float, float]:
        """Get the SI volume and the SI absolute elevation of the bottom of a space"""
        shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), space)
        volume = ifcopenshell.util.shape.get_volume(shape.geometry)
        elevation = ifcopenshell.util.shape.get_shape_bottom_elevation(shape, shape.geometry)
        return volume, elevation

    def test_run(self):
        self.create_project()
        space = self.create_space(3500.0)
        self.assign_brep(space)

        assert self.get_geometry(space) == pytest.approx((L_SHAPE_AREA * 2.5, 3.5))
        self.run()
        # The space now starts at the storey and still ends where it used to.
        assert self.get_geometry(space) == pytest.approx((L_SHAPE_AREA * 3.0, 3.0))

        body = ifcopenshell.util.representation.get_representation(space, "Model", "Body")
        assert body.RepresentationType == "SweptSolid"
        assert len(body.Items) == 1
        assert body.Items[0].is_a("IfcExtrudedAreaSolid")
        # The brep it was converted from is purged, not left dangling.
        assert not self.file.by_type("IfcFacetedBrep")

    def test_extruding_from_the_storey_elevation(self):
        self.create_project()
        space = self.create_space(3500.0)
        self.assign_brep(space)
        self.run()

        extrusion = ifcopenshell.util.representation.get_representation(space, "Model", "Body").Items[0]
        # The space sits 500mm above its storey, so the profile drops by that much.
        assert extrusion.Position.Location.Coordinates == (0.0, 0.0, -500.0)
        assert extrusion.Depth == 3000.0

    def test_extruding_from_the_storey_elevation_of_a_rotated_space(self):
        self.create_project()
        space = self.create_space(3500.0, angle=np.radians(30.0))
        self.assign_brep(space)
        matrix = ifcopenshell.util.placement.get_local_placement(space.ObjectPlacement)
        self.run()

        assert self.get_geometry(space) == pytest.approx((L_SHAPE_AREA * 3.0, 3.0))
        # The rotation belongs to the placement and must survive untouched.
        assert np.allclose(ifcopenshell.util.placement.get_local_placement(space.ObjectPlacement), matrix)

    def test_falling_back_to_the_space_height_if_the_storey_is_above_the_space(self):
        self.create_project()
        # The space tops out at 1500mm, well below its storey at 3000mm, which
        # would otherwise ask for a negative extrusion depth.
        space = self.create_space(1000.0)
        self.assign_brep(space, height=500.0)
        self.run()

        assert self.get_geometry(space) == pytest.approx((L_SHAPE_AREA * 0.5, 3.0))

    def test_converting_a_column_in_a_space_into_a_profile_void(self):
        self.create_project()
        space = self.create_space(3500.0)
        self.assign_extrusion_with_a_void(space)
        self.run()

        assert self.get_geometry(space) == pytest.approx((RECTANGLE_AREA * 3.0, 3.0))
        profile = ifcopenshell.util.representation.get_representation(space, "Model", "Body").Items[0].SweptArea
        assert profile.is_a("IfcArbitraryProfileDefWithVoids")
        assert len(profile.InnerCurves) == 1

    def test_obscene_precision_makes_revit_convert_more_rooms(self):
        self.create_project()
        self.run()

        contexts = self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False)
        assert [c.Precision for c in contexts] == [10.0]

    def test_ignoring_spaces_without_a_body_representation(self):
        self.create_project()
        space = self.create_space(3500.0)
        self.run()

        assert space.Representation is None

    def test_ignoring_spaces_that_are_not_on_a_storey(self):
        self.create_project()
        space = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSpace")
        self.place(space, 3500.0)
        self.assign_brep(space)
        self.run()

        assert self.get_geometry(space) == pytest.approx((L_SHAPE_AREA * 2.5, 3.5))
        assert self.file.by_type("IfcFacetedBrep")


class TestFixArchiCADToRevitSpacesIFC2X3(test.bootstrap.IFC2X3, TestFixArchiCADToRevitSpaces):
    pass
