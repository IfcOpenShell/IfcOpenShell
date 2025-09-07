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
from pytest import fixture
import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.unit


@pytest.fixture(scope="module")
def default_names_alignment():
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_conversion_based_unit(file, name="foot")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    coordinates = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
    radii = [(1000.0), (1250.0), (950.0)]
    vpoints = [(0.0, 100.0), (2000.0, 135.0), (5000.0, 105.0), (7400.0, 153.0), (9800.0, 105.0), (12800.0, 90.0)]
    lengths = [(1600.0), (1200.0), (2000.0), (800.0)]

    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        file, "TestAlignment", coordinates, radii, vpoints, lengths
    )
    yield alignment


def _hcallback(prev_segment, segment):
    if (prev_segment is None) and (segment is not None):
        label = "A"
    elif (prev_segment is not None) and (segment is None):
        label = "Z"
    else:
        label = "Q"
    return label


def _vcallback(prev_segment, segment):
    if (prev_segment is None) and (segment is not None):
        label = "a"
    elif (prev_segment is not None) and (segment is None):
        label = "z"
    else:
        label = "q"
    return label


@pytest.fixture(scope="module")
def callback_alignment():
    ifcopenshell.api.alignment.register_referent_name_callback(_hcallback, _vcallback, None)
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_conversion_based_unit(file, name="foot")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    coordinates = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
    radii = [(1000.0), (1250.0), (950.0)]
    vpoints = [(0.0, 100.0), (2000.0, 135.0), (5000.0, 105.0), (7400.0, 153.0), (9800.0, 105.0), (12800.0, 90.0)]
    lengths = [(1600.0), (1200.0), (2000.0), (800.0)]

    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        file, "TestAlignment", coordinates, radii, vpoints, lengths
    )
    yield alignment


def test_with_default_names(default_names_alignment):
    referent_nest = ifcopenshell.api.alignment.get_referent_nest(None, default_names_alignment)

    expected = ["P.O.B", "P.C.", "P.T.", "P.O.E.", "V.P.O.B.", "P.V.C.", "P.V.T.", "V.P.O.E"]
    for r in referent_nest.RelatedObjects:
        assert [x in r.Name for x in expected]


def test_with_callbacks(callback_alignment):
    referent_nest = ifcopenshell.api.alignment.get_referent_nest(None, callback_alignment)

    expected = ["A", "Q", "Z", "a", "q", "z"]
    for r in referent_nest.RelatedObjects:
        assert [x in r.Name for x in expected]
