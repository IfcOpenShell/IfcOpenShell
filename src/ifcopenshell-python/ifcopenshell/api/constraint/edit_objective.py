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
from typing import Any


def edit_objective(
    file: ifcopenshell.file, objective: ifcopenshell.entity_instance, attributes: dict[str, Any]
) -> None:
    """Edit the attributes of a objective

    For more information about the attributes and data types of an
    IfcObjective, consult the IFC documentation.

    :param objective: The IfcObjective you want to edit.
    :param attributes: a dictionary of attribute names and values.
    :return: None

    Example:

    .. code:: python

        objective = ifcopenshell.api.constraint.add_objective(model)
        ifcopenshell.api.constraint.edit_objective(model,
            objective=objective, attributes={"ConstraintGrade": "HARD"})
    """
    for name, value in attributes.items():
        setattr(objective, name, value)
