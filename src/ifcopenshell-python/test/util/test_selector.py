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


class TestGetElementValue(test.bootstrap.IFC4):
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
        ifcopenshell.api.run("material.assign_material", self.file, product=element, material=material_set)
        assert subject.get_element_value(element, "material.MaterialLayers.Name") == ["L1", "L2"]
        # Allow to use "item" to generically select an item in a material set
        assert subject.get_element_value(element, "material.item.Name") == ["L1", "L2"]
        assert subject.get_element_value(element, '"material"."item"."Name"') == ["L1", "L2"]
        assert subject.get_element_value(element, 'r"material"."item"."Name"') == ["L1", "L2"]
        # Provide shortform for convenience
        assert subject.get_element_value(element, "mat.i.Name") == ["L1", "L2"]


class TestSelector(test.bootstrap.IFC4):
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

    def test_selecting_by_property_existence(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Bar"})
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Foo]") == [element]
        assert subject.Selector.parse(self.file, ".IfcElement[Foo_Bar.Fox]") == []

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
        assert subject.Selector.parse(self.file, '.IfcElement[Foo_Bar.Foo != "Bar"]') == [element_2]
        assert subject.Selector.parse(self.file, '.IfcElement[Foo_Bar.Foo != "BOO"]') == [element_1]

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
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=element_type)
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element_type2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element2, relating_type=element_type2)
        assert set(subject.Selector.parse(self.file, "* .IfcWallType")) == {element, element2}

    def test_getting_decomposition_of_a_filtered_type(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcMember")
        building = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.run("spatial.assign_container", self.file, product=element, relating_structure=building)
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
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
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=element_type)
        assert set(subject.Selector.parse(self.file, '.IfcWall[type.Name="Foo"]')) == {element}

    def test_selecting_via_a_material(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        ifcopenshell.api.run("material.assign_material", self.file, product=element, material=material)
        assert set(subject.Selector.parse(self.file, '.IfcWall[material.Name="CON01"]')) == {element}

    def test_selecting_via_a_material_set(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = ifcopenshell.api.run("material.add_material", self.file, name="CON01")
        material_set = ifcopenshell.api.run(
            "material.add_material_set", self.file, name="FOO", set_type="IfcMaterialLayerSet"
        )
        layer = ifcopenshell.api.run("material.add_layer", self.file, layer_set=material_set, material=material)
        ifcopenshell.api.run("material.edit_layer", self.file, layer=layer, attributes={"LayerThickness": 13})
        ifcopenshell.api.run("material.assign_material", self.file, product=element, material=material_set)
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
        ifcopenshell.api.run("material.assign_material", self.file, product=element, material=material_set)
        assert set(subject.Selector.parse(self.file, '.IfcWall[material.item.Material.Name="CON01"]')) == {element}
        assert set(subject.Selector.parse(self.file, '.IfcWall[material.item.Material.Name="CON02"]')) == {element}
        assert set(subject.Selector.parse(self.file, '.IfcWall[material.item.Material.Name="CON03"]')) == set()
