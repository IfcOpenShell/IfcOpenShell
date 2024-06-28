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
import ifcopenshell.api.root


def add_structural_analysis_model(file: ifcopenshell.file) -> ifcopenshell.entity_instance:
    """Add a new structural analysis model

    A structural analysis model is a group of all the loads, reactions,
    structural members, and structural connections required to describe a
    structural analysis model.

    A 3D analytical model is assumed.

    :return: The newly created IfcStructuralAnalysisModel
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # Create a fresh blank structural analysis
        analysis = ifcopenshell.api.structural.add_structural_analysis_model(model)
    """
    return ifcopenshell.api.root.create_entity(
        file, ifc_class="IfcStructuralAnalysisModel", predefined_type="LOADING_3D"
    )
