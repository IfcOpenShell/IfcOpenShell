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
import ifcopenshell.api.owner
import ifcopenshell.guid


def assign_resource(
    file: ifcopenshell.file,
    relating_resource: ifcopenshell.entity_instance,
    related_object: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance:
    """Assigns a resource to an object

    Two types of objects are typically assigned to resources: products and
    actors.

    If a product is assigned to a resource, that means that the product
    represents the resource on site. This may be represented via material
    handling zones on a construction site, or equipment like cranes and
    their physical locations.

    If an actor is assigned to a resource, that means that the actor (person
    or organisation) is the actor consuming the resource (e.g. if the
    resource is material or equipment) or the actor performing the work
    (e.g. if the resource is a labour resource).

    :param relating_resource: The IfcResource to assign the object to.
    :param related_object: The IfcProduct or IfcActor to assign to the
        object.
    :return: The newly created IfcRelAssignsToResource

    Example:

    .. code:: python

        # Add our own crew
        crew = ifcopenshell.api.resource.add_resource(model, ifc_class="IfcCrewResource")

        # Add some a tower crane to our crew.
        crane = ifcopenshell.api.resource.add_resource(model,
            parent_resource=crew, ifc_class="IfcConstructionEquipmentResource", name="Tower Crane 01")

        # Our tower crane will be placed via this physical product.
        product = ifcopenshell.api.root.create_entity(model,
            ifc_class="IfcBuildingElementProxy", predefined_type="CRANE")

        # Let's place our crane at some X, Y coordinates.
        matrix = numpy.eye(4)
        matrix[0][3], matrix[1][3] = 3.0, 4.0
        ifcopenshell.api.geometry.edit_object_placement(model, product=crane, matrix=matrix)

        # Let's assign our crane to the resource. The crane now represents
        # the resource.
        ifcopenshell.api.resource.assign_resource(model, relating_resource=crane, related_object=product)

        # Setup an organisation actor who will operate the crane
        organisation = ifcopenshell.api.owner.add_organisation(model,
            identification="UCO", name="Unionised Crane Operators Pty Ltd")
        role = ifcopenshell.api.owner.add_role(model, assigned_object=organisation, role="CREW")
        actor = ifcopenshell.api.owner.add_actor(model, actor=organisation)

        # This means that UCO is now our crane operator.
        ifcopenshell.api.resource.assign_resource(model, relating_resource=crane, related_object=actor)
    """
    if related_object.HasAssignments:
        for assignment in related_object.HasAssignments:
            if assignment.is_a("IfclRelAssignsToResource") and assignment.RelatingResource == relating_resource:
                return assignment

    resource_of = None
    if relating_resource.ResourceOf:
        resource_of = relating_resource.ResourceOf[0]

    if resource_of:
        related_objects = list(resource_of.RelatedObjects)
        related_objects.append(related_object)
        resource_of.RelatedObjects = related_objects
        ifcopenshell.api.owner.update_owner_history(file, **{"element": resource_of})
    else:
        resource_of = file.create_entity(
            "IfcRelAssignsToResource",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
                "RelatedObjects": [related_object],
                "RelatingResource": relating_resource,
            }
        )
    return resource_of
