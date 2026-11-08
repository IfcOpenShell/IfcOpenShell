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
import ifcopenshell.util.element


def unassign_from_building(
    file: ifcopenshell.file,
    structural_analysis_model: ifcopenshell.entity_instance,
    building: ifcopenshell.entity_instance,
) -> None:
    """Removes the association between a structural analysis model and a building

    This undoes :func:`assign_to_building`. If the building was the last one
    the model serves, the IfcRelServicesBuildings relationship is removed.
    If the model does not serve the building, nothing happens.

    :param structural_analysis_model: The IfcStructuralAnalysisModel serving
        the building.
    :param building: The IfcBuilding (or other IfcSpatialStructureElement)
        to stop serving.
    :return: None

    Example:

    .. code:: python

        building = ifcopenshell.util.selector.filter_elements(model, "IfcBuilding")[0]
        model_ = ifcopenshell.api.structural.add_structural_analysis_model(model)
        ifcopenshell.api.structural.assign_to_building(model,
            structural_analysis_model=model_, building=building)
        ifcopenshell.api.structural.unassign_from_building(model,
            structural_analysis_model=model_, building=building)
    """
    for rel in structural_analysis_model.ServicesBuildings or []:
        if building not in rel.RelatedBuildings:
            continue
        related_buildings = [b for b in rel.RelatedBuildings if b != building]
        if related_buildings:
            rel.RelatedBuildings = related_buildings
            ifcopenshell.api.owner.update_owner_history(file, element=rel)
        else:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
