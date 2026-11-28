# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.unit
import pytest

import bonsai.bim.prop
import bonsai.tool as tool
from test.bim.bootstrap import NewFile


def import_single_property(ifc, element, prop):
    """Import a single existing IfcProperty into a real, addon-registered
    PsetProperties collection, exactly as the property editor does, and
    return its `metadata` (an `Attribute`)."""
    pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Pset_Test")
    pset.HasProperties = [prop]
    obj = bpy.data.objects.new(prop.Name, None)
    tool.Ifc.link(element, obj)
    props = obj.PsetProperties
    tool.Pset.import_pset_from_existing(pset, props, None)
    return props.properties[prop.Name].metadata


class TestGetDisplayName(NewFile):
    def test_appends_the_resolved_unit_symbol(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        pressure = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="PRESSUREUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[pressure])

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcPressureMeasure(5.0))
        metadata = import_single_property(ifc, element, prop)

        assert metadata.display_name == "Foo, Pa"

    def test_falls_back_to_the_plain_name_when_no_unit_is_resolvable(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        # No units assigned to the project at all -- nothing to resolve.

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcPressureMeasure(5.0))
        metadata = import_single_property(ifc, element, prop)

        assert metadata.unit_symbol == ""
        assert metadata.display_name == "Foo"

    def test_falls_back_to_the_plain_name_for_a_non_measure_property(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcText("Bar"))
        metadata = import_single_property(ifc, element, prop)

        assert metadata.unit_symbol == ""
        assert metadata.display_name == "Foo"

    def test_resolves_a_unit_explicitly_attached_to_a_generic_numeric_value(self):
        # A generic IfcReal has no unit semantics per its own declared type, but a property
        # set may still explicitly attach a real Unit to a specific instance to convey the
        # dimension the spec's generic typing doesn't. That explicit Unit is real, deliberate
        # data (not incidental/stray), so it should resolve normally.
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcReal(150.0), Unit=length_mm)
        metadata = import_single_property(ifc, element, prop)

        assert metadata.unit_symbol == "mm"
        assert metadata.display_name == "Foo, mm"


class TestGetAttributeUnitEnumItems(NewFile):
    def test_returns_default_plus_one_per_candidate_for_a_measurable_type(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_mm])
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcLengthMeasure(2.5))
        metadata = import_single_property(ifc, element, prop)

        items = bonsai.bim.prop.get_attribute_unit_enum_items(metadata, bpy.context)
        identifiers = [i[0] for i in items]
        assert identifiers[0] == "0"
        assert str(length_mm.id()) in identifiers
        assert str(length_m.id()) in identifiers
        assert len([i for i in items if not i[0].startswith("+")]) == 3  # Default + mm + m

    def test_returns_just_default_for_non_measurable_types(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcText("Bar"))
        metadata = import_single_property(ifc, element, prop)

        items = bonsai.bim.prop.get_attribute_unit_enum_items(metadata, bpy.context)
        assert [i[0] for i in items] == ["0"]


class TestUndefinedVersusDefaultUnits(NewFile):
    """Regression tests for #10074: when the project's IfcUnitAssignment defines no unit for a
    measure type, the picker's no-override entry used to read "Default", implying a unit exists.
    It must read "Undefined" instead, and only read "Default (<symbol>)" when one really does."""

    def test_picker_reads_undefined_when_the_project_defines_no_unit(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        # A pressure unit exists in the file (usable as an override) but isn't assigned.
        pascal = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="PRESSUREUNIT")

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcPressureMeasure(5.0))
        metadata = import_single_property(ifc, element, prop)

        items = bonsai.bim.prop.get_attribute_unit_enum_items(metadata, bpy.context)
        assert items[0] == ("0", "Undefined", tool.Pset.UNDEFINED_UNIT_DESCRIPTION)
        assert str(pascal.id()) in [i[0] for i in items]

    def test_picker_reads_undefined_with_no_units_at_all(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcAreaMeasure(5.0))
        metadata = import_single_property(ifc, element, prop)

        items = bonsai.bim.prop.get_attribute_unit_enum_items(metadata, bpy.context)
        assert [i[:2] for i in items if not i[0].startswith("+")] == [("0", "Undefined")]

    def test_picker_reads_default_when_the_project_defines_a_unit(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        pascal = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="PRESSUREUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[pascal])

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcPressureMeasure(5.0))
        metadata = import_single_property(ifc, element, prop)

        items = bonsai.bim.prop.get_attribute_unit_enum_items(metadata, bpy.context)
        assert items[0][:2] == ("0", "Default (Pa)")

    def test_picker_switches_from_undefined_to_default_once_a_unit_is_assigned(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        assert bonsai.bim.prop.get_unit_enum_items_for_special_type("AREA", ifc)[0][1] == "Undefined"

        area = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[area])

        assert bonsai.bim.prop.get_unit_enum_items_for_special_type("AREA", ifc)[0][1] == "Default (m2)"

    def test_non_measurable_types_keep_the_plain_default_entry(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        assert bonsai.bim.prop.get_unit_enum_items_for_special_type("", ifc) == [("0", "Default", "")]


class TestDuplicateUnitsAreListedOnce(NewFile):
    """Each conversion-based unit carries its own hidden METRE (its conversion factor's unit),
    so a foot + inch project used to list "METRE (m)" twice in every length picker."""

    def setup_foot_and_inch_project(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        foot = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name="foot")
        ifcopenshell.api.unit.assign_unit(ifc, units=[foot])
        inch = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name="inch")
        return ifc, foot, inch

    def test_identical_metres_appear_once(self):
        ifc, foot, inch = self.setup_foot_and_inch_project()
        assert len([u for u in ifc.by_type("IfcSIUnit") if u.UnitType == "LENGTHUNIT"]) == 2
        labels = [i[1] for i in bonsai.bim.prop.get_unit_enum_items_for_special_type("LENGTH", ifc)]
        assert labels == ["Default (ft)", "foot (ft)", "inch (in)", "METRE (m)"]

    def test_the_lowest_id_represents_a_group(self):
        ifc, foot, inch = self.setup_foot_and_inch_project()
        metres = sorted(u.id() for u in ifc.by_type("IfcSIUnit") if u.UnitType == "LENGTHUNIT")
        ids = [i[0] for i in bonsai.bim.prop.get_unit_enum_items_for_special_type("LENGTH", ifc)]
        assert str(metres[0]) in ids
        assert str(metres[1]) not in ids

    def test_a_property_using_a_duplicate_keeps_it_selectable_without_a_second_entry(self):
        ifc, foot, inch = self.setup_foot_and_inch_project()
        second_metre = max((u for u in ifc.by_type("IfcSIUnit") if u.UnitType == "LENGTHUNIT"), key=lambda u: u.id())

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(
            Name="Foo", NominalValue=ifc.createIfcLengthMeasure(2.0), Unit=second_metre
        )
        metadata = import_single_property(ifc, element, prop)

        items = bonsai.bim.prop.get_attribute_unit_enum_items(metadata, bpy.context)
        assert [i[1] for i in items].count("METRE (m)") == 1
        assert str(second_metre.id()) in [i[0] for i in items]
        assert metadata.unit_id_enum == str(second_metre.id())

    def test_distinct_units_with_the_same_type_are_kept(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        assert tool.Unit.get_distinct_units([mm, m]) == [mm, m]


class TestPickingANewCatalogUnitForAProperty(NewFile):
    def setup_pressure_property(self, value=6894.7572932):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        pascal = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="PRESSUREUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[pascal])
        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcPressureMeasure(value))
        return ifc, pascal, import_single_property(ifc, element, prop)

    def test_the_picker_offers_catalog_units_not_in_the_file(self):
        ifc, pascal, metadata = self.setup_pressure_property()
        items = bonsai.bim.prop.get_attribute_unit_enum_items(metadata, bpy.context)
        identifiers = [i[0] for i in items]
        assert identifiers[:2] == ["0", str(pascal.id())]
        for name in ("psi", "ksi", "psf", "ksf"):
            assert f"+CONV:{name}" in identifiers
        assert "+SI:KILO" in identifiers  # kPa
        assert "+SI:" not in identifiers  # Pa is already in the file

    def test_picking_one_creates_it_selects_it_and_converts_the_value(self):
        ifc, pascal, metadata = self.setup_pressure_property(6894.7572932)  # 1 psi, in Pa
        metadata.unit_id_enum = "+CONV:psi"

        psi = next(u for u in ifc.by_type("IfcConversionBasedUnit") if u.Name == "psi")
        assert metadata.unit_id == psi.id()
        assert metadata.unit_id_enum == str(psi.id())
        assert metadata.float_value == pytest.approx(1.0)
        assert metadata.unit_symbol == "psi"
        # Added to the file, not made the project default.
        assert ifcopenshell.util.unit.get_project_unit(ifc, "PRESSUREUNIT") == pascal
        # Now an ordinary entry, no longer a "+" one.
        identifiers = [i[0] for i in bonsai.bim.prop.get_attribute_unit_enum_items(metadata, bpy.context)]
        assert str(psi.id()) in identifiers
        assert "+CONV:psi" not in identifiers

    def test_derived_measures_offer_no_catalog_entries(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        items = bonsai.bim.prop.get_unit_enum_items_for_special_type("MOMENTOFINERTIA", ifc, include_new=True)
        assert [i[0] for i in items] == ["0"]

    def test_other_pickers_do_not_offer_catalog_entries(self):
        ifc, pascal, metadata = self.setup_pressure_property()
        items = bonsai.bim.prop.get_unit_enum_items_for_special_type("PRESSURE", ifc)
        assert not any(i[0].startswith("+") for i in items)


class TestGetUnitEnumItemsForSpecialType(NewFile):
    def test_matches_the_attribute_wrapper_output(self):
        # Regression test for extracting get_unit_enum_items_for_special_type out of
        # get_attribute_unit_enum_items: the wrapper must still produce identical items for
        # the plain (no own-unit-fallback-needed) case.
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_mm])
        ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcLengthMeasure(2.5))
        metadata = import_single_property(ifc, element, prop)

        direct_items = bonsai.bim.prop.get_unit_enum_items_for_special_type(metadata.special_type, ifc)
        wrapper_items = bonsai.bim.prop.get_attribute_unit_enum_items(metadata, bpy.context)
        # The attribute picker additionally offers "+" catalog units to create on pick.
        assert direct_items == [i for i in wrapper_items if not i[0].startswith("+")]

    def test_returns_just_default_when_ifc_file_is_none(self):
        assert bonsai.bim.prop.get_unit_enum_items_for_special_type("LENGTH", None) == [("0", "Default", "")]


class TestUnitSymbolWithAreaVolumeDerivedFromLength(NewFile):
    """Regression test: AREAUNIT/VOLUMEUNIT have no IfcDerivedUnitEnum member, so a project
    whose area/volume default is an IfcDerivedUnit rather than a literal-UnitType-matching
    IfcSIUnit/IfcConversionBasedUnit has no literal UnitType to match on.
    ifcopenshell.util.unit.get_project_unit() used to only match by literal UnitType, so the
    read-only unit symbol and the edit-mode "Default (<symbol>)" picker entry both silently
    fell back to no symbol at all in that case.
    """

    def setup_project_with_derived_area_and_volume(self, ifc):
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        area = ifcopenshell.api.unit.add_derived_unit(ifc, "USERDEFINED", "area-ish", {length: 2})
        volume = ifcopenshell.api.unit.add_derived_unit(ifc, "USERDEFINED", "volume-ish", {length: 3})
        ifcopenshell.api.unit.assign_unit(ifc, units=[length, area, volume])

    def test_default_picker_entry_shows_the_resolved_symbol(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        self.setup_project_with_derived_area_and_volume(ifc)

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcAreaMeasure(5.0))
        metadata = import_single_property(ifc, element, prop)

        items = bonsai.bim.prop.get_attribute_unit_enum_items(metadata, bpy.context)
        assert items[0][1] == "Default (m2)"

    def test_read_only_display_resolves_the_symbol(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        self.setup_project_with_derived_area_and_volume(ifc)

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcVolumeMeasure(5.0))
        metadata = import_single_property(ifc, element, prop)

        assert metadata.unit_symbol == "m3"
        assert metadata.display_name == "Foo, m3"


class TestUpdateAttributeUnitId(NewFile):
    def test_syncs_unit_id_and_converts_float_value_when_unit_id_enum_changes(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_mm])
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcLengthMeasure(2500.0))
        metadata = import_single_property(ifc, element, prop)
        assert metadata.unit_id == 0
        assert metadata.float_value == 2500.0
        assert metadata.unit_symbol == "mm"
        assert metadata.display_name == "Foo, mm"

        metadata.unit_id_enum = str(length_m.id())

        assert metadata.unit_id == length_m.id()
        assert metadata.float_value == pytest.approx(2.5)  # converted, not just relabeled
        # Regression test: unit_symbol/display_name used to be a snapshot taken once at import
        # time, so picking a different unit converted the value but left the label showing the
        # old unit's symbol.
        assert metadata.unit_symbol == "m"
        assert metadata.display_name == "Foo, m"


class TestUnitSymbolReflectsLiveProjectState(NewFile):
    def test_symbol_updates_after_a_project_default_unit_is_assigned_later(self):
        # Regression test: unit_symbol used to be a snapshot computed once at import time, so a
        # property/quantity imported before its measure type had a project default unit assigned
        # kept showing no symbol even after one was added, unless the panel was closed and
        # reopened (re-triggering import). It's now computed fresh on every access.
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        # No AREAUNIT assigned yet.

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcAreaMeasure(5.0))
        metadata = import_single_property(ifc, element, prop)
        assert metadata.unit_symbol == ""
        assert metadata.display_name == "Foo"

        area = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="AREAUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[area])

        assert metadata.unit_symbol == "m2"
        assert metadata.display_name == "Foo, m2"


class TestImportPsetFromExistingWithAGenericNumericValueAndAnExplicitUnit(NewFile):
    def test_run(self):
        # Regression test: some property set specifications declare a property as a generic
        # IfcReal rather than a proper measure class, relying on an explicit Unit attribute
        # alone to convey the dimension. get_property_unit() already handled this fine for
        # display (it checks prop.Unit before looking at NominalValue's type at all), but
        # get_special_type_for_prop() only looked at NominalValue's class ending in "Measure"
        # -- so special_type came back "", the picker never appeared, and the real Unit
        # override never got seeded into unit_id even though it was legitimately set.
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcReal(150.0), Unit=length_mm)
        metadata = import_single_property(ifc, element, prop)

        assert metadata.special_type == "LENGTH"
        assert tool.Pset.is_measurable_special_type(metadata.special_type)
        assert metadata.unit_symbol == "mm"
        assert metadata.unit_id == length_mm.id()
        assert metadata.unit_id_enum == str(length_mm.id())

        items = bonsai.bim.prop.get_attribute_unit_enum_items(metadata, bpy.context)
        assert str(length_mm.id()) in [i[0] for i in items]


class TestImportPsetFromExistingWithAStrayUnitOnANonMeasureProperty(NewFile):
    def test_run(self):
        # Regression test: some real-world exporters set a Unit on a property whose
        # NominalValue isn't actually a measure (e.g. a text classification), which used
        # to crash import_pset_from_existing with "enum '<id>' not found in ('0')" -- unit_id
        # was seeded from prop.Unit unconditionally, before the special_type gate that decides
        # whether Unit is even meaningful for this property.
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcLabel("Bar"), Unit=length_m)
        metadata = import_single_property(ifc, element, prop)  # must not raise

        assert metadata.special_type == ""
        assert metadata.unit_id == 0
        assert metadata.unit_id_enum == "0"


class TestGetAttributeUnitEnumItemsWithAMismatchedUnit(NewFile):
    def test_own_unit_is_always_representable_even_if_not_a_normal_candidate(self):
        # Regression test: a property's own Unit might not satisfy
        # get_candidate_units_for_special_type's matching (e.g. mismatched UnitType in messy
        # real-world data). Seeding must never crash trying to select it, and it should still
        # show up in the picker so the user can see/change it.
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        # A LENGTHUNIT attached to a PRESSURE-typed property -- a real mismatch, not a candidate
        # get_candidate_units_for_special_type("PRESSURE", ...) would ever return.
        mismatched_unit = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(
            Name="Foo", NominalValue=ifc.createIfcPressureMeasure(5.0), Unit=mismatched_unit
        )
        metadata = import_single_property(ifc, element, prop)  # must not raise

        assert metadata.special_type == "PRESSURE"
        assert metadata.unit_id == mismatched_unit.id()
        assert metadata.unit_id_enum == str(mismatched_unit.id())

        items = bonsai.bim.prop.get_attribute_unit_enum_items(metadata, bpy.context)
        assert str(mismatched_unit.id()) in [i[0] for i in items]


class TestGetValueRoundsLengthToModelPrecision(NewFile):
    def test_strips_float32_noise_from_a_length_value(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(ifc, context_type="Model")

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcLengthMeasure(1.0))
        metadata = import_single_property(ifc, element, prop)
        metadata.float_value = 67.74

        assert metadata.special_type == "LENGTH"
        assert metadata.get_value() == 67.74
