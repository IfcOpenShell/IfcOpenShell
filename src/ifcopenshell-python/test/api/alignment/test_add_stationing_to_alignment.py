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


def test_add_stationing_to_alignment():
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

    referent_nest = ifcopenshell.api.alignment.get_referent_nest(file, alignment)
    referent = referent_nest.RelatedObjects[0]

    assert referent.PredefinedType == "STATION"
    assert referent.Name == "2+000.000"
    assert ifcopenshell.util.element.get_pset(element=referent, name="Pset_Stationing")
    assert ifcopenshell.util.element.get_pset(element=referent, name="Pset_Stationing", prop="Station") == 2000.0
    assert referent.ObjectPlacement != None

    # add a station equation at 1000 distance along. this is station 3+000 in coming and 4+000 outgoing.
    # this is a gap equation.
    second_referent = ifcopenshell.api.alignment.add_stationing_referent(
        file, "4+000.000", alignment, distance_along=1000.0, station=4000.0, incoming_station=3000.0
    )

    referent_nest = ifcopenshell.api.alignment.get_referent_nest(file, alignment)
    assert len(referent_nest.RelatedObjects) == 2

    assert second_referent == referent_nest.RelatedObjects[1]

    assert second_referent.PredefinedType == "STATION"
    assert second_referent.Name == "4+000.000"
    assert ifcopenshell.util.element.get_pset(element=second_referent, name="Pset_Stationing")
    assert ifcopenshell.util.element.get_pset(element=second_referent, name="Pset_Stationing", prop="Station") == 4000.0
    assert (
        ifcopenshell.util.element.get_pset(element=second_referent, name="Pset_Stationing", prop="IncomingStation")
        == 3000.0
    )
    assert second_referent.ObjectPlacement != None


test_add_stationing_to_alignment()
