# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Thomas Krijnen <thomas@aecgeeks.com>
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

import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.unit


def _test_horizontal():
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    alignment = ifcopenshell.api.alignment.create(file, "TestAlignment")
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    assert True == ifcopenshell.api.alignment.has_zero_length_segment(horizontal)


def _test_horizontal_vertical():
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    alignment = ifcopenshell.api.alignment.create(file, "TestAlignment", include_vertical=True)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    assert True == ifcopenshell.api.alignment.has_zero_length_segment(horizontal)
    vertical = ifcopenshell.api.alignment.get_vertical_layout(alignment)
    assert True == ifcopenshell.api.alignment.has_zero_length_segment(vertical)


def _test_horizontal_vertical_cant():
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    alignment = ifcopenshell.api.alignment.create(file, "TestAlignment", include_vertical=True, include_cant=True)
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    assert True == ifcopenshell.api.alignment.has_zero_length_segment(horizontal)
    vertical = ifcopenshell.api.alignment.get_vertical_layout(alignment)
    assert True == ifcopenshell.api.alignment.has_zero_length_segment(vertical)
    cant = ifcopenshell.api.alignment.get_cant_layout(alignment)
    assert True == ifcopenshell.api.alignment.has_zero_length_segment(cant)


def test_has_zero_length_segment():
    _test_horizontal()
    _test_horizontal_vertical()
    _test_horizontal_vertical_cant()


test_has_zero_length_segment()
