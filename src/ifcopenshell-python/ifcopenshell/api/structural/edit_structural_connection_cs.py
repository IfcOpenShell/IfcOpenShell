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
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"structural_item": None, "axis": [0.0, 0.0, 1.0], "ref_direction": [1.0, 0.0, 0.0]}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["structural_item"].ConditionCoordinateSystem is None:
            point = self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
            ccs = self.file.createIfcAxis2Placement3D(point, None, None)
            self.settings["structural_item"].ConditionCoordinateSystem = ccs
            print(ccs)

        ccs = self.settings["structural_item"].ConditionCoordinateSystem
        print("use case")
        print(ccs)
        if ccs.Axis and len(self.file.get_inverse(ccs.Axis)) == 1:
            self.file.remove(ccs.Axis)
        ccs.Axis = self.file.createIfcDirection(self.settings["axis"])
        if ccs.RefDirection and len(self.file.get_inverse(ccs.RefDirection)) == 1:
            self.file.remove(ccs.RefDirection)
        ccs.RefDirection = self.file.createIfcDirection(self.settings["ref_direction"])
