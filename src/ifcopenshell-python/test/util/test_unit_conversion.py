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
import pathlib

import pytest

import ifcopenshell.util.unit

UNITS_FIXTURE_DIR = pathlib.Path(__file__).parent.parent / "fixtures" / "units"


@pytest.mark.parametrize("ifc_file", UNITS_FIXTURE_DIR.glob("*.ifc"))
def test_file_units_length_convert(ifc_file):
    f = ifcopenshell.open(ifc_file)
    project_unit = ifcopenshell.util.unit.get_project_unit(f, "LENGTHUNIT")
    if project_unit.Prefix == "MILLI":
        target_units = "METERS"
        scale = 0.001
    else:
        target_units = "MILLIMETERS"
        scale = 1000

    new_f = ifcopenshell.util.unit.convert_file_length_units(f, target_units)

    for element, attr, val in ifcopenshell.util.unit.iter_element_and_attributes_per_type(new_f, "IfcLengthMeasure"):
        elem_id = element.id()
        original_element = f.by_id(elem_id)
        original_val = getattr(original_element, attr.name())
        if isinstance(original_val, tuple):
            # assert element is equal to original element times scale
            assert val == tuple([v * scale for v in original_val])
        else:
            # assert element is equal to original element times scale
            assert val == original_val * scale
