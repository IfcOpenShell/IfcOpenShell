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
import ifcopenshell.guid
from typing import Optional


def add_prop_template(
    file: ifcopenshell.file,
    pset_template: ifcopenshell.entity_instance,
    name: str = "NewProperty",
    description: Optional[str] = None,
    template_type: str = "P_SINGLEVALUE",
    primary_measure_type: str = "IfcLabel",
) -> ifcopenshell.entity_instance:
    """Adds new property templates to a property set template

    Assuming you first have a property set template, this allows you to add
    templates for properties within that property set. A property template
    lets you specify the name, description, and data type of a property.
    When the template is provided to a model author, this gives them clear
    instructions about the intention of the property and exactly which data
    type to use.

    Types of properties and quantities include:

    * P_SINGLEVALUE - a single value, the most common type of property.
    * P_ENUMERATEDVALUE	- the property value may one or more values chosen
        from a preset list of values.
    * P_BOUNDEDVALUE - the property has a minimum, maximum, and set value.
    * P_LISTVALUE - the property has a list of values.
    * P_TABLEVALUE - the property has a table of values.
    * P_REFERENCEVALUE - the property is a parametric reference to another
        value. This is only for advanced users.
    * Q_LENGTH - the quantity is a length.
    * Q_AREA - the quantity is an area.
    * Q_VOLUME - the quantity is a volume.
    * Q_COUNT - the quantity is counting a item.
    * Q_WEIGHT - the quantity is a weight.
    * Q_TIME - the quantity is a time duration.

    :param pset_template: The property set template to add the property
        template to.
    :type pset_template: ifcopenshell.entity_instance
    :param name: The name of the property
    :type name: str,optional
    :param description: A few words describing what the property stores.
    :type description: str,optional
    :param primary_measure_type: The data type of the property. Consult the
        IFC documentation for the full list of data types.
    :param primary_measure_type: str,optional
    :return: The newly created IfcSimplePropertyTemplate.
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # Create a simple template that may be applied to all types
        template = ifcopenshell.api.pset_template.add_pset_template(model, name="ABC_RiskFactors")

        # Here's one example property
        ifcopenshell.api.pset_template.add_prop_template(model, pset_template=template,
            name="HighVoltage", description="Whether there is a risk of high voltage.",
            primary_measure_type="IfcBoolean")

        # Here's another
        ifcopenshell.api.pset_template.add_prop_template(model, pset_template=template,
            name="ChemicalType", description="The class of chemical spillage.",
            primary_measure_type="IfcLabel")
    """
    settings = {
        "pset_template": pset_template,
        "name": name,
        "description": description,
        "template_type": template_type,
        "primary_measure_type": primary_measure_type,
    }

    prop_template = file.create_entity(
        "IfcSimplePropertyTemplate",
        **{
            "GlobalId": ifcopenshell.guid.new(),
            "Name": settings["name"],
            "Description": settings["description"],
            "PrimaryMeasureType": settings["primary_measure_type"],
            "TemplateType": settings["template_type"],
            "AccessState": "READWRITE",
            "Enumerators": None,
        }
    )
    has_property_templates = list(settings["pset_template"].HasPropertyTemplates or [])
    has_property_templates.append(prop_template)
    settings["pset_template"].HasPropertyTemplates = has_property_templates
    return prop_template
