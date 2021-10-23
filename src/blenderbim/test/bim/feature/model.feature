@model
Feature: Model

Scenario: Add type instance - add from a mesh
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I set "scene.BIMTypeProperties.ifc_class" to "IfcWallType"
    And the variable "cube" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I set "scene.BIMTypeProperties.relating_type" to "{cube}"
    When I press "bim.add_type_instance"
    Then the object "IfcWall/Instance" exists

Scenario: Add type instance - add from an empty
    Given an empty IFC project
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    And I set "scene.BIMTypeProperties.ifc_class" to "IfcWallType"
    And the variable "empty" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I set "scene.BIMTypeProperties.relating_type" to "{empty}"
    When I press "bim.add_type_instance"
    Then the object "IfcWall/Instance" exists

Scenario: Add grid
    Given an empty IFC project
    When I press "mesh.add_grid"
    Then the object "IfcGrid/Grid" is an "IfcGrid"
    And the object "IfcGridAxis/A" is an "IfcGridAxis"
    And the object "IfcGridAxis/B" is an "IfcGridAxis"
    And the object "IfcGridAxis/C" is an "IfcGridAxis"
    And the object "IfcGridAxis/01" is an "IfcGridAxis"
    And the object "IfcGridAxis/02" is an "IfcGridAxis"
    And the object "IfcGridAxis/03" is an "IfcGridAxis"
