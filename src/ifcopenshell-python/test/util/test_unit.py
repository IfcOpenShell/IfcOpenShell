# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

import tempfile
from math import pi
from pathlib import Path

import ifcpatch
import numpy as np
import pytest
from ifcpatch.recipes import Ifc2Sql

import ifcopenshell.api.context
import ifcopenshell.api.georeference
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.element
import ifcopenshell.util.geolocation
import ifcopenshell.util.unit as subject
import test.bootstrap
from ifcopenshell.util.shape_builder import ShapeBuilder


class TestMmToM:
    def test_converts_a_positive_value(self):
        assert subject.mm_to_m(150) == 0.15

    def test_returns_zero_for_zero(self):
        assert subject.mm_to_m(0) == 0.0

    def test_passes_through_negative_values(self):
        assert subject.mm_to_m(-25) == -0.025


class TestCacheUnits(test.bootstrap.IFC4):
    def test_run(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        assert self.file.units == {}
        subject.cache_units(self.file)
        assert self.file.units == {"LENGTHUNIT": length, "AREAUNIT": area}


class TestClearUnitCache(test.bootstrap.IFC4):
    def test_run(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        subject.cache_units(self.file)
        subject.clear_unit_cache(self.file)
        assert self.file.units == {}


class TestGetProjectUnit(test.bootstrap.IFC4):
    def test_run(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        assert subject.get_project_unit(self.file, "LENGTHUNIT") == length
        assert subject.get_project_unit(self.file, "AREAUNIT") == area

    def test_using_a_cache(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        length2 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="CENTI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        assert self.file.units == {}
        assert subject.get_project_unit(self.file, "LENGTHUNIT", use_cache=True) == length
        assert self.file.units == {"LENGTHUNIT": length, "AREAUNIT": area}
        ifcopenshell.api.unit.assign_unit(self.file, units=[length2])
        assert subject.get_project_unit(self.file, "LENGTHUNIT", use_cache=True) == length
        subject.clear_unit_cache(self.file)
        assert subject.get_project_unit(self.file, "LENGTHUNIT", use_cache=True) == length2
        assert self.file.units == {"LENGTHUNIT": length2, "AREAUNIT": area}

    def test_area_and_volume_derived_from_length_are_matched_dimensionally(self):
        # AREAUNIT/VOLUMEUNIT have no IfcDerivedUnitEnum member, so a project whose area/volume
        # default is an IfcDerivedUnit has no literal UnitType match for either -- get_project_unit
        # must still resolve them by dimensional analysis, like get_candidate_units already does.
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        area = ifcopenshell.api.unit.add_derived_unit(self.file, "USERDEFINED", "area-ish", {length: 2})
        volume = ifcopenshell.api.unit.add_derived_unit(self.file, "USERDEFINED", "volume-ish", {length: 3})
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area, volume])

        assert subject.get_project_unit(self.file, "AREAUNIT") == area
        assert subject.get_project_unit(self.file, "VOLUMEUNIT") == volume

    def test_literal_unit_type_match_takes_priority_over_dimensional(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        literal_area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        derived_area = ifcopenshell.api.unit.add_derived_unit(self.file, "USERDEFINED", "area-ish", {length: 2})
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, literal_area, derived_area])

        assert subject.get_project_unit(self.file, "AREAUNIT") == literal_area

    def test_dimensional_fallback_also_applies_when_using_a_cache(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        area = ifcopenshell.api.unit.add_derived_unit(self.file, "USERDEFINED", "area-ish", {length: 2})
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])

        assert subject.get_project_unit(self.file, "AREAUNIT", use_cache=True) == area
        assert self.file.units["AREAUNIT"] == area


class TestGetCandidateUnits(test.bootstrap.IFC4):
    def test_returns_only_units_matching_the_unit_type(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        mm = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        m = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        candidates = subject.get_candidate_units(self.file, "LENGTHUNIT")
        assert set(candidates) == {mm, m}
        assert area not in candidates

    def test_returns_all_matching_units_not_just_the_assigned_default(self):
        # Unlike get_project_unit, which only returns the one assigned default.
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        mm = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        m = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[mm])
        assert subject.get_project_unit(self.file, "LENGTHUNIT") == mm
        assert set(subject.get_candidate_units(self.file, "LENGTHUNIT")) == {mm, m}

    def test_derived_unit_matched_by_literal_unit_type(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        force = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="FORCEUNIT")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        modulus = ifcopenshell.api.unit.add_derived_unit(
            self.file, "MODULUSOFELASTICITYUNIT", None, {force: 1, area: -1}
        )
        assert subject.get_candidate_units(self.file, "MODULUSOFELASTICITYUNIT") == [modulus]

    def test_userdefined_derived_unit_matched_by_dimensional_fallback(self):
        # No literal UnitType match (USERDEFINED), but dimensionally it's a pressure unit,
        # and PRESSUREUNIT is one of the core families covered by named_dimensions.
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        force = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="FORCEUNIT")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        weird_pressure = ifcopenshell.api.unit.add_derived_unit(
            self.file, "USERDEFINED", "pressure-ish", {force: 1, area: -1}
        )
        assert subject.get_candidate_units(self.file, "PRESSUREUNIT") == [weird_pressure]

    def test_empty_when_nothing_matches(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        assert subject.get_candidate_units(self.file, "MASSUNIT") == []


class TestGetPropertyUnit(test.bootstrap.IFC4):
    def test_no_unit(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        prop = self.file.createIfcQuantityLength(Name="Foo", LengthValue=42.0)
        assert subject.get_property_unit(prop, self.file) is None

    def test_simple_quantity(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        length2 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="CENTI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        prop = self.file.createIfcQuantityLength(Name="Foo", LengthValue=42.0)
        assert subject.get_property_unit(prop, self.file) == length
        prop.Unit = length2
        assert subject.get_property_unit(prop, self.file) == length2

    def test_single_value(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        length2 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="CENTI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        prop = self.file.createIfcPropertySingleValue(Name="Foo", NominalValue=self.file.createIfcLengthMeasure(42.0))
        assert subject.get_property_unit(prop, self.file) == length
        prop.Unit = length2
        assert subject.get_property_unit(prop, self.file) == length2

    def test_single_value_with_no_nominal_value(self):
        # NominalValue is optional -- a property may be null. Must not crash.
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        prop = self.file.createIfcPropertySingleValue(Name="Foo", NominalValue=None)
        assert subject.get_property_unit(prop, self.file) is None

    def test_enumerated_value(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        length2 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="CENTI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        prop = self.file.createIfcPropertyEnumeratedValue(
            Name="Foo", EnumerationValues=[self.file.createIfcLengthMeasure(42.0)]
        )
        assert subject.get_property_unit(prop, self.file) == length
        prop.EnumerationValues = []
        prop.EnumerationReference = self.file.createIfcPropertyEnumeration(
            "Foo", [self.file.createIfcAreaMeasure(42.0)]
        )
        assert subject.get_property_unit(prop, self.file) == area
        prop.EnumerationReference = self.file.createIfcPropertyEnumeration(
            "Foo", [self.file.createIfcAreaMeasure(42.0)], Unit=length2
        )
        assert subject.get_property_unit(prop, self.file) == length2
        prop.EnumerationValues = [self.file.createIfcAreaMeasure(42.0)]
        assert subject.get_property_unit(prop, self.file) == length2
        prop.EnumerationReference.Unit = None
        assert subject.get_property_unit(prop, self.file) == area

    def test_list_value(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        length2 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="CENTI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        prop = self.file.createIfcPropertyListValue(Name="Foo", ListValues=[self.file.createIfcLengthMeasure(42.0)])
        assert subject.get_property_unit(prop, self.file) == length
        prop.Unit = length2
        assert subject.get_property_unit(prop, self.file) == length2
        prop.Unit = None
        prop.ListValues = []
        assert subject.get_property_unit(prop, self.file) is None

    def test_bounded_value(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        length2 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="CENTI")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length, area])
        prop = self.file.createIfcPropertyBoundedValue(Name="Foo")
        assert subject.get_property_unit(prop, self.file) is None
        prop.UpperBoundValue = self.file.createIfcLengthMeasure(42.0)
        assert subject.get_property_unit(prop, self.file) == length
        prop.UpperBoundValue = None
        prop.LowerBoundValue = self.file.createIfcLengthMeasure(42.0)
        assert subject.get_property_unit(prop, self.file) == length
        prop.LowerBoundValue = None
        prop.SetPointValue = self.file.createIfcLengthMeasure(42.0)
        assert subject.get_property_unit(prop, self.file) == length
        prop.Unit = length2
        assert subject.get_property_unit(prop, self.file) == length2


class TestConvert(test.bootstrap.IFC4):
    def test_run(self):
        assert subject.convert(1, None, "METRE", None, "METRE") == 1
        assert subject.convert(1, None, "METRE", "MILLI", "METRE") == 1000
        assert subject.convert(1000, "MILLI", "METRE", None, "METRE") == 1
        assert subject.convert(1, None, "SQUARE_METRE", None, "SQUARE_METRE") == 1
        assert subject.convert(1, None, "SQUARE_METRE", "MILLI", "SQUARE_METRE") == 1000000
        assert subject.convert(1, None, "CUBIC_METRE", "MILLI", "CUBIC_METRE") == 1000000000


class TestCalculateUnitScale(test.bootstrap.IFC4):
    def test_prefix_and_conversion_based_units_are_considered(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_conversion_based_unit(self.file, name="foot")
        length.ConversionFactor.UnitComponent.Prefix = "MILLI"
        ifcopenshell.api.unit.assign_unit(self.file, units=[length])
        assert subject.calculate_unit_scale(self.file) == 0.3048 * 0.001

        angle = ifcopenshell.api.unit.add_conversion_based_unit(self.file, name="degree")
        angle.ConversionFactor.UnitComponent.Prefix = "MILLI"
        ifcopenshell.api.unit.assign_unit(self.file, units=[angle])
        assert subject.calculate_unit_scale(self.file, "PLANEANGLEUNIT") == pi / 180 * 0.001

    def test_derived_units_are_considered(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        force = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="FORCEUNIT")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT", prefix="MILLI")
        modulus = ifcopenshell.api.unit.add_derived_unit(
            self.file, "MODULUSOFELASTICITYUNIT", None, {force: 1, area: -1}
        )
        ifcopenshell.api.unit.assign_unit(self.file, units=[modulus])
        # AREAUNIT is a pure power of length, so its MILLI prefix is raised to
        # the length exponent (2) per #9278: (1e-3)**2 = 1e-6, inverted by the
        # derived unit's -1 exponent to give 1e6.
        assert subject.calculate_unit_scale(self.file, "MODULUSOFELASTICITYUNIT") == pytest.approx(1_000_000.0)

    def test_prefix_is_raised_to_the_length_exponent_for_area_and_volume(self):
        # A prefixed square/cubic metre is (prefix-metre) squared/cubed:
        # DECI SQUARE_METRE = dm2 = 1e-2 m2, DECI CUBIC_METRE = dm3 (litre) = 1e-3 m3.
        # https://github.com/IfcOpenShell/IfcOpenShell/issues/9278
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        area.Prefix = "DECI"
        volume = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="VOLUMEUNIT")
        volume.Prefix = "DECI"
        ifcopenshell.api.unit.assign_unit(self.file, units=[area, volume])
        assert subject.calculate_unit_scale(self.file, "AREAUNIT") == pytest.approx(0.1**2)
        assert subject.calculate_unit_scale(self.file, "VOLUMEUNIT") == pytest.approx(0.1**3)

    def test_prefix_stays_linear_for_units_that_are_not_a_pure_power_of_length(self):
        # For derived and non-length SI units the prefix scales the unit itself:
        # KILO PASCAL = 1e3 Pa, KILO GRAM = 1e3 g.
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        pressure = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="PRESSUREUNIT")
        pressure.Prefix = "KILO"
        mass = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="MASSUNIT")
        mass.Prefix = "KILO"
        ifcopenshell.api.unit.assign_unit(self.file, units=[pressure, mass])
        assert subject.calculate_unit_scale(self.file, "PRESSUREUNIT") == pytest.approx(1000)
        assert subject.calculate_unit_scale(self.file, "MASSUNIT") == pytest.approx(1000)


class TestCalculateUnitScaleOnLinkedFile(test.bootstrap.IFC4):
    def test_run(self):
        # Regression test: IfcSIUnit.Dimensions is a schema-*derived*
        # attribute that isn't computed for SQLite-linked files (used for
        # Bonsai's "linked project" large-model workflow) and raises there
        # instead of returning an IfcDimensionalExponents entity.
        # Test ensures `calculate_unit_scale` doesn't rely on derived attribute computation.
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[length])

        patcher = Ifc2Sql.Patcher(self.file, sql_type="SQLite")
        patcher.patch()
        tmp_file = Path(tempfile.mkstemp(suffix=".ifcsqlite")[1])
        ifcpatch.write(patcher.get_output(), tmp_file)

        try:
            linked_file = ifcopenshell.open(str(tmp_file))
            assert subject.calculate_unit_scale(linked_file, "LENGTHUNIT") == 1.0
        finally:
            if isinstance(linked_file, ifcopenshell.sqlite):
                linked_file.db.close()
            tmp_file.unlink(missing_ok=True)


class TestGetNamedUnitScale(test.bootstrap.IFC4):
    def test_prefix_is_raised_to_the_length_exponent_for_area_and_volume(self):
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT", prefix="DECI")
        assert subject.get_named_unit_scale(area) == pytest.approx(0.1**2)

    def test_prefix_stays_linear_for_units_that_are_not_a_pure_power_of_length(self):
        pressure = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="PRESSUREUNIT", prefix="KILO")
        assert subject.get_named_unit_scale(pressure) == pytest.approx(1000)


class TestGetDerivedUnitScale(test.bootstrap.IFC4):
    def test_composes_scale_from_elements(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        mass = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="MASSUNIT", prefix="KILO")
        volume = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="VOLUMEUNIT")
        density = ifcopenshell.api.unit.add_derived_unit(self.file, "MASSDENSITYUNIT", None, {mass: 1, volume: -1})
        assert subject.get_derived_unit_scale(density) == 1000.0

    def test_unnamed_derived_unit_still_composes(self):
        # A made-up "force per unit time" derived unit with no IfcDerivedUnitEnum match.
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        force = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="FORCEUNIT")
        time = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="TIMEUNIT", prefix="MILLI")
        weird = ifcopenshell.api.unit.add_derived_unit(self.file, "USERDEFINED", "force per time", {force: 1, time: -1})
        assert subject.get_derived_unit_scale(weird) == pytest.approx(1 / 0.001)


class TestGetUnitScale(test.bootstrap.IFC4):
    def test_dispatches_to_named_unit_scale_for_si_and_conversion_based_units(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        mm = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ft = ifcopenshell.api.unit.add_conversion_based_unit(self.file, name="foot")
        assert subject.get_unit_scale(mm) == subject.get_named_unit_scale(mm)
        assert subject.get_unit_scale(ft) == subject.get_named_unit_scale(ft)

    def test_dispatches_to_derived_unit_scale_for_derived_units(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        mass = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="MASSUNIT", prefix="KILO")
        volume = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="VOLUMEUNIT")
        density = ifcopenshell.api.unit.add_derived_unit(self.file, "MASSDENSITYUNIT", None, {mass: 1, volume: -1})
        assert subject.get_unit_scale(density) == subject.get_derived_unit_scale(density)


class TestGetUnitSymbol(test.bootstrap.IFC4):
    def test_derived_unit_composes_a_symbol(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        force = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="FORCEUNIT")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        modulus = ifcopenshell.api.unit.add_derived_unit(
            self.file, "MODULUSOFELASTICITYUNIT", None, {force: 1, area: -1}
        )
        assert subject.get_unit_symbol(modulus) == "N/m2"

    def test_unnamed_derived_unit_still_composes_a_symbol_without_crashing(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        force = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="FORCEUNIT")
        time = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="TIMEUNIT")
        weird = ifcopenshell.api.unit.add_derived_unit(self.file, "USERDEFINED", "force per time", {force: 1, time: -1})
        assert subject.get_unit_symbol(weird) == "N/s"

    def test_context_dependent_userdefined_unit_is_not_shadowed_by_the_derived_unit_check(self):
        # IfcContextDependentUnit (e.g. "each", "boxes") is a distinct entity
        # from IfcDerivedUnit, so the is_a("IfcDerivedUnit") check added for
        # derived-unit symbol composition must not shadow this fallback.
        each = ifcopenshell.api.unit.add_context_dependent_unit(self.file, name="EACH")
        assert subject.get_unit_symbol(each) == "EACH"


class TestIdentifyUnitDimensions(test.bootstrap.IFC4):
    def test_matches_a_named_unit_type_by_dimension(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        force = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="FORCEUNIT")
        area = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="AREAUNIT")
        modulus = ifcopenshell.api.unit.add_derived_unit(
            self.file, "MODULUSOFELASTICITYUNIT", None, {force: 1, area: -1}
        )
        assert subject.identify_unit_dimensions(modulus) == "PRESSUREUNIT"

    def test_returns_none_for_no_match(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        force = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="FORCEUNIT")
        time = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="TIMEUNIT")
        weird = ifcopenshell.api.unit.add_derived_unit(self.file, "USERDEFINED", "force per time", {force: 1, time: -1})
        assert subject.identify_unit_dimensions(weird) is None


class TestFormatLength(test.bootstrap.IFC4):
    def test_run(self):
        assert subject.format_length(1, 1, decimal_places=0, unit_system="metric") == "1"
        assert subject.format_length(1, 1, decimal_places=2, unit_system="metric") == "1.00"
        assert subject.format_length(3, 5, decimal_places=2, unit_system="metric") == "5.00"
        assert subject.format_length(3.123, 0.01, decimal_places=2, unit_system="metric") == "3.12"

        assert subject.format_length(3, 1, unit_system="imperial", input_unit="foot") == "3'"
        assert subject.format_length(3.5, 1, unit_system="imperial", input_unit="foot") == "3' - 6\""
        assert subject.format_length(3.123, 1, unit_system="imperial", input_unit="foot") == "3' - 1\""
        assert subject.format_length(3.123, 2, unit_system="imperial", input_unit="foot") == "3' - 1 1/2\""
        assert subject.format_length(3.123, 4, unit_system="imperial", input_unit="foot") == "3' - 1 1/2\""
        assert subject.format_length(3.123, 32, unit_system="imperial", input_unit="foot") == "3' - 1 15/32\""
        assert subject.format_length(24, 1, unit_system="imperial", input_unit="inch") == "2'"
        assert subject.format_length(25.23, 1, unit_system="imperial", input_unit="inch") == "2' - 1\""
        assert subject.format_length(25.23, 4, unit_system="imperial", input_unit="inch") == "2' - 1 1/4\""

        assert subject.format_length(3, 1, unit_system="imperial", input_unit="foot", output_unit="inch") == '36"'
        assert subject.format_length(3.5, 1, unit_system="imperial", input_unit="foot", output_unit="inch") == '42"'
        assert subject.format_length(3.123, 1, unit_system="imperial", input_unit="foot", output_unit="inch") == '37"'
        assert (
            subject.format_length(3.123, 2, unit_system="imperial", input_unit="foot", output_unit="inch") == '37 1/2"'
        )
        assert (
            subject.format_length(3.123, 4, unit_system="imperial", input_unit="foot", output_unit="inch") == '37 1/2"'
        )
        assert (
            subject.format_length(3.123, 32, unit_system="imperial", input_unit="foot", output_unit="inch")
            == '37 15/32"'
        )
        assert subject.format_length(24, 1, unit_system="imperial", input_unit="inch", output_unit="inch") == '24"'
        assert subject.format_length(25.23, 1, unit_system="imperial", input_unit="inch", output_unit="inch") == '25"'
        assert (
            subject.format_length(25.23, 4, unit_system="imperial", input_unit="inch", output_unit="inch") == '25 1/4"'
        )


class TestIsAttrType(test.bootstrap.IFC4):
    def test_run(self):
        schema = ifcopenshell.schema_by_name("IFC4")
        declaration = schema.declaration_by_name("IfcPropertySingleValue").as_entity()
        assert declaration
        nominal_value = declaration.attribute_by_index(2).type_of_attribute()
        assert subject.is_attr_type(nominal_value, "IfcValue")
        assert subject.is_attr_type(nominal_value, "IfcLengthMeasure")
        assert not subject.is_attr_type(nominal_value, "IfcLengthMeasure", include_select_types=False)


class TestConvertFileLengthUnits(test.bootstrap.IFC2X3):
    def test_run(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        output = subject.convert_file_length_units(self.file, target_units="METER")
        # there was some renumbering bug in the rocksdb rewrite this statement is to test for that
        assert max(i.id() for i in output) == len(output.entity_names()) + 1
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "METRE"

    def test_precision_conversion(self):
        # Regression test for #6127: IfcGeometricRepresentationContext.Precision
        # is typed IfcReal but interpreted in the project length unit, so it must
        # be scaled along with the length measures.
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        context = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        context.Precision = 0.01
        # Subcontexts derive Precision from the parent and must be left alone.
        ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=context
        )
        output = subject.convert_file_length_units(self.file, target_units="METER")
        new_context = output.by_type("IfcGeometricRepresentationContext", include_subtypes=False)[0]
        assert new_context.Precision == pytest.approx(0.00001)

    def test_attribute_conversion(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")

        builder = ShapeBuilder(self.file)
        rectangle = builder.rectangle((100, 100))
        extrusion = builder.extrude(rectangle, 1000)

        # IfcLengthMeasure entities.
        product = ifcopenshell.api.root.create_entity(self.file, "IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product, "TestPset")
        # Consider weird case when same entity is reused.
        length_measure = self.file.create_entity("IfcLengthMeasure", 50.0)
        enum_property = self.file.create_entity(
            "IfcPropertyEnumeratedValue",
            Name="Enum",
            # Not entirely sure if there are real life cases when mixed typed entities used in the list
            # but just to be safe.
            EnumerationValues=[
                length_measure,
                self.file.create_entity("IfcLabel", "TEXT"),
                self.file.create_entity("IfcLengthMeasure", 250.0),
                length_measure,
            ],
        )
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset,
            properties={
                "Length": self.file.create_entity("IfcLengthMeasure", 25.0),
                "Enum": enum_property,
            },
        )

        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        output = subject.convert_file_length_units(self.file, target_units="METER")
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "METRE"
        extrusion = output.by_type("IfcExtrudedAreaSolid")[0]

        # Simple float attribute.
        assert extrusion.Depth == 1

        # List of floats in IFC2X3 and list of lists of floats in IFC4+.
        rectangle = extrusion.SweptArea.OuterCurve
        expected_points = [(0.0, 0.0), (0.1, 0.0), (0.1, 0.1), (0.0, 0.1)]
        if self.file.schema == "IFC2X3":
            # IfcPolyline.
            points = [p.Coordinates for p in rectangle.Points]
            expected_points += expected_points[:1]
        else:
            # IfcIndexedPolyCurve.
            points = rectangle.Points.CoordList
        assert np.allclose(points, expected_points)

        # IfcLengthMeasure entities.
        product = output.by_type("IfcWall")[0]
        pset_data = ifcopenshell.util.element.get_pset(product, "TestPset")
        assert pset_data["Length"] == 0.025
        assert pset_data["Enum"] == [0.05, "TEXT", 0.25, 0.05]

    def test_converting_map_conversion_if_there_is_no_map_unit(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        ifcopenshell.api.georeference.edit_georeferencing(self.file, coordinate_operation={"Eastings": 10000})
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        output = subject.convert_file_length_units(self.file, target_units="METER")
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "METRE"
        if self.file.schema == "IFC2X3":
            parameters = ifcopenshell.util.geolocation.get_helmert_transformation_parameters(output)
            assert parameters
            assert parameters.e == 10
        else:
            assert output.by_type("IfcMapConversion")[0].Eastings == 10

    def test_preserving_enh_if_there_is_a_map_unit(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        meter = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        map_unit = subject.get_full_unit_name(meter) if self.file.schema == "IFC2X3" else meter
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"MapUnit": map_unit},
            coordinate_operation={"Eastings": 10, "Scale": 0.001},
        )
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        output = subject.convert_file_length_units(self.file, target_units="METER")
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "METRE"
        if self.file.schema == "IFC2X3":
            parameters = ifcopenshell.util.geolocation.get_helmert_transformation_parameters(output)
            assert parameters
            assert parameters.e == 10
            assert parameters.n == 0
            assert parameters.scale == 1
            crs = ifcopenshell.util.element.get_pset(output.by_type("IfcProject")[0], name="ePSet_ProjectedCRS")
            assert crs["MapUnit"] == "METRE"
        else:
            map_conversion = output.by_type("IfcMapConversion")[0]
            assert map_conversion.Eastings == 10
            assert map_conversion.Northings == 0
            assert map_conversion.Scale == 1
            assert subject.get_full_unit_name(output.by_type("IfcProjectedCRS")[0].MapUnit) == "METRE"

    def test_preserving_enh_if_there_is_a_map_unit_which_is_also_the_project_default(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        meter = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.context.add_context(self.file, "Model")
        ifcopenshell.api.georeference.add_georeferencing(self.file)
        map_unit = subject.get_full_unit_name(meter) if self.file.schema == "IFC2X3" else meter
        ifcopenshell.api.georeference.edit_georeferencing(
            self.file,
            projected_crs={"MapUnit": map_unit},
            coordinate_operation={"Eastings": 10, "Scale": 1},
        )
        ifcopenshell.api.unit.assign_unit(self.file, units=[meter])
        output = subject.convert_file_length_units(self.file, target_units="MILLIMETER")
        assert subject.get_full_unit_name(subject.get_project_unit(output, "LENGTHUNIT")) == "MILLIMETRE"
        if self.file.schema == "IFC2X3":
            parameters = ifcopenshell.util.geolocation.get_helmert_transformation_parameters(output)
            assert parameters
            assert parameters.e == 10
            assert parameters.n == 0
            assert parameters.scale == 1
            crs = ifcopenshell.util.element.get_pset(output.by_type("IfcProject")[0], name="ePSet_ProjectedCRS")
            assert crs["MapUnit"] == "METRE"
        else:
            map_conversion = output.by_type("IfcMapConversion")[0]
            assert map_conversion.Eastings == 10
            assert map_conversion.Northings == 0
            assert map_conversion.Scale == 0.001
            assert subject.get_full_unit_name(output.by_type("IfcProjectedCRS")[0].MapUnit) == "METRE"

        unit_assignment = subject.get_unit_assignment(output)
        assert unit_assignment
        assert len(unit_assignment.Units) == 1


class TestConvertFileLengthUnitsIFC4(test.bootstrap.IFC4, TestConvertFileLengthUnits):
    pass


class TestConvertFileLengthUnitsIFC4X3(test.bootstrap.IFC4X3, TestConvertFileLengthUnits):
    pass
