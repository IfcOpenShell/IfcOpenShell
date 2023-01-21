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

import ifcopenshell.api


class Usecase:
    def __init__(
        self, file, parent_resource=None, ifc_class="IfcCrewResource", name=None, predefined_type="NOTDEFINED"
    ):
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
        :type parent_resource: ifcopenshell.entity_instance.entity_instance
        :param ifc_class: The class of resource chosen from
            IfcConstructionEquipmentResource, IfcConstructionMaterialResource,
            IfcConstructionProductResource, IfcCrewResource, IfcLaborResource,
            or IfcSubContractResource.
        :type ifc_class: str,optional
        :param name: The name of the resource
        :type name: str,optional
        :param predefined_type: Consult the IFC documentation for the valid
            predefined types for each type of resource class.
        :type predefined_type: str,optional
        :return: The newly created resource depending on the nominated IFC
            class.
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Add our own crew
            crew = ifcopenshell.api.run("resource.add_resource", model, ifc_class="IfcCrewResource")

            # Add some labour to our crew.
            ifcopenshell.api.run("resource.add_resource", model, parent_resource=crew, ifc_class="IfcLaborResource")
        """
        self.file = file
        self.settings = {
            "parent_resource": parent_resource,
            "ifc_class": ifc_class,
            "name": name,
            "predefined_type": predefined_type,
        }

    def execute(self):
        resource = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class=self.settings["ifc_class"],
            predefined_type=self.settings["predefined_type"],
            name=self.settings["name"] or "Unnamed",
        )
        # TODO: this is an ambiguity by buildingSMART: Can we nest an IfcCrewResource under an IfcCrewResource ?
        # https://forums.buildingsmart.org/t/what-are-allowed-to-be-root-level-construction-resources/3550
        if self.settings["parent_resource"]:
            ifcopenshell.api.run(
                "nest.assign_object",
                self.file,
                related_object=resource,
                relating_object=self.settings["parent_resource"],
            )
        else:
            context = self.file.by_type("IfcContext")[0]
            ifcopenshell.api.run(
                "project.assign_declaration",
                self.file,
                definition=resource,
                relating_context=context,
            )
        return resource
