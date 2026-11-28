# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
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
from typing import Any

import ifcopenshell


def edit_structural_activity(
    file: ifcopenshell.file, activity: ifcopenshell.entity_instance, attributes: dict[str, Any]
) -> None:
    """Edits the attributes of an IfcStructuralActivity

    For more information about the attributes and data types of an
    IfcStructuralActivity, consult the IFC documentation.

    IFC allows a load per projected length or area (a ProjectedOrTrue of
    PROJECTED_LENGTH) only in global coordinates. An activity turned to
    local coordinates (a GlobalOrLocal of LOCAL_COORDS) is therefore set to
    TRUE_LENGTH, and asking for both at once is refused.

    :param activity: The IfcStructuralActivity entity you want to edit
    :param attributes: a dictionary of attribute names and values.
    :return: None

    Example:

    .. code:: python

        # Snow on a rafter, given per horizontal length
        ifcopenshell.api.structural.edit_structural_activity(model,
            activity=activity, attributes={"ProjectedOrTrue": "PROJECTED_LENGTH"})
    """
    global_or_local = attributes.get("GlobalOrLocal", activity.GlobalOrLocal)
    projected_or_true = attributes.get("ProjectedOrTrue", getattr(activity, "ProjectedOrTrue", None))
    if global_or_local == "LOCAL_COORDS" and projected_or_true == "PROJECTED_LENGTH":
        if attributes.get("ProjectedOrTrue") == "PROJECTED_LENGTH":
            raise ValueError("A load per projected length or area must be in global coordinates")
        attributes = attributes | {"ProjectedOrTrue": "TRUE_LENGTH"}
    for name, value in attributes.items():
        setattr(activity, name, value)
