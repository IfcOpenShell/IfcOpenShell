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
from typing import Any


def edit_metric(file: ifcopenshell.file, metric: ifcopenshell.entity_instance, attributes: dict[str, Any]) -> None:
    """Edit the attributes of a metric

    For more information about the attributes and data types of an
    IfcMetric, consult the IFC documentation.

    :param metric: The IfcMetric you want to edit.
    :param attributes: a dictionary of attribute names and values.
    :return: None

    Example:

    .. code:: python

        objective = ifcopenshell.api.constraint.add_objective(model)
        metric = ifcopenshell.api.constraint.add_metric(model,
            objective=objective)
        ifcopenshell.api.constraint.edit_metric(model,
            metric=metric, attributes={"ConstraintGrade": "HARD"})
    """
    for name, value in attributes.items():
        setattr(metric, name, value)
