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


def edit_pset_template(
    file: ifcopenshell.file, pset_template: ifcopenshell.entity_instance, attributes: dict[str, Any]
) -> None:
    """Edits the attributes of an IfcPropertySetTemplate

    For more information about the attributes and data types of an
    IfcPropertySetTemplate, consult the IFC documentation.

    :param pset_template: The IfcPropertySetTemplate entity you want to edit
    :param attributes: a dictionary of attribute names and values.
    :return: None

    Example:

    .. code:: python

        # Whoops! We named it with a buildingSMART reserved "Pset_" prefix!
        template = ifcopenshell.api.pset_template.add_pset_template(model, name="Pset_RiskFactors")

        # Let's fix it to prefix with our company code instead.
        ifcopenshell.api.pset_template.edit_pset_template(model,
            pset_template=template, attributes={"Name": "ABC_RiskFactors"})
    """
    for name, value in attributes.items():
        setattr(pset_template, name, value)
