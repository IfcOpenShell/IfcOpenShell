# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.unit
import pytest

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.pset import Pset as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Pset)


class TestGetElementPset(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcWall()
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo")
        assert subject.get_element_pset(element, "Foo") == pset


class TestIsPsetEmpty(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        element = ifc.createIfcWall()
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Foo")
        assert subject.is_pset_empty(pset) is True
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": "Bar"})
        assert subject.is_pset_empty(pset) is False
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"Foo": None})
        assert subject.is_pset_empty(pset) is True


class TestEditingAnOverriddenUnitPropertyRoundTrips(NewFile):
    def test_run(self):
        # Project default is mm, but this property is authored directly in m.
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_mm])
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")

        element = ifc.createIfcWall()
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Pset_Test")
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcLengthMeasure(2.5), Unit=length_m)
        pset.HasProperties = [prop]

        obj = bpy.data.objects.new("Wall", None)
        tool.Ifc.link(element, obj)
        blender_props = obj.PsetProperties
        subject.import_pset_from_existing(pset, blender_props, None)

        metadata = blender_props.properties["Foo"].metadata
        assert metadata.unit_symbol == "m"
        assert metadata.float_value == 2.5  # raw stored value, not rescaled to the project's mm

        # Simulate a user edit in the property editor.
        metadata.float_value = 3.5

        # Simulate what EditPset.execute() does: collect the raw value straight
        # off the metadata and write it back, with no rescaling step.
        properties = {"Foo": metadata.get_value()}
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties=properties)

        assert prop.NominalValue.wrappedValue == 3.5  # not rescaled to 3500mm
        assert prop.Unit == length_m  # override preserved


class TestImportingATemplatedQuantityRespectsItsOwnUnitOverride(NewFile):
    def test_run(self):
        # Regression test: import_pset_from_template's Q_ branch used to
        # unconditionally re-template existing quantities, which shadowed
        # their own Unit override with the project default -- edit mode
        # showed "m" while the read-only panel correctly showed "mm".
        # Project default is m, but this quantity is authored directly in mm.
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_m])
        length_mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")

        element = ifc.createIfcBeam()
        qto = ifcopenshell.api.pset.add_qto(ifc, product=element, name="Qto_Test")
        quantity = ifc.createIfcQuantityLength(Name="Foo", Unit=length_mm, LengthValue=2500.0)
        qto.Quantities = [quantity]

        pset_template = ifc.createIfcPropertySetTemplate(
            Name="Qto_Test",
            TemplateType="PSET_TYPEDRIVENOVERRIDE",
            ApplicableEntity="IfcBeam",
            HasPropertyTemplates=[ifc.createIfcSimplePropertyTemplate(Name="Foo", TemplateType="Q_LENGTH")],
        )

        obj = bpy.data.objects.new("Beam", None)
        tool.Ifc.link(element, obj)
        blender_props = obj.PsetProperties
        # Mirrors core/pset.py's enable_pset_editing: template pass, then existing-data pass.
        subject.import_pset_from_template(pset_template, qto, blender_props)
        subject.import_pset_from_existing(qto, blender_props, pset_template)

        assert len(blender_props.properties) == 1  # not duplicated by the template pass
        metadata = blender_props.properties["Foo"].metadata
        assert metadata.unit_symbol == "mm"  # the quantity's own override, not the project default "m"
        assert metadata.float_value == 2500.0  # raw stored value, not rescaled


class TestIsMeasurableSpecialType(NewFile):
    def test_run(self):
        for special_type in ("", "DATE", "DATETIME", "LOGICAL", "URI", "DURATION"):
            assert subject.is_measurable_special_type(special_type) is False
        assert subject.is_measurable_special_type("LENGTH") is True
        assert subject.is_measurable_special_type("PRESSURE") is True


class TestGetCandidateUnitsForSpecialType(NewFile):
    def test_returns_candidates_matching_the_special_type(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.add_si_unit(ifc, unit_type="AREAUNIT")
        assert set(subject.get_candidate_units_for_special_type("LENGTH", ifc)) == {length_mm, length_m}

    def test_gating_returns_empty_for_non_measurable_special_types(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        assert subject.get_candidate_units_for_special_type("", ifc) == []
        assert subject.get_candidate_units_for_special_type("URI", ifc) == []


class TestResolveEffectiveUnit(NewFile):
    def test_own_override_takes_precedence_over_project_default(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_mm])
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        assert subject.resolve_effective_unit("LENGTH", length_m.id(), ifc) == length_m

    def test_falls_back_to_project_default_when_unit_id_is_zero(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_mm])
        assert subject.resolve_effective_unit("LENGTH", 0, ifc) == length_mm


class TestConvertAttributeUnit(NewFile):
    def _new_metadata(self, ifc: ifcopenshell.file):
        element = ifc.createIfcWall()
        obj = bpy.data.objects.new("Wall", None)
        tool.Ifc.link(element, obj)
        props = obj.PsetProperties
        new_prop = props.properties.add()
        new_prop.name = "Foo"
        return new_prop.metadata

    def test_converts_value_between_two_explicit_units(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")

        metadata = self._new_metadata(ifc)
        metadata.special_type = "LENGTH"
        metadata.unit_id = length_mm.id()
        metadata.float_value = 2500.0

        subject.convert_attribute_unit(metadata, length_m.id(), ifc)
        assert metadata.float_value == pytest.approx(2.5)

    def test_converts_value_when_switching_to_and_from_the_project_default(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_m])
        length_ft = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name="foot")

        metadata = self._new_metadata(ifc)
        metadata.special_type = "LENGTH"
        metadata.unit_id = length_ft.id()
        metadata.float_value = 10.0  # 10 ft

        subject.convert_attribute_unit(metadata, 0, ifc)  # 0 = switch to project default (m)
        assert metadata.float_value == pytest.approx(3.048)

    def test_noop_when_old_and_new_resolve_to_the_same_unit(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_m])

        metadata = self._new_metadata(ifc)
        metadata.special_type = "LENGTH"
        metadata.unit_id = 0  # already resolves to length_m (the project default)
        metadata.float_value = 5.0

        subject.convert_attribute_unit(metadata, length_m.id(), ifc)
        assert metadata.float_value == 5.0

    def test_noop_for_a_non_measurable_special_type(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")

        metadata = self._new_metadata(ifc)
        metadata.special_type = ""
        metadata.unit_id = 0
        metadata.float_value = 5.0

        subject.convert_attribute_unit(metadata, length_m.id(), ifc)
        assert metadata.float_value == 5.0


def _build_wrapped_properties_from_ui(blender_props) -> dict:
    """Mirrors EditPset._execute()'s properties-building loop (operator.py)."""
    properties = {}
    for entry in blender_props.properties:
        metadata = entry.metadata
        value = metadata.get_value()
        if value is not None and subject.is_measurable_special_type(metadata.special_type):
            unit = tool.Ifc.get().by_id(metadata.unit_id) if metadata.unit_id else None
            value = {"NominalValue": value, "Unit": unit}
        properties[metadata.name] = value
    return properties


class TestEditPsetWithUnitOverridePicker(NewFile):
    def test_picking_a_different_unit_converts_the_displayed_value_and_writes_it_back(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_mm])
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")

        element = ifc.createIfcWall()
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Pset_Test")
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcLengthMeasure(2500.0))
        pset.HasProperties = [prop]

        obj = bpy.data.objects.new("Wall", None)
        tool.Ifc.link(element, obj)
        blender_props = obj.PsetProperties
        subject.import_pset_from_existing(pset, blender_props, None)

        metadata = blender_props.properties["Foo"].metadata
        assert metadata.unit_id == 0
        assert metadata.float_value == 2500.0

        # Simulate the user picking "m" in the unit picker dropdown.
        metadata.unit_id_enum = str(length_m.id())
        assert metadata.float_value == pytest.approx(2.5)  # converted live, not just relabeled
        assert metadata.unit_id == length_m.id()

        properties = _build_wrapped_properties_from_ui(blender_props)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties=properties)

        assert prop.NominalValue.wrappedValue == pytest.approx(2.5)
        assert prop.Unit == length_m

    def test_picking_default_after_an_override_converts_back_and_clears_the_unit(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_mm = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix="MILLI")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_mm])
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")

        element = ifc.createIfcWall()
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Pset_Test")
        prop = ifc.createIfcPropertySingleValue(Name="Foo", NominalValue=ifc.createIfcLengthMeasure(2.5), Unit=length_m)
        pset.HasProperties = [prop]

        obj = bpy.data.objects.new("Wall", None)
        tool.Ifc.link(element, obj)
        blender_props = obj.PsetProperties
        subject.import_pset_from_existing(pset, blender_props, None)

        metadata = blender_props.properties["Foo"].metadata
        assert metadata.unit_id == length_m.id()
        assert metadata.float_value == 2.5

        # Simulate picking "Default" (mm).
        metadata.unit_id_enum = "0"
        assert metadata.float_value == pytest.approx(2500.0)
        assert metadata.unit_id == 0

        properties = _build_wrapped_properties_from_ui(blender_props)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties=properties)

        assert prop.Unit is None
        assert prop.NominalValue.wrappedValue == pytest.approx(2500.0)

    def test_editing_an_unrelated_sibling_property_does_not_disturb_this_ones_override(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        length_m = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(ifc, units=[length_m])
        length_ft = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name="foot")

        element = ifc.createIfcWall()
        pset = ifcopenshell.api.pset.add_pset(ifc, product=element, name="Pset_Test")
        overridden_prop = ifc.createIfcPropertySingleValue(
            Name="Foo", NominalValue=ifc.createIfcLengthMeasure(10.0), Unit=length_ft
        )
        untouched_prop = ifc.createIfcPropertySingleValue(Name="Bar", NominalValue=ifc.createIfcLengthMeasure(3.0))
        pset.HasProperties = [overridden_prop, untouched_prop]

        obj = bpy.data.objects.new("Wall", None)
        tool.Ifc.link(element, obj)
        blender_props = obj.PsetProperties
        subject.import_pset_from_existing(pset, blender_props, None)

        # Edit only "Bar", never touching "Foo"'s unit dropdown.
        blender_props.properties["Bar"].metadata.float_value = 4.0

        properties = _build_wrapped_properties_from_ui(blender_props)
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties=properties)

        assert overridden_prop.Unit == length_ft  # untouched override survives
        assert overridden_prop.NominalValue.wrappedValue == 10.0
        assert untouched_prop.NominalValue.wrappedValue == 4.0


class TestEditQtoRoundingLoopPreservesUnitWrappedValues(NewFile):
    def test_run(self):
        # Regression test for EditPset._execute()'s qto post-processing loop: it must reach
        # into {"Unit": ..., "NominalValue": ...}-wrapped values to round them, rather than
        # treating the whole dict as a bare float/int (which would zero it out).
        properties = {
            "Foo": {"NominalValue": 2.123456, "Unit": None},
            "Bar": 3,
        }
        for key, value in properties.items():
            if value is None:
                continue
            is_wrapped = isinstance(value, dict) and "Unit" in value
            raw = value["NominalValue"] if is_wrapped else value
            if raw is None:
                continue
            if isinstance(raw, float):
                raw = round(raw, 4)
            elif not isinstance(raw, int):
                raw = 0
            if is_wrapped:
                value["NominalValue"] = raw
            else:
                properties[key] = raw
        assert properties["Foo"]["NominalValue"] == 2.1235
        assert properties["Foo"]["Unit"] is None
        assert properties["Bar"] == 3
