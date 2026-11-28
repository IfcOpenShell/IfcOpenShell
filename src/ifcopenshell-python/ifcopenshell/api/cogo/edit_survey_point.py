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


from ifcopenshell import entity_instance


def edit_survey_point(annotation: entity_instance, x: float, y: float, z: float = 0.0):
    """
    Edits the location of a previously defined survey point

    :param survey_point: The survey point
    :return: None

    Example:

    .. code:: python

        model = ifcopenshell.file(schema="IFC4X3")
        ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
        model_context = ifcopenshell.api.context.add_context(model, context_type="Model")
        ifcopenshell.api.context.add_context(model, context_type="Model",
            context_identifier="Annotation", target_view="MODEL_VIEW", parent=model_context)
        ifcopenshell.api.root.create_entity(model, ifc_class="IfcSite")
        point = model.createIfcCartesianPoint((4000.0, 3500.0))
        annotation = ifcopenshell.api.cogo.add_survey_point(model, survey_point=point)
        ifcopenshell.api.cogo.edit_survey_point(annotation, x=3500.0, y=2000.0)
    """
    if annotation.Representation.Representations[0].Items[0].Dim == 2:
        annotation.Representation.Representations[0].Items[0].Coordinates = (x, y)
    else:
        annotation.Representation.Representations[0].Items[0].Coordinates = (x, y, z)
