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
        And I add a cube
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

    @test.bim.bootstrap.scenario
    def test_adding_an_opening_on_an_opening(self):
        """An opening can't legally be voided by another opening"""
        return """
        Given an empty IFC project
        And I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
        And I press "bim.assign_class"
        And I add a cube
        And the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
        And I press "bim.assign_class"
        And the object "IfcOpeningElement/Cube" is selected
        And additionally the object "IfcOpeningElement/Cube.001" is selected
        And I press "bim.add_opening(opening='IfcOpeningElement/Cube', obj='IfcOpeningElement/Cube.001')"
        Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
        And the object "IfcOpeningElement/Cube" should display as "WIRE"
        And the object "IfcOpeningElement/Cube" is not a void
        Then the object "IfcOpeningElement/Cube.001" is an "IfcOpeningElement"
        And the object "IfcOpeningElement/Cube.001" should display as "WIRE"
        Then the object "IfcOpeningElement/Cube.001" has no boolean difference by "IfcOpeningElement/Cube"
        And the object "IfcOpeningElement/Cube.001" is not voided by "Cube"
        """

    @test.bim.bootstrap.scenario
    def test_adding_an_opening_on_a_null_object(self):
        return """
        Given an empty IFC project
        And I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
        And I press "bim.assign_class"
        And I deselect all objects
        And I press "bim.add_opening(opening='IfcOpeningElement/Cube')"
        Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
        And the object "IfcOpeningElement/Cube" should display as "WIRE"
        And the object "IfcOpeningElement/Cube" is not a void
        """

    @test.bim.bootstrap.scenario
    def test_adding_an_opening_on_a_non_ifc_object(self):
        return """
        Given an empty IFC project
        And I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
        And I press "bim.assign_class"
        And I add a cube
        And the object "Cube" is selected
        And I press "bim.add_opening(opening='IfcOpeningElement/Cube', obj='Cube')"
        Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
        And the object "IfcOpeningElement/Cube" should display as "WIRE"
        And the object "IfcOpeningElement/Cube" is not a void
        And the object "Cube" is not an IFC element
        """

    @test.bim.bootstrap.scenario
    def test_adding_an_opening_with_a_null_object(self):
        return """
        Given an empty IFC project
        And I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        And I deselect all objects
        And I press "bim.add_opening(obj='IfcWall/Cube')"
        Then the object "IfcWall/Cube" is an "IfcWall"
        And the object "IfcWall/Cube" is not voided
        """

    @test.bim.bootstrap.scenario
    def test_adding_an_opening_to_element_b_with_a_void_that_already_voids_element_a(self):
        """An opening can legally void at most one element"""
        return """
        Given an empty IFC project
        And I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        And I add a cube
        And I press "bim.add_opening(opening='Cube', obj='IfcWall/Cube')"
        And I add a cube
        And the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        And I press "bim.add_opening(opening='IfcOpeningElement/Cube', obj='IfcWall/Cube.001')"
        Then the object "IfcWall/Cube" is not voided
        And the object "IfcWall/Cube" has no boolean difference by "IfcOpeningElement/Cube"  
        And the object "IfcWall/Cube.001" is voided by "Cube"
        And the object "IfcWall/Cube.001" has a boolean difference by "IfcOpeningElement/Cube"  
        """


class TestRemoveOpening(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_removing_an_opening_manually(self):
        return """
        Given an empty IFC project
        And I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        And I add a cube of size "1" at "1,0,0"
        And the object "Cube" is selected
        And additionally the object "IfcWall/Cube" is selected
        And I press "bim.add_opening(opening='Cube', obj='IfcWall/Cube')"
        And the variable "opening_id" is "IfcStore.get_file().by_type('IfcOpeningElement')[0].id()"
        And I press "bim.remove_opening(opening_id={opening_id}, obj='IfcWall/Cube')"
        Then the object "IfcWall/Cube" has no boolean difference by "IfcOpeningElement/Cube"
        And the object "IfcWall/Cube" is not voided by "Cube"
        And the object "Cube" is not an IFC element
        """

    @test.bim.bootstrap.scenario
    def test_removing_a_non_dynamic_opening_manually(self):
        return """
        Given an empty IFC project
        And I add a cube
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
        And the variable "opening_id" is "IfcStore.get_file().by_type('IfcOpeningElement')[0].id()"
        When I press "bim.remove_opening(opening_id={opening_id}, obj='IfcWall/Cube')"
        Then the object "IfcWall/Cube" has "8" vertices
        And the object "Cube" is not an IFC element
        """

    @test.bim.bootstrap.scenario
    def test_removing_an_opening_using_deletion(self):
        return """
        Given an empty IFC project
        And I add a cube
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
        And I add a cube
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
        And I add a cube
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

    @test.bim.bootstrap.scenario
    def test_adding_a_filling_on_null_object(self):
        return """
        Given an empty IFC project
        And I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
        And I press "bim.assign_class"
        And the object "IfcDoor/Cube" is selected
        And I press "bim.add_filling(obj='IfcDoor/Cube')"
        Then the object "IfcDoor/Cube" is an "IfcDoor"
        And the object "IfcDoor/Cube" is not a filling
        """

    @test.bim.bootstrap.scenario
    def test_adding_a_filling_on_itself(self):
        return """
        Given an empty IFC project
        And I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
        And I press "bim.assign_class"
        And the object "IfcOpeningElement/Cube" is selected
        And I press "bim.add_filling(opening='IfcOpeningElement/Cube', obj='IfcOpeningElement/Cube')"
        Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
        And the void "IfcOpeningElement/Cube" is not filled by "Cube"
        And the object "IfcOpeningElement/Cube" is not a filling
        """

    @test.bim.bootstrap.scenario
    def test_adding_a_filling_with_a_non_ifc_object(self):
        return """
        Given an empty IFC project
        And I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
        And I press "bim.assign_class"
        And I add a cube
        And the object "IfcOpeningElement/Cube" is selected
        And I press "bim.add_filling(opening='IfcOpeningElement/Cube', obj='Cube')"
        Then the object "Cube" is not an IFC element
        And the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
        And the void "IfcOpeningElement/Cube" is not filled by "Cube"
        """

    @test.bim.bootstrap.scenario
    def test_adding_a_filling_on_a_non_ifc_object(self):
        return """
        Given an empty IFC project
        And I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
        And I press "bim.assign_class"
        And I add a cube
        And the object "Cube" is selected
        And I press "bim.add_filling(opening='Cube', obj='IfcDoor/Cube')"
        Then the object "Cube" is not an IFC element
        And the object "IfcDoor/Cube" is an "IfcDoor"
        """

    @test.bim.bootstrap.scenario
    def test_adding_a_filling_on_opening_b_when_the_filling_alread_fills_element_a(self):
        return """
        Given an empty IFC project
        And I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
        And I press "bim.assign_class"
        And I add a cube
        And the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
        And I press "bim.assign_class"
        And I press "bim.add_filling(opening='IfcOpeningElement/Cube', obj='IfcDoor/Cube')"
        And I add a cube
        And the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
        And I press "bim.assign_class"
        And I press "bim.add_filling(opening='IfcOpeningElement/Cube.001', obj='IfcDoor/Cube')"
        Then the void "IfcOpeningElement/Cube" is not filled by "Cube"
        And the void "IfcOpeningElement/Cube.001" is filled by "Cube"
        """


class TestRemoveFilling(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_removing_a_filling(self):
        return """
        Given an empty IFC project
        And I add a cube
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

    @test.bim.bootstrap.scenario
    def test_removing_a_filling_which_is_not_an_ifc_object(self):
        return """
        Given an empty IFC project
        And I add a cube
        When the object "Cube" is selected
        And I press "bim.remove_filling(obj='Cube')"
        Then the object "Cube" is not an IFC element
        """

    @test.bim.bootstrap.scenario
    def test_removing_a_filling_which_is_not_a_filling(self):
        return """
        Given an empty IFC project
        And I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
        And I press "bim.assign_class"
        And I press "bim.remove_filling(obj='IfcDoor/Cube')"
        Then the object "IfcDoor/Cube" is an "IfcDoor"
        And the object "IfcDoor/Cube" is not a filling
        """

    @test.bim.bootstrap.scenario
    def test_removing_a_filling_which_is_null(self):
        return """
        Given an empty IFC project
        And I press "bim.remove_filling()"
        Then nothing interesting happens
        """

    @test.bim.bootstrap.scenario
    def test_removing_a_filling_using_deletion_on_the_filling(self):
        return """
        Given an empty IFC project
        And I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
        And I press "bim.assign_class"
        And I add a cube
        And the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
        And I press "bim.assign_class"
        And I press "bim.add_filling(opening='IfcOpeningElement/Cube', obj='IfcDoor/Cube')"
        And the object "IfcDoor/Cube" is selected
        And I delete the selected objects
        Then the object "IfcOpeningElement/Cube" is an "IfcOpeningElement"
        And the void "IfcOpeningElement/Cube" is not filled by "Cube"
        """

    @test.bim.bootstrap.scenario
    def test_removing_a_filling_using_deletion_on_the_opening(self):
        return """
        Given an empty IFC project
        And I add a cube
        When the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcOpeningElement"
        And I press "bim.assign_class"
        And I add a cube
        And the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcDoor"
        And I press "bim.assign_class"
        And I press "bim.add_filling(opening='IfcOpeningElement/Cube', obj='IfcDoor/Cube')"
        And the object "IfcOpeningElement/Cube" is selected
        And I delete the selected objects
        Then the object "IfcDoor/Cube" is an "IfcDoor"
        And the object "IfcDoor/Cube" is not a filling
        """
