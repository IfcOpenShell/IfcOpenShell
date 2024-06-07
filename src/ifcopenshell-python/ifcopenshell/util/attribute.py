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
from typing import Union


def get_primitive_type(
    attribute_or_data_type: Union[ifcopenshell_wrapper.attribute, ifcopenshell_wrapper.parameter_type]
) -> Union[str, tuple[str, list[str]]]:
    if hasattr(attribute_or_data_type, "type_of_attribute"):
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
    elif "<boolean>" in data_type or "<logical>" in data_type:
        return "boolean"
    elif "<enumeration" in data_type:
        return "enum"
    elif "<binary" in data_type:
        return "binary"


def get_enum_items(attribute):
    return attribute.type_of_attribute().declared_type().enumeration_items()


def get_select_items(attribute):
    return attribute.type_of_attribute().declared_type().select_list()
