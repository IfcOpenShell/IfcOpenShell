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


class TestWeightUnitConversion:
    """get_weight() must land in the project's declared MassUnit, and its
    profile-based path must scale Depth (raw project length units) to SI
    metres before multiplying by an SI MassPerLength (kg/m). Both stages were
    silently skipping their unit conversion, only invisible for the common
    METRE/KILOGRAM combination."""

    def make_wall_cube(self, file, body, side: float) -> ifcopenshell.entity_instance:
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
