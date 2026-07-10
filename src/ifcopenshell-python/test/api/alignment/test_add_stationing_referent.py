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


def _create_test_file():
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
    return file


def _create_test_alignment_with_vertical(file):
    # include_vertical=True so that get_curve() (IfcGradientCurve, on the "Axis" representation)
    # and get_basis_curve() (IfcCompositeCurve, on the "FootPrint" representation) are different
    # entities, letting the on_basis_curve option be observed.
    alignment = ifcopenshell.api.alignment.create(file, "TestAlignment", include_vertical=True, start_station=0.0)
    assert ifcopenshell.api.alignment.get_basis_curve(alignment).is_a("IfcCompositeCurve")
    assert ifcopenshell.api.alignment.get_curve(alignment).is_a("IfcGradientCurve")
    assert ifcopenshell.api.alignment.get_basis_curve(alignment) != ifcopenshell.api.alignment.get_curve(alignment)
    return alignment


def _assert_common_referent_asserts(referent, name, station):
    assert referent.is_a("IfcReferent")
    assert referent.PredefinedType == "STATION"
    assert referent.Name == name
    assert ifcopenshell.util.element.get_pset(element=referent, name="Pset_Stationing")
    assert ifcopenshell.util.element.get_pset(element=referent, name="Pset_Stationing", prop="Station") == station
    assert referent.ObjectPlacement != None


def test_add_stationing_referent_on_basis_curve_none_defaults_to_basis_curve():
    # on_basis_curve=None should behave the same as on_basis_curve=True
    file = _create_test_file()
    alignment = _create_test_alignment_with_vertical(file)

    referent = ifcopenshell.api.alignment.add_stationing_referent(
        file, "1+00.000", alignment, distance_along=100.0, station=100.0, on_basis_curve=None
    )

    _assert_common_referent_asserts(referent, "1+00.000", 100.0)

    assert referent.ObjectPlacement.is_a("IfcLinearPlacement")
    assert referent.ObjectPlacement.RelativePlacement.Location.BasisCurve == ifcopenshell.api.alignment.get_basis_curve(
        alignment
    )


def test_add_stationing_referent_on_basis_curve_true():
    file = _create_test_file()
    alignment = _create_test_alignment_with_vertical(file)

    referent = ifcopenshell.api.alignment.add_stationing_referent(
        file, "1+00.000", alignment, distance_along=100.0, station=100.0, on_basis_curve=True
    )

    _assert_common_referent_asserts(referent, "1+00.000", 100.0)

    assert referent.ObjectPlacement.is_a("IfcLinearPlacement")
    assert referent.ObjectPlacement.RelativePlacement.Location.BasisCurve == ifcopenshell.api.alignment.get_basis_curve(
        alignment
    )


def test_add_stationing_referent_on_basis_curve_false():
    # with a vertical layout present, on_basis_curve=False positions the referent on the
    # alignment curve (IfcGradientCurve) rather than on the basis curve (IfcCompositeCurve).
    file = _create_test_file()
    alignment = _create_test_alignment_with_vertical(file)

    referent = ifcopenshell.api.alignment.add_stationing_referent(
        file, "1+00.000", alignment, distance_along=100.0, station=100.0, on_basis_curve=False
    )

    _assert_common_referent_asserts(referent, "1+00.000", 100.0)

    assert referent.ObjectPlacement.is_a("IfcLinearPlacement")
    basis_curve = referent.ObjectPlacement.RelativePlacement.Location.BasisCurve
    assert basis_curve == ifcopenshell.api.alignment.get_curve(alignment)
    assert basis_curve != ifcopenshell.api.alignment.get_basis_curve(alignment)


test_add_stationing_referent_on_basis_curve_none_defaults_to_basis_curve()
test_add_stationing_referent_on_basis_curve_true()
test_add_stationing_referent_on_basis_curve_false()
