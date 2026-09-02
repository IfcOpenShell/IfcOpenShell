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

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.feature
import ifcopenshell.api.root
import ifcopenshell.api.unit
import pytest

import ifc5d.qto


class TestOpeningQuantities:
    """Openings authored in a Z-up local frame, as produced by Bonsai (#6835)."""

    def setup_method(self):
        self.file = ifcopenshell.file(schema="IFC4X3")
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject", name="Test")
        f = self.file
        units = [
            f.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE"),
            f.createIfcSIUnit(None, "AREAUNIT", None, "SQUARE_METRE"),
            f.createIfcSIUnit(None, "VOLUMEUNIT", None, "CUBIC_METRE"),
        ]
        ifcopenshell.api.unit.assign_unit(self.file, units=units)
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        self.body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )

    def create_opening(self, profile_x: float, profile_y: float, position, extrude_dir, depth: float):
        f = self.file
        opening = ifcopenshell.api.root.create_entity(f, ifc_class="IfcOpeningElement")
        opening.ObjectPlacement = f.createIfcLocalPlacement(
            None, f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        )
        profile = f.createIfcRectangleProfileDef("AREA", None, None, profile_x, profile_y)
        solid = f.createIfcExtrudedAreaSolid(profile, position, f.createIfcDirection(extrude_dir), depth)
        rep = f.createIfcShapeRepresentation(self.body, "Body", "SweptSolid", [solid])
        opening.Representation = f.createIfcProductDefinitionShape(None, None, [rep])
        return opening

    def quantify(self, opening) -> dict[str, float]:
        rules = ifc5d.qto.rules["IFC4X3QtoBaseQuantities"]
        results = ifc5d.qto.quantify(self.file, {opening}, rules)
        return results[opening]["Qto_OpeningElementBaseQuantities"]

    def test_vertical_wall_opening(self):
        # A 0.9 x 2.0 door opening voiding a wall along +Y, with Bonsai's
        # oversized 1.2m void depth: local extents x=0.9, y=1.2, z=2.0.
        f = self.file
        position = f.createIfcAxis2Placement3D(
            f.createIfcCartesianPoint((0.0, -0.6, 1.0)),
            f.createIfcDirection((0.0, -1.0, 0.0)),
            f.createIfcDirection((1.0, 0.0, 0.0)),
        )
        opening = self.create_opening(0.9, 2.0, position, (0.0, 0.0, -1.0), 1.2)
        quantities = self.quantify(opening)
        assert quantities["Width"] == pytest.approx(0.9)
        assert quantities["Height"] == pytest.approx(2.0)
        assert quantities["Depth"] == pytest.approx(1.2)
        assert quantities["Area"] == pytest.approx(1.8)
        assert quantities["Volume"] == pytest.approx(2.16)

    def test_horizontal_slab_opening(self):
        # A 1.0 x 0.5 opening voiding a 0.3 thick slab: extents x=1.0, y=0.5, z=0.3.
        f = self.file
        position = f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        opening = self.create_opening(1.0, 0.5, position, (0.0, 0.0, -1.0), 0.3)
        quantities = self.quantify(opening)
        assert quantities["Width"] == pytest.approx(1.0)
        assert quantities["Height"] == pytest.approx(0.5)
        assert quantities["Depth"] == pytest.approx(0.3)
        assert quantities["Area"] == pytest.approx(0.5)
        assert quantities["Volume"] == pytest.approx(0.15)


class TestMemberLength:
    """Beam, column and member Length comes from the extrusion depth, not a bounding box."""

    CASES = [
        ("IfcBeam", "Qto_BeamBaseQuantities"),
        ("IfcColumn", "Qto_ColumnBaseQuantities"),
        ("IfcMember", "Qto_MemberBaseQuantities"),
    ]

    def setup_method(self):
        self.file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject", name="Test")
        f = self.file
        units = [
            f.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE"),
            f.createIfcSIUnit(None, "AREAUNIT", None, "SQUARE_METRE"),
            f.createIfcSIUnit(None, "VOLUMEUNIT", None, "CUBIC_METRE"),
        ]
        ifcopenshell.api.unit.assign_unit(self.file, units=units)
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        self.body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )

    def create_element(self, ifc_class, items):
        f = self.file
        element = ifcopenshell.api.root.create_entity(f, ifc_class=ifc_class)
        element.ObjectPlacement = f.createIfcLocalPlacement(
            None, f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        )
        rep = f.createIfcShapeRepresentation(self.body, "Body", "SweptSolid", items)
        element.Representation = f.createIfcProductDefinitionShape(None, None, [rep])
        return element

    def create_extruded(self, ifc_class, x, y, depth, direction=(0.0, 0.0, 1.0)):
        f = self.file
        profile = f.createIfcRectangleProfileDef("AREA", None, None, x, y)
        position = f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        solid = f.createIfcExtrudedAreaSolid(profile, position, f.createIfcDirection(direction), depth)
        return self.create_element(ifc_class, [solid])

    def length_of(self, element, qto_name):
        rules = ifc5d.qto.rules["IFC4QtoBaseQuantities"]
        results = ifc5d.qto.quantify(self.file, {element}, rules)
        return results[element][qto_name]["Length"]

    @pytest.mark.parametrize("ifc_class,qto_name", CASES)
    def test_squat_member_uses_extrusion_depth(self, ifc_class, qto_name):
        # A 1.0 x 1.0 m pedestal extruded only 0.3 m. The cross section is larger
        # than the run, so a bounding box maximum reports 1.0 instead of 0.3.
        element = self.create_extruded(ifc_class, 1.0, 1.0, 0.3)
        assert self.length_of(element, qto_name) == pytest.approx(0.3)

    @pytest.mark.parametrize("ifc_class,qto_name", CASES)
    def test_slender_member_is_unchanged(self, ifc_class, qto_name):
        element = self.create_extruded(ifc_class, 0.2, 0.4, 6.0)
        assert self.length_of(element, qto_name) == pytest.approx(6.0)

    def test_oblique_extrusion_direction(self):
        # Depth is the swept displacement, so it is the length whatever the
        # direction: here the solid only spans 0.3/sqrt(2) in local Y and Z.
        element = self.create_extruded("IfcBeam", 1.0, 1.0, 0.3, direction=(0.0, 1.0, 1.0))
        assert self.length_of(element, "Qto_BeamBaseQuantities") == pytest.approx(0.3)

    def test_tapered_extrusion(self):
        f = self.file
        start = f.createIfcRectangleProfileDef("AREA", None, None, 1.0, 1.0)
        end = f.createIfcRectangleProfileDef("AREA", None, None, 0.5, 0.5)
        position = f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        solid = f.createIfcExtrudedAreaSolidTapered(start, position, f.createIfcDirection((0.0, 0.0, 1.0)), 0.3, end)
        element = self.create_element("IfcColumn", [solid])
        assert self.length_of(element, "Qto_ColumnBaseQuantities") == pytest.approx(0.3)

    def test_opening_does_not_shorten_length(self):
        # A 6.0 m column with a void removing its top 1.0 m is still 6.0 m long.
        f = self.file
        element = self.create_extruded("IfcColumn", 0.2, 0.4, 6.0)
        opening = ifcopenshell.api.root.create_entity(f, ifc_class="IfcOpeningElement")
        opening.ObjectPlacement = f.createIfcLocalPlacement(
            None, f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 5.0)), None, None)
        )
        profile = f.createIfcRectangleProfileDef("AREA", None, None, 2.0, 2.0)
        position = f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        solid = f.createIfcExtrudedAreaSolid(profile, position, f.createIfcDirection((0.0, 0.0, 1.0)), 1.0)
        rep = f.createIfcShapeRepresentation(self.body, "Body", "SweptSolid", [solid])
        opening.Representation = f.createIfcProductDefinitionShape(None, None, [rep])
        ifcopenshell.api.feature.add_feature(f, feature=opening, element=element)
        assert self.length_of(element, "Qto_ColumnBaseQuantities") == pytest.approx(6.0)

    def test_arbitrary_profile_falls_back_to_bounding_box(self):
        # A 4.0 x 3.0 plate swept by its 0.05 thickness, as a stair stringer is
        # authored. The sweep is the thickness, not the length, so we do not
        # trust the depth and keep the previous heuristic.
        f = self.file
        points = [
            f.createIfcCartesianPoint((0.0, 0.0)),
            f.createIfcCartesianPoint((4.0, 0.0)),
            f.createIfcCartesianPoint((4.0, 3.0)),
            f.createIfcCartesianPoint((0.0, 3.0)),
            f.createIfcCartesianPoint((0.0, 0.0)),
        ]
        profile = f.createIfcArbitraryClosedProfileDef("AREA", None, f.createIfcPolyline(points))
        position = f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        solid = f.createIfcExtrudedAreaSolid(profile, position, f.createIfcDirection((0.0, 0.0, 1.0)), 0.05)
        element = self.create_element("IfcMember", [solid])
        assert self.length_of(element, "Qto_MemberBaseQuantities") == pytest.approx(4.0)

    def test_unsupported_representation_falls_back_to_bounding_box(self):
        # A swept disk has no extrusion depth. We keep the previous heuristic
        # rather than guess, so the value is the bounding box maximum.
        f = self.file
        points = f.createIfcCartesianPointList3D(((0.0, 0.0, 0.0), (0.0, 0.0, 2.0)))
        directrix = f.createIfcIndexedPolyCurve(points)
        solid = f.createIfcSweptDiskSolid(directrix, 0.1)
        element = self.create_element("IfcMember", [solid])
        assert self.length_of(element, "Qto_MemberBaseQuantities") == pytest.approx(2.0)
