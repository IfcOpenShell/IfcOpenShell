# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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


import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.unit as subject
import test.bootstrap


class TestGetUnitSymbol(test.bootstrap.IFC4):
    def test_run(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        assert subject.get_unit_symbol(length) == "m"

    def test_a_nameless_unit_falls_back_to_a_placeholder_symbol(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = self.file.create_entity("IfcSIUnit", UnitType="LENGTHUNIT")
        assert length.Name is None
        assert subject.get_unit_symbol(length) == "?"

    def test_a_nameless_context_dependent_unit_falls_back_to_a_placeholder_symbol(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = self.file.create_entity("IfcContextDependentUnit", UnitType="USERDEFINED")
        assert unit.Name is None
        assert subject.get_unit_symbol(unit) == "?"


class TestGetFullUnitName(test.bootstrap.IFC4):
    def test_run(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        assert subject.get_full_unit_name(length) == "MILLIMETRE"

    def test_a_nameless_unit_falls_back_to_unknown(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = self.file.create_entity("IfcSIUnit", UnitType="LENGTHUNIT")
        assert length.Name is None
        assert subject.get_full_unit_name(length) == "UNKNOWN"


class TestConvertNamelessUnit(test.bootstrap.IFC4):
    def test_a_nameless_unit_does_not_crash(self):
        assert subject.convert(1, None, None, None, "METRE") == 1
        assert subject.convert(1, None, "METRE", None, None) == 1
        assert subject.convert(1, None, None, None, None) == 1
