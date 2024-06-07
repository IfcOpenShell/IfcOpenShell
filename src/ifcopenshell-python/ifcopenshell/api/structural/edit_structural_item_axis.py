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


def edit_structural_item_axis(
    file: ifcopenshell.file,
    structural_item: ifcopenshell.entity_instance,
    axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
) -> None:
    """Edits the coordinate system of a structural connection

    :param structural_item: The IfcStructuralItem you want to modify.
    :type structural_item: ifcopenshell.entity_instance
    :param axis: The unit Z axis vector defined as a list of 3 floats.
        Defaults to (0., 0., 1.).
    :type axis: tuple[float, float, float]
    :return: None
    :rtype: None
    """
    settings = {"structural_item": structural_item, "axis": axis}

    if len(file.get_inverse(settings["structural_item"].Axis)) == 1:
        file.remove(settings["structural_item"].Axis)
    settings["structural_item"].Axis = file.createIfcDirection(settings["axis"])
