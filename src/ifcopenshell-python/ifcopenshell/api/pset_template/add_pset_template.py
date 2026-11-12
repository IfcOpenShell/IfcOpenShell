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


def add_pset_template(
    file: ifcopenshell.file,
    name: str = "New_Pset",
    template_type: str = "PSET_TYPEDRIVENOVERRIDE",
    applicable_entity: str = "IfcObject,IfcTypeObject",
) -> ifcopenshell.entity_instance:
    """Adds a new property set template

    This creates a new template for property sets. A template defines what
    the name of the property set should be, what properties it can have,
    what entities (e.g. wall) the property set can be assigned to, whether
    it should be assigned at a type or occurrence level, the data types of
    the properties, and descriptions of the properties. This template can
    then be used as a project, company, or local government standard.

    buildingSMART itself ships a catalogue of property sets using these
    templates, ensuring that internationally common properties (e.g.  fire
    rating of a wall) are all implemented exactly the same way across all
    vendors and projects. Naturally, not everything can be standardised
    internationally, so this allows you to create your own templates.

    You may either create a property template to store properties, or a
    quantity template to store quantities. For convenience, we will always
    call them "property templates" as they are conceptually very similar.

    This function only creates a template for the property set, not the
    properties themselves within the property set. At this level, you are
    allowed to define the name of the property set, whether it is type or
    occurrence based, and which entities it applies to.

    See the documentation for IfcPropertySetTemplate for instructions on
    the types of template type and list of applicable entities.

    The types of property set templates are:

    * PSET_TYPEDRIVENONLY - assigned only to types
    * PSET_TYPEDRIVENOVERRIDE - assigned to types or occurrences. If both,
        the occurrence overrides the type.
    * PSET_OCCURRENCEDRIVEN - assigned to occurrences only.
    * PSET_PERFORMANCEDRIVEN - assigned as a timeseries data range. This is
        only recommended for advanced users.
    * QTO_TYPEDRIVENONLY - assigned only to types, but for quantities.
    * QTO_TYPEDRIVENOVERRIDE - assigned to types or occurrences, but for
        quantities. If both, the occurrence overrides the type.
    * QTO_OCCURRENCEDRIVEN - assigned to occurrences only, but for
        quantities.

    By default, this creates a template that can be applied to types, but
    overridden by occurrences, and is applicable to everything.

    :param name: The name of the property set
    :param template_type: Choose from one of PSET_TYPEDRIVENONLY,
        PSET_TYPEDRIVENOVERRIDE, PSET_OCCURRENCEDRIVEN,
        PSET_PERFORMANCEDRIVEN, QTO_TYPEDRIVENONLY, QTO_TYPEDRIVENOVERRIDE,
        QTO_OCCURRENCEDRIVEN, NOTDEFINED
    :param applicable_entity: The entity that this template is allowed to be
        applied to. For example, IfcWall means that the property set may be
        assigned to walls only. IfcTypeObject, the default, means that the
        property set may be assigned to any type.
    :return: The newly created IfcPropertySetTemplate

    Example:

    .. code:: python

        # Create a simple template that may be applied to all types
        ifcopenshell.api.pset_template.add_pset_template(model, name="ABC_RiskFactors")

        # Note that we aren't finished yet. Our property set template
        # doesn't have any properties in it. Let's add a minimum of one
        # property.
        ifcopenshell.api.pset_template.add_prop_template(model, pset_template=template,
            name="HighVoltage", description="Whether there is a risk of high voltage.",
            primary_measure_type="IfcBoolean")
    """
    return file.create_entity(
        "IfcPropertySetTemplate",
        GlobalId=ifcopenshell.guid.new(),
        Name=name,
        TemplateType=template_type,
        ApplicableEntity=applicable_entity,
    )
