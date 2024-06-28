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


def edit_monetary_unit(file: ifcopenshell.file, unit: ifcopenshell.entity_instance, attributes: dict[str, Any]) -> None:
    """Edits the attributes of an IfcMonetaryUnit

    For more information about the attributes and data types of an
    IfcMonetaryUnit, consult the IFC documentation.

    :param unit: The IfcMonetaryUnit entity you want to edit
    :type unit: ifcopenshell.entity_instance
    :param attributes: a dictionary of attribute names and values.
    :type attributes: dict
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # If you do all your cost plans in Zimbabwean dollars then nobody
        # knows how accurate the numbers are.
        zwl = ifcopenshell.api.unit.add_monetary_unit(model, currency="ZWL")

        # Ah who are we kidding
        ifcopenshell.api.unit.edit_monetary_unit(model, unit=zwl, attributes={"Currency": "USD"})
    """
    settings = {"unit": unit, "attributes": attributes or {}}

    for name, value in settings["attributes"].items():
        setattr(settings["unit"], name, value)
