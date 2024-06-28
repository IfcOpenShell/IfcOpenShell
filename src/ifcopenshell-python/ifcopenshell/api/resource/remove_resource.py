# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021-2022, Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>
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
import ifcopenshell.api.resource
import ifcopenshell.util.element


def remove_resource(file: ifcopenshell.file, resource: ifcopenshell.entity_instance) -> None:
    """Removes a resource and all relationships

    Example:

    .. code:: python

        # Add our own crew
        crew = ifcopenshell.api.resource.add_resource(model, ifc_class="IfcCrewResource")

        # Fire our crew
        ifcopenshell.api.resource.remove_resource(model, resource=crew)
    """
    settings = {"resource": resource}

    # TODO: review deep purge
    for inverse in file.get_inverse(settings["resource"]):
        if inverse.is_a("IfcRelNests"):
            if inverse.RelatingObject == settings["resource"]:
                for related_object in inverse.RelatedObjects:
                    ifcopenshell.api.resource.remove_resource(file, resource=related_object)
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
        elif inverse.is_a("IfcRelAssignsToControl"):
            if len(inverse.RelatedObjects) == 1:
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
            else:
                related_objects = list(inverse.RelatedObjects)
                related_objects.remove(settings["resource"])
                inverse.RelatedObjects = related_objects
        elif inverse.is_a("IfcRelAssignsToResource"):
            if inverse.RelatingResource == settings["resource"]:
                for related_object in inverse.RelatedObjects:
                    ifcopenshell.api.resource.unassign_resource(
                        file, related_object=related_object, relating_resource=settings["resource"]
                    )
            elif inverse.RelatedObjects == tuple(settings["resource"]):
                history = inverse.OwnerHistory
                file.remove(inverse)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)
    # Usage was added in IFC4.
    if usage := getattr(settings["resource"], "Usage", None):
        file.remove(usage)
    if settings["resource"].BaseQuantity:
        ifcopenshell.api.resource.remove_resource_quantity(file, resource=settings["resource"])
    history = settings["resource"].OwnerHistory
    file.remove(settings["resource"])
    if history:
        ifcopenshell.util.element.remove_deep2(file, history)
