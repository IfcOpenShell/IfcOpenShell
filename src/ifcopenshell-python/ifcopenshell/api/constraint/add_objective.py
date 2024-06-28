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


def add_objective(file: ifcopenshell.file) -> ifcopenshell.entity_instance:
    """Add a new objective constraint

    Parametric constraints may be defined by the user. The constraint is defined
    by first creating an objective describing the purpose of the constraint and
    whether it is a hard or soft constraint. Later on, metrics may be added to
    check whether the constraint has been met by connecting it to properties and
    quantities. See ifcopenshell.api.constraint.add_metric for more information.

    :return: The newly created IfcObjective entity
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # Create a new objective for code compliance requirements
        objective = ifcopenshell.api.constraint.add_objective(model)
        objective.ConstraintGrade = "ADVISORY"
        objective.ObjectiveQualifier = "CODECOMPLIANCE"
        # Note: the objective right now is purely qualitative and for
        # information purposes. You may wish to add quantiative metrics.
    """
    settings = {}

    return file.create_entity(
        "IfcObjective", **{"Name": "Unnamed", "ConstraintGrade": "NOTDEFINED", "ObjectiveQualifier": "NOTDEFINED"}
    )
