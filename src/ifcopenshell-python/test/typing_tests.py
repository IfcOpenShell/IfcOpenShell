# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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
"""Typing tests for ifcopenshell.

This file should produce no warnings from type checker (currently pyright).
Those tests are not automatically checked and just there to make sure overloads are making sense.
"""

from typing import Union

from typing_extensions import assert_type

import ifcopenshell


def ifcopenshell_open_test(str_: str, bool_: bool):
    ifc_file = ifcopenshell.open(str_)
    assert_type(ifc_file, Union[ifcopenshell.file, ifcopenshell.sqlite])

    ifc_file = ifcopenshell.open(str_, should_stream=bool_)
    assert_type(ifc_file, Union[ifcopenshell.file, ifcopenshell.sqlite, ifcopenshell.stream])

    ifc_file = ifcopenshell.open(str_, should_stream=True)
    assert_type(ifc_file, ifcopenshell.stream)

    ifc_file = ifcopenshell.open(str_, readonly=True)


def get_inverse_test(ifc_file: ifcopenshell.file, inst: ifcopenshell.entity_instance, bool_: bool):
    # Default: allow_duplicate=False, with_attribute_indices=False
    result = ifc_file.get_inverse(inst)
    assert_type(result, set[ifcopenshell.entity_instance])

    # Explicit allow_duplicate=False
    result = ifc_file.get_inverse(inst, allow_duplicate=False)
    assert_type(result, set[ifcopenshell.entity_instance])

    # allow_duplicate=True without indices
    result = ifc_file.get_inverse(inst, allow_duplicate=True)
    assert_type(result, list[ifcopenshell.entity_instance])

    # allow_duplicate=True with indices
    result = ifc_file.get_inverse(inst, allow_duplicate=True, with_attribute_indices=True)
    assert_type(result, list[tuple[ifcopenshell.entity_instance, int]])

    # Dynamic bool values (falls back to generic overload)
    result = ifc_file.get_inverse(inst, allow_duplicate=bool_)
    assert_type(result, list[ifcopenshell.entity_instance] | set[ifcopenshell.entity_instance])
