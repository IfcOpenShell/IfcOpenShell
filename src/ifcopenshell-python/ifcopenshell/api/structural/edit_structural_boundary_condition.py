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
from typing import Any, TypedDict, Literal, Union


class AttributeDict(TypedDict):
    type: Union[
        Literal["string", "null"],
        str,  # IFC Class.
    ]
    value: Any


def edit_structural_boundary_condition(
    file: ifcopenshell.file,
    condition: ifcopenshell.entity_instance,
    attributes: dict[str, AttributeDict],
) -> None:
    """Edits the attributes of an IfcBoundaryCondition

    For more information about the attributes and data types of an
    IfcBoundaryCondition, consult the IFC documentation.

    :param condition: The IfcBoundaryCondition entity you want to edit
    :param attributes: a dictionary of attribute names and values.
        Each value is represented by a dictionary.
    :return: None
    """
    for name, data in attributes.items():
        if data["type"] == "string" or data["type"] == "null":
            value = data["value"]
        elif data["type"] == "IfcBoolean":
            value = file.createIfcBoolean(data["value"])
        else:
            value = file.create_entity(data["type"], data["value"])
        setattr(condition, name, value)
