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


class Usecase:
    def __init__(self, file, structural_item=None, axis=None, ref_direction=None):
        """Edits the coordinate system of a structural connection

        :param structural_item: The IfcStructuralItem you want to modify.
        :type structural_item: ifcopenshell.entity_instance.entity_instance
        :param axis: The unit Z axis vector defined as a list of 3 floats.
            Defaults to [0., 0., 1.].
        :type axis: list[float]
        :param ref_direction: The unit X axis vector defined as a list of 3
            floats. Defaults to [1., 0., 0.].
        :type ref_direction: list[float]
        :return: None
        :rtype: None
        """
        self.file = file
        self.settings = {
            "structural_item": structural_item,
            "axis": axis or [0.0, 0.0, 1.0],
            "ref_direction": ref_direction or [1.0, 0.0, 0.0],
        }

    def execute(self):
        if self.settings["structural_item"].ConditionCoordinateSystem is None:
            point = self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
            ccs = self.file.createIfcAxis2Placement3D(point, None, None)
            self.settings["structural_item"].ConditionCoordinateSystem = ccs

        ccs = self.settings["structural_item"].ConditionCoordinateSystem
        if ccs.Axis and len(self.file.get_inverse(ccs.Axis)) == 1:
            self.file.remove(ccs.Axis)
        ccs.Axis = self.file.createIfcDirection(self.settings["axis"])
        if ccs.RefDirection and len(self.file.get_inverse(ccs.RefDirection)) == 1:
            self.file.remove(ccs.RefDirection)
        ccs.RefDirection = self.file.createIfcDirection(self.settings["ref_direction"])
