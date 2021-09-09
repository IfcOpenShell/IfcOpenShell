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
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        Then the object "IfcWall/Cube" is an "IfcWall"
        And the object "IfcWall/Cube" is in the collection "Collection"
        And the object "IfcWall/Cube" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"
        """

    @test.bim.bootstrap.scenario
    def test_assigning_a_type_class_to_a_cube(self):
        return """
        Given an empty IFC project
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
        And I press "bim.assign_class"
        Then the object "IfcWallType/Cube" is an "IfcWallType"
        And the object "IfcWallType/Cube" is in the collection "Types"
        And the object "IfcWallType/Cube" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"
        """

    @test.bim.bootstrap.scenario
    def test_assigning_a_spatial_class_to_a_cube(self):
        return """
        Given an empty IFC project
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_product" to "IfcSpatialElement"
        And I set "scene.BIMRootProperties.ifc_class" to "IfcBuilding"
        And I press "bim.assign_class"
        Then the object "IfcBuilding/Cube" is an "IfcBuilding"
        And the object "IfcBuilding/Cube" is in the collection "IfcBuilding/Cube"
        And the object "IfcBuilding/Cube" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"
        """

    @test.bim.bootstrap.scenario
    def test_assigning_an_opening_class_to_a_cube(self):
        return """
        Given an empty IFC project
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
        And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
        And I press "bim.assign_class"
        Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
        And the object "IfcOpeningElement/Cube" should display as "WIRE"
        And the object "IfcOpeningElement/Cube" is in the collection "IfcOpeningElements"
        And the object "IfcOpeningElement/Cube" has a "Tessellation" representation of "Model/Body/MODEL_VIEW"
        """

    @test.bim.bootstrap.scenario
    def test_assigning_a_class_to_a_cube_in_a_collection(self):
        return """
        Given an empty IFC project
        When the object "Cube" is selected
        And the object "Cube" is placed in the collection "IfcBuildingStorey/My Storey"
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        Then the object "IfcWall/Cube" is contained in "My Storey"
        """


class TestCopyClass(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_copying_a_wall(self):
        return """
        Given an empty IFC project
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        And I duplicate the selected objects
        Then the object "IfcWall/Cube" and "IfcWall/Cube.001" are different elements
        """

    @test.bim.bootstrap.scenario
    def test_copying_a_storey(self):
        return """
        Given an empty IFC project
        And the object "IfcBuildingStorey/My Storey" is selected
        When I duplicate the selected objects
        Then the object "IfcBuildingStorey/My Storey" and "IfcBuildingStorey/My Storey.001" are different elements
        And the object "IfcBuildingStorey/My Storey" is in the collection "IfcBuildingStorey/My Storey"
        And the object "IfcBuildingStorey/My Storey.001" is in the collection "IfcBuildingStorey/My Storey.001"
        And the collection "IfcBuildingStorey/My Storey.001" is in the collection "IfcBuilding/My Building"
        """
