# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api.owner
import ifcopenshell.guid


def assign_to_building(
    file: ifcopenshell.file,
    structural_analysis_model: ifcopenshell.entity_instance,
    building: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance:
    """Associates a structural analysis model with a building via IfcRelServicesBuildings

    The existing :func:`assign_structural_analysis_model` handles
    IfcRelAssignsToGroup (linking structural members to the analysis model).
    This function handles the separate model-to-building relationship, which
    records which building the structural analysis model serves.

    :param structural_analysis_model: The IfcStructuralAnalysisModel to
        associate with the building.
    :param building: The IfcBuilding (or other IfcSpatialStructureElement)
        that the structural analysis model serves.
    :return: The IfcRelServicesBuildings relationship.

    Example:

    .. code:: python

        building = ifcopenshell.util.selector.filter_elements(model, "IfcBuilding")[0]
        model_ = ifcopenshell.api.structural.add_structural_analysis_model(model)
        ifcopenshell.api.structural.assign_to_building(model,
            structural_analysis_model=model_, building=building)
    """
    for rel in structural_analysis_model.ServicesBuildings or []:
        if building in rel.RelatedBuildings:
            return rel
        rel.RelatedBuildings = list(rel.RelatedBuildings) + [building]
        return rel

    return file.create_entity(
        "IfcRelServicesBuildings",
        ifcopenshell.guid.new(),
        OwnerHistory=ifcopenshell.api.owner.create_owner_history(file),
        RelatingSystem=structural_analysis_model,
        RelatedBuildings=[building],
    )
