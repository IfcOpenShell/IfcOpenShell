# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Ryan Schultz
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

import ifcopenshell


def unassign_structural_load_group(
    file: ifcopenshell.file,
    load_groups: list[ifcopenshell.entity_instance],
    structural_analysis_model: ifcopenshell.entity_instance,
) -> None:
    """Unassigns load groups or load cases from an analysis model

    LoadedBy is reset to unset when its last load group is removed, as the
    schema does not allow an empty set.

    :param load_groups: The IfcStructuralLoadGroups (including
        IfcStructuralLoadCases) to unassign.
    :param structural_analysis_model: The IfcStructuralAnalysisModel to
        unassign them from.
    :return: None

    Example:

    .. code:: python

        ifcopenshell.api.structural.unassign_structural_load_group(
            model, load_groups=[dead], structural_analysis_model=model)
    """
    loaded_by = [g for g in structural_analysis_model.LoadedBy or [] if g not in load_groups]
    structural_analysis_model.LoadedBy = loaded_by or None
