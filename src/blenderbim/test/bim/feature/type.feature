@type
Feature: Type

Scenario: Assign type
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElementType"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWallType"
    And I press "bim.assign_class"
    When the variable "type" is "{ifc}.by_type('IfcWallType')[0].id()"
    And I press "bim.assign_type(relating_type={type}, related_object="IfcWall/Cube")"
    Then nothing happens
