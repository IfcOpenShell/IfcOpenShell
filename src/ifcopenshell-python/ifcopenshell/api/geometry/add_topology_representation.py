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

from typing import Optional

import ifcopenshell

_ITEM_TYPE_TO_REP_TYPE = {
    "IfcVertex": "Vertex",
    "IfcVertexPoint": "Vertex",
    "IfcEdge": "Edge",
    "IfcOrientedEdge": "Edge",
    "IfcEdgeCurve": "Edge",
    "IfcEdgeLoop": "Edge",
    "IfcPath": "Edge",
    "IfcFace": "Face",
    "IfcFaceSurface": "Face",
    "IfcAdvancedFace": "Face",
    "IfcClosedShell": "Face",
    "IfcOpenShell": "Face",
    "IfcConnectedFaceSet": "Face",
}


def add_topology_representation(
    file: ifcopenshell.file,
    context: ifcopenshell.entity_instance,
    item: ifcopenshell.entity_instance,
    representation_identifier: Optional[str] = None,
    representation_type: Optional[str] = None,
) -> ifcopenshell.entity_instance:
    """Adds an IfcTopologyRepresentation for a structural element

    Structural analysis elements (IfcStructuralSurfaceMember,
    IfcStructuralCurveMember) use topology representations rather than solid
    geometry. This is analogous to :func:`add_axis_representation` and
    :func:`add_profile_representation` but produces an
    IfcTopologyRepresentation instead of an IfcShapeRepresentation.

    The representation type ("Face", "Edge", "Vertex") is inferred from the
    item's IFC class if not provided explicitly.

    :param context: The IfcGeometricRepresentationContext for the
        representation, typically a Reference context.
    :param item: The IfcTopologicalRepresentationItem (e.g. IfcFaceSurface,
        IfcEdge) to include in the representation.
    :param representation_identifier: The RepresentationIdentifier string.
        Defaults to the context's ContextIdentifier.
    :param representation_type: The RepresentationType string ("Face",
        "Edge", "Vertex"). Inferred from item class if not given.
    :return: The newly created IfcTopologyRepresentation entity.

    Example:

    .. code:: python

        context = ifcopenshell.util.representation.get_context(
            model, "Model", "Reference", "GRAPH_VIEW")
        face = model.createIfcFaceSurface(bounds, surface, True)
        rep = ifcopenshell.api.geometry.add_topology_representation(
            model, context=context, item=face)
        ifcopenshell.api.geometry.assign_representation(
            model, product=member, representation=rep)
    """
    if representation_identifier is None:
        representation_identifier = context.ContextIdentifier

    if representation_type is None:
        for ifc_class, rep_type in _ITEM_TYPE_TO_REP_TYPE.items():
            if item.is_a(ifc_class):
                representation_type = rep_type
                break
        else:
            representation_type = "Undefined"

    return file.createIfcTopologyRepresentation(
        context,
        representation_identifier,
        representation_type,
        [item],
    )
