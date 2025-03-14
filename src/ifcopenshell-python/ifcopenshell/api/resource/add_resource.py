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

import ifcopenshell.api.root
import ifcopenshell.api.nest
import ifcopenshell.api.project
from typing import Optional


def add_resource(
    file: ifcopenshell.file,
    parent_resource: Optional[ifcopenshell.entity_instance] = None,
    ifc_class: str = "IfcCrewResource",
    name: Optional[str] = None,
    predefined_type: str = "NOTDEFINED",
) -> ifcopenshell.entity_instance:
    """Add a new construction resource

    Construction resources may be managed and connected to cost schedules
    and construction schedules. This allows calculations to be done on
    resource utilisation, cost optimisation (e.g. labour rates), and
    optioneering on build strategies.

    There are typically two types of resources. Crew resources are resources
    where you manage your own crew and you have full control over the
    equipment, labour, products, and materials used by your crew.
    Alternatively, there are subcontractor resources, where you simply
    delegate all the details to a subcontractor and it is not decomposed
    into further levels of detail.

    This means when adding resources, you'd first either add a crew or
    subcontract resource. If it is a crew resource, you'd then add child
    resources to that crew, such as equipment (cranes, excavators, hoists,
    etc), material (wood, concrete, etc), and labour (rigging crews,
    formworkers, etc).

    :param parent_resource: If this is a child resource (typically to a crew
        resource), then nominate the parent IfcConstructionResource here.
    :param ifc_class: The class of resource chosen from
        IfcConstructionEquipmentResource, IfcConstructionMaterialResource,
        IfcConstructionProductResource, IfcCrewResource, IfcLaborResource,
        or IfcSubContractResource.
    :param name: The name of the resource
    :param predefined_type: Consult the IFC documentation for the valid
        predefined types for each type of resource class.
    :return: The newly created resource depending on the nominated IFC
        class.

    Example:

    .. code:: python

        # Add our own crew
        crew = ifcopenshell.api.resource.add_resource(model, ifc_class="IfcCrewResource")

        # Add some labour to our crew.
        ifcopenshell.api.resource.add_resource(model, parent_resource=crew, ifc_class="IfcLaborResource")
    """

    resource = ifcopenshell.api.root.create_entity(
        file,
        ifc_class=ifc_class,
        predefined_type=predefined_type,
        name=name or "Unnamed",
    )
    # TODO: this is an ambiguity by buildingSMART: Can we nest an IfcCrewResource under an IfcCrewResource ?
    # https://forums.buildingsmart.org/t/what-are-allowed-to-be-root-level-construction-resources/3550
    if parent_resource:
        ifcopenshell.api.nest.assign_object(file, related_objects=[resource], relating_object=parent_resource)
    elif file.schema != "IFC2X3":
        context = file.by_type("IfcContext")[0]
        ifcopenshell.api.project.assign_declaration(file, definitions=[resource], relating_context=context)
    return resource
