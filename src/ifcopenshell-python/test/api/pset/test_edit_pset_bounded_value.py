# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.api.pset
import ifcopenshell.api.root
import test.bootstrap


class BoundedValueTests:
    def add_pset(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        return ifcopenshell.api.pset.add_pset(self.file, product=element, name="Custom_Pset")

    def add_unit(self):
        return self.file.create_entity("IfcSIUnit", UnitType="LENGTHUNIT", Name="METRE", Prefix="MILLI")

    def test_adding_a_bounded_valued_property_with_a_unit(self):
        pset = self.add_pset()
        unit = self.add_unit()
        properties = {"Foo": {"LowerBoundValue": self.file.createIfcReal(1.0), "Unit": unit}}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties)
        assert pset.HasProperties[0].Unit == unit

    def test_adding_a_bounded_valued_property_with_a_none_unit(self):
        pset = self.add_pset()
        properties = {"Foo": {"LowerBoundValue": self.file.createIfcReal(1.0), "Unit": None}}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties)
        assert pset.HasProperties[0].Unit is None

    def test_editing_a_bounded_valued_property_keeps_the_unit_if_it_is_not_specified(self):
        pset = self.add_pset()
        unit = self.add_unit()
        properties = {"Foo": {"LowerBoundValue": self.file.createIfcReal(1.0), "Unit": unit}}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties)
        properties = {"Foo": {"UpperBoundValue": self.file.createIfcReal(2.0)}}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties)
        assert pset.HasProperties[0].Unit == unit

    def test_editing_a_bounded_valued_property_sets_the_unit(self):
        pset = self.add_pset()
        unit = self.add_unit()
        properties = {"Foo": {"LowerBoundValue": self.file.createIfcReal(1.0)}}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties)
        properties = {"Foo": {"LowerBoundValue": self.file.createIfcReal(1.0), "Unit": unit}}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties)
        assert pset.HasProperties[0].Unit == unit

    def test_editing_a_bounded_valued_property_clears_the_unit_if_it_is_none(self):
        pset = self.add_pset()
        properties = {"Foo": {"LowerBoundValue": self.file.createIfcReal(1.0), "Unit": self.add_unit()}}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties)
        properties = {"Foo": {"LowerBoundValue": self.file.createIfcReal(1.0), "Unit": None}}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties)
        assert pset.HasProperties[0].Unit is None

    def test_not_adding_a_bounded_valued_property_if_all_values_are_none_and_should_purge_is_true(self):
        pset = self.add_pset()
        properties = {"Foo": {"LowerBoundValue": None, "UpperBoundValue": None}}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties, should_purge=True)
        assert not pset.HasProperties
        assert not self.file.by_type("IfcPropertyBoundedValue")

    def test_adding_a_bounded_valued_property_if_all_values_are_none_and_should_purge_is_false(self):
        pset = self.add_pset()
        properties = {"Foo": {"LowerBoundValue": None, "UpperBoundValue": None}}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties, should_purge=False)
        assert len(pset.HasProperties) == 1
        assert pset.HasProperties[0].is_a("IfcPropertyBoundedValue")

    def test_removing_a_bounded_valued_property_if_its_only_value_is_set_to_none(self):
        pset = self.add_pset()
        properties = {"Foo": {"UpperBoundValue": self.file.createIfcReal(1.0)}}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties)
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Foo": {"UpperBoundValue": None}})
        assert not pset.HasProperties

    def test_keeping_a_bounded_valued_property_if_its_only_value_is_set_to_none_and_should_purge_is_false(self):
        pset = self.add_pset()
        properties = {"Foo": {"UpperBoundValue": self.file.createIfcReal(1.0)}}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties)
        properties = {"Foo": {"UpperBoundValue": None}}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties, should_purge=False)
        prop = pset.HasProperties[0]
        assert prop.LowerBoundValue is None
        assert prop.UpperBoundValue is None


class TestEditPsetBoundedValueIFC2X3(test.bootstrap.IFC2X3, BoundedValueTests):
    def test_not_adding_a_bounded_valued_property_with_a_set_point_value(self):
        pset = self.add_pset()
        properties = {"Foo": {"LowerBoundValue": self.file.createIfcReal(1.0), "SetPointValue": 1.5}}
        with pytest.raises(ValueError, match="SetPointValue"):
            ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties)
        assert not pset.HasProperties

    def test_not_editing_a_bounded_valued_property_with_a_set_point_value(self):
        pset = self.add_pset()
        properties = {"Foo": {"LowerBoundValue": self.file.createIfcReal(1.0)}}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties=properties)
        with pytest.raises(ValueError, match="SetPointValue"):
            ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Foo": {"SetPointValue": 1.5}})
        assert pset.HasProperties[0].LowerBoundValue.wrappedValue == 1.0


class TestEditPsetBoundedValue(test.bootstrap.IFC4, BoundedValueTests):
    def test_adding_a_bounded_valued_property(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcElectricDistributionBoard")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_ElectricalDeviceCommon")
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={"RatedCurrent": {"LowerBoundValue": 1.0, "UpperBoundValue": 2.5}},
        )
        prop = pset.HasProperties[0]
        assert prop.is_a("IfcPropertyBoundedValue")
        assert prop.Name == "RatedCurrent"
        assert prop.LowerBoundValue.is_a("IfcElectricCurrentMeasure")
        assert prop.LowerBoundValue.wrappedValue == 1.0
        assert prop.UpperBoundValue.wrappedValue == 2.5
        assert prop.SetPointValue is None

    def test_editing_an_existing_bounded_valued_property(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcElectricDistributionBoard")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_ElectricalDeviceCommon")
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={"RatedCurrent": {"LowerBoundValue": 1.0, "UpperBoundValue": 2.5}},
        )
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"RatedCurrent": {"SetPointValue": 3.3}})
        prop = pset.HasProperties[0]
        assert prop.LowerBoundValue.wrappedValue == 1.0
        assert prop.UpperBoundValue.wrappedValue == 2.5
        assert prop.SetPointValue.wrappedValue == 3.3

    def test_removing_a_bounded_valued_property_if_specified(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcElectricDistributionBoard")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_ElectricalDeviceCommon")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"RatedCurrent": {"LowerBoundValue": 1.0}})
        assert len(pset.HasProperties) == 1
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"RatedCurrent": None})
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert len(pset.HasProperties) == 0

    def test_removing_a_bounded_valued_property_if_its_only_value_is_the_set_point_value(self):
        pset = self.add_pset()
        ifcopenshell.api.pset.edit_pset(
            self.file, pset=pset, properties={"Foo": {"SetPointValue": self.file.createIfcReal(1.0)}}
        )
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Foo": {"SetPointValue": None}})
        assert not pset.HasProperties


@test.bootstrap.requires_ifc4x3
class TestEditPsetBoundedValueIFC4X3(test.bootstrap.IFC4X3, TestEditPsetBoundedValue):
    pass
