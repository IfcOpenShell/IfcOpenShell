# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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
# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.root


def assign_product(
    file: ifcopenshell.file,
    relating_product: ifcopenshell.entity_instance,
    related_object: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance:
    """Links an object to a product via IfcRelAssignsToProduct

    Typically used to associate a physical building element with a structural
    analysis member (IfcStructuralSurfaceMember, IfcStructuralCurveMember) so
    that analysis results can be traced back to the physical model.

    :param relating_product: The IfcProduct that the object is assigned to,
        typically an IfcStructuralMember.
    :param related_object: The IfcObjectDefinition being assigned, typically
        a physical building element such as an IfcWall or IfcSlab.
    :return: The IfcRelAssignsToProduct relationship.

    Example:

    .. code:: python

        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        member = ifcopenshell.api.root.create_entity(
            model, ifc_class="IfcStructuralSurfaceMember")
        ifcopenshell.api.structural.assign_product(model,
            relating_product=member, related_object=wall)
    """
    for rel in relating_product.ReferencedBy or []:
        if not rel.is_a("IfcRelAssignsToProduct"):
            continue
        if related_object in rel.RelatedObjects:
            return rel
        related_objects = list(rel.RelatedObjects)
        related_objects.append(related_object)
        rel.RelatedObjects = related_objects
        return rel

    rel = ifcopenshell.api.root.create_entity(file, ifc_class="IfcRelAssignsToProduct")
    rel.RelatingProduct = relating_product
    rel.RelatedObjects = [related_object]
    return rel
