# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.util.selector as subject
import ifcopenshell.util.placement
import ifcopenshell.util.pset
import numpy as np


class TestFormat:
    def test_no_formatting(self):
        assert subject.format("123") == "123"
        assert subject.format('"123"') == "123"
        assert subject.format('"foo"') == "foo"

    def test_string_formatting(self):
        assert subject.format('upper("fOo")') == "FOO"
        assert subject.format('lower("fOo")') == "foo"
        assert subject.format('title("fOo")') == "Foo"
        assert subject.format('concat("fOo", "bar")') == "fOobar"
        assert subject.format('upper(concat("fOo", "bar"))') == "FOOBAR"
        assert subject.format('substr("foobar", 3)') == "bar"
        assert subject.format('substr("foobar", 1, 2)') == "o"
        assert subject.format('substr("foobar", 1, -1)') == "ooba"

    def test_number_formatting(self):
        assert subject.format("round(123, 5)") == "125"
        assert subject.format('round("123", 5)') == "125"
        assert subject.format("number(123)") == "123"
        assert subject.format("number(1234.56)") == "1,234.56"
        assert subject.format('number(123, ".")') == "123"
        assert subject.format('number("123", ".")') == "123"
        assert subject.format('number(123.12, ".")') == "123.12"
        assert subject.format('number(123.12, ",")') == "123,12"
        assert subject.format('number(1234.12, ",", ".")') == "1.234,12"
        assert subject.format("metric_length(123, 5, 2)") == "125.00"
        assert subject.format("metric_length(123.123, 0.1, 2)") == "123.10"
        assert subject.format('metric_length("123", 5, 2)') == "125.00"
        assert subject.format("imperial_length(1, 1)") == "1'"
        assert subject.format("imperial_length(3.123, 1)") == "3' - 1\""
        assert subject.format("imperial_length(3.123, 2)") == "3' - 1 1/2\""
        assert subject.format('imperial_length("3.123", 2)') == "3' - 1 1/2\""
        assert subject.format('imperial_length("123.123", 2, "inch", "foot")') == "10' - 3\""
        assert subject.format('imperial_length("123.123", 2, "inch", "inch")') == '123"'


class TestGetElementValue(test.bootstrap.IFC4):
    def test_selecting_an_elements_class_or_id_using_a_query(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        assert subject.get_element_value(element, "class") == "IfcWall"
        assert subject.get_element_value(element, "id") == element.id()

    def test_selecting_an_elements_value_using_a_query(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element.Name = "Foobar"
        assert subject.get_element_value(element, "Name") == "Foobar"

    def test_selecting_using_a_multiple_key_query(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        material2 = ifcopenshell.api.run("material.add_material", self.file, name="CON02")
        material_set = ifcopenshell.api.run(
            "material.add_material_set", self.file, name="FOO", set_type="IfcMaterialLayerSet"
        )
        layer = ifcopenshell.api.run("material.add_layer", self.file, layer_set=material_set, material=material)
        layer.Name = "L1"
        layer = ifcopenshell.api.run("material.add_layer", self.file, layer_set=material_set, material=material)
        layer.Name = "L2"
        ifcopenshell.api.run("material.edit_layer", self.file, layer=layer, attributes={"LayerThickness": 13})
        ifcopenshell.api.run("material.assign_material", self.file, products=[element], material=material_set)
        assert subject.get_element_value(element, "material.MaterialLayers.Name") == ["L1", "L2"]
        # Allow to use "item" to generically select an item in a material set
        assert subject.get_element_value(element, "material.item.Name") == ["L1", "L2"]
        assert subject.get_element_value(element, "material.item.Name.0") == "L1"
        assert subject.get_element_value(element, "material.item.Name.1") == "L2"
        assert subject.get_element_value(element, '"material"."item"."Name"') == ["L1", "L2"]
        assert subject.get_element_value(element, 'material."item"."Name"') == ["L1", "L2"]
        # Provide shortform for convenience
        assert subject.get_element_value(element, "mat.i.Name") == ["L1", "L2"]

    def test_selecting_a_query_that_fails_silently(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        assert subject.get_element_value(element, "material.item.Name.0") is None

    def test_selecting_a_list_item_that_fails_silently(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        material2 = ifcopenshell.api.run("material.add_material", self.file, name="CON02")
        material_set = ifcopenshell.api.run(
            "material.add_material_set", self.file, name="FOO", set_type="IfcMaterialLayerSet"
        )
        layer = ifcopenshell.api.run("material.add_layer", self.file, layer_set=material_set, material=material)
        layer.Name = "L1"
        ifcopenshell.api.run("material.assign_material", self.file, products=[element], material=material_set)
        assert subject.get_element_value(element, "material.item.Name.0") == "L1"
        assert subject.get_element_value(element, "material.item.Name.1") is None

    def test_selecting_a_pset(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foobar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Bar"})
        assert subject.get_element_value(element, "Foobar.Foo") == "Bar"
        assert subject.get_element_value(element, "Foobar./F.*/") == "Bar"
        assert subject.get_element_value(element, "/Foo.*/./F.*/") == "Bar"
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Baz": 123})
        assert subject.get_element_value(element, "/Foo.*/./B.*/") == 123
        assert subject.get_element_value(element, "/Foo.*/./.*/") == ["Bar", 123]
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Bay": 123.3})
        assert subject.get_element_value(element, "/Foo.*/./B.*/") == [123, 123.3]
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Pset_WallCommon")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Status": ["New"]})
        assert subject.get_element_value(element, "/Pset_.*Common/.Status") == ["New"]
        assert subject.get_element_value(element, "/Pset_.*Common/.Status.0") == "New"


class TestFilterElements(test.bootstrap.IFC4):
    def test_selecting_by_globalid(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        guid1 = element.GlobalId
        guid2 = element2.GlobalId
        assert subject.filter_elements(self.file, f"{guid1}") == {element}
        assert subject.filter_elements(self.file, f"{guid1}, {guid2}") == {element, element2}
        assert subject.filter_elements(self.file, f"{guid1}, {guid2}, ! {guid2}") == {element}
        assert subject.filter_elements(self.file, f"IfcElement, ! {guid2}") == {element}

    def test_selecting_by_class(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element.Name = "Foo"
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        assert subject.filter_elements(self.file, "IfcWall") == {element}
        assert subject.filter_elements(self.file, "IfcElement, ! IfcWall") == {element2}

    def test_selecting_by_attribute(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element.Name = "Foo"
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2.Name = "Bar"
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        assert subject.filter_elements(self.file, "IfcWall, Name=Foo") == {element}
        element.Name = 'Foo\'s "quoted" name...'
        assert subject.filter_elements(self.file, 'IfcWall, Name="Foo\'s \\"quoted\\" name..."') == {element}
        assert subject.filter_elements(self.file, "IfcWall, Name=/Fo.*/") == {element}
        assert subject.filter_elements(self.file, "IfcWall, Description=NULL") == {element, element2}
        element.Name = "Foo"
        element.Description = "Foobar"
        assert subject.filter_elements(self.file, "IfcWall, Name=Foo, Description=Foobar") == {element}

        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        element_type.PredefinedType = "SOLIDWALL"
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element], relating_type=element_type)
        assert subject.filter_elements(self.file, "IfcWall, PredefinedType=SOLIDWALL") == {element}

    def test_selecting_by_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element], relating_type=element_type)
        assert subject.filter_elements(self.file, "IfcWall, type=Foo") == set()
        element_type.Name = "Foo"
        assert subject.filter_elements(self.file, "IfcWall, type=Foo") == {element}
        assert subject.filter_elements(self.file, 'IfcWall, type="Foo"') == {element}
        assert subject.filter_elements(self.file, "IfcWall, type=/Fo.*/") == {element}

    def test_selecting_by_material(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        assert subject.filter_elements(self.file, "IfcWall, material=NULL") == {element, element2}
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, products=[element], material=material)
        assert subject.filter_elements(self.file, "IfcWall, material=CON01") == {element}
        assert subject.filter_elements(self.file, "IfcWall, material!=CON01") == {element2}

    def test_selecting_by_property(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foobar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Bar"})
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Foo=Bar") == {element}
        assert subject.filter_elements(self.file, 'IfcWall, Foobar."Foo"=Bar') == {element}
        assert subject.filter_elements(self.file, "IfcWall, Foobar./Fo.*/=Bar") == {element}
        assert subject.filter_elements(self.file, "IfcWall, Foobar./Fo.*/!=Bar") == {element2}
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Bar": False})
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Bar=FALSE") == {element}
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Baz": 123})
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Baz=123") == {element}
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Bay": 123.3})
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Pset_WallCommon")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Status": ["New"]})
        assert subject.filter_elements(self.file, "IfcWall, Pset_WallCommon.Status=New") == {element}

    def test_selecting_by_property_with_comparisons(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foobar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Baz": 123})
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Baz>100") == {element}
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Baz<100") == set()
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Baz>=100") == {element}
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Baz<=100") == set()
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Bar"})
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Foo*=ar") == {element}
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Foo!*=ar") == {element2}
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Foo*=Foo") == set()

    def test_selecting_by_classification(self):
        project = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        assert subject.filter_elements(self.file, "IfcWall, classification=NULL") == {element, element2}
        result = ifcopenshell.api.run("classification.add_classification", self.file, classification="Name")
        ifcopenshell.api.run(
            "classification.add_reference",
            self.file,
            products=[element],
            identification="X",
            name="Foobar",
            classification=result,
        )
        assert subject.filter_elements(self.file, "IfcWall, classification=NULL") == {element2}
        assert subject.filter_elements(self.file, "IfcWall, classification=X") == {element}
        assert subject.filter_elements(self.file, "IfcWall, classification=Foobar") == {element}
        assert subject.filter_elements(self.file, "IfcWall, classification!=X") == {element2}

    def test_selecting_by_location(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        space = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSpace", name="Space")
        storey = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuildingStorey", name="G")
        building = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding", name="Building")
        project = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject", name="Project")
        ifcopenshell.api.run("spatial.assign_container", self.file, products=[element], relating_structure=space)
        ifcopenshell.api.run("spatial.assign_container", self.file, products=[element2], relating_structure=storey)
        ifcopenshell.api.run("aggregate.assign_object", self.file, products=[space], relating_object=storey)
        ifcopenshell.api.run("aggregate.assign_object", self.file, products=[storey], relating_object=building)
        ifcopenshell.api.run("aggregate.assign_object", self.file, products=[building], relating_object=project)
        assert subject.filter_elements(self.file, "IfcWall, location=NULL") == set()
        assert subject.filter_elements(self.file, "IfcWall, location=Space") == {element}
        assert subject.filter_elements(self.file, "IfcWall, location=G") == {element, element2}
        assert subject.filter_elements(self.file, "IfcWall, location=Building") == {element, element2}
        assert subject.filter_elements(self.file, "IfcWall, location!=Space") == {element2}

    def test_selecting_by_group(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        group = ifcopenshell.api.run("group.add_group", self.file, name="Foo")
        ifcopenshell.api.run("group.assign_group", self.file, products=[element], group=group)
        assert subject.filter_elements(self.file, "IfcWall, group=Foo") == {element}
        assert subject.filter_elements(self.file, "IfcWall, group!=Foo") == {element2}

    def test_selecting_by_parent(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall", name="Element1")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall", name="Element2")
        element3 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall", name="Element3")
        space = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSpace", name="Space")
        storey = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuildingStorey", name="G")
        building = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding", name="Building")
        project = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject", name="Project")
        ifcopenshell.api.run("spatial.assign_container", self.file, products=[element], relating_structure=space)
        ifcopenshell.api.run("spatial.assign_container", self.file, products=[element2], relating_structure=storey)
        ifcopenshell.api.run("aggregate.assign_object", self.file, products=[element3], relating_object=element2)
        ifcopenshell.api.run("aggregate.assign_object", self.file, products=[space], relating_object=storey)
        ifcopenshell.api.run("aggregate.assign_object", self.file, products=[storey], relating_object=building)
        ifcopenshell.api.run("aggregate.assign_object", self.file, products=[building], relating_object=project)
        assert subject.filter_elements(self.file, "IfcWall, parent=Project") == {element, element2, element3}
        assert subject.filter_elements(self.file, "IfcWall, parent=Space") == {element}
        assert subject.filter_elements(self.file, "IfcWall, parent=G") == {element, element2, element3}
        assert subject.filter_elements(self.file, "IfcWall, parent=Element2") == {element3}

    def test_selecting_multiple_filter_groups(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element.Name = "Foo"
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        element2.Name = "Bar"
        assert subject.filter_elements(self.file, "IfcWall + IfcSlab") == {element, element2}
        assert subject.filter_elements(self.file, "IfcWall, IfcSlab, Name=Foo") == {element}
        assert subject.filter_elements(self.file, "IfcWall, Name=Foo + IfcSlab") == {element, element2}
        assert subject.filter_elements(self.file, "IfcWall, Name=Foo + IfcSlab, Name=Bar") == {element, element2}

    def test_using_elements_argument(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        slab = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        door = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcDoor")
        elements = {wall, slab}
        results = subject.filter_elements(self.file, "IfcWall", {wall, slab})
        assert results != elements
        assert results == {wall}
        elements = {wall, slab, door}
        assert subject.filter_elements(self.file, "IfcWall, IfcSlab", elements) == {wall, slab}

    def test_editing_in_place(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        original_set = {wall}
        new_set = subject.filter_elements(self.file, "IfcWall", original_set, edit_in_place=True)
        assert new_set == original_set == {wall}


class TestSetElementValue(test.bootstrap.IFC4):
    def test_set_xyz_coordinates(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)

        items = list(zip("xyz", ("5", "10", "15")))
        matrix = np.eye(4)
        matrix[:, 3] = (5, 10, 15, 1)

        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("geometry.edit_object_placement", self.file, product=element, is_si=False)
        for coord, value in items:
            subject.set_element_value(self.file, element, coord, value)
        assert np.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)

        element_without_placement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        for coord, value in items:
            subject.set_element_value(self.file, element_without_placement, coord, value)
        assert np.array_equal(
            ifcopenshell.util.placement.get_local_placement(element_without_placement.ObjectPlacement), matrix
        )

    def test_set_attribute(self):
        element = self.file.createIfcWall()
        subject.set_element_value(self.file, element, "Name", "Foo")
        assert element.Name == "Foo"
        subject.set_element_value(self.file, element, "Name", 123)
        assert element.Name == "123"

    def test_set_attributes_attribute(self):
        material = self.file.create_entity("IfcMaterial")
        layer = self.file.create_entity("IfcMaterialLayer")
        layer.Material = material
        subject.set_element_value(self.file, layer, "Material.Name", "Foo")
        assert material.Name == "Foo"


class TestSelector(test.bootstrap.IFC4):
    def test_selecting_from_specified_elements(self):
        elements = [ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall") for _ in range(2)]
        assert subject.Selector.parse(self.file, ".IfcWall", elements[:1]) == [elements[0]]

    def test_selecting_by_class(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        assert subject.Selector.parse(self.file, ".IfcWall") == [element]

    def test_selecting_by_globalid(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        assert subject.Selector.parse(self.file, f"#{element.GlobalId}") == [element]

    def test_selecting_by_attribute_existence(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element.Name = "Foobar"
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        assert subject.Selector.parse(self.file, ".IfcElement[Name]") == [element]
        assert subject.Selector.parse(self.file, ".IfcElement[Description]") == []

    def test_selecting_by_attribute(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element.Name = "Foobar"
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        assert subject.Selector.parse(self.file, '.IfcElement[Name="Foobar"]') == [element]
        assert subject.Selector.parse(self.file, '.IfcElement[Name="Foobaz"]') == []

    def test_selecting_by_regex(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element.Name = "Foobar"
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        assert subject.Selector.parse(self.file, '.IfcElement[Name=r"Foo.*"]') == [element]

    def test_selecting_by_property_existence(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Bar"})
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Foo]") == [element]
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Fox]") == []
        assert subject.Selector.parse(self.file, '.IfcElement[r"Foo.*ar"."Fo.*"]') == [element]

    def test_selecting_by_string_property(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Bar"})
        assert subject.Selector.parse(self.file, '.IfcElement[Foo_Bar.Foo="Bar"]') == [element]

    def test_selecting_by_enumerated_property(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Pset_WallCommon")
        template = ifcopenshell.util.pset.get_template("IFC4").get_by_name("Pset_WallCommon")
        ifcopenshell.api.run(
            "pset.edit_pset", self.file, pset=pset, properties={"Status": ["NEW"]}, pset_template=template
        )
        assert subject.Selector.parse(self.file, '.IfcElement[Pset_WallCommon.Status="NEW"]') == [element]

    def test_selecting_by_integer_property(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": 42})
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Foo=42]") == [element]

    def test_selecting_by_float_property(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": 4.2})
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Foo=4.2]") == [element]

    def test_selecting_by_boolean_property(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": True})
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Foo=TRUE]") == [element]
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": False})
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Foo=FALSE]") == [element]

    def test_selecting_by_null_property(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Bar"})
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Foo=NULL]") == []
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": None})
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Foo=NULL]") == [element]

    def test_comparing_by_not_equal(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element.Name = "Foobar"
        assert subject.Selector.parse(self.file, '.IfcElement[Name!="Foobaz"]') == [element]
        assert subject.Selector.parse(self.file, '.IfcElement[Name!="Foobar"]') == []

    def test_comparing_by_ranges(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": 4.2})
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Foo>2]") == [element]
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Foo>20]") == []
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Foo<2]") == []
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Foo<20]") == [element]
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Foo>=4.2]") == [element]
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Foo<=4.2]") == [element]

    def test_comparing_if_value_contains_a_wildcard_string(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element.Name = "Foobar"
        assert subject.Selector.parse(self.file, '.IfcElement[Name*="Foo"]') == [element]
        assert subject.Selector.parse(self.file, '.IfcElement[Name*="oba"]') == [element]
        assert subject.Selector.parse(self.file, '.IfcElement[Name*="abc"]') == []

    def test_selecting_if_value_not_matching(self):
        element_1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset_1 = ifcopenshell.api.run("pset.add_pset", self.file, product=element_1, name="Foo_Bar")
        pset_2 = ifcopenshell.api.run("pset.add_pset", self.file, product=element_2, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset_1, properties={"Foo": "Bar"})
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset_2, properties={"Foo": "BOO"})
        assert subject.Selector.parse(self.file, '.IfcElement["Foo_Bar"."Foo" != "Bar"]') == [element_2]
        assert subject.Selector.parse(self.file, '.IfcElement["Foo_Bar"."Foo" != "BOO"]') == [element_1]

    def test_selecting_when_attribute_is_none(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        assert subject.Selector.parse(self.file, '.IfcElement[PredefinedType !="non-existent predefined type"]') == [
            element
        ]

    def test_selecting_a_property_which_includes_non_standard_characters(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="a !%$§&/()?|*-+,€~#@µ^°a")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"a !%$§&/()?|*-+,€~#@µ^°a": "Bar"})
        assert subject.Selector.parse(
            self.file, '.IfcElement["a !%$§&/()?|*-+,€~#@µ^°a"."a !%$§&/()?|*-+,€~#@µ^°a"="Bar"]'
        ) == [element]

    def test_selecting_a_property_which_includes_a_dot(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="a.b")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"c.d": "Bar"})
        assert subject.Selector.parse(self.file, '.IfcElement["a.b"."c.d"="Bar"]') == [element]

    def test_selecting_a_property_which_includes_an_escaped_quote(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name='"a.b"')
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={'"c.d"': "Bar"})
        assert subject.Selector.parse(self.file, r'.IfcElement["\"a.b\""."\"c.d\""="Bar"]') == [element]

    def test_comparing_if_value_is_in_a_list(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element.Name = "Foobar"
        assert subject.Selector.parse(self.file, '.IfcElement[Name%="Foobar,Foobaz"]') == [element]
        element.Name = "Foobaz"
        assert subject.Selector.parse(self.file, '.IfcElement[Name%="Foobar,Foobaz"]') == [element]
        element.Name = "Foobat"
        assert subject.Selector.parse(self.file, '.IfcElement[Name%="Foobar,Foobaz"]') == []

    def test_getting_occurrences_of_a_filtered_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element], relating_type=element_type)
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element2], relating_type=element_type2)
        assert set(subject.Selector.parse(self.file, "* .IfcWallType")) == {element, element2}

    def test_getting_decomposition_of_a_filtered_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcMember")
        building = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.run("spatial.assign_container", self.file, products=[element], relating_structure=building)
        ifcopenshell.api.run("aggregate.assign_object", self.file, products=[subelement], relating_object=element)
        assert set(subject.Selector.parse(self.file, "@ .IfcBuilding")) == {element, subelement}

    def test_selecting_elements_from_a_prefiltered_list(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        assert subject.Selector.parse(self.file, ".IfcWall", elements=[element])
        assert not subject.Selector.parse(self.file, ".IfcWall", elements=[element2])

    def test_selecting_a_property_via_a_wildcard_pset_name(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foobar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Bar"})
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foobaz")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Baz"})
        assert subject.Selector.parse(self.file, '.IfcElement[r"Foo.*"."Foo"="Bar"]') == [element]

    def test_selecting_a_property_via_a_wildcard_property_name(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foobar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Bar"})
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foobaz")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Baz"})
        assert subject.Selector.parse(self.file, '.IfcElement[r"Foo.*"."F.*"="Bar"]') == [element]

    def test_selecting_an_attribute_via_a_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        element_type.Name = "Foo"
        ifcopenshell.api.run("type.assign_type", self.file, related_objects=[element], relating_type=element_type)
        assert set(subject.Selector.parse(self.file, '.IfcWall[type.Name="Foo"]')) == {element}

    def test_selecting_via_a_material(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, products=[element], material=material)
        assert set(subject.Selector.parse(self.file, '.IfcWall[material.Name="CON01"]')) == {element}

    def test_selecting_via_a_material_set(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        material_set = ifcopenshell.api.run(
            "material.add_material_set", self.file, name="FOO", set_type="IfcMaterialLayerSet"
        )
        layer = ifcopenshell.api.run("material.add_layer", self.file, layer_set=material_set, material=material)
        ifcopenshell.api.run("material.edit_layer", self.file, layer=layer, attributes={"LayerThickness": 13})
        ifcopenshell.api.run("material.assign_material", self.file, products=[element], material=material_set)
        assert set(subject.Selector.parse(self.file, '.IfcWall[material.LayerSetName="FOO"]')) == {element}

    def test_selecting_via_a_material_set_item(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        material2 = ifcopenshell.api.run("material.add_material", self.file, name="CON02")
        material_set = ifcopenshell.api.run(
            "material.add_material_set", self.file, name="FOO", set_type="IfcMaterialLayerSet"
        )
        layer = ifcopenshell.api.run("material.add_layer", self.file, layer_set=material_set, material=material)
        layer = ifcopenshell.api.run("material.add_layer", self.file, layer_set=material_set, material=material2)
        ifcopenshell.api.run("material.assign_material", self.file, products=[element], material=material_set)
        assert set(subject.Selector.parse(self.file, '.IfcWall[material.item.Material.Name="CON01"]')) == {element}
        assert set(subject.Selector.parse(self.file, '.IfcWall[material.item.Material.Name="CON02"]')) == {element}
        assert set(subject.Selector.parse(self.file, '.IfcWall[material.item.Material.Name="CON03"]')) == set()
