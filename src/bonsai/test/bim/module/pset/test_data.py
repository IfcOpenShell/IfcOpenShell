# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.unit

import bonsai.tool as tool
from bonsai.bim.module.pset.data import Data
from test.bim.bootstrap import NewFile


def display_data(ifc, prop):
    return Data.property_display_data(ifc, prop.Name, {"id": prop.id(), "value": prop.NominalValue.wrappedValue})


class TestPropertyDisplayDataUnitUndefined(NewFile):
    """#10074: the read-only property list must distinguish a measure with no unit at all from
    one whose unit merely has no symbol to show."""

    def setup_file(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        return ifc

    def test_flags_a_measure_without_any_unit(self):
        ifc = self.setup_file()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcPressureMeasure(5.0))
        data = display_data(ifc, prop)
        assert data["UnitSymbol"] == ""
        assert data["UnitUndefined"] is True

    def test_does_not_flag_a_measure_with_a_project_default(self):
        ifc = self.setup_file()
        pascal = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="PRESSUREUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[pascal])
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcPressureMeasure(5.0))
        data = display_data(ifc, prop)
        assert data["UnitSymbol"] == "Pa"
        assert data["UnitUndefined"] is False

    def test_does_not_flag_a_non_measure(self):
        ifc = self.setup_file()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcLabel("Bar"))
        data = display_data(ifc, prop)
        assert data["UnitUndefined"] is False

    def test_does_not_flag_plain_attribute_values(self):
        ifc = self.setup_file()
        data = Data.property_display_data(ifc, "Foo", 5.0)
        assert data["UnitUndefined"] is False
