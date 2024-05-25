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

import ifcopenshell.api
from typing import Literal


def add_structural_activity(
    file: ifcopenshell.file,
    applied_load: ifcopenshell.entity_instance,
    structural_member: ifcopenshell.entity_instance,
    ifc_class: str = "IfcStructuralPlanarAction",
    predefined_type: str = "CONST",
    global_or_local: Literal["GLOBAL_COORDS", "LOCAL_COORDS"] = "GLOBAL_COORDS",
) -> None:
    """Adds a new structural activity

    A structural activity is either a structural action or a reaction. It
    may be applied to a point, a curve, or a planar surface, and may be a
    constant load, linear, etc.

    The activity must be defined using an applied load, and associated with
    a structural member.

    :param ifc_class: Choose from any subtype of IfcStructuralActivity.
    :type ifc_class: str
    :param predefined_type: View the IFC documentation for what valid
        predefined types may be chosen.
    :type predefined_type: str
    :param global_or_local: The location coordinates of the load is always
        defined locally relative to the structural member the activity is
        assigned to. However, the directions of the applied load may either
        be specified globally or locally depending on how this argument is
        set. Choose from GLOBAL_COORDS or LOCAL_COORDS.
    :type global_or_local: str
    :param applied_load: The IfcStructuralLoad that is applied in this
        activity.
    :type applied_load: ifcopenshell.entity_instance
    :param structural_member: The IfcStructuralMember that the load is
        applied to.
    :type structural_member: ifcopenshell.entity_instance
    :return: The newly created entity based on the ifc_class
    :rtype: ifcopenshell.entity_instance
    """
    settings = {
        "ifc_class": ifc_class,
        "predefined_type": predefined_type,
        "global_or_local": global_or_local,
        "applied_load": applied_load,
        "structural_member": structural_member,
    }

    activity = ifcopenshell.api.run(
        "root.create_entity",
        file,
        ifc_class=settings["ifc_class"],
        predefined_type=settings["predefined_type"],
    )
    activity.AppliedLoad = settings["applied_load"]
    activity.GlobalOrLocal = settings["global_or_local"]

    rel = ifcopenshell.api.run("root.create_entity", file, ifc_class="IfcRelConnectsStructuralActivity")
    rel.RelatingElement = settings["structural_member"]
    rel.RelatedStructuralActivity = activity
    return activity
