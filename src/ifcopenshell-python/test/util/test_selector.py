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


class TestSelector(test.bootstrap.IFC4):
    def test_selecting_by_class(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        assert subject.Selector.parse(self.file, ".IfcWall") == [element]

    def test_selecting_by_globalid(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        assert subject.Selector.parse(self.file, f"#{element.GlobalId}") == [element]

    def test_selecting_by_attribute(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element.Name = "Foobar"
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        assert subject.Selector.parse(self.file, '.IfcElement[Name="Foobar"]') == [element]
        assert subject.Selector.parse(self.file, '.IfcElement[Name="Foobaz"]') == []

    def test_selecting_by_string_property(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Bar"})
        assert subject.Selector.parse(self.file, '.IfcElement[Foo_Bar.Foo="Bar"]') == [element]

    def test_selecting_by_integer_property(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": 42})
        assert subject.Selector.parse(self.file, '.IfcElement[Foo_Bar.Foo=42]') == [element]

    def test_selecting_by_float_property(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": 4.2})
        assert subject.Selector.parse(self.file, '.IfcElement[Foo_Bar.Foo=4.2]') == [element]

    def test_selecting_by_boolean_property(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": True})
        assert subject.Selector.parse(self.file, '.IfcElement[Foo_Bar.Foo=TRUE]') == [element]
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": False})
        assert subject.Selector.parse(self.file, '.IfcElement[Foo_Bar.Foo=FALSE]') == [element]

    def test_selecting_by_null_property(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foo_Bar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": "Bar"})
        assert subject.Selector.parse(self.file, '.IfcElement[Foo_Bar.Foo=NULL]') == []
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Foo": None})
        assert subject.Selector.parse(self.file, '.IfcElement[Foo_Bar.Foo=NULL]') == [element]
