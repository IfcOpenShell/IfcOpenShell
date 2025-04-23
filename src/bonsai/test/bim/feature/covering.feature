@covering
Feature: Covering
    Covers covering tool.

Scenario: Execute generate flooring coverings from walls
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    # 1st wall
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And I press "bim.change_layer_length(length=3.6)"
    # 2nd wall
    And the cursor is at "3.6,0.1,3"
    And I set "scene.BIMModelProperties.length" to "2.0"
    And I press "bim.add_occurrence"
    # 3rd wall
    And the cursor is at "3.5,2.1,3"
    And I set "scene.BIMModelProperties.length" to "3.5"
    And I press "bim.add_occurrence"
    # 4th wall
    And the cursor is at "0,2.0,0"
    And I set "scene.BIMModelProperties.length" to "1.9"
    And I press "bim.add_occurrence"
    # add_instance_flooring_coverings_from_walls is expecting FLOORING predefined type.
    And the object "IfcCoveringType/COV30" is selected
    And I look at the "Attributes" panel
    And I click "Edit"
    And I set the "PredefinedType" property to "FLOORING"
    And I click "Save Attributes"
    # Run the operator.
    When the object "IfcWall/Wall" is selected
    And additionally the object "IfcWall/Wall.001" is selected
    And additionally the object "IfcWall/Wall.002" is selected
    And additionally the object "IfcWall/Wall.003" is selected
    And I set "scene.BIMModelProperties.ifc_class" to "IfcCoveringType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcCoveringType') if e.Name == 'COV30'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_instance_flooring_coverings_from_walls"
    Then the object "IfcCovering/Covering0" exists
    And the object "IfcCovering/Covering0" is at "1.8,1.05,0.0"
    And the object "IfcCovering/Covering0" dimensions are "3.4,1.9,0.03"
