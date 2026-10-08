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


def assign_structural_load_group(
    file: ifcopenshell.file,
    load_groups: list[ifcopenshell.entity_instance],
    structural_analysis_model: ifcopenshell.entity_instance,
) -> None:
    """Assigns load groups or load cases to the analysis model they load

    The analysis model lists the load groups it is subjected to in its
    LoadedBy attribute. Load groups already assigned are skipped.

    :param load_groups: The IfcStructuralLoadGroups (including
        IfcStructuralLoadCases) to assign.
    :param structural_analysis_model: The IfcStructuralAnalysisModel loaded
        by the load groups.
    :return: None

    Example:

    .. code:: python

        model = ifcopenshell.api.structural.add_structural_analysis_model(model)
        dead = ifcopenshell.api.structural.add_structural_load_case(model, name="Dead")
        ifcopenshell.api.structural.assign_structural_load_group(
            model, load_groups=[dead], structural_analysis_model=model)
    """
    loaded_by = list(structural_analysis_model.LoadedBy or [])
    loaded_by.extend(g for g in load_groups if g not in loaded_by)
    structural_analysis_model.LoadedBy = loaded_by or None
