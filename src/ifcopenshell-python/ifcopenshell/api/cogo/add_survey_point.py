# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Thomas Krijnen <thomas@aecgeeks.com>
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
import ifcopenshell.api.spatial
import ifcopenshell.util.representation
from ifcopenshell import entity_instance
from typing import Union


def add_survey_point(
    file: ifcopenshell.file, survey_point: entity_instance, site: Union[entity_instance, None] = None
) -> entity_instance:
    """
    Adds a single survey point to the model based on IFC Concept Template 4.1.7.1.2.5.
    Survey points are located relative to IfcRepresentationContext.WorldCoordinateSystem

    :param survey_point: The survey point
    :return: an IfcAnnotation entity

    Example:

    .. code:: python

        annotation = ifcopenshell.api.cogo.add_survey_point(file,file.createIfcCartesianPoint(4000.0,3500.0)))
    """
    context = ifcopenshell.util.representation.get_context(file, "Model", "Annotation", "MODEL_VIEW")
    shape_representation = file.createIfcShapeRepresentation(
        ContextOfItems=context, RepresentationIdentifier="Annotation", RepresentationType="Point", Items=[survey_point]
    )
    representation = file.createIfcProductDefinitionShape(Representations=[shape_representation])
    annotation = file.createIfcAnnotation(
        ifcopenshell.guid.new(),
        ObjectPlacement=context.WorldCoordinateSystem,
        Representation=representation,
        PredefinedType="SURVEY",
    )

    if site == None:
        site = file.by_type("IfcSite")[0]

    ifcopenshell.api.spatial.assign_container(file, relating_structure=site, products=[annotation])

    return annotation
