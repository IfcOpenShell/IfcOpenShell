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
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.unit
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
        assert len(items) == 3  # Default + mm + m

    def test_returns_just_default_for_non_measurable_types(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")

        element = ifc.createIfcWall()
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcText("Bar"))
        metadata = import_single_property(ifc, element, prop)

        items = bonsai.bim.prop.get_attribute_unit_enum_items(metadata, bpy.context)
        assert [i[0] for i in items] == ["0"]


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

        metadata.unit_id_enum = str(length_m.id())

        assert metadata.unit_id == length_m.id()
        assert metadata.float_value == pytest.approx(2.5)  # converted, not just relabeled


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
        prop = ifc.createIfcPropertySingleValue(
            Name="Foo", NominalValue=ifc.createIfcReal(150.0), Unit=length_mm
        )
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
        prop = ifc.createIfcPropertySingleValue(
            Name="Foo", NominalValue=ifc.createIfcLabel("Bar"), Unit=length_m
        )
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
