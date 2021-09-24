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


class TestAddOpening(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_adding_an_opening(self):
        return """
        Given an empty IFC project
        Given I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        And I add a cube
        And the object "IfcWall/Cube" is selected
        And additionally the object "Cube" is selected
        And I press "bim.add_opening(opening='Cube', obj='IfcWall/Cube')"
        Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
        And the object "IfcOpeningElement/Cube" should display as "WIRE"
        And the object "IfcWall/Cube" has a boolean difference by "IfcOpeningElement/Cube"
        And the object "IfcWall/Cube" is voided by "Cube"
        """


class TestRemoveOpening(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_removing_an_opening_manually(self):
        return """
        Given an empty IFC project
        Given I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        And I add a cube of size "1" at "1,0,0"
        And the object "IfcWall/Cube" is selected
        And additionally the object "Cube" is selected
        And I press "bim.add_opening(opening='Cube', obj='IfcWall/Cube')"
        And I press "bim.remove_opening(opening_id=97, obj='IfcWall/Cube')"
        Then the object "IfcWall/Cube" has no boolean difference by "IfcOpeningElement/Cube"
        And the object "IfcWall/Cube" is not voided by "Cube"
        And the object "Cube" is not an IFC element
        """

    @test.bim.bootstrap.scenario
    def test_removing_a_non_dynamic_opening_manually(self):
        return """
        Given an empty IFC project
        Given I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        And I add a cube of size "1" at "1,0,0"
        And the object "IfcWall/Cube" is selected
        And additionally the object "Cube" is selected
        And I press "bim.add_opening(opening='Cube', obj='IfcWall/Cube')"
        And the object "IfcWall/Cube" is selected
        And I press "bim.switch_representation(ifc_definition_id=86, should_reload=True)"
        Then the object "IfcWall/Cube" has no boolean difference by "IfcOpeningElement/Cube"
        And the object "IfcWall/Cube" has "16" vertices
        When I press "bim.remove_opening(opening_id=97, obj='IfcWall/Cube')"
        Then the object "IfcWall/Cube" has "8" vertices
        And the object "Cube" is not an IFC element
        """

    @test.bim.bootstrap.scenario
    def test_removing_an_opening_using_deletion(self):
        return """
        Given an empty IFC project
        Given I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        And I add a cube of size "1" at "1,0,0"
        And the object "IfcWall/Cube" is selected
        And additionally the object "Cube" is selected
        And I press "bim.add_opening(opening='Cube', obj='IfcWall/Cube')"
        And the object "IfcOpeningElement/Cube" is selected
        And I delete the selected objects
        Then the object "IfcWall/Cube" has no boolean difference by "IfcOpeningElement/Cube"
        And the object "IfcWall/Cube" is not voided by "Cube"
        """

    @test.bim.bootstrap.scenario
    def test_removing_an_opening_indirectly_by_deleting_its_building_element(self):
        return """
        Given an empty IFC project
        Given I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        And I add a cube of size "1" at "1,0,0"
        And the object "IfcWall/Cube" is selected
        And additionally the object "Cube" is selected
        And I press "bim.add_opening(opening='Cube', obj='IfcWall/Cube')"
        And the object "IfcWall/Cube" is selected
        And I delete the selected objects
        Then the object "Cube" is not an IFC element
        """


class TestAddFilling(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_adding_a_filling(self):
        return """
        Given an empty IFC project
        Given I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
        And I press "bim.assign_class"
        And I add a cube
        And the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
        And I press "bim.assign_class"
        And the object "IfcOpeningElement/Cube" is selected
        And I press "bim.add_filling(opening='IfcOpeningElement/Cube', obj='IfcDoor/Cube')"
        Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
        And the object "IfcOpeningElement/Cube" should display as "WIRE"
        And the object "IfcDoor/Cube" is an "IfcDoor"
        And the void "IfcOpeningElement/Cube" is filled by "Cube"
        """


class TestRemoveFilling(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_adding_a_filling(self):
        return """
        Given an empty IFC project
        Given I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
        And I press "bim.assign_class"
        And I add a cube
        And the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
        And I press "bim.assign_class"
        And I press "bim.add_filling(opening='IfcOpeningElement/Cube', obj='IfcDoor/Cube')"
        And I press "bim.remove_filling(obj='IfcDoor/Cube')"
        Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
        And the object "IfcDoor/Cube" is an "IfcDoor"
        And the void "IfcOpeningElement/Cube" is not filled by "Cube"
        """
