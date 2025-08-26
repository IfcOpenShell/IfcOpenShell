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

import ifcopenshell
import pytest
import ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.util.attribute as subject


def getattr_(ifc_class: str, attr_name: str) -> W.attribute:
    schema = ifcopenshell.schema_by_name("IFC4")
    declaration = schema.declaration_by_name(ifc_class).as_entity()
    assert declaration
    i = declaration.attribute_index(attr_name)
    attr = declaration.all_attributes()[i]
    return attr


class TestGetPrimitiveType:
    def test_run(self):
        assert subject.get_primitive_type(getattr_("IfcWindow", "OverallHeight")) == "float"
        assert subject.get_primitive_type(getattr_("IfcRelVoidsElement", "RelatingBuildingElement")) == "entity"
        assert subject.get_primitive_type(getattr_("IfcPostalAddress", "Description")) == "string"
        assert subject.get_primitive_type(getattr_("IfcPostalAddress", "Purpose")) == "enum"
        assert subject.get_primitive_type(getattr_("IfcPostalAddress", "AddressLines")) == ("list", "string")


class TestGetEnumItems:
    def test_run(self):
        assert subject.get_enum_items(getattr_("IfcPostalAddress", "Purpose")) == (
            "OFFICE",
            "SITE",
            "HOME",
            "DISTRIBUTIONPOINT",
            "USERDEFINED",
        )


class TestGetSelectItems:
    def test_run(self):
        select_items = subject.get_select_items(getattr_("IfcLocalPlacement", "RelativePlacement"))
        assert type(select_items) is tuple
        assert len(select_items) == 2
        assert all(isinstance(i, W.declaration) for i in select_items)
        assert [i.name() for i in select_items] == ["IfcAxis2Placement2D", "IfcAxis2Placement3D"]
