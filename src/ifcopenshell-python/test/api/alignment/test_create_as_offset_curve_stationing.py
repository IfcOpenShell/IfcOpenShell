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

import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit
import ifcopenshell.util.element


def test_create_as_offset_curve_honors_start_station_with_a_stationing_referent():
    # create_as_offset_curve() accepted start_station but silently dropped it -- unlike every
    # other create path (create(), create_by_pi_method()), it never established the alignment's
    # stationing referent.
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])

    # the basis alignment only needs a real (if empty) Axis representation for
    # IfcPointByDistanceExpression.BasisCurve to reference -- no real segments needed.
    basis_alignment = ifcopenshell.api.alignment.create(file, "Basis", include_geometry=True)
    basis_curve = ifcopenshell.api.alignment.get_curve(basis_alignment)
    assert basis_curve.is_a("IfcCompositeCurve")

    offsets = [
        file.createIfcPointByDistanceExpression(
            DistanceAlong=file.createIfcLengthMeasure(0.0), OffsetLateral=10.0, BasisCurve=basis_curve
        ),
    ]

    offset_alignment = ifcopenshell.api.alignment.create_as_offset_curve(file, "Offset", offsets, start_station=1000.0)

    curve = ifcopenshell.api.alignment.get_curve(offset_alignment)
    assert curve.is_a("IfcOffsetCurveByDistances")

    # the referent must be created even though the basis curve has no segments yet, so there is
    # nothing to build a linear placement on -- it falls back to a plain IfcLocalPlacement, same as
    # when there's no representation at all.
    referent_nest = ifcopenshell.api.alignment.get_stationing_nest(file, offset_alignment)
    assert referent_nest is not None
    assert len(referent_nest.RelatedObjects) == 1

    referent = referent_nest.RelatedObjects[0]
    assert referent.is_a("IfcReferent")
    assert referent.PredefinedType == "STATION"
    assert referent.ObjectPlacement is not None
    assert referent.ObjectPlacement.is_a("IfcLocalPlacement")
    assert ifcopenshell.util.element.get_pset(referent, name="Pset_Stationing", prop="Station") == 1000.0


def test_create_as_offset_curve_default_start_station_is_zero():
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])

    basis_alignment = ifcopenshell.api.alignment.create(file, "Basis", include_geometry=True)
    basis_curve = ifcopenshell.api.alignment.get_curve(basis_alignment)

    offsets = [
        file.createIfcPointByDistanceExpression(
            DistanceAlong=file.createIfcLengthMeasure(0.0), OffsetLateral=10.0, BasisCurve=basis_curve
        ),
    ]

    offset_alignment = ifcopenshell.api.alignment.create_as_offset_curve(file, "Offset", offsets)

    referent_nest = ifcopenshell.api.alignment.get_stationing_nest(file, offset_alignment)
    assert referent_nest is not None
    referent = referent_nest.RelatedObjects[0]
    assert ifcopenshell.util.element.get_pset(referent, name="Pset_Stationing", prop="Station") == 0.0


def test_offset_curve_stationing_referent_is_placed_on_the_offset_curve():
    # with real geometry to offset from, the referent gets a linear placement on the offset curve
    # itself (distance along its basis curve, then offset), not a local placement at the origin
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])

    basis_alignment = ifcopenshell.api.alignment.create_by_pi_method(
        file, "Basis", hpoints=[(0.0, 0.0), (100.0, 0.0)], radii=[], vpoints=[], lengths=[]
    )
    basis_curve = ifcopenshell.api.alignment.get_basis_curve(basis_alignment)

    offsets = [
        file.createIfcPointByDistanceExpression(
            DistanceAlong=file.createIfcLengthMeasure(0.0), OffsetLateral=10.0, BasisCurve=basis_curve
        ),
    ]
    offset_alignment = ifcopenshell.api.alignment.create_as_offset_curve(file, "Offset", offsets)
    offset_curve = ifcopenshell.api.alignment.get_curve(offset_alignment)

    # an offset of the offset curve resolves through both to the same basis geometry
    offset_of_offset = ifcopenshell.api.alignment.create_as_offset_curve(
        file,
        "Offset of offset",
        [
            file.createIfcPointByDistanceExpression(
                DistanceAlong=file.createIfcLengthMeasure(0.0), OffsetLateral=5.0, BasisCurve=offset_curve
            )
        ],
    )

    for alignment, curve, y in (
        (offset_alignment, offset_curve, 10.0),
        (offset_of_offset, ifcopenshell.api.alignment.get_curve(offset_of_offset), 15.0),
    ):
        referent = ifcopenshell.api.alignment.add_stationing_referent(file, "0+050", alignment, 50.0, 50.0)
        placement = referent.ObjectPlacement
        assert placement.is_a("IfcLinearPlacement")
        assert placement.RelativePlacement.Location.BasisCurve == curve
        assert placement.CartesianPosition.Location.Coordinates == pytest.approx((50.0, y, 0.0))


test_create_as_offset_curve_honors_start_station_with_a_stationing_referent()
test_create_as_offset_curve_default_start_station_is_zero()
test_offset_curve_stationing_referent_is_placed_on_the_offset_curve()
