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
import ifcopenshell.guid
import pytest

import ifc5d.qto


class TestEarthworksCutQuantities:
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

    def create_box(self, ifc_class: str, size_x: float, size_y: float, size_z: float, origin):
        f = self.file
        element = ifcopenshell.api.root.create_entity(f, ifc_class=ifc_class)
        element.ObjectPlacement = f.createIfcLocalPlacement(
            None, f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
        )
        profile = f.createIfcRectangleProfileDef("AREA", None, None, size_x, size_y)
        position = f.createIfcAxis2Placement3D(
            f.createIfcCartesianPoint((origin[0] + size_x / 2, origin[1] + size_y / 2, origin[2])), None, None
        )
        solid = f.createIfcExtrudedAreaSolid(profile, position, f.createIfcDirection((0.0, 0.0, 1.0)), size_z)
        rep = f.createIfcShapeRepresentation(self.body, "Body", "SweptSolid", [solid])
        element.Representation = f.createIfcProductDefinitionShape(None, None, [rep])
        return element

    def void(self, host, cut):
        self.file.createIfcRelVoidsElement(ifcopenshell.guid.new(), None, None, None, host, cut)

    def quantify(self, cut) -> dict[str, float]:
        rules = ifc5d.qto.rules["IFC4X3QtoBaseQuantities"]
        results = ifc5d.qto.quantify(self.file, {cut}, rules)
        return results[cut]["Qto_EarthworksCutBaseQuantities"]

    def test_cut_voiding_a_host(self):
        host = self.create_box("IfcGeographicElement", 10.0, 10.0, 2.0, (0.0, 0.0, 0.0))
        cut = self.create_box("IfcEarthworksCut", 2.0, 2.0, 3.0, (4.0, 4.0, 1.0))
        self.void(host, cut)
        quantities = self.quantify(cut)
        assert quantities["UndisturbedVolume"] == pytest.approx(4.0)
        assert quantities["Depth"] == pytest.approx(1.0)
        assert quantities["Length"] == pytest.approx(2.0)
        assert quantities["Width"] == pytest.approx(2.0)

    def test_cut_on_host_with_several_voids_omits_the_volume(self):
        host = self.create_box("IfcGeographicElement", 10.0, 10.0, 2.0, (0.0, 0.0, 0.0))
        cut = self.create_box("IfcEarthworksCut", 2.0, 2.0, 3.0, (4.0, 4.0, 1.0))
        other = self.create_box("IfcEarthworksCut", 1.0, 1.0, 3.0, (1.0, 1.0, 1.0))
        self.void(host, cut)
        self.void(host, other)
        quantities = self.quantify(cut)
        assert "UndisturbedVolume" not in quantities
        assert quantities["Depth"] == pytest.approx(1.0)
        assert quantities["Length"] == pytest.approx(2.0)
        assert quantities["Width"] == pytest.approx(2.0)

    def test_cut_voiding_nothing_measures_its_own_shape(self):
        cut = self.create_box("IfcEarthworksCut", 2.0, 2.0, 3.0, (4.0, 4.0, 1.0))
        quantities = self.quantify(cut)
        assert quantities["UndisturbedVolume"] == pytest.approx(12.0)
        assert quantities["Depth"] == pytest.approx(3.0)
        assert quantities["Length"] == pytest.approx(2.0)
        assert quantities["Width"] == pytest.approx(2.0)
