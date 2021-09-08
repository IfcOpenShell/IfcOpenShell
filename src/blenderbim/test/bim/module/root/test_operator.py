# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import test.bim.bootstrap


class TestAssignClass(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_assigning_a_class_to_a_cube(self):
        return """
        Given an empty IFC project
        When I add a cube
        And the object "Cube" is selected
        And I select "IfcWall" in "scene.BIMRootProperties.ifc_class"
        And I press "bim.assign_class"
        And the object "IfcWall/Cube" is an "IfcWall"
        """

    @test.bim.bootstrap.scenario
    def test_assigning_a_type_class_to_a_cube(self):
        return """
        Given an empty IFC project
        When I add a cube
        And the object "Cube" is selected
        And I select "IfcElementType" in "scene.BIMRootProperties.ifc_product"
        And I select "IfcWallType" in "scene.BIMRootProperties.ifc_class"
        And I press "bim.assign_class"
        And the object "IfcWallType/Cube" is an "IfcWallType"
        And the object "IfcWallType/Cube" is in the collection "Types"
        """
