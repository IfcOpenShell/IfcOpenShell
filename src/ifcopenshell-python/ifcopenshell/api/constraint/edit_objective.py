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
    :type objective: ifcopenshell.entity_instance
    :param attributes: a dictionary of attribute names and values.
    :type attributes: dict
    :return: None
    :rtype: None

    Example:

    .. code:: python

        objective = ifcopenshell.api.run("constraint.add_objective", model)
        ifcopenshell.api.run("constraint.edit_objective", model,
            objective=objective, attributes={"ConstraintGrade": "HARD"})
    """
    settings = {"objective": objective, "attributes": attributes or {}}

    for name, value in settings["attributes"].items():
        setattr(settings["objective"], name, value)
