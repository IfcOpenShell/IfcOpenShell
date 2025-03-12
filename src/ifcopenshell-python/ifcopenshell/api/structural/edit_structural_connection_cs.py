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
from ifcopenshell.util.shape_builder import VectorType, ifc_safe_vector_type


def edit_structural_connection_cs(
    file: ifcopenshell.file,
    structural_item: ifcopenshell.entity_instance,
    axis: VectorType = (0.0, 0.0, 1.0),
    ref_direction: VectorType = (1.0, 0.0, 0.0),
) -> None:
    """Edits the coordinate system of a structural connection

    :param structural_item: The IfcStructuralItem you want to modify.
    :param axis: The unit Z axis vector defined as a list of 3 floats.
        Defaults to (0., 0., 1.).
    :param ref_direction: The unit X axis vector defined as a list of 3
        floats. Defaults to (1., 0., 0.).
    :return: None
    """
    if structural_item.ConditionCoordinateSystem is None:
        point = file.createIfcCartesianPoint((0.0, 0.0, 0.0))
        ccs = file.createIfcAxis2Placement3D(point, None, None)
        structural_item.ConditionCoordinateSystem = ccs

    ccs = structural_item.ConditionCoordinateSystem
    if (current_axis := ccs.Axis) and file.get_total_inverses(current_axis) == 1:
        file.remove(current_axis)
    ccs.Axis = file.create_entity("IfcDirection", ifc_safe_vector_type(axis))
    if (prev_ref_direction := ccs.RefDirection) and file.get_total_inverses(prev_ref_direction) == 1:
        file.remove(prev_ref_direction)
    ccs.RefDirection = file.create_entity("IfcDirection", ifc_safe_vector_type(ref_direction))
