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

import operator
import test.bootstrap
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.guid
import ifcopenshell.util.element
from typing import Union


def get_properties(material: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    ifc_file = material.file
    if ifc_file.schema == "IFC2X3":
        for props in ifc_file.by_type("IfcExtendedMaterialProperties"):
            if props.Material == material:
                return props
        return None
    return next(iter(material.HasProperties), None)


class TestEditPsetIFC2X3(test.bootstrap.IFC2X3):
    def test_editing_a_templated_pset_with_automatic_casting_of_primitive_data_types(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={"ThermalTransmittance": "42"},
        )
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Reference": "bar", "Status": None})
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition

        assert pset.HasProperties[0].Name == "ThermalTransmittance"
        assert pset.HasProperties[0].NominalValue.is_a("IfcThermalTransmittanceMeasure")
        assert pset.HasProperties[0].NominalValue.wrappedValue == 42

    def test_adding_a_property_if_it_is_none(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Reference": None}, should_purge=False)
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert len(pset.HasProperties) == 1

    def test_not_adding_a_property_if_it_is_none_and_should_purge_is_true(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Reference": None}, should_purge=True)
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert len(pset.HasProperties) == 0

    def test_removing_a_none_property_if_specified(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Reference": "Foo"})
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Reference": None}, should_purge=True)
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert len(pset.HasProperties) == 0

    def test_editing_a_pset_name(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="foo")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, name="bar")
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert pset.Name == "bar"

    def test_adding_properties_without_a_template_with_autodetected_and_manual_data_types(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={
                "MyLabel": "foobar",
                "MyBool": True,
                "MyInteger": 42,
                "MyFloat": 42.0,
                "MyCustom": self.file.createIfcContextDependentMeasure(123),
            },
        )
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition

        assert pset.HasProperties[0].Name == "MyLabel"
        assert pset.HasProperties[0].NominalValue.is_a("IfcLabel")
        assert pset.HasProperties[0].NominalValue.wrappedValue == "foobar"

        assert pset.HasProperties[1].Name == "MyBool"
        assert pset.HasProperties[1].NominalValue.is_a("IfcBoolean")
        assert pset.HasProperties[1].NominalValue.wrappedValue == True

        assert pset.HasProperties[2].Name == "MyInteger"
        assert pset.HasProperties[2].NominalValue.is_a("IfcInteger")
        assert pset.HasProperties[2].NominalValue.wrappedValue == 42

        assert pset.HasProperties[3].Name == "MyFloat"
        assert pset.HasProperties[3].NominalValue.is_a("IfcReal")
        assert pset.HasProperties[3].NominalValue.wrappedValue == 42.0

        assert pset.HasProperties[4].Name == "MyCustom"
        assert pset.HasProperties[4].NominalValue.is_a("IfcContextDependentMeasure")
        assert pset.HasProperties[4].NominalValue.wrappedValue == 123.0

    def test_editing_properties_with_autodetected_existing_types(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={
                "MyCustom": self.file.createIfcContextDependentMeasure(12),
            },
        )
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={
                "MyCustom": 34,
            },
        )
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert pset.HasProperties[0].Name == "MyCustom"
        assert pset.HasProperties[0].NominalValue.is_a("IfcContextDependentMeasure")
        assert pset.HasProperties[0].NominalValue.wrappedValue == 34

    def test_editing_properties_with_an_explicit_type(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={
                "MyCustom": self.file.createIfcLabel("True"),
            },
        )
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={
                "MyCustom": self.file.createIfcBoolean(True),
            },
        )
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert pset.HasProperties[0].Name == "MyCustom"
        assert pset.HasProperties[0].NominalValue.is_a("IfcBoolean")
        assert pset.HasProperties[0].NominalValue.wrappedValue is True

    def test_editing_properties_with_custom_units(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        custom_unit = self.file.createIfcSIUnit(UnitType="PRESSUREUNIT", Prefix="GIGA", Name="PASCAL")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={
                "MyCustom": self.file.createIfcModulusOfElasticityMeasure(20),
            },
        )
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={
                "MyCustom": {"NominalValue": 30, "Unit": custom_unit},
            },
        )
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition
        unit = pset.HasProperties[0].Unit
        assert pset.HasProperties[0].Name == "MyCustom"
        assert pset.HasProperties[0].NominalValue.is_a("IfcModulusOfElasticityMeasure")
        assert pset.HasProperties[0].NominalValue.wrappedValue == 30
        assert unit.UnitType == "PRESSUREUNIT"
        assert unit.Prefix == "GIGA"
        assert unit.Name == "PASCAL"

    def test_editing_properties_of_non_rooted_elements(self):
        element = self.file.createIfcMaterial()
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"foo": "bar"})

        props = get_properties(element)
        assert props
        assert props == pset
        props_ = getattr(props, "ExtendedProperties" if self.file.schema == "IFC2X3" else "Properties")
        assert props_[0].Name == "foo"
        assert props_[0].NominalValue.is_a("IfcLabel")
        assert props_[0].NominalValue.wrappedValue == "bar"

    def test_editing_a_shared_property(self):
        element1 = self.file.createIfcMaterial()
        element2 = self.file.createIfcMaterial()
        pset1 = ifcopenshell.api.pset.add_pset(self.file, product=element1, name="Foo_Bar")
        pset2 = ifcopenshell.api.pset.add_pset(self.file, product=element2, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset1, properties={"foo": "bar"})
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset2, properties={"foo2": "bar2"})

        props1 = get_properties(element1)
        props2 = get_properties(element2)
        assert props1 and props2
        props_attr = "ExtendedProperties" if self.file.schema == "IFC2X3" else "Properties"
        shared_props = list(getattr(props1, props_attr)) + list(getattr(props2, props_attr))
        setattr(props1, props_attr, shared_props)

        assert ifcopenshell.util.element.get_pset(element1, "Foo_Bar", "foo2") == "bar2"
        assert ifcopenshell.util.element.get_pset(element2, "Foo_Bar", "foo2") == "bar2"
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset1, properties={"foo2": "bar3"})
        assert ifcopenshell.util.element.get_pset(element1, "Foo_Bar", "foo2") == "bar3"
        assert ifcopenshell.util.element.get_pset(element2, "Foo_Bar", "foo2") == "bar2"


class TestEditPsetIFC4(test.bootstrap.IFC4, TestEditPsetIFC2X3):
    def test_editing_a_blank_buildingsmart_templated_pset(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={"Reference": "reference", "Status": ["NEW"], "Combustible": True, "ThermalTransmittance": 42},
        )
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition

        assert pset.HasProperties[0].Name == "Reference"
        assert pset.HasProperties[0].NominalValue.is_a("IfcIdentifier")
        assert pset.HasProperties[0].NominalValue.wrappedValue == "reference"

        assert pset.HasProperties[1].Name == "Status"
        assert pset.HasProperties[1].EnumerationValues[0].is_a("IfcLabel")
        assert pset.HasProperties[1].EnumerationValues[0].wrappedValue == "NEW"

        assert pset.HasProperties[2].Name == "Combustible"
        assert pset.HasProperties[2].NominalValue.is_a("IfcBoolean")
        assert pset.HasProperties[2].NominalValue.wrappedValue == True

        assert pset.HasProperties[3].Name == "ThermalTransmittance"
        assert pset.HasProperties[3].NominalValue.is_a("IfcThermalTransmittanceMeasure")
        assert pset.HasProperties[3].NominalValue.wrappedValue == 42

    def test_editing_an_existing_buildingsmart_templated_pset(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={"Reference": "foo", "Status": ["NEW"], "Combustible": True, "ThermalTransmittance": 42},
        )
        ifcopenshell.api.pset.edit_pset(
            self.file, pset=pset, properties={"Reference": "bar", "Status": []}, should_purge=False
        )
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition

        assert pset.HasProperties[0].Name == "Reference"
        assert pset.HasProperties[0].NominalValue.is_a("IfcIdentifier")
        assert pset.HasProperties[0].NominalValue.wrappedValue == "bar"

        assert pset.HasProperties[1].Name == "Status"
        assert pset.HasProperties[1].EnumerationValues is None

    def test_editing_a_custom_templated_pset(self):
        template = self.file.create_entity(
            "IfcPropertySetTemplate",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "Name": "Foo_Bar",
                "TemplateType": "PSET_TYPEDRIVENOVERRIDE",
                "ApplicableEntity": "IfcWall",
                "HasPropertyTemplates": [
                    self.file.create_entity(
                        "IfcSimplePropertyTemplate",
                        **{
                            "GlobalId": ifcopenshell.guid.new(),
                            "Name": "foo",
                            "TemplateType": "P_SINGLEVALUE",
                            "PrimaryMeasureType": "IfcContextDependentMeasure",
                        },
                    )
                ],
            },
        )
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            pset_template=template,
            properties={
                "foo": 12,
            },
        )
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert pset.HasProperties[0].Name == "foo"
        assert pset.HasProperties[0].NominalValue.is_a("IfcContextDependentMeasure")
        assert pset.HasProperties[0].NominalValue.wrappedValue == 12

    def test_removing_a_none_enumeration_property_if_specified(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Status": ["NEW"]})
        assert pset.HasProperties[0].Name == "Status"
        assert pset.HasProperties[0].EnumerationValues[0].wrappedValue == "NEW"
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Status": []}, should_purge=True)
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert len(pset.HasProperties) == 0

    def test_editing_list_valued_properties(self):
        cable = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDistributionPort", predefined_type="CABLE")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=cable, name="Pset_DistributionPortTypeCable")
        ifcopenshell.api.pset.edit_pset(
            self.file,
            pset=pset,
            properties={
                "Protocols": ["One", "Two", "Three"],
            },
        )
        assert pset.HasProperties[0].is_a("IfcPropertyListValue")
        assert len(pset.HasProperties[0].ListValues) == 3
        assert set(map(ifcopenshell.entity_instance.is_a, pset.HasProperties[0].ListValues)) == {"IfcIdentifier"}
        assert list(map(operator.itemgetter(0), pset.HasProperties[0].ListValues)) == ["One", "Two", "Three"]
