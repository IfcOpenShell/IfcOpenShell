import test.bootstrap
import ifcopenshell.api


class TestEditPset(test.bootstrap.IFC4):
    def test_editing_a_blank_buildingsmart_templated_pset(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Pset_WallCommon")
        ifcopenshell.api.run(
            "pset.edit_pset",
            self.file,
            pset=pset,
            properties={"Reference": "reference", "Status": "NEW", "Combustible": True, "ThermalTransmittance": 42},
        )
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition

        assert pset.HasProperties[0].Name == "Reference"
        assert pset.HasProperties[0].NominalValue.is_a("IfcIdentifier")
        assert pset.HasProperties[0].NominalValue.wrappedValue == "reference"

        assert pset.HasProperties[1].Name == "Status"
        assert pset.HasProperties[1].NominalValue.is_a("IfcLabel")
        assert pset.HasProperties[1].NominalValue.wrappedValue == "NEW"

        assert pset.HasProperties[2].Name == "Combustible"
        assert pset.HasProperties[2].NominalValue.is_a("IfcBoolean")
        assert pset.HasProperties[2].NominalValue.wrappedValue == True

        assert pset.HasProperties[3].Name == "ThermalTransmittance"
        assert pset.HasProperties[3].NominalValue.is_a("IfcThermalTransmittanceMeasure")
        assert pset.HasProperties[3].NominalValue.wrappedValue == 42

    def test_editing_an_existing_buildingsmart_templated_pset(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Pset_WallCommon")
        ifcopenshell.api.run(
            "pset.edit_pset",
            self.file,
            pset=pset,
            properties={"Reference": "foo", "Status": "NEW", "Combustible": True, "ThermalTransmittance": 42},
        )
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Reference": "bar", "Status": None})
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition

        assert pset.HasProperties[0].Name == "Reference"
        assert pset.HasProperties[0].NominalValue.is_a("IfcIdentifier")
        assert pset.HasProperties[0].NominalValue.wrappedValue == "bar"

        assert pset.HasProperties[1].Name == "Status"
        assert pset.HasProperties[1].NominalValue is None

    def test_not_adding_a_property_if_it_is_none(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Pset_WallCommon")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Reference": None})
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert len(pset.HasProperties) == 0

    def test_editing_a_pset_name(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="foo")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, name="bar")
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition
        assert pset.Name == "bar"

    def test_adding_properties_without_a_template_with_autodetected_and_manual_data_types(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run(
            "pset.edit_pset",
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
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run(
            "pset.edit_pset",
            self.file,
            pset=pset,
            properties={
                "MyCustom": self.file.createIfcContextDependentMeasure(12),
            },
        )
        ifcopenshell.api.run(
            "pset.edit_pset",
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

    def test_editing_properties_of_non_rooted_elements(self):
        element = self.file.createIfcMaterial()
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"foo": "bar"})

        assert element.HasProperties[0] == pset
        assert pset.Properties[0].Name == "foo"
        assert pset.Properties[0].NominalValue.is_a("IfcLabel")
        assert pset.Properties[0].NominalValue.wrappedValue == "bar"

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
                        }
                    )
                ],
            }
        )
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run(
            "pset.edit_pset",
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
