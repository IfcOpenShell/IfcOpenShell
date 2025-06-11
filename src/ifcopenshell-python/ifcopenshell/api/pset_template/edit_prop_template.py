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


def edit_prop_template(
    file: ifcopenshell.file, prop_template: ifcopenshell.entity_instance, attributes: dict[str, Any]
) -> None:
    """Edits the attributes of an IfcSimplePropertyTemplate

    For more information about the attributes and data types of an
    IfcSimplePropertyTemplate, consult the IFC documentation.

    :param prop_template: The IfcSimplePropertyTemplate entity you want to edit
    :param attributes: a dictionary of attribute names and values.
    :return: None

    Example:

    .. code:: python

        template = ifcopenshell.api.pset_template.add_pset_template(model, name="ABC_RiskFactors")

        # Here's a property with just default values.
        prop = ifcopenshell.api.pset_template.add_prop_template(model, pset_template=template)

        # Let's edit it to give the actual values we need.
        ifcopenshell.api.pset_template.edit_prop_template(model,
            prop_template=prop, attributes={"Name": "DemoA", "PrimaryMeasureType": "IfcLengthMeasure"})
    """
    if enum_values := attributes.get("Enumerators", None):
        prop_name = attributes.get("Name", None) or getattr(prop_template, "Name", None) or "Unnamed"
        primary_measure_type = (
            attributes.get("PrimaryMeasureType", None)
            or getattr(prop_template, "PrimaryMeasureType", None)
            or "IfcLabel"
        )
        enum_values = [file.create_entity(primary_measure_type, v) for v in enum_values]
        if enumerators := prop_template.Enumerators:
            enumerators.Name = prop_name
            enumerators.EnumerationValues = enum_values
        else:
            prop_template.Enumerators = file.create_entity("IfcPropertyEnumeration", prop_name, enum_values)

    if "Enumerators" in attributes:
        del attributes["Enumerators"]

    for name, value in attributes.items():
        setattr(prop_template, name, value)
