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
import ifcopenshell.api.material
import ifcopenshell.api.pset
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


class TestWeightUnitConversion:
    """get_weight() must land in the project's declared MassUnit, and its
    profile-based path must scale Depth (raw project length units) to SI
    metres before multiplying by an SI MassPerLength (kg/m). Both stages were
    silently skipping their unit conversion, only invisible for the common
    METRE/KILOGRAM combination."""

    def make_wall_cube(self, file, body, side: float) -> ifcopenshell.entity_instance:
        """A `side` x `side` x `side` cube-shaped wall (in raw project length units)."""
        f = file
        wall = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="TestWall")
        wall.ObjectPlacement = f.createIfcLocalPlacement(
            None, f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        )
        profile = f.createIfcRectangleProfileDef("AREA", None, None, side, side)
        position = f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        solid = f.createIfcExtrudedAreaSolid(profile, position, f.createIfcDirection((0.0, 0.0, 1.0)), side)
        rep = f.createIfcShapeRepresentation(body, "Body", "SweptSolid", [solid])
        wall.Representation = f.createIfcProductDefinitionShape(None, None, [rep])
        return wall

    def test_density_based_weight_converts_to_project_mass_unit(self):
        # A 1000mm cube (= 1 real m^3) of 7850 kg/m3 steel weighs 7850kg in
        # reality. The project's MassUnit is GRAM, so the stored NetWeight/
        # GrossWeight must be 7,850,000, not the raw SI-kilogram 7850.
        f = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="Test")
        units = [
            f.createIfcSIUnit(None, "LENGTHUNIT", "MILLI", "METRE"),
            f.createIfcSIUnit(None, "AREAUNIT", None, "SQUARE_METRE"),
            f.createIfcSIUnit(None, "VOLUMEUNIT", None, "CUBIC_METRE"),
            f.createIfcSIUnit(None, "MASSUNIT", None, "GRAM"),
        ]
        ifcopenshell.api.unit.assign_unit(f, units=units)
        model = ifcopenshell.api.context.add_context(f, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )

        wall = self.make_wall_cube(f, body, 1000.0)
        material = ifcopenshell.api.material.add_material(f, name="Steel")
        material_pset = ifcopenshell.api.pset.add_pset(f, product=material, name="Pset_MaterialCommon")
        ifcopenshell.api.pset.edit_pset(f, pset=material_pset, properties={"MassDensity": 7850.0})
        ifcopenshell.api.material.assign_material(f, products=[wall], material=material)

        rules = {
            "calculators": {
                "IfcOpenShell": {
                    "IfcWall": {
                        "Qto_WallBaseQuantities": {"NetWeight": "net_get_weight", "GrossWeight": "gross_get_weight"}
                    }
                }
            }
        }
        results = ifc5d.qto.quantify(f, {wall}, rules)
        quantities = results[wall]["Qto_WallBaseQuantities"]
        assert quantities["NetWeight"] == pytest.approx(7_850_000.0)
        assert quantities["GrossWeight"] == pytest.approx(7_850_000.0)

    def test_profile_based_weight_scales_depth_to_si(self):
        # A 100x200mm profile extruded 2000mm (= 2 real metres) with an
        # authored MassPerLength of 50 kg/m weighs 100kg in reality
        # (50 kg/m * 2m). The project's LengthUnit is MILLIMETRE, so Depth
        # (a raw 2000.0) must be scaled to SI metres before the multiply.
        f = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="Test")
        units = [
            f.createIfcSIUnit(None, "LENGTHUNIT", "MILLI", "METRE"),
            f.createIfcSIUnit(None, "AREAUNIT", None, "SQUARE_METRE"),
            f.createIfcSIUnit(None, "VOLUMEUNIT", None, "CUBIC_METRE"),
            f.createIfcSIUnit(None, "MASSUNIT", "KILO", "GRAM"),
        ]
        ifcopenshell.api.unit.assign_unit(f, units=units)
        model = ifcopenshell.api.context.add_context(f, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )

        beam = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBeam", name="Beam1")
        beam.ObjectPlacement = f.createIfcLocalPlacement(
            None, f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        )
        profile = f.createIfcRectangleProfileDef("AREA", "RectProfile", None, 100.0, 200.0)
        position = f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        solid = f.createIfcExtrudedAreaSolid(profile, position, f.createIfcDirection((0.0, 0.0, 1.0)), 2000.0)
        rep = f.createIfcShapeRepresentation(body, "Body", "SweptSolid", [solid])
        beam.Representation = f.createIfcProductDefinitionShape(None, None, [rep])

        f.create_entity(
            "IfcProfileProperties",
            Name="Pset_ProfileMechanical",
            ProfileDefinition=profile,
            Properties=[
                f.create_entity(
                    "IfcPropertySingleValue",
                    Name="MassPerLength",
                    NominalValue=f.create_entity("IfcMassPerLengthMeasure", 50.0),
                )
            ],
        )

        rules = {
            "calculators": {
                "IfcOpenShell": {"IfcBeam": {"Qto_BeamBaseQuantities": {"GrossWeight": "gross_get_weight"}}}
            }
        }
        results = ifc5d.qto.quantify(f, {beam}, rules)
        assert results[beam]["Qto_BeamBaseQuantities"]["GrossWeight"] == pytest.approx(100.0)
