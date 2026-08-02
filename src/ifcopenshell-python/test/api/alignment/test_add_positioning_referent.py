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
import ifcopenshell.util.element


def test_add_positioning_referent():
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

    alignment = ifcopenshell.api.alignment.create(file, "TestAlignment", start_station=2000.0)

    horizontal_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    segment = ifcopenshell.api.alignment.get_layout_segments(horizontal_layout)[0]

    referent = ifcopenshell.api.alignment.add_positioning_referent(
        file, "P.C.", alignment, distance_along=0.0, station=2000.0, positioned_product=segment
    )

    assert referent.is_a("IfcReferent")
    assert referent.PredefinedType == "POSITION"
    assert referent.Name == "P.C."
    assert ifcopenshell.util.element.get_pset(element=referent, name="Pset_Stationing")
    assert ifcopenshell.util.element.get_pset(element=referent, name="Pset_Stationing", prop="Station") == 2000.0
    assert referent.ObjectPlacement != None

    assert len(referent.Positions) == 1
    rel_positions = referent.Positions[0]
    assert rel_positions.is_a("IfcRelPositions")
    assert rel_positions.RelatingPositioningElement == referent
    assert rel_positions.RelatedProducts == (segment,)


def test_add_positioning_referent_creates_separate_referent_per_call():
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

    alignment = ifcopenshell.api.alignment.create(file, "TestAlignment", start_station=2000.0)

    horizontal_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    segment = ifcopenshell.api.alignment.get_layout_segments(horizontal_layout)[0]

    first_referent = ifcopenshell.api.alignment.add_positioning_referent(
        file, "P.C.", alignment, distance_along=0.0, station=2000.0, positioned_product=segment
    )

    other_product = file.createIfcBuildingElementProxy(GlobalId=ifcopenshell.guid.new(), Name="Sign")
    second_referent = ifcopenshell.api.alignment.add_positioning_referent(
        file, "P.C.", alignment, distance_along=0.0, station=2000.0, positioned_product=other_product
    )

    # each call creates its own IfcReferent, each with its own IfcRelPositions to the product passed in
    assert first_referent != second_referent
    assert len(first_referent.Positions) == 1
    assert first_referent.Positions[0].RelatedProducts == (segment,)
    assert len(second_referent.Positions) == 1
    assert second_referent.Positions[0].RelatedProducts == (other_product,)


test_add_positioning_referent()
test_add_positioning_referent_creates_separate_referent_per_call()
