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

import ifcopenshell.api.profile
import pytest
import test.bootstrap
import ifcopenshell.api.void
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.type
import ifcopenshell.api.nest
import ifcopenshell.api.style
import ifcopenshell.api.layer
import ifcopenshell.api.library
import ifcopenshell.api.context
import ifcopenshell.api.spatial
import ifcopenshell.api.geometry
import ifcopenshell.api.sequence
import ifcopenshell.api.classification
import ifcopenshell.api.material
import ifcopenshell.api.document
import ifcopenshell.api.aggregate
import ifcopenshell.api.group
import ifcopenshell.guid
import ifcopenshell.util.element as subject


class TestGetPsetIFC4(test.bootstrap.IFC4):
    def test_getting_the_psets_of_a_product_as_a_dictionary(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        assert subject.get_pset(element, "name") is None
        assert subject.get_pset(element, "name", "a") is None
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"a": "b"})
        assert subject.get_pset(element, "name") == {"a": "b", "id": pset.id()}
        assert subject.get_pset(element, "name", "a") == "b"
        assert subject.get_pset(element, "name", "a", verbose=True) == {
            "id": 4,
            "class": "IfcPropertySingleValue",
            "value": "b",
            "value_type": "IfcLabel",
        }

    def test_getting_the_psets_of_a_product_type_as_a_dictionary(self):
        type_element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        foo = subject.get_pset(type_element, "name") is None
        pset = ifcopenshell.api.pset.add_pset(self.file, product=type_element, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"x": "y"})
        assert subject.get_pset(type_element, "name") == {"x": "y", "id": pset.id()}
        assert subject.get_pset(type_element, "name", verbose=True) == {
            "x": {
                "id": 3,
                "class": "IfcPropertySingleValue",
                "value": "y",
                "value_type": "IfcLabel",
            },
            "id": pset.id(),
        }

    def test_getting_inherited_psets(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        type_element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=type_element)
        pset = ifcopenshell.api.pset.add_pset(self.file, product=type_element, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"a": 1, "x": 1})
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"a": 2, "b": 3})
        result = subject.get_pset(element, "name")
        assert result["id"] == pset.id()
        assert result["a"] == 2
        assert result["x"] == 1
        assert result["b"] == 3
        assert subject.get_pset(element, "name", "a") == 2
        assert subject.get_pset(element, "name", "x") == 1
        assert subject.get_pset(element, "name", "b") == 3
        pset = ifcopenshell.api.pset.add_pset(self.file, product=type_element, name="name2")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"z": False})
        assert subject.get_pset(element, "name2", "z") is False

        # test filters with inherited psets
        assert subject.get_pset(element, "name", psets_only=True) == result
        assert subject.get_pset(element, "name", qtos_only=True) == None

    def test_excluding_inherited_psets(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        type_element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=type_element)
        pset = ifcopenshell.api.pset.add_pset(self.file, product=type_element, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"a": 1, "x": 1})
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"a": 2, "b": 3})
        result = subject.get_pset(element, "name", should_inherit=False)
        assert result["id"] == pset.id()
        assert result["a"] == 2
        assert result["b"] == 3
        assert "x" not in result
        assert subject.get_pset(element, "name", "a") == 2
        assert subject.get_pset(element, "name", "b") == 3

    def test_getting_the_psets_of_a_material_as_a_dictionary(self):
        material = self.file.createIfcMaterial()
        assert subject.get_pset(material, "name") is None
        assert subject.get_pset(material, "name", "x") is None
        pset = ifcopenshell.api.pset.add_pset(self.file, product=material, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"x": "y"})
        assert subject.get_pset(material, "name") == {"x": "y", "id": pset.id()}
        assert subject.get_pset(material, "name", "x") == "y"

    def test_getting_the_psets_of_a_profile_as_a_dictionary(self):
        profile = self.file.createIfcCircleProfileDef()
        assert subject.get_pset(profile, "name") is None
        assert subject.get_pset(profile, "name", "x") is None
        pset = ifcopenshell.api.pset.add_pset(self.file, product=profile, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"x": "y"})
        assert subject.get_pset(profile, "name") == {"x": "y", "id": pset.id()}
        assert subject.get_pset(profile, "name", "x") == "y"

    def test_getting_psets_from_an_element_which_cannot_have_psets(self):
        assert subject.get_pset(self.file.create_entity("IfcPerson"), "name") is None
        assert subject.get_pset(self.file.create_entity("IfcPerson"), "name", "a") is None


class TestGetPsetsIFC4(test.bootstrap.IFC4):
    def test_getting_the_psets_of_a_product_as_a_dictionary(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        assert subject.get_psets(element) == {}
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"a": "b"})
        assert subject.get_psets(element) == {"name": {"a": "b", "id": pset.id()}}

    def test_getting_the_psets_of_a_product_type_as_a_dictionary(self):
        type_element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        assert subject.get_psets(type_element) == {}
        pset = ifcopenshell.api.pset.add_pset(self.file, product=type_element, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"x": "y"})
        assert subject.get_psets(type_element) == {"name": {"x": "y", "id": pset.id()}}

    def test_getting_inherited_psets(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        type_element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=type_element)
        pset = ifcopenshell.api.pset.add_pset(self.file, product=type_element, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"a": 1, "x": 1})
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"a": 2, "b": 3})
        psets = subject.get_psets(element)
        assert psets["name"]["id"] == pset.id()
        assert psets["name"]["a"] == 2
        assert psets["name"]["x"] == 1
        assert psets["name"]["b"] == 3

    def test_getting_the_psets_of_a_material_as_a_dictionary(self):
        material = self.file.createIfcMaterial()
        assert subject.get_psets(material) == {}
        pset = ifcopenshell.api.pset.add_pset(self.file, product=material, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"x": "y"})
        assert subject.get_psets(material) == {"name": {"x": "y", "id": pset.id()}}

    def test_getting_the_psets_of_a_profile_as_a_dictionary(self):
        profile = self.file.createIfcCircleProfileDef()
        assert subject.get_psets(profile) == {}
        pset = ifcopenshell.api.pset.add_pset(self.file, product=profile, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"x": "y"})
        assert subject.get_psets(profile) == {"name": {"x": "y", "id": pset.id()}}

    def test_getting_psets_from_an_element_which_cannot_have_psets(self):
        assert subject.get_psets(self.file.create_entity("IfcPerson")) == {}

    def test_only_getting_psets_and_not_qtos(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="pset")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"a": "b"})
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="qto")
        ifcopenshell.api.pset.edit_qto(self.file, qto=qto, properties={"x": 42})
        assert subject.get_psets(element, psets_only=True) == {"pset": {"a": "b", "id": pset.id()}}

    def test_only_getting_qtos_and_not_psets(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="pset")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"a": "b"})
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="qto")
        ifcopenshell.api.pset.edit_qto(self.file, qto=qto, properties={"x": 42})
        assert subject.get_psets(element, qtos_only=True) == {"qto": {"x": 42, "id": qto.id()}}


class TestGetPropertyDefinitionIFC4(test.bootstrap.IFC4):
    def test_getting_the_properties_of_a_pset(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"a": "b"})
        assert subject.get_property_definition(pset) == {"a": "b", "id": pset.id()}

    def test_getting_the_properties_of_a_qto(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="name")
        ifcopenshell.api.pset.edit_qto(self.file, qto=qto, properties={"x": 42})
        assert subject.get_property_definition(qto) == {"x": 42, "id": qto.id()}

    def test_getting_the_properties_of_a_material_property(self):
        pset = self.file.createIfcMaterialProperties()
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"a": "b"})
        assert subject.get_property_definition(pset) == {"a": "b", "id": pset.id()}

    def test_getting_the_properties_of_a_profile_property(self):
        pset = self.file.createIfcProfileProperties()
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"a": "b"})
        assert subject.get_property_definition(pset) == {"a": "b", "id": pset.id()}

    def test_getting_the_properties_of_a_predefined_pset(self):
        pset = self.file.create_entity("IfcDoorLiningProperties", ifcopenshell.guid.new())
        pset.LiningDepth = 42
        assert subject.get_property_definition(pset) == {"LiningDepth": 42, "id": pset.id()}


class TestGetQuantitiesIFC4(test.bootstrap.IFC4):
    def test_getting_quantities_from_a_qto(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        qto = ifcopenshell.api.pset.add_qto(self.file, product=element, name="name")
        ifcopenshell.api.pset.edit_qto(self.file, qto=qto, properties={"x": 42})
        assert subject.get_quantities(qto.Quantities) == {"x": 42}


class TestGetPropertiesIFC4(test.bootstrap.IFC4):
    def test_getting_no_properties_when_none_are_available(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="name")
        assert subject.get_properties(pset.HasProperties) == {}

    def test_getting_single_properties_from_a_list_of_properties(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"a": "b"})
        assert subject.get_properties(pset.HasProperties) == {"a": "b"}

    def test_getting_complex_properties_from_a_list_of_properties(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="pset")
        complex_property = self.file.createIfcComplexProperty(Name="prop", UsageName="usage_name")
        ifcopenshell.api.pset.edit_pset(self.file, pset=complex_property, properties={"a": "b"})
        pset.HasProperties = [complex_property]
        assert subject.get_properties(pset.HasProperties) == {
            "prop": {
                "UsageName": "usage_name",
                "id": 4,
                "type": "IfcComplexProperty",
                "properties": {"a": "b"},
            }
        }


class TestGetElementsUsingPset(test.bootstrap.IFC4):
    def test_run(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        pset = self.file.create_entity("IfcPropertySet")
        ifcopenshell.api.pset.assign_pset(self.file, [element, element_type], pset)
        assert subject.get_elements_by_pset(pset) == {element, element_type}

    def test_get_material_for_pset(self):
        material = ifcopenshell.api.material.add_material(self.file)
        pset = ifcopenshell.api.pset.add_pset(self.file, material, "FooBar")
        assert subject.get_elements_by_pset(pset) == {material}

    def test_get_profile_for_pset(self):
        profile = ifcopenshell.api.profile.add_parameterized_profile(self.file, ifc_class="IfcRectangleProfileDef")
        pset = ifcopenshell.api.pset.add_pset(self.file, profile, "FooBar")
        assert subject.get_elements_by_pset(pset) == {profile}


class TestGetElementsUsingPsetIFC2X3(test.bootstrap.IFC2X3, TestGetElementsUsingPset): ...


class TestGetPredefinedTypeIFC4(test.bootstrap.IFC4):
    def test_getting_an_element_predefined_type(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element.PredefinedType = "PARTITIONING"
        assert subject.get_predefined_type(element) == "PARTITIONING"

    def test_getting_an_element_userdefined_type(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element.PredefinedType = "USERDEFINED"
        element.ObjectType = "FOOBAR"
        assert subject.get_predefined_type(element) == "FOOBAR"

    def test_getting_an_element_type_without_a_predefined_type_attribute(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcAnnotation")
        element.ObjectType = "FOOBAR"
        assert subject.get_predefined_type(element) == "FOOBAR"

    def test_getting_an_inherited_predefined_type(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        element_type.PredefinedType = "PARTITIONING"
        assert subject.get_predefined_type(element) == "PARTITIONING"

    def test_getting_an_inherited_userdefined_type_for_an_element_type(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        element_type.PredefinedType = "USERDEFINED"
        element_type.ElementType = "FOOBAR"
        assert subject.get_predefined_type(element) == "FOOBAR"

    def test_getting_an_overriden_predefined_type(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        element_type.PredefinedType = "NOTDEFINED"
        element.PredefinedType = "PARTITIONING"
        assert subject.get_predefined_type(element) == "PARTITIONING"

    def test_getting_an_inherited_userdefined_type_for_a_process_type(self):
        element = ifcopenshell.api.sequence.add_task(self.file)
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTaskType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        element_type.PredefinedType = "USERDEFINED"
        element_type.ProcessType = "FOOBAR"
        assert subject.get_predefined_type(element) == "FOOBAR"

    def test_getting_an_element_type_predefined_type(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element_type.PredefinedType = "PARTITIONING"
        assert subject.get_predefined_type(element_type) == "PARTITIONING"

    def test_getting_an_element_type_null_predefined_type(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element_type.PredefinedType = "NOTDEFINED"
        assert subject.get_predefined_type(element_type) == "NOTDEFINED"


class TestGetTypeIFC4(test.bootstrap.IFC4):
    def test_getting_the_type_of_a_product(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        assert subject.get_type(element) == element_type
        assert subject.get_type(element_type) == element_type


class TestGetTypeIFC2X3(test.bootstrap.IFC2X3, TestGetTypeIFC4):
    pass


class TestGetTypes(test.bootstrap.IFC4):
    def test_getting_the_type_of_a_product(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        assert subject.get_types(element_type) == (element,)


class TestGetTypesIFC2X3(test.bootstrap.IFC2X3, TestGetTypes):
    pass


class TestGetShapeAspects(test.bootstrap.IFC4):
    def test_getting_the_shape_aspects_of_a_product_type(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        shape_aspect = self.file.createIfcShapeAspect()
        representation_map = self.file.createIfcRepresentationMap()
        element_type.RepresentationMaps = (representation_map,)
        shape_aspect.PartOfProductDefinitionShape = representation_map
        assert tuple(subject.get_shape_aspects(element_type)) == (shape_aspect,)

    def test_getting_the_shape_aspects_of_a_product(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        shape_aspect = self.file.createIfcShapeAspect()
        product_shape = self.file.createIfcProductDefinitionShape()
        element.Representation = product_shape
        shape_aspect.PartOfProductDefinitionShape = product_shape
        assert tuple(subject.get_shape_aspects(element)) == (shape_aspect,)


class TestGetMaterial(test.bootstrap.IFC4):
    def test_getting_the_material_of_a_product(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(self.file)
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material)
        assert subject.get_material(element) == material

    def test_getting_a_material_list_of_a_product(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(self.file)
        rel = ifcopenshell.api.material.assign_material(
            self.file, products=[element], type="IfcMaterialList", material=material
        )
        assert subject.get_material(element) == rel.RelatingMaterial

    def test_getting_a_material_layer_set_of_a_product(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.material.assign_material(self.file, products=[element], type="IfcMaterialLayerSet")
        assert subject.get_material(element) == rel.RelatingMaterial

    def test_getting_a_material_profile_set_of_a_product(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.material.assign_material(self.file, products=[element], type="IfcMaterialProfileSet")
        assert subject.get_material(element) == rel.RelatingMaterial

    def test_getting_a_material_layer_set_usage_of_a_product(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.material.assign_material(self.file, products=[element], type="IfcMaterialLayerSetUsage")
        assert subject.get_material(element) == rel.RelatingMaterial

    def test_getting_a_material_profile_set_usage_of_a_product(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.material.assign_material(
            self.file, products=[element], type="IfcMaterialProfileSetUsage"
        )
        assert subject.get_material(element) == rel.RelatingMaterial

    def test_getting_a_material_layer_set_indirectly_from_an_assigned_usage(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.material.assign_material(self.file, products=[element], type="IfcMaterialLayerSetUsage")
        assert subject.get_material(element, should_skip_usage=True) == rel.RelatingMaterial.ForLayerSet

    def test_getting_a_material_profile_set_indirectly_from_an_assigned_usage(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.material.assign_material(
            self.file, products=[element], type="IfcMaterialProfileSetUsage"
        )
        assert subject.get_material(element, should_skip_usage=True) == rel.RelatingMaterial.ForProfileSet

    def test_getting_an_inherited_material_from_the_elements_type(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        material = ifcopenshell.api.material.add_material(self.file)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type], material=material)
        assert subject.get_material(element) == material

    def test_getting_an_overridden_material_from_the_elements_occurrence(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        material = ifcopenshell.api.material.add_material(self.file)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type], material=material)
        material = ifcopenshell.api.material.add_material(self.file)
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material)
        assert subject.get_material(element) == material

    def test_getting_direct_materials_without_checking_inheritance(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        material = ifcopenshell.api.material.add_material(self.file)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type], material=material)
        assert subject.get_material(element, should_inherit=False) is None


class TestGetMaterials(test.bootstrap.IFC4):
    def test_getting_the_materials_of_a_product(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(self.file)
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material)
        assert subject.get_materials(element) == [material]


class TestGetStyles(test.bootstrap.IFC4):
    def test_getting_the_styles_of_a_product(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        assert subject.get_styles(element) == []

        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            self.file,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model,
        )

        material = ifcopenshell.api.material.add_material(self.file)
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material)

        style = ifcopenshell.api.style.add_style(self.file)
        ifcopenshell.api.style.add_surface_style(
            self.file,
            style=style,
            ifc_class="IfcSurfaceStyleShading",
            attributes={
                "SurfaceColour": {"Name": None, "Red": 1.0, "Green": 0.8, "Blue": 0.8},
                "Transparency": 0.0,  # 0 is opaque, 1 is transparent
            },
        )
        ifcopenshell.api.style.assign_material_style(self.file, material=material, style=style, context=body)

        assert subject.get_styles(element) == [style]

        style2 = ifcopenshell.api.style.add_style(self.file)
        ifcopenshell.api.style.add_surface_style(
            self.file,
            style=style2,
            ifc_class="IfcSurfaceStyleShading",
            attributes={
                "SurfaceColour": {"Name": None, "Red": 1.0, "Green": 0.8, "Blue": 0.8},
                "Transparency": 0.0,  # 0 is opaque, 1 is transparent
            },
        )

        representation = ifcopenshell.api.geometry.add_wall_representation(
            self.file, context=body, length=5, height=3, thickness=0.118
        )

        ifcopenshell.api.geometry.assign_representation(self.file, product=element, representation=representation)
        ifcopenshell.api.style.assign_representation_styles(
            self.file, shape_representation=representation, styles=[style2]
        )

        assert subject.get_styles(element) == [style, style2]


class TestGetElementsByMaterial(test.bootstrap.IFC4):
    def test_getting_elements_of_a_material(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(self.file)
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material)
        assert subject.get_elements_by_material(self.file, material) == {element}

    def test_getting_elements_of_a_material_layer_set(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        material = ifcopenshell.api.material.add_material(self.file)
        material_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialLayerSet")
        ifcopenshell.api.material.add_layer(self.file, layer_set=material_set, material=material)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type], material=material_set)
        ifcopenshell.api.material.assign_material(self.file, products=[element], type="IfcMaterialLayerSetUsage")
        usage = self.file.by_type("IfcMaterialLayerSetUsage")[0]
        assert subject.get_elements_by_material(self.file, material) == {element, element_type}
        assert subject.get_elements_by_material(self.file, material_set) == {element, element_type}
        assert subject.get_elements_by_material(self.file, usage) == {element}

    def test_getting_elements_of_a_material_profile_set(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        material = ifcopenshell.api.material.add_material(self.file)
        material_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialProfileSet")
        ifcopenshell.api.material.add_profile(self.file, profile_set=material_set, material=material)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type], material=material_set)
        ifcopenshell.api.material.assign_material(self.file, products=[element], type="IfcMaterialProfileSetUsage")
        usage = self.file.by_type("IfcMaterialProfileSetUsage")[0]
        assert subject.get_elements_by_material(self.file, material) == {element, element_type}
        assert subject.get_elements_by_material(self.file, material_set) == {element, element_type}
        assert subject.get_elements_by_material(self.file, usage) == {element}

    def test_getting_elements_of_a_material_constituent_set(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(self.file)
        material_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialConstituentSet")
        ifcopenshell.api.material.add_constituent(self.file, constituent_set=material_set, material=material)
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material_set)
        assert subject.get_elements_by_material(self.file, material) == {element}
        assert subject.get_elements_by_material(self.file, material_set) == {element}

    def test_getting_elements_of_a_material_list(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(self.file)
        material_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialList")
        ifcopenshell.api.material.add_list_item(self.file, material_list=material_set, material=material)
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material_set)
        assert subject.get_elements_by_material(self.file, material) == {element}
        assert subject.get_elements_by_material(self.file, material_set) == {element}


class TestGetElementsByStyle(test.bootstrap.IFC4):
    def test_getting_elements_of_a_styled_representation_item(self):
        element = self.file.createIfcWall()
        style = self.file.createIfcSurfaceStyle()
        item = self.file.createIfcExtrudedAreaSolid()
        self.file.createIfcStyledItem(Item=item, Styles=[style])
        element.Representation = self.file.createIfcProductDefinitionShape(
            Representations=[self.file.createIfcShapeRepresentation(Items=[item])]
        )
        assert subject.get_elements_by_style(self.file, style) == {element}

    def test_getting_elements_of_a_styled_mapped_representation_item(self):
        element = self.file.createIfcWall()
        style = self.file.createIfcSurfaceStyle()
        item = self.file.createIfcExtrudedAreaSolid()
        self.file.createIfcStyledItem(Item=item, Styles=[style])
        element.Representation = self.file.createIfcProductDefinitionShape(
            Representations=[
                self.file.createIfcShapeRepresentation(
                    Items=[
                        self.file.createIfcMappedItem(
                            MappingSource=self.file.createIfcRepresentationMap(
                                MappedRepresentation=self.file.createIfcShapeRepresentation(Items=[item])
                            )
                        )
                    ]
                )
            ]
        )
        assert subject.get_elements_by_style(self.file, style) == {element}

    def test_getting_type_elements_of_a_styled_mapped_representation_item(self):
        element = self.file.createIfcWallType()
        style = self.file.createIfcSurfaceStyle()
        item = self.file.createIfcExtrudedAreaSolid()
        self.file.createIfcStyledItem(Item=item, Styles=[style])
        element.RepresentationMaps = [
            self.file.createIfcRepresentationMap(
                MappedRepresentation=self.file.createIfcShapeRepresentation(Items=[item])
            )
        ]
        assert subject.get_elements_by_style(self.file, style) == {element}

    def test_getting_elements_of_a_styled_material(self):
        element = self.file.createIfcWall()
        material = ifcopenshell.api.material.add_material(self.file)
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material)
        style = self.file.createIfcSurfaceStyle()
        self.file.createIfcMaterialDefinitionRepresentation(
            RepresentedMaterial=material,
            Representations=[
                self.file.createIfcStyledRepresentation(Items=[self.file.createIfcStyledItem(Styles=[style])])
            ],
        )
        assert subject.get_elements_by_style(self.file, style) == {element}

    def test_getting_elements_of_a_styled_material_with_curve_style_hatching(self):
        element = self.file.create_entity("IfcWall")
        material = ifcopenshell.api.material.add_material(self.file)
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material)
        curve_style = self.file.create_entity("IfcCurveStyle")
        fill_style = self.file.create_entity("IfcFillAreaStyleHatching", HatchLineAppearance=curve_style)
        style = self.file.create_entity("IfcFillAreaStyle", FillStyles=[fill_style])
        self.file.create_entity(
            "IfcMaterialDefinitionRepresentation",
            RepresentedMaterial=material,
            Representations=[
                self.file.create_entity(
                    "IfcStyledRepresentation", Items=[self.file.create_entity("IfcStyledItem", Styles=[style])]
                )
            ],
        )
        assert subject.get_elements_by_style(self.file, curve_style) == {element}

    def test_getting_elements_of_a_styled_material_with_fill_area_style_tiles(self):
        # NOTE: Not sure if this the exactly correct way to implement IfcFillAreaStyleTiles
        # couldn't find any .ifc files implementing it, so taking my best guess.
        # Ref: https://web.archive.org/web/20220711062839/https://ifcdoctor.com/2022/07/11/graphics-in-ifc/
        element = self.file.create_entity("IfcWall")
        material = ifcopenshell.api.material.add_material(self.file)
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material)
        tile_style = self.file.create_entity("IfcCurveStyle")
        tile_curve = self.file.create_entity("IfcGeometricSet")
        styled_item = self.file.create_entity("IfcStyledItem", Styles=[tile_style], Item=tile_curve)
        fill_style = self.file.create_entity("IfcFillAreaStyleTiles", Tiles=[styled_item])
        style = self.file.create_entity("IfcFillAreaStyle", FillStyles=[fill_style])
        self.file.create_entity(
            "IfcMaterialDefinitionRepresentation",
            RepresentedMaterial=material,
            Representations=[
                self.file.create_entity(
                    "IfcStyledRepresentation", Items=[self.file.create_entity("IfcStyledItem", Styles=[style])]
                )
            ],
        )
        assert subject.get_elements_by_style(self.file, tile_style) == {element}


class TestGetElementsByRepresentation(test.bootstrap.IFC4):
    def test_getting_elements_of_a_styled_representation_item(self):
        element = self.file.createIfcWall()
        representation = self.file.createIfcShapeRepresentation()
        element.Representation = self.file.createIfcProductDefinitionShape(Representations=[representation])
        assert subject.get_elements_by_representation(self.file, representation) == {element}

    def test_getting_elements_of_a_styled_mapped_representation_item(self):
        element = self.file.createIfcWall()
        representation = self.file.createIfcShapeRepresentation()
        element.Representation = self.file.createIfcProductDefinitionShape(
            Representations=[
                self.file.createIfcShapeRepresentation(
                    Items=[
                        self.file.createIfcMappedItem(
                            MappingSource=self.file.createIfcRepresentationMap(MappedRepresentation=representation)
                        )
                    ]
                )
            ]
        )
        assert subject.get_elements_by_representation(self.file, representation) == {element}

    def test_getting_type_elements_of_a_styled_mapped_representation_item(self):
        element = self.file.createIfcWallType()
        representation = self.file.createIfcShapeRepresentation()
        element.RepresentationMaps = [self.file.createIfcRepresentationMap(MappedRepresentation=representation)]
        assert subject.get_elements_by_representation(self.file, representation) == {element}


class TestGetElementsByLayer(test.bootstrap.IFC4):
    def test_getting_the_elements_of_a_layer(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        layer = ifcopenshell.api.layer.add_layer(self.file)
        representation = self.file.createIfcShapeRepresentation()
        element.Representation = self.file.createIfcProductDefinitionShape(Representations=[representation])
        ifcopenshell.api.layer.assign_layer(self.file, items=[representation], layer=layer)
        assert list(subject.get_elements_by_layer(self.file, layer)) == [element]


class TestGetlayersIFC2X3(test.bootstrap.IFC2X3):
    def test_getting_the_layer_of_a_product_item(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        layer = ifcopenshell.api.layer.add_layer(self.file)
        item = self.file.createIfcExtrudedAreaSolid()
        representation = self.file.createIfcShapeRepresentation(Items=[item])
        element.Representation = self.file.createIfcProductDefinitionShape(Representations=[representation])
        ifcopenshell.api.layer.assign_layer(self.file, items=[item], layer=layer)
        assert subject.get_layers(self.file, element) == [layer]

    def test_getting_the_layer_of_a_type_product_item(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        layer = ifcopenshell.api.layer.add_layer(self.file)
        item = self.file.createIfcExtrudedAreaSolid()
        representation = self.file.createIfcShapeRepresentation(Items=[item])
        element.RepresentationMaps = [self.file.createIfcRepresentationMap(MappedRepresentation=representation)]
        ifcopenshell.api.layer.assign_layer(self.file, items=[item], layer=layer)
        assert subject.get_layers(self.file, element) == [layer]


class TestGetlayers(test.bootstrap.IFC4, TestGetlayersIFC2X3):
    def test_getting_the_layer_of_a_product_representation(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        layer = ifcopenshell.api.layer.add_layer(self.file)
        representation = self.file.createIfcShapeRepresentation()
        element.Representation = self.file.createIfcProductDefinitionShape(Representations=[representation])
        ifcopenshell.api.layer.assign_layer(self.file, items=[representation], layer=layer)
        assert subject.get_layers(self.file, element) == [layer]

    def test_getting_the_layer_of_a_type_product_representation(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        layer = ifcopenshell.api.layer.add_layer(self.file)
        representation = self.file.createIfcShapeRepresentation()
        element.RepresentationMaps = [self.file.createIfcRepresentationMap(MappedRepresentation=representation)]
        ifcopenshell.api.layer.assign_layer(self.file, items=[representation], layer=layer)
        assert subject.get_layers(self.file, element) == [layer]


class TestGetContainerIFC4(test.bootstrap.IFC4):
    def test_getting_the_spatial_container_of_an_element(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.spatial.assign_container(self.file, products=[element], relating_structure=building)
        assert subject.get_container(element) == building

    def test_getting_an_indirect_spatial_container_of_an_element(self):
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcElementAssembly")
        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.spatial.assign_container(self.file, products=[element], relating_structure=building)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=element)
        assert subject.get_container(subelement) == building

    def test_getting_nothing_if_we_enforce_only_getting_direct_spatial_containers(self):
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcElementAssembly")
        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.spatial.assign_container(self.file, products=[element], relating_structure=building)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=element)
        assert subject.get_container(subelement, should_get_direct=True) is None


class TestGetReferencedStructures(test.bootstrap.IFC4):
    def test_getting_references_of_an_element(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        assert subject.get_referenced_structures(element) == []
        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.spatial.reference_structure(self.file, products=[element], relating_structure=building)
        assert subject.get_referenced_structures(element) == [building]
        building2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.spatial.reference_structure(self.file, products=[element], relating_structure=building2)
        assert subject.get_referenced_structures(element) == [building, building2]


class TestGetReferencedStructuresIFC2X3(test.bootstrap.IFC2X3, TestGetReferencedStructures):
    pass


class TestGetStructureReferencedElements(test.bootstrap.IFC4):
    def test_getting_references_of_an_element(self):
        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        assert subject.get_structure_referenced_elements(building) == set()
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.spatial.reference_structure(self.file, products=[element], relating_structure=building)
        assert subject.get_structure_referenced_elements(building) == {element}
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.spatial.reference_structure(self.file, products=[element2], relating_structure=building)
        assert subject.get_structure_referenced_elements(building) == {element, element2}


class TestGetStructureReferencedElementsIFC2X3(test.bootstrap.IFC2X3, TestGetStructureReferencedElements):
    pass


class TestGetDecompositionIFC4(test.bootstrap.IFC4):
    def test_getting_decomposed_subelements_of_an_element(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBeam")
        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.spatial.assign_container(self.file, products=[element], relating_structure=building)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=element)
        results = subject.get_decomposition(building)
        assert element in results
        assert subelement in results

    def test_getting_openings_and_fills_of_an_element(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        subsubelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWindow")
        ifcopenshell.api.void.add_opening(self.file, element=element, opening=subelement)
        ifcopenshell.api.void.add_filling(self.file, element=subsubelement, opening=subelement)
        results = subject.get_decomposition(element)
        assert subelement in results
        assert subsubelement in results


class TestGetGroupsIFC4(test.bootstrap.IFC4):
    def test_run(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        group1 = ifcopenshell.api.group.add_group(self.file)
        group2 = ifcopenshell.api.group.add_group(self.file)

        # assign group for multiple elements
        ifcopenshell.api.group.assign_group(self.file, products=[element], group=group1)
        ifcopenshell.api.group.assign_group(self.file, products=[element], group=group2)

        assert set(subject.get_groups(element)) == set([group1, group2])


class TestGetGroupsIFC2X3(test.bootstrap.IFC2X3, TestGetGroupsIFC4):
    pass


class TestGetAggregateIFC4(test.bootstrap.IFC4):
    def test_getting_the_containing_aggregate_of_a_subelement(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcCovering")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=element)
        assert subject.get_aggregate(subelement) == element


class TestGetNestIFC4(test.bootstrap.IFC4):
    def test_getting_the_nest_parent_of_an_element(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        ifcopenshell.api.nest.assign_object(self.file, related_objects=[subelement], relating_object=element)
        assert subject.get_nest(subelement) == element


class TestGetNestIFC2X3(test.bootstrap.IFC2X3, TestGetNestIFC4):
    pass


class TestGetPartsIFC4(test.bootstrap.IFC4):
    def test_run(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWindow")
        ifcopenshell.api.aggregate.assign_object(self.file, products=[subelement], relating_object=element)

        # Test two separate rels.
        rel = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcRelAggregates")
        subelement2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWindow")
        rel.RelatingObject = element
        rel.RelatedObjects = [subelement2]

        assert set(subject.get_parts(element)) == {subelement, subelement2}


class TestGetPartsIFC2X3(test.bootstrap.IFC2X3, TestGetPartsIFC4):
    pass


class TestGetReferencedElements(test.bootstrap.IFC4):
    # TODO: test other references:
    # IfcExternallyDefinedHatchStyle
    # IfcExternallyDefinedSurfaceStyle
    # IfcExternallyDefinedTextFont
    def test_get_elements_referenced_by_classification_reference(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        elements = [ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")]
        if self.file.schema != "IFC2X3":
            elements.append(self.file.create_entity("IfcCostValue"))
        result = ifcopenshell.api.classification.add_classification(self.file, classification="Name")
        reference = ifcopenshell.api.classification.add_reference(
            self.file,
            products=elements,
            identification="X",
            name="Foobar",
            classification=result,
        )
        assert reference
        assert subject.get_referenced_elements(reference) == set(elements)

    def test_get_elements_referenced_by_library_reference(self):
        reference = self.file.createIfcLibraryReference()
        elements = [
            ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall"),
            ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall"),
        ]
        ifcopenshell.api.library.assign_reference(self.file, reference=reference, products=elements)
        assert subject.get_referenced_elements(reference) == set(elements)

    def test_get_elements_referenced_by_document_reference(self):
        reference = ifcopenshell.api.document.add_reference(self.file, information=None)
        elements = [
            ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall"),
            ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall"),
        ]
        ifcopenshell.api.document.assign_document(self.file, document=reference, products=elements)
        assert subject.get_referenced_elements(reference) == set(elements)

    def test_get_elements_referenced_by_document_info(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        info = ifcopenshell.api.document.add_information(self.file)
        assert subject.get_referenced_elements(info) == set([project])

    def test_get_elements_referenced_by_classification(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        info = ifcopenshell.api.classification.add_classification(self.file, classification="Name")
        assert subject.get_referenced_elements(info) == set([project])

    def test_get_elements_referenced_by_library(self):
        info = ifcopenshell.api.library.add_library(self.file, name="Name")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        rel = self.file.create_entity("IfcRelAssociatesLibrary")
        rel.RelatingLibrary = info
        rel.RelatedObjects = [element]
        assert subject.get_referenced_elements(info) == set([element])


class TestGetReferencedElementsIFC2X3(test.bootstrap.IFC2X3, TestGetReferencedElements):
    pass


class TestReplaceAttributeIFC4(test.bootstrap.IFC4):
    def test_replacing_an_elements_attribute(self):
        element = self.file.createIfcWall("foo")
        subject.replace_attribute(element, "foo", "bar")
        assert element.GlobalId == "bar"

    def test_replacing_a_value_in_a_list(self):
        old = self.file.createIfcWall()
        new = self.file.createIfcWall()
        rel = self.file.createIfcRelAggregates()
        rel.RelatedObjects = [old]
        subject.replace_attribute(rel, old, new)
        assert rel.RelatedObjects == (new,)


class TestHasElementReferenceIFC4(test.bootstrap.IFC4):
    def test_if_a_element_attribute_references_another_element(self):
        old = self.file.createIfcWall()
        new = self.file.createIfcWall()
        rel = self.file.createIfcRelAggregates()
        rel.RelatedObjects = [old]
        assert subject.has_element_reference(rel.RelatedObjects, old) is True
        assert subject.has_element_reference(rel.RelatedObjects, new) is False


class TestRemoveDeepIFC4(test.bootstrap.IFC4):
    def test_removing_an_element_along_with_all_direct_attributes_recursively(self):
        owner = self.file.createIfcOwnerHistory()
        element = self.file.createIfcWall(GlobalId="id", OwnerHistory=owner)
        subject.remove_deep(self.file, element)
        with pytest.raises(RuntimeError):
            self.file.by_id(1)
            self.file.by_id(2)

    def test_removing_an_element_recursively_except_if_an_element_is_referenced_elsewhere(self):
        owner = self.file.createIfcOwnerHistory()
        element = self.file.createIfcWall(GlobalId="id1", OwnerHistory=owner)
        element2 = self.file.createIfcWall(GlobalId="id2", OwnerHistory=owner)
        subject.remove_deep(self.file, element)
        with pytest.raises(RuntimeError):
            self.file.by_guid("id1")
        assert self.file.by_id(1)
        assert self.file.by_guid("id2")


class TestRemoveDeep2IFC4(test.bootstrap.IFC4):
    def test_removing_an_element_along_with_all_direct_attributes_recursively(self):
        owner = self.file.createIfcOwnerHistory()
        element = self.file.createIfcWall(GlobalId="id", OwnerHistory=owner)
        subject.remove_deep2(self.file, element)
        with pytest.raises(RuntimeError):
            self.file.by_id(1)
            self.file.by_id(2)

    def test_removing_an_element_recursively_except_if_an_element_is_referenced_elsewhere(self):
        owner = self.file.createIfcOwnerHistory()
        element = self.file.createIfcWall(GlobalId="id1", OwnerHistory=owner)
        element2 = self.file.createIfcWall(GlobalId="id2", OwnerHistory=owner)
        subject.remove_deep2(self.file, element)
        with pytest.raises(RuntimeError):
            self.file.by_guid("id1")
        assert self.file.by_id(1)
        assert self.file.by_guid("id2")

    def test_not_removing_an_element_still_referenced_somewhere(self):
        owner = self.file.createIfcOwnerHistory()
        element = self.file.createIfcWall(GlobalId="id1", OwnerHistory=owner)
        subject.remove_deep2(self.file, owner)
        assert self.file.by_id(1)
        assert self.file.by_guid("id1")


class TestBatchRemoveDeep2IFC4(test.bootstrap.IFC4):
    def test_run(self):
        owner = self.file.createIfcOwnerHistory()
        element = self.file.createIfcWall(GlobalId="id", OwnerHistory=owner)
        subject.batch_remove_deep2(self.file)
        subject.remove_deep2(self.file, element)
        new = subject.unbatch_remove_deep2(self.file)
        assert self.file.by_id(1)
        with pytest.raises(RuntimeError):
            new.by_id(1)


class TestCopyIFC4(test.bootstrap.IFC4):
    def test_copying_an_element(self):
        element = self.file.createIfcWall(GlobalId="id", Name="name")
        element2 = subject.copy(self.file, element)
        assert element.is_a() == element2.is_a()
        assert element.GlobalId != element2.GlobalId
        assert element.Name == element2.Name


class TestCopyDeepIFC4(test.bootstrap.IFC4):
    def test_copying_an_element_recursively(self):
        owner = self.file.createIfcOwnerHistory()
        owner.State = "READWRITE"
        element = self.file.createIfcWall(GlobalId="id", Name="name", OwnerHistory=owner)
        element2 = subject.copy_deep(self.file, element)
        assert element.OwnerHistory != element2.OwnerHistory
        assert element.GlobalId != element2.GlobalId
        assert element.OwnerHistory.State == element2.OwnerHistory.State

    def test_copying_an_element_recursively_even_if_references_are_aggregated(self):
        element = self.file.createIfcWall(Name="name")
        rel = self.file.createIfcRelAggregates()
        rel.RelatedObjects = [element]
        rel2 = subject.copy_deep(self.file, rel)
        assert rel.RelatedObjects != rel2.RelatedObjects
        assert rel.RelatedObjects[0].Name == rel2.RelatedObjects[0].Name

    def test_copying_an_element_recursively_with_an_exclude_filter(self):
        owner = self.file.createIfcOwnerHistory()
        owner.State = "READWRITE"
        element = self.file.createIfcWall(GlobalId="id", Name="name", OwnerHistory=owner)
        element2 = subject.copy_deep(self.file, element, exclude=["IfcOwnerHistory"])
        assert element.OwnerHistory == element2.OwnerHistory

    def test_copying_an_element_recursively_with_aggregates_with_an_exclude_filter(self):
        element = self.file.createIfcWall(Name="name")
        rel = self.file.createIfcRelAggregates()
        rel.RelatedObjects = [element]
        rel2 = subject.copy_deep(self.file, rel, exclude=["IfcWall"])
        assert rel.RelatedObjects == rel2.RelatedObjects

    def test_copying_an_element_recursively_with_aggregates_with_an_exclude_callback(self):
        element = self.file.createIfcWall(Name="name")
        rel = self.file.createIfcRelAggregates()
        rel.RelatedObjects = [element]
        rel2 = subject.copy_deep(self.file, rel, exclude_callback=lambda x: x.is_a("IfcWall"))
        assert rel.RelatedObjects == rel2.RelatedObjects

    def test_copying_and_reusing_element_references(self):
        points = self.file.createIfcCartesianPointList2D()
        subelement1 = self.file.createIfcIndexedPolyCurve(points)
        subelement2 = self.file.createIfcIndexedPolyCurve(points)
        element = self.file.createIfcGeometricCurveSet([subelement1, subelement2])
        element2 = subject.copy_deep(self.file, element)
        assert element2.Elements[0].Points.id() == element2.Elements[1].Points.id()

    def test_copying_primitive_entities(self):
        element = self.file.createIfcIndexedPolyCurve(
            Segments=(self.file.createIfcLineIndex((1, 2)), self.file.createIfcLineIndex((3, 4)))
        )
        element2 = subject.copy_deep(self.file, element)
        assert element2.Segments[0][0] == (1, 2)
        assert element2.Segments[1][0] == (3, 4)
