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
import pytest

import ifc5d.qto


class TestGeographicElementQuantities:
    def test_a_geographic_element_gets_a_custom_base_quantity_set(self):
        file = ifcopenshell.file(schema="IFC4X3")
        ifcopenshell.api.root.create_entity(file, ifc_class="IfcProject", name="Test")
        ifcopenshell.api.unit.assign_unit(file, length={"is_metric": True, "raw": "METERS"})
        model = ifcopenshell.api.context.add_context(file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        element = ifcopenshell.api.root.create_entity(file, ifc_class="IfcGeographicElement")
        element.ObjectPlacement = file.createIfcLocalPlacement(
            None, file.createIfcAxis2Placement3D(file.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        )
        profile = file.createIfcRectangleProfileDef("AREA", None, None, 4.0, 2.0)
        position = file.createIfcAxis2Placement3D(file.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        solid = file.createIfcExtrudedAreaSolid(profile, position, file.createIfcDirection((0.0, 0.0, 1.0)), 1.0)
        rep = file.createIfcShapeRepresentation(body, "Body", "SweptSolid", [solid])
        element.Representation = file.createIfcProductDefinitionShape(None, None, [rep])

        results = ifc5d.qto.quantify(file, {element}, ifc5d.qto.rules["IFC4X3QtoBaseQuantities"])

        assert results[element]["EQto_GeographicElementBaseQuantities"] == {
            "Depth": pytest.approx(1.0),
            "GrossArea": pytest.approx(8.0),
            "GrossVolume": pytest.approx(8.0),
            "NetArea": pytest.approx(8.0),
            "NetVolume": pytest.approx(8.0),
            "Perimeter": pytest.approx(12.0),
        }
