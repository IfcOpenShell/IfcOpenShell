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


def edit_structural_analysis_model(
    file: ifcopenshell.file, structural_analysis_model: ifcopenshell.entity_instance, attributes: dict[str, Any]
) -> None:
    """Edits the attributes of an IfcStructuralAnalysisModel

    For more information about the attributes and data types of an
    IfcStructuralAnalysisModel, consult the IFC documentation.

    :param structural_analysis_model: The IfcStructuralAnalysisModel entity you want to edit
    :param attributes: a dictionary of attribute names and values.
    :return: None
    """
    for name, value in attributes.items():
        setattr(structural_analysis_model, name, value)
