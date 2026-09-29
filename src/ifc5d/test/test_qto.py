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
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.element
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


class TestGetQuantityMeasures:
    def test_resolves_measures_from_the_calculator_function_table(self):
        measures = ifc5d.qto.get_quantity_measures(ifc5d.qto.rules["IFC4X3QtoBaseQuantities"])
        assert measures["Qto_WallBaseQuantities"]["Length"] == "IfcLengthMeasure"
        assert measures["Qto_WallBaseQuantities"]["NetWeight"] == "IfcMassMeasure"


class TestEditQtos:
    def setup_method(self):
        self.file = ifcopenshell.file(schema="IFC4X3")
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject", name="Test")
        self.wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")

    def get_quantity(self, name: str) -> ifcopenshell.entity_instance:
        pset = ifcopenshell.util.element.get_pset(self.wall, "Qto_WallBaseQuantities", should_inherit=False)
        qto = self.file.by_id(pset["id"])
        return next(q for q in qto.Quantities if q.Name == name)

    def test_new_quantity_with_no_target_unit_is_a_bare_value(self):
        metre = self.file.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")
        ifcopenshell.api.unit.assign_unit(self.file, units=[metre])

        ifc5d.qto.edit_qtos(self.file, {self.wall: {"Qto_WallBaseQuantities": {"Length": 5.0}}})

        quantity = self.get_quantity("Length")
        assert quantity.LengthValue == pytest.approx(5.0)
        assert quantity.Unit is None

    def test_existing_manual_unit_override_is_reconverted_not_left_stale(self):
        metre = self.file.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")
        ifcopenshell.api.unit.assign_unit(self.file, units=[metre])
        millimetre = self.file.createIfcSIUnit(None, "LENGTHUNIT", "MILLI", "METRE")

        ifc5d.qto.edit_qtos(self.file, {self.wall: {"Qto_WallBaseQuantities": {"Length": 5.0}}})
        quantity = self.get_quantity("Length")
        # Simulate a user picking a millimetre override via the per-property picker.
        quantity.Unit = millimetre
        quantity.LengthValue = 5000.0

        # Re-running take-off recomputes the value in the project default (metres) again --
        # this must not leave the recomputed metres value mislabeled as millimetres.
        ifc5d.qto.edit_qtos(self.file, {self.wall: {"Qto_WallBaseQuantities": {"Length": 6.0}}})

        quantity = self.get_quantity("Length")
        assert quantity.Unit == millimetre
        assert quantity.LengthValue == pytest.approx(6000.0)

    def test_target_unit_applies_only_to_brand_new_quantities(self):
        metre = self.file.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")
        ifcopenshell.api.unit.assign_unit(self.file, units=[metre])
        millimetre = self.file.createIfcSIUnit(None, "LENGTHUNIT", "MILLI", "METRE")
        rules = {"calculators": {"IfcOpenShell": {"IfcWall": {"Qto_WallBaseQuantities": {"Length": "net_get_x"}}}}}

        ifc5d.qto.edit_qtos(
            self.file,
            {self.wall: {"Qto_WallBaseQuantities": {"Length": 5.0}}},
            target_units={"IfcLengthMeasure": millimetre},
            rules=rules,
        )

        quantity = self.get_quantity("Length")
        assert quantity.Unit == millimetre
        assert quantity.LengthValue == pytest.approx(5000.0)

    def test_target_units_are_ignored_without_rules(self):
        metre = self.file.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")
        ifcopenshell.api.unit.assign_unit(self.file, units=[metre])
        millimetre = self.file.createIfcSIUnit(None, "LENGTHUNIT", "MILLI", "METRE")

        # `rules` is required to resolve a quantity's measure class -- without it, target_units
        # has nothing to key off, so brand new quantities fall back to today's bare-float path.
        ifc5d.qto.edit_qtos(
            self.file,
            {self.wall: {"Qto_WallBaseQuantities": {"Length": 5.0}}},
            target_units={"IfcLengthMeasure": millimetre},
        )

        quantity = self.get_quantity("Length")
        assert quantity.Unit is None
        assert quantity.LengthValue == pytest.approx(5.0)

    def test_reconvert_treats_a_missing_project_default_as_raw_si(self):
        # No LENGTHUNIT is assigned to the project at all, so SI2ProjectUnitConverter.convert()
        # would have left the calculated value as raw SI (metres) -- _reconvert must match.
        millimetre = self.file.createIfcSIUnit(None, "LENGTHUNIT", "MILLI", "METRE")
        rules = {"calculators": {"IfcOpenShell": {"IfcWall": {"Qto_WallBaseQuantities": {"Length": "net_get_x"}}}}}

        ifc5d.qto.edit_qtos(
            self.file,
            {self.wall: {"Qto_WallBaseQuantities": {"Length": 5.0}}},
            target_units={"IfcLengthMeasure": millimetre},
            rules=rules,
        )

        quantity = self.get_quantity("Length")
        assert quantity.LengthValue == pytest.approx(5000.0)


class TestEditQtosIntegration:
    """A real quantify() + edit_qtos() round trip, guarding against edit_qto's own
    class-inference disagreeing with get_quantity_measures()'s notion of measure.
    """

    def test_target_unit_produces_the_correct_quantity_class(self):
        file = ifcopenshell.file(schema="IFC4X3")
        ifcopenshell.api.root.create_entity(file, ifc_class="IfcProject", name="Test")
        metre = file.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")
        sqm = file.createIfcSIUnit(None, "AREAUNIT", None, "SQUARE_METRE")
        cum = file.createIfcSIUnit(None, "VOLUMEUNIT", None, "CUBIC_METRE")
        ifcopenshell.api.unit.assign_unit(file, units=[metre, sqm, cum])
        model = ifcopenshell.api.context.add_context(file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )

        wall = ifcopenshell.api.root.create_entity(file, ifc_class="IfcWall")
        wall.ObjectPlacement = file.createIfcLocalPlacement(
            None, file.createIfcAxis2Placement3D(file.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        )
        profile = file.createIfcRectangleProfileDef("AREA", None, None, 5.0, 0.2)
        position = file.createIfcAxis2Placement3D(file.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        solid = file.createIfcExtrudedAreaSolid(profile, position, file.createIfcDirection((0.0, 0.0, 1.0)), 3.0)
        rep = file.createIfcShapeRepresentation(body, "Body", "SweptSolid", [solid])
        wall.Representation = file.createIfcProductDefinitionShape(None, None, [rep])

        millimetre = file.createIfcSIUnit(None, "LENGTHUNIT", "MILLI", "METRE")
        rules = ifc5d.qto.rules["IFC4X3QtoBaseQuantities"]
        results = ifc5d.qto.quantify(file, {wall}, rules)
        ifc5d.qto.edit_qtos(file, results, target_units={"IfcLengthMeasure": millimetre}, rules=rules)

        pset = ifcopenshell.util.element.get_pset(wall, "Qto_WallBaseQuantities", should_inherit=False)
        qto = file.by_id(pset["id"])
        length = next(q for q in qto.Quantities if q.Name == "Length")
        assert length.is_a("IfcQuantityLength")
        assert length.Unit == millimetre
        assert length.LengthValue == pytest.approx(5000.0)
