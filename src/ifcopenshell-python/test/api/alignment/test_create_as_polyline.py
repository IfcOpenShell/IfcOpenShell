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
import ifcopenshell.api.unit
import ifcopenshell.util.element


def test_create_as_polyline():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])

    points = [
        file.createIfcCartesianPoint((945.2, 583.6, 50.0)),
        file.createIfcCartesianPoint((756.3, 871.7, 66.2)),
        file.createIfcCartesianPoint((567.4, 1159.7, 78.5)),
        file.createIfcCartesianPoint((379.4, 1448.3, 86.8)),
        file.createIfcCartesianPoint((201.7, 1743.3, 91.1)),
        file.createIfcCartesianPoint((36.8, 2045.7, 91.3)),
        file.createIfcCartesianPoint((-118.9, 2353.0, 87.5)),
        file.createIfcCartesianPoint((-274.3, 2660.4, 79.7)),
        file.createIfcCartesianPoint((-429.6, 2967.8, 68.3)),
        file.createIfcCartesianPoint((-585.0, 3275.2, 56.2)),
    ]

    alignment = ifcopenshell.api.alignment.create_as_polyline(file, "A1", points, start_station=100.0)
    curve = ifcopenshell.api.alignment.get_curve(alignment)
    assert curve.is_a("IfcPolyline")
    assert len(curve.Points) == 10

    # stationing referent's Name must include the alignment's own name, the
    # same "<alignment name> <station>" convention create() and
    # update_key_point_referents() use -- previously this reassigned the
    # local `name` variable (shadowing the "A1" parameter) to just the bare
    # station string, losing the alignment name entirely.
    referents = [r for r in ifcopenshell.util.element.get_components(alignment) if r.is_a("IfcReferent")]
    assert len(referents) == 1
    assert referents[0].Name == "A1 0+100.000"


test_create_as_polyline()
