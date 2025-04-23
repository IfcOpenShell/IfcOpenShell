# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import test.bootstrap
import ifcopenshell.api
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.unit
import ifcpatch


class TestConvertLengthUnit(test.bootstrap.IFC4):
    # NOTE: conversion itself is covered by `ifcopenshell.util.unit.convert_file_length_units` tests
    def test_run(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        output = ifcpatch.execute(
            {"input": "input.ifc", "file": self.file, "recipe": "ConvertLengthUnit", "arguments": ["METER"]}
        )
        unit = ifcopenshell.util.unit.get_project_unit(output, "LENGTHUNIT")
        assert ifcopenshell.util.unit.get_full_unit_name(unit) == "METRE"


class TestConvertLengthUnitIFC2X3(test.bootstrap.IFC2X3, TestConvertLengthUnit):
    pass
