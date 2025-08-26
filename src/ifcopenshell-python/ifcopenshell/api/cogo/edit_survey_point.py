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


def edit_survey_point(annotation: entity_instance, x: float, y: float, z: float = 0.0):
    """
    Edits the location of a previously defined survey point

    :param survey_point: The survey point
    :return: None

    Example:

    .. code:: python

        annotation = ifcopenshell.api.cogo.add_survey_point(file,file.createIfcCartesianPoint(4000.0,3500.0)))
        ifcopenshell.api.cogo.edit_surve_point(annotation,3500.0,2000.0)
    """
    if annotation.Representation.Representations[0].Items[0].Dim == 2:
        annotation.Representation.Representations[0].Items[0].Coordinates = (x, y)
    else:
        annotation.Representation.Representations[0].Items[0].Coordinates = (x, y, z)
