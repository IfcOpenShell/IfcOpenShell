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

from typing import Optional

import ifcopenshell.api.root


def add_structural_load_combination(
    file: ifcopenshell.file, name: str = "Unnamed", purpose: Optional[str] = None
) -> ifcopenshell.entity_instance:
    """Adds a new load combination, in which load cases are combined with factors

    Load cases are assigned to it with a factor each using
    :func:`assign_structural_load_combination`.

    :param name: The name of the load combination
    :param purpose: The limit state the combination is for, such as SLS,
        ULS or ALS.
    :return: The new IfcStructuralLoadGroup

    Example:

    .. code:: python

        dead = ifcopenshell.api.structural.add_structural_load_case(model, name="Dead", action_type="PERMANENT_G")
        uls = ifcopenshell.api.structural.add_structural_load_combination(model, name="ULS 1", purpose="ULS")
        ifcopenshell.api.structural.assign_structural_load_combination(
            model, load_case=dead, load_combination=uls, factor=1.35
        )
    """
    load_combination = ifcopenshell.api.root.create_entity(
        file, ifc_class="IfcStructuralLoadGroup", predefined_type="LOAD_COMBINATION", name=name
    )
    load_combination.ActionType = "NOTDEFINED"
    load_combination.ActionSource = "NOTDEFINED"
    load_combination.Purpose = purpose
    return load_combination
