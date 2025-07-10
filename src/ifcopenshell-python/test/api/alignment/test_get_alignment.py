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

import pytest
import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.unit


def test_get_alignment():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
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

    include_vertical = [False, True, True]
    include_cant = [False, False, True]

    for i in range(0, 3):
        ali = ifcopenshell.api.alignment.create(file, "A1", include_vertical[i], include_cant[i])
        assert ali != None

        horiz = ifcopenshell.api.alignment.get_horizontal_layout(ali)
        vert = ifcopenshell.api.alignment.get_vertical_layout(ali)
        cant = ifcopenshell.api.alignment.get_cant_layout(ali)

        assert ali == ifcopenshell.api.alignment.get_alignment(horiz)
        if include_vertical[i]:
            assert ali == ifcopenshell.api.alignment.get_alignment(vert)

        if include_cant[i]:
            assert ali == ifcopenshell.api.alignment.get_alignment(cant)
