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
import numpy as np

UNITS_FIXTURE_DIR = pathlib.Path(__file__).parent.parent / "fixtures" / "units"


@pytest.mark.parametrize("ifc_file", UNITS_FIXTURE_DIR.glob("*.ifc"))
def test_file_units_length_convert(ifc_file: str):
    f = ifcopenshell.open(ifc_file)

    def get_project_unit(f: ifcopenshell.file) -> str:
        unit = ifcopenshell.util.unit.get_project_unit(f, "LENGTHUNIT")
        return ifcopenshell.util.unit.get_full_unit_name(unit)

    base_project_unit = get_project_unit(f)
    target_units = ["MILLIMETRE", "METRE", "CENTIMETRE", "INCH", "FOOT"]

    def convert_file_and_test(f: ifcopenshell.file, project_unit: str, target_unit: str) -> ifcopenshell.file:
        scale = ifcopenshell.util.unit.convert(
            value=1,
            from_prefix=ifcopenshell.util.unit.get_prefix(project_unit),
            from_unit=ifcopenshell.util.unit.get_unit_name_universal(project_unit),
            to_prefix=ifcopenshell.util.unit.get_prefix(target_unit),
            to_unit=ifcopenshell.util.unit.get_unit_name_universal(target_unit),
        )
        new_f = ifcopenshell.util.unit.convert_file_length_units(f, target_unit)

        for element, attr, val in ifcopenshell.util.unit.iter_element_and_attributes_per_type(
            new_f, "IfcLengthMeasure"
        ):
            elem_id = element.id()
            original_element = f.by_id(elem_id)
            original_val = getattr(original_element, attr.name())

            def convert_value(value):
                if not isinstance(value, tuple):
                    return value * scale
                return tuple(convert_value(v) for v in value)

            # assert element is equal to original element times scale
            assert np.allclose([val], [convert_value(original_val)])

        assert get_project_unit(new_f) == target_unit
        return new_f

    for target_unit in target_units:
        new_f = convert_file_and_test(f, base_project_unit, target_unit)
        convert_file_and_test(new_f, target_unit, base_project_unit)
