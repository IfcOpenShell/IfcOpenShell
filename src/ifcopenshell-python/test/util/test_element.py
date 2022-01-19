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
import test.bootstrap
import ifcopenshell.api
import ifcopenshell.util.element as subject


class TestGetPsetsIFC4(test.bootstrap.IFC4):
    def test_getting_the_psets_of_a_product_as_a_dictionary(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        assert subject.get_psets(element) == {}
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="name")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"a": "b"})
        assert subject.get_psets(element) == {"name": {"a": "b", "id": pset.id()}}

    def test_getting_the_psets_of_a_product_type_as_a_dictionary(self):
        type_element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        assert subject.get_psets(type_element) == {}
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=type_element, name="name")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"x": "y"})
        assert subject.get_psets(type_element) == {"name": {"x": "y", "id": pset.id()}}

    def test_getting_the_psets_of_a_material_as_a_dictionary(self):
        material = self.file.createIfcMaterial()
        assert subject.get_psets(material) == {}
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=material, name="name")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"x": "y"})
        assert subject.get_psets(material) == {"name": {"x": "y", "id": pset.id()}}

    def test_getting_the_psets_of_a_profile_as_a_dictionary(self):
        profile = self.file.createIfcCircleProfileDef()
        assert subject.get_psets(profile) == {}
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=profile, name="name")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"x": "y"})
        assert subject.get_psets(profile) == {"name": {"x": "y", "id": pset.id()}}

    def test_getting_psets_from_an_element_which_cannot_have_psets(self):
        assert subject.get_psets(self.file.create_entity("IfcPerson")) == {}

    def test_only_getting_psets_and_not_qtos(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="pset")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"a": "b"})
        qto = ifcopenshell.api.run("pset.add_qto", self.file, product=element, name="qto")
        ifcopenshell.api.run("pset.edit_qto", self.file, qto=qto, properties={"x": 42})
        assert subject.get_psets(element, psets_only=True) == {"pset": {"a": "b", "id": pset.id()}}

    def test_only_getting_qtos_and_not_psets(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="pset")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"a": "b"})
        qto = ifcopenshell.api.run("pset.add_qto", self.file, product=element, name="qto")
        ifcopenshell.api.run("pset.edit_qto", self.file, qto=qto, properties={"x": 42})
        assert subject.get_psets(element, qtos_only=True) == {"qto": {"x": 42, "id": qto.id()}}


class TestGetPropertyDefinitionIFC4(test.bootstrap.IFC4):
    def test_getting_the_properties_of_a_pset(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="name")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"a": "b"})
        assert subject.get_property_definition(pset) == {"a": "b", "id": pset.id()}

    def test_getting_the_properties_of_a_qto(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        qto = ifcopenshell.api.run("pset.add_qto", self.file, product=element, name="name")
        ifcopenshell.api.run("pset.edit_qto", self.file, qto=qto, properties={"x": 42})
        assert subject.get_property_definition(qto) == {"x": 42, "id": qto.id()}

    def test_getting_the_properties_of_a_material_property(self):
        pset = self.file.createIfcMaterialProperties()
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"a": "b"})
        assert subject.get_property_definition(pset) == {"a": "b", "id": pset.id()}

    def test_getting_the_properties_of_a_profile_property(self):
        pset = self.file.createIfcProfileProperties()
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"a": "b"})
        assert subject.get_property_definition(pset) == {"a": "b", "id": pset.id()}

    def test_getting_the_properties_of_a_predefined_pset(self):
        pset = self.file.create_entity("IfcDoorLiningProperties", ifcopenshell.guid.new())
        pset.LiningDepth = 42
        assert subject.get_property_definition(pset) == {"LiningDepth": 42, "id": pset.id()}


class TestGetQuantitiesIFC4(test.bootstrap.IFC4):
    def test_getting_quantities_from_a_qto(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        qto = ifcopenshell.api.run("pset.add_qto", self.file, product=element, name="name")
        ifcopenshell.api.run("pset.edit_qto", self.file, qto=qto, properties={"x": 42})
        assert subject.get_quantities(qto.Quantities) == {"x": 42}


class TestGetPropertiesIFC4(test.bootstrap.IFC4):
    def test_getting_no_properties_when_none_are_available(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="name")
        assert subject.get_properties(pset.HasProperties) == {}

    def test_getting_single_properties_from_a_list_of_properties(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="name")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"a": "b"})
        assert subject.get_properties(pset.HasProperties) == {"a": "b"}

    def test_getting_complex_properties_from_a_list_of_properties(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="pset")
        complex_property = self.file.createIfcComplexProperty(Name="prop", UsageName="usage_name")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=complex_property, properties={"a": "b"})
        pset.HasProperties = [complex_property]
        assert subject.get_properties(pset.HasProperties) == {
            "prop": {
                "UsageName": "usage_name",
                "id": 4,
                "type": "IfcComplexProperty",
                "properties": {"a": "b"},
            }
        }


class TestGetPredefinedTypeIFC4(test.bootstrap.IFC4):
    def test_getting_an_element_predefined_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element.PredefinedType = "PARTITIONING"
        assert subject.get_predefined_type(element) == "PARTITIONING"

    def test_getting_an_element_userdefined_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element.PredefinedType = "USERDEFINED"
        element.ObjectType = "FOOBAR"
        assert subject.get_predefined_type(element) == "FOOBAR"

    def test_getting_an_inherited_predefined_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=element_type)
        element_type.PredefinedType = "PARTITIONING"
        assert subject.get_predefined_type(element) == "PARTITIONING"

    def test_getting_an_inherited_userdefined_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=element_type)
        element_type.PredefinedType = "USERDEFINED"
        element_type.ElementType = "FOOBAR"
        assert subject.get_predefined_type(element) == "FOOBAR"

    def test_getting_an_overriden_predefined_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=element_type)
        element_type.PredefinedType = "NOTDEFINED"
        element.PredefinedType = "PARTITIONING"
        assert subject.get_predefined_type(element) == "PARTITIONING"


class TestGetTypeIFC4(test.bootstrap.IFC4):
    def test_getting_the_type_of_a_product(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=element_type)
        assert subject.get_type(element) == element_type
        assert subject.get_type(element_type) == element_type


class TestGetTypeIFC2X3(test.bootstrap.IFC2X3):
    def test_getting_the_type_of_a_product(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=element_type)
        assert subject.get_type(element) == element_type
        assert subject.get_type(element_type) == element_type


class TestGetTypes(test.bootstrap.IFC4):
    def test_getting_the_type_of_a_product(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=element_type)
        assert subject.get_types(element_type) == (element,)


class TestGetTypesIFC2X3(test.bootstrap.IFC2X3):
    def test_getting_the_type_of_a_product(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=element_type)
        assert subject.get_types(element_type) == (element,)


class TestGetMaterial(test.bootstrap.IFC4):
    def test_getting_the_material_of_a_product(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file)
        ifcopenshell.api.run("material.assign_material", self.file, product=element, material=material)
        assert subject.get_material(element) == material

    def test_getting_a_material_list_of_a_product(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file)
        rel = ifcopenshell.api.run(
            "material.assign_material", self.file, product=element, type="IfcMaterialList", material=material
        )
        assert subject.get_material(element) == rel.RelatingMaterial

    def test_getting_a_material_layer_set_of_a_product(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialLayerSet")
        assert subject.get_material(element) == rel.RelatingMaterial

    def test_getting_a_material_profile_set_of_a_product(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.run("material.assign_material", self.file, product=element, type="IfcMaterialProfileSet")
        assert subject.get_material(element) == rel.RelatingMaterial

    def test_getting_a_material_layer_set_usage_of_a_product(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.run(
            "material.assign_material", self.file, product=element, type="IfcMaterialLayerSetUsage"
        )
        assert subject.get_material(element) == rel.RelatingMaterial

    def test_getting_a_material_profile_set_usage_of_a_product(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.run(
            "material.assign_material", self.file, product=element, type="IfcMaterialProfileSetUsage"
        )
        assert subject.get_material(element) == rel.RelatingMaterial

    def test_getting_a_material_layer_set_indirectly_from_an_assigned_usage(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.run(
            "material.assign_material", self.file, product=element, type="IfcMaterialLayerSetUsage"
        )
        assert subject.get_material(element, should_skip_usage=True) == rel.RelatingMaterial.ForLayerSet

    def test_getting_a_material_profile_set_indirectly_from_an_assigned_usage(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.run(
            "material.assign_material", self.file, product=element, type="IfcMaterialProfileSetUsage"
        )
        assert subject.get_material(element, should_skip_usage=True) == rel.RelatingMaterial.ForProfileSet

    def test_getting_an_inherited_material_from_the_elements_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=element_type)
        material = ifcopenshell.api.run("material.add_material", self.file)
        ifcopenshell.api.run("material.assign_material", self.file, product=element_type, material=material)
        assert subject.get_material(element) == material


class TestGetlayers(test.bootstrap.IFC4):
    def test_getting_the_layer_of_a_product_representation(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        layer = ifcopenshell.api.run("layer.add_layer", self.file)
        representation = self.file.createIfcShapeRepresentation()
        element.Representation = self.file.createIfcProductDefinitionShape(Representations=[representation])
        ifcopenshell.api.run("layer.assign_layer", self.file, item=representation, layer=layer)
        assert subject.get_layers(self.file, element) == [layer]

    def test_getting_the_layer_of_a_product_item(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        layer = ifcopenshell.api.run("layer.add_layer", self.file)
        item = self.file.createIfcExtrudedAreaSolid()
        representation = self.file.createIfcShapeRepresentation(Items=[item])
        element.Representation = self.file.createIfcProductDefinitionShape(Representations=[representation])
        ifcopenshell.api.run("layer.assign_layer", self.file, item=item, layer=layer)
        assert subject.get_layers(self.file, element) == [layer]

    def test_getting_the_layer_of_a_type_product_representation(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        layer = ifcopenshell.api.run("layer.add_layer", self.file)
        representation = self.file.createIfcShapeRepresentation()
        element.RepresentationMaps = [self.file.createIfcRepresentationMap(MappedRepresentation=representation)]
        ifcopenshell.api.run("layer.assign_layer", self.file, item=representation, layer=layer)
        assert subject.get_layers(self.file, element) == [layer]

    def test_getting_the_layer_of_a_type_product_item(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        layer = ifcopenshell.api.run("layer.add_layer", self.file)
        item = self.file.createIfcExtrudedAreaSolid()
        representation = self.file.createIfcShapeRepresentation(Items=[item])
        element.RepresentationMaps = [self.file.createIfcRepresentationMap(MappedRepresentation=representation)]
        ifcopenshell.api.run("layer.assign_layer", self.file, item=item, layer=layer)
        assert subject.get_layers(self.file, element) == [layer]


class TestGetlayers(test.bootstrap.IFC2X3):
    def test_getting_the_layer_of_a_product_item(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        layer = ifcopenshell.api.run("layer.add_layer", self.file)
        item = self.file.createIfcExtrudedAreaSolid()
        representation = self.file.createIfcShapeRepresentation(Items=[item])
        element.Representation = self.file.createIfcProductDefinitionShape(Representations=[representation])
        ifcopenshell.api.run("layer.assign_layer", self.file, item=item, layer=layer)
        assert subject.get_layers(self.file, element) == [layer]

    def test_getting_the_layer_of_a_type_product_item(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        layer = ifcopenshell.api.run("layer.add_layer", self.file)
        item = self.file.createIfcExtrudedAreaSolid()
        representation = self.file.createIfcShapeRepresentation(Items=[item])
        element.RepresentationMaps = [self.file.createIfcRepresentationMap(MappedRepresentation=representation)]
        ifcopenshell.api.run("layer.assign_layer", self.file, item=item, layer=layer)
        assert subject.get_layers(self.file, element) == [layer]


class TestGetContainerIFC4(test.bootstrap.IFC4):
    def test_getting_the_spatial_container_of_an_element(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        building = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.run("spatial.assign_container", self.file, product=element, relating_structure=building)
        assert subject.get_container(element) == building

    def test_getting_an_indirect_spatial_container_of_an_element(self):
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcElementAssembly")
        building = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.run("spatial.assign_container", self.file, product=element, relating_structure=building)
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
        assert subject.get_container(subelement) == building

    def test_getting_nothing_if_we_enforce_only_getting_direct_spatial_containers(self):
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcElementAssembly")
        building = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.run("spatial.assign_container", self.file, product=element, relating_structure=building)
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
        assert subject.get_container(subelement, should_get_direct=True) is None


class TestGetDecompositionIFC4(test.bootstrap.IFC4):
    def test_getting_decomposed_subelements_of_an_element(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBeam")
        building = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.run("spatial.assign_container", self.file, product=element, relating_structure=building)
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
        results = subject.get_decomposition(building)
        assert element in results
        assert subelement in results


class TestGetAggregateIFC4(test.bootstrap.IFC4):
    def test_getting_the_containing_aggregate_of_a_subelement(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcCovering")
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
        assert subject.get_aggregate(subelement) == element


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

    def test_removing_an_element_still_referenced_somewhere(self):
        owner = self.file.createIfcOwnerHistory()
        element = self.file.createIfcWall(GlobalId="id1", OwnerHistory=owner)
        subject.remove_deep2(self.file, owner)
        assert self.file.by_id(1)
        assert self.file.by_guid("id1")


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
        assert element.OwnerHistory.State == element2.OwnerHistory.State

    def test_copying_an_element_recursively_even_if_references_are_aggregated(self):
        element = self.file.createIfcWall(Name="name")
        rel = self.file.createIfcRelAggregates()
        rel.RelatedObjects = [element]
        rel2 = subject.copy_deep(self.file, rel)
        assert rel.RelatedObjects != rel2.RelatedObjects
        assert rel.RelatedObjects[0].Name == rel2.RelatedObjects[0].Name
