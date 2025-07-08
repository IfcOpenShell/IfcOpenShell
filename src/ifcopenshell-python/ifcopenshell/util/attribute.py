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

import ifcopenshell.ifcopenshell_wrapper as ifcopenshell_wrapper
from typing import Union, Literal

PrimitiveType = Literal["entity", "string", "float", "integer", "boolean", "enum", "binary"]
ComplexPrimitiveType = Literal["list", "array", "set"]
PrimitiveTypeOutput = Union[
    PrimitiveType,
    tuple[ComplexPrimitiveType, "PrimitiveTypeOutput"],
    tuple[Literal["select"], tuple["PrimitiveTypeOutput", ...]],
    None,
]


def get_primitive_type(
    attribute_or_data_type: Union[ifcopenshell_wrapper.attribute, ifcopenshell_wrapper.parameter_type],
) -> PrimitiveTypeOutput:
    if isinstance(attribute_or_data_type, ifcopenshell_wrapper.attribute):
        data_type = str(attribute_or_data_type.type_of_attribute())
    else:
        data_type = str(attribute_or_data_type)
    if data_type.find("<type") == 0:
        return get_primitive_type(data_type[data_type[1:].find("<") + 1 :])
    elif data_type.find("<list") == 0:
        return ("list", get_primitive_type(data_type[data_type[1:].find("<") + 1 :]))
    elif data_type.find("<array") == 0:
        return ("array", get_primitive_type(data_type[data_type[1:].find("<") + 1 :]))
    elif data_type.find("<set") == 0:
        return ("set", get_primitive_type(data_type[data_type[1:].find("<") + 1 :]))
    elif data_type.find("<select") == 0:
        select_definition = data_type[data_type.find("(") + 1 : data_type.find(")")].split("|")
        select_types = [get_primitive_type(d.strip()) for d in select_definition]
        return ("select", tuple(select_types))
    elif "<entity" in data_type:
        return "entity"
    elif "<string>" in data_type:
        return "string"
    elif "<real>" in data_type:
        return "float"
    elif "<number>" in data_type or "<integer>" in data_type:
        return "integer"
    elif "<boolean>" in data_type:
        return "boolean"
    elif "<logical>" in data_type or "<enumeration" in data_type:
        return "enum"
    elif "<binary" in data_type:
        return "binary"


def get_enum_items(attribute: ifcopenshell_wrapper.attribute) -> tuple[str, ...]:
    named_type = attribute.type_of_attribute().as_named_type()
    assert named_type
    enumeration = named_type.declared_type().as_enumeration_type()
    assert enumeration
    return enumeration.enumeration_items()


def get_select_items(attribute: ifcopenshell_wrapper.attribute) -> tuple[ifcopenshell_wrapper.declaration, ...]:
    named_type = attribute.type_of_attribute().as_named_type()
    assert named_type
    select_type = named_type.declared_type().as_select_type()
    assert select_type
    return select_type.select_list()
