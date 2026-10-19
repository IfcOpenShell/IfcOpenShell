@boundary
Feature: Boundary

Scenario: Add boundary from space
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the cursor is at "1.1,0,0"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall.001" is selected
    And I press "bim.hotkey(hotkey='S_R')"
    And the cursor is at "0,.9,0"
    And I press "bim.add_occurrence"
    And the cursor is at "-1,0,0"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall.003" is selected
    And I press "bim.hotkey(hotkey='S_R')"
    And the object "IfcWall/Wall.003" is moved to "0,0,0"
    And the cursor is at "0.5,0.5,0"
    And I deselect all objects
    And I press "bim.generate_space"
    And I look at the "Spatial Decomposition" panel
    And I set the "is_visible" property to "TRUE"
    When I select the object "IfcSpace/Space"
    And I press "bim.add_boundary"
    Then the object "IfcRelSpaceBoundary/None" exists
    And the object "IfcRelSpaceBoundary/None.001" exists
    And the object "IfcRelSpaceBoundary/None.002" exists
    And the object "IfcRelSpaceBoundary/None.003" exists

Scenario: Add boundary from space with a standalone window
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the cursor is at "1.1,0,0"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall.001" is selected
    And I press "bim.hotkey(hotkey='S_R')"
    And the cursor is at "0,.9,0"
    And I press "bim.add_occurrence"
    And the cursor is at "-1,0,0"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall.003" is selected
    And I press "bim.hotkey(hotkey='S_R')"
    And the object "IfcWall/Wall.003" is moved to "0,0,0"
    And the cursor is at "0.5,0.5,0"
    And I deselect all objects
    And I press "bim.generate_space"
    And I look at the "Spatial Decomposition" panel
    And I set the "is_visible" property to "TRUE"
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWindowType"
    And the variable "window_type" is "[e for e in {ifc}.by_type('IfcWindowType') if e.Name == 'WT01'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{window_type}"
    And the cursor is at "0.5,0.1,0.8"
    And I press "bim.add_occurrence"
    And I deselect all objects
    When I select the object "IfcSpace/Space"
    And I press "bim.add_boundary"
    And the variable "classes" is "sorted(b.RelatedBuildingElement.is_a() for b in {ifc}.by_type('IfcRelSpaceBoundary'))"
    Then the variable "classes" equals "['IfcWall', 'IfcWall', 'IfcWall', 'IfcWall', 'IfcWindow']"
