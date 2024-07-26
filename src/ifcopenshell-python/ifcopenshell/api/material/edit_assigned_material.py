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


def edit_assigned_material(
    file: ifcopenshell.file, element: ifcopenshell.entity_instance, attributes: dict[str, Any]
) -> None:
    """Edits the attributes of an IfcMaterial

    For more information about the attributes and data types of an
    IfcMaterial, consult the IFC documentation.

    :param element: The IfcMaterial entity you want to edit
    :type element: ifcopenshell.entity_instance
    :param attributes: a dictionary of attribute names and values.
    :type attributes: dict
    :return: None
    :rtype: None

    Example:

    .. code:: python

        concrete = ifcopenshell.api.material.add_material(model, name="CON01", category="concrete")
        ifcopenshell.api.material.edit_assigned_material(model,
            element=concrete, attributes={"Description": "40MPA concrete with broom finish"})
    """
    settings = {"element": element, "attributes": attributes}

    for name, value in settings["attributes"].items():
        setattr(settings["element"], name, value)
