@misc
Feature: Misc

Scenario: Set override colour
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.set_override_colour"
    Then nothing happens

Scenario: Snap spaces together
    Given an empty Blender session
    And I add a cube
    And I add a cube
    And the object "Cube" is selected
    And additionally the object "Cube.001" is selected
    When I press "bim.snap_spaces_together"
    Then nothing happens

Scenario: Resize to storey
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And the object "IfcWall/Cube" is selected
    And I look at the "Spatial Decomposition" panel
    And I select the "My Storey" item in the "BIM_UL_containers_manager" list
    And I click "Set Default"
    # Assign Container.
    And I click "FOLDER_REDIRECT"
    And I look at the "Miscellaneous" panel
    When I click "Resize To Storey"
    Then nothing happens

Scenario: Split along edge - boolean mode
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And I add a plane of size "4" at "0,0,0"
    And the object "IfcWall/Cube" is selected
    And additionally the object "Plane" is selected
    And I look at the "Miscellaneous" panel
    When I click "Split Along Edge"
    Then the object "IfcWall/Cube" is an "IfcWall"
    And the object "IfcWall/Cube.001" is an "IfcWall"

Scenario: Split along edge - bisect mode
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And I add a plane of size "4" at "0,0,0"
    And the object "IfcWall/Cube" is selected
    And additionally the object "Plane" is selected
    And I look at the "Miscellaneous" panel
    When I click "Bisect At Faces"
    Then the object "IfcWall/Cube" is an "IfcWall"
    And the object "IfcWall/Cube.001" is an "IfcWall"


