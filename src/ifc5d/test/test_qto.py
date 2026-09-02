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
import ifcopenshell.guid
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


class TestWeightQuantities:
    """gross_get_weight/net_get_weight for a profile-based element with an
    opening (#6344): GROSS weight should prefer the authored
    Pset_ProfileMechanical.MassPerLength over a density*volume estimate, even
    when the element has openings, since GROSS ignores openings entirely."""

    def setup_method(self):
        self.file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject", name="Test")
        f = self.file
        units = [
            f.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE"),
            f.createIfcSIUnit(None, "AREAUNIT", None, "SQUARE_METRE"),
            f.createIfcSIUnit(None, "VOLUMEUNIT", None, "CUBIC_METRE"),
            f.createIfcSIUnit(None, "MASSUNIT", None, "GRAM"),
        ]
        ifcopenshell.api.unit.assign_unit(self.file, units=units)
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        self.body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )

    def test_gross_weight_prefers_profile_mass_over_density_when_voided(self):
        f = self.file

        # 0.1 x 0.2m rectangular profile extruded 2m along local Z: a beam.
        profile = f.createIfcRectangleProfileDef("AREA", "RectProfile", None, 0.1, 0.2)
        position = f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        solid = f.createIfcExtrudedAreaSolid(profile, position, f.createIfcDirection((0.0, 0.0, 1.0)), 2.0)
        rep = f.createIfcShapeRepresentation(self.body, "Body", "SweptSolid", [solid])

        beam = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBeam", name="Beam1")
        beam.ObjectPlacement = f.createIfcLocalPlacement(
            None, f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        )
        beam.Representation = f.createIfcProductDefinitionShape(None, None, [rep])

        # Authored manufacturer mass: 50 kg/m, deliberately different to density*area.
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

        # Steel density: 7850 kg/m3, so density-based gross weight would be 314kg,
        # clearly distinguishable from the 100kg profile-based value.
        material = ifcopenshell.api.material.add_material(f, name="Steel")
        ifcopenshell.api.material.assign_material(f, products=[beam], material=material)
        material_pset = ifcopenshell.api.pset.add_pset(f, product=material, name="Pset_MaterialCommon")
        ifcopenshell.api.pset.edit_pset(f, pset=material_pset, properties={"MassDensity": 7850.0})

        # A through-hole bolt hole voiding the beam, so has_openings(beam) is True.
        opening = ifcopenshell.api.root.create_entity(f, ifc_class="IfcOpeningElement", name="Hole")
        opening.ObjectPlacement = f.createIfcLocalPlacement(
            None, f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        )
        op_profile = f.createIfcRectangleProfileDef("AREA", None, None, 0.02, 0.02)
        op_position = f.createIfcAxis2Placement3D(
            f.createIfcCartesianPoint((-0.06, 0.0, 1.0)),
            f.createIfcDirection((1.0, 0.0, 0.0)),
            f.createIfcDirection((0.0, 1.0, 0.0)),
        )
        op_solid = f.createIfcExtrudedAreaSolid(op_profile, op_position, f.createIfcDirection((0.0, 0.0, 1.0)), 0.2)
        op_rep = f.createIfcShapeRepresentation(self.body, "Body", "SweptSolid", [op_solid])
        opening.Representation = f.createIfcProductDefinitionShape(None, None, [op_rep])
        f.createIfcRelVoidsElement(ifcopenshell.guid.new(), None, None, None, beam, opening)

        rules = {
            "calculators": {
                "IfcOpenShell": {
                    "IfcBeam": {
                        "Qto_BeamBaseQuantities": {
                            "GrossWeight": "gross_get_weight",
                            "NetWeight": "net_get_weight",
                        }
                    }
                }
            }
        }
        results = ifc5d.qto.quantify(self.file, {beam}, rules)
        quantities = results[beam]["Qto_BeamBaseQuantities"]

        # GROSS ignores openings entirely: it must use the authored MassPerLength
        # (50 kg/m * 2m = 100kg), not density * un-subtracted volume (314kg).
        assert quantities["GrossWeight"] == pytest.approx(100.0)
        # NET has an opening, so it correctly falls back to density * true net
        # volume (openings are not supported for the profile-based NET path).
        assert quantities["NetWeight"] == pytest.approx(7850.0 * (0.1 * 0.2 * 2 - 0.02 * 0.02 * 0.1))
