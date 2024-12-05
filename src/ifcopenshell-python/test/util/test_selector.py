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
import ifcopenshell.api.spatial
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.classification
import ifcopenshell.api.pset
import ifcopenshell.api.type
import ifcopenshell.api.material
import ifcopenshell.api.geometry
import ifcopenshell.api.aggregate
import ifcopenshell.api.group
import ifcopenshell.api.sequence
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
        assert subject.format("int(123.123)") == "123"
        assert subject.format("int(123)") == "123"
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
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        assert subject.get_element_value(element, "class") == "IfcWall"
        assert subject.get_element_value(element, "id") == element.id()

    def test_selecting_an_elements_value_using_a_query(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element.Name = "Foobar"
        assert subject.get_element_value(element, "Name") == "Foobar"

    def test_selecting_using_a_multiple_key_query(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        material2 = ifcopenshell.api.material.add_material(self.file, name="CON02")
        material_set = ifcopenshell.api.material.add_material_set(self.file, name="FOO", set_type="IfcMaterialLayerSet")
        layer = ifcopenshell.api.material.add_layer(self.file, layer_set=material_set, material=material)
        layer.Name = "L1"
        layer = ifcopenshell.api.material.add_layer(self.file, layer_set=material_set, material=material)
        layer.Name = "L2"
        ifcopenshell.api.material.edit_layer(self.file, layer=layer, attributes={"LayerThickness": 13})
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material_set)
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
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        assert subject.get_element_value(element, "material.item.Name.0") is None

    def test_selecting_a_list_item_that_fails_silently(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        material2 = ifcopenshell.api.material.add_material(self.file, name="CON02")
        material_set = ifcopenshell.api.material.add_material_set(self.file, name="FOO", set_type="IfcMaterialLayerSet")
        layer = ifcopenshell.api.material.add_layer(self.file, layer_set=material_set, material=material)
        layer.Name = "L1"
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material_set)
        assert subject.get_element_value(element, "material.item.Name.0") == "L1"
        assert subject.get_element_value(element, "material.item.Name.1") is None

    def test_selecting_a_pset(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Foobar")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Foo": "Bar"})
        assert subject.get_element_value(element, "Foobar.Foo") == "Bar"
        assert subject.get_element_value(element, "Foobar./F.*/") == "Bar"
        assert subject.get_element_value(element, "/Foo.*/./F.*/") == "Bar"
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Baz": 123})
        assert subject.get_element_value(element, "/Foo.*/./B.*/") == 123
        assert subject.get_element_value(element, "/Foo.*/./.*/") == ["Bar", 123]
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Bay": 123.3})
        assert subject.get_element_value(element, "/Foo.*/./B.*/") == [123, 123.3]
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Status": ["New"]})
        assert subject.get_element_value(element, "/Pset_.*Common/.Status") == ["New"]
        assert subject.get_element_value(element, "/Pset_.*Common/.Status.0") == "New"


class TestFilterElements(test.bootstrap.IFC4):
    def test_selecting_by_globalid(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSlab")
        guid1 = element.GlobalId
        guid2 = element2.GlobalId
        assert subject.filter_elements(self.file, f"{guid1}") == {element}
        assert subject.filter_elements(self.file, f"{guid1}, {guid2}") == {element, element2}
        assert subject.filter_elements(self.file, f"{guid1}, {guid2}, ! {guid2}") == {element}
        assert subject.filter_elements(self.file, f"IfcElement, ! {guid2}") == {element}

    def test_selecting_by_class(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element.Name = "Foo"
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSlab")
        assert subject.filter_elements(self.file, "IfcWall") == {element}
        assert subject.filter_elements(self.file, "IfcElement, ! IfcWall") == {element2}

    def test_selecting_by_attribute(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element.Name = "Foo"
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2.Name = "Bar"
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSlab")
        assert subject.filter_elements(self.file, "IfcWall, Name=Foo") == {element}
        element.Name = 'Foo\'s "quoted" name...'
        assert subject.filter_elements(self.file, 'IfcWall, Name="Foo\'s \\"quoted\\" name..."') == {element}
        assert subject.filter_elements(self.file, "IfcWall, Name=/Fo.*/") == {element}
        assert subject.filter_elements(self.file, "IfcWall, Description=NULL") == {element, element2}
        element.Name = "Foo"
        element.Description = "Foobar"
        assert subject.filter_elements(self.file, "IfcWall, Name=Foo, Description=Foobar") == {element}

        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element_type.PredefinedType = "SOLIDWALL"
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        assert subject.filter_elements(self.file, "IfcWall, PredefinedType=SOLIDWALL") == {element}

    def test_selecting_by_type(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        assert subject.filter_elements(self.file, "IfcWall, type=Foo") == set()
        element_type.Name = "Foo"
        assert subject.filter_elements(self.file, "IfcWall, type=Foo") == {element}
        assert subject.filter_elements(self.file, 'IfcWall, type="Foo"') == {element}
        assert subject.filter_elements(self.file, "IfcWall, type=/Fo.*/") == {element}

    def test_selecting_by_material(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        assert subject.filter_elements(self.file, "IfcWall, material=NULL") == {element, element2}
        material = ifcopenshell.api.material.add_material(self.file, name="CON01")
        ifcopenshell.api.material.assign_material(self.file, products=[element], material=material)
        assert subject.filter_elements(self.file, "IfcWall, material=CON01") == {element}
        assert subject.filter_elements(self.file, "IfcWall, material!=CON01") == {element2}

    def test_selecting_by_property(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Foobar")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Foo": "Bar"})
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Foo=Bar") == {element}
        assert subject.filter_elements(self.file, 'IfcWall, Foobar."Foo"=Bar') == {element}
        assert subject.filter_elements(self.file, "IfcWall, Foobar./Fo.*/=Bar") == {element}
        assert subject.filter_elements(self.file, "IfcWall, Foobar./Fo.*/!=Bar") == {element2}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Bar": False})
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Bar=FALSE") == {element}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Baz": 123})
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Baz=123") == {element}
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Bay": 123.3})
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Status": ["New"]})
        assert subject.filter_elements(self.file, "IfcWall, Pset_WallCommon.Status=New") == {element}

    def test_selecting_by_property_with_comparisons(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Foobar")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Baz": 123})
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Baz>100") == {element}
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Baz<100") == set()
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Baz>=100") == {element}
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Baz<=100") == set()
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Foo": "Bar"})
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Foo*=ar") == {element}
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Foo!*=ar") == {element2}
        assert subject.filter_elements(self.file, "IfcWall, Foobar.Foo*=Foo") == set()

    def test_selecting_by_classification(self):
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        assert subject.filter_elements(self.file, "IfcWall, classification=NULL") == {element, element2}
        result = ifcopenshell.api.classification.add_classification(self.file, classification="Name")
        ifcopenshell.api.classification.add_reference(
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
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        space = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSpace", name="Space")
        storey = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey", name="G")
        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding", name="Building")
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject", name="Project")
        ifcopenshell.api.spatial.assign_container(self.file, products=[element], relating_structure=space)
        ifcopenshell.api.spatial.assign_container(self.file, products=[element2], relating_structure=storey)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[space], relating_object=storey)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[storey], relating_object=building)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[building], relating_object=project)
        assert subject.filter_elements(self.file, "IfcWall, location=NULL") == set()
        assert subject.filter_elements(self.file, "IfcWall, location=Space") == {element}
        assert subject.filter_elements(self.file, "IfcWall, location=G") == {element, element2}
        assert subject.filter_elements(self.file, "IfcWall, location=Building") == {element, element2}
        assert subject.filter_elements(self.file, "IfcWall, location!=Space") == {element2}

    def test_selecting_by_group(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        group = ifcopenshell.api.group.add_group(self.file, name="Foo")
        ifcopenshell.api.group.assign_group(self.file, products=[element], group=group)
        assert subject.filter_elements(self.file, "IfcWall, group=Foo") == {element}
        assert subject.filter_elements(self.file, "IfcWall, group!=Foo") == {element2}

    def test_selecting_by_parent(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall", name="Element1")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall", name="Element2")
        element3 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall", name="Element3")
        space = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSpace", name="Space")
        storey = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingStorey", name="G")
        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding", name="Building")
        project = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject", name="Project")
        ifcopenshell.api.spatial.assign_container(self.file, products=[element], relating_structure=space)
        ifcopenshell.api.spatial.assign_container(self.file, products=[element2], relating_structure=storey)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[element3], relating_object=element2)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[space], relating_object=storey)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[storey], relating_object=building)
        ifcopenshell.api.aggregate.assign_object(self.file, products=[building], relating_object=project)
        assert subject.filter_elements(self.file, "IfcWall, parent=Project") == {element, element2, element3}
        assert subject.filter_elements(self.file, "IfcWall, parent=Space") == {element}
        assert subject.filter_elements(self.file, "IfcWall, parent=G") == {element, element2, element3}
        assert subject.filter_elements(self.file, "IfcWall, parent=Element2") == {element3}

    def test_selecting_multiple_filter_groups(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element.Name = "Foo"
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSlab")
        element2.Name = "Bar"
        assert subject.filter_elements(self.file, "IfcWall + IfcSlab") == {element, element2}
        assert subject.filter_elements(self.file, "IfcWall, IfcSlab, Name=Foo") == {element}
        assert subject.filter_elements(self.file, "IfcWall, Name=Foo + IfcSlab") == {element, element2}
        assert subject.filter_elements(self.file, "IfcWall, Name=Foo + IfcSlab, Name=Bar") == {element, element2}

    def test_using_elements_argument(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        slab = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSlab")
        door = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcDoor")
        elements = {wall, slab}
        results = subject.filter_elements(self.file, "IfcWall", {wall, slab})
        assert results != elements
        assert results == {wall}
        elements = {wall, slab, door}
        assert subject.filter_elements(self.file, "IfcWall, IfcSlab", elements) == {wall, slab}

    def test_editing_in_place(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        original_set = {wall}
        new_set = subject.filter_elements(self.file, "IfcWall", original_set, edit_in_place=True)
        assert new_set == original_set == {wall}


class TestSetElementValue(test.bootstrap.IFC4):
    def test_set_xyz_coordinates(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file)

        items = list(zip("xyz", ("5", "10", "15")))
        matrix = np.eye(4)
        matrix[:, 3] = (5, 10, 15, 1)

        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=element, is_si=False)
        for coord, value in items:
            subject.set_element_value(self.file, element, coord, value)
        assert np.array_equal(ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement), matrix)

        element_without_placement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
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


class TestSetElementValuePredefinedType(test.bootstrap.IFC4):
    def test_setting_an_element_predefined_type(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWindow")
        subject.set_element_value(self.file, element, "predefined_type", "LIGHTDOME")
        assert element.PredefinedType == "LIGHTDOME"
        assert element.ObjectType == None

    def test_setting_an_element_predefined_type_to_none(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWindow")
        subject.set_element_value(self.file, element, "predefined_type", None)
        assert element.PredefinedType == None
        assert element.ObjectType == None

    def test_setting_an_element_userdefined_type(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWindow")
        subject.set_element_value(self.file, element, "predefined_type", "FOOBAR")
        assert element.PredefinedType == "USERDEFINED"
        assert element.ObjectType == "FOOBAR"

    def test_setting_an_element_inherited_predefined_type(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWindow")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWindowType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        subject.set_element_value(self.file, element, "predefined_type", "LIGHTDOME")
        assert element_type.PredefinedType == "LIGHTDOME"
        assert element_type.ElementType == None
        assert element.PredefinedType == None
        assert element.ObjectType == None

    def test_setting_an_element_inherited_predefined_type_to_none(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWindow")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWindowType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        subject.set_element_value(self.file, element, "predefined_type", None)
        assert element_type.PredefinedType == "NOTDEFINED"
        assert element_type.ElementType == None
        assert element.PredefinedType == None
        assert element.ObjectType == None

    def test_setting_an_element_inherited_userdefined_type(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWindow")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWindowType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        subject.set_element_value(self.file, element, "predefined_type", "FOOBAR")
        assert element_type.PredefinedType == "USERDEFINED"
        assert element_type.ElementType == "FOOBAR"
        assert element.PredefinedType == None
        assert element.ObjectType == None
