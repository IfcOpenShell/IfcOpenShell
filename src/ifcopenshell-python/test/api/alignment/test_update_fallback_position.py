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


def test_update_fallback_position():
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

    basis_curve = ifcopenshell.api.alignment.get_basis_curve(alignment)
    pde = file.createIfcPointByDistanceExpression(
        DistanceAlong=file.createIfcLengthMeasure(4500.0), OffsetLateral=20.0, BasisCurve=basis_curve
    )

    placement = file.createIfcAxis2PlacementLinear(
        Location=pde,
    )

    lp = file.createIfcLinearPlacement(RelativePlacement=placement)

    assert lp.CartesianPosition == None

    ifcopenshell.api.alignment.update_fallback_position(file, lp)

    assert lp.CartesianPosition != None
    assert lp.CartesianPosition.Location.Coordinates == pytest.approx((3781.0625905626425, 2663.2859940077856, 0.0))
    assert lp.CartesianPosition.RefDirection.DirectionRatios == pytest.approx(
        (0.22453152656315067, 0.9744668252840736, 0.0)
    )
    assert lp.CartesianPosition.Axis.DirectionRatios == pytest.approx((0.0, 0.0, 1.0))


test_update_fallback_position()
