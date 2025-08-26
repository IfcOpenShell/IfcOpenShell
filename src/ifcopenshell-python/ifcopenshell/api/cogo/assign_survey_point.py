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
from ifcopenshell import entity_instance
import typing


def assign_survey_point(annotation: entity_instance, survey_point: entity_instance):
    """
    Assigns a coordinate point to a survey point annotation

    :param annotaton: The survey point annotation
    :param survey_point: The survey point
    :return: None

    Example:

    .. code:: python

        annotation = ifcopenshell.api.cogo.add_survey_point(file,file.createIfcCartesianPoint(4000.0,3500.0)))
        ifcopenshell.api.cogo.assign_surve_point(annotation,file.createIfcCartesianPoint(4000.0,3500.0,100.0))
    """
    annotation.Representation.Representations[0].Items = [survey_point]
