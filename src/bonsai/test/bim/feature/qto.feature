@qto
Feature: Qto

Scenario: Calculate circle radius
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Simple Quantity Calculator" panel
    When I click "Calculate Circle Radius"
    Then I see the "Results" property is "1.732"

Scenario: Calculate edge lengths
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Simple Quantity Calculator" panel
    When I click "Calculate Edge Lengths"
    Then I see the "Results" property is "24.0"

Scenario: Calculate face areas
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Simple Quantity Calculator" panel
    When I click "Calculate Face Areas"
    Then I see the "Results" property is "24.0"

Scenario: Calculate object volumes
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Simple Quantity Calculator" panel
    When I click "Calculate Object Volumes"
    Then I see the "Results" property is "8.0"

Scenario: Execute qto method - formwork areas
    Given an empty Blender session
    And I add a cube
    And I add a cube of size "1" at "1,0,0"
    And the object "Cube" is selected
    And additionally the object "Cube.001" is selected
    When I press "bim.calculate_formwork_area"
    Then "scene.BIMQtoProperties.qto_result" is "21.5"

Scenario: Execute qto method - side formwork areas
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.calculate_side_formwork_area"
    Then "scene.BIMQtoProperties.qto_result" is "16.0"

Scenario: Perform quantity take-off - no objects
    Given an empty IFC project
    When I look at the "Quantity Take-off" panel
    Then I see "Quantifying All Objects"
    When I click "Perform Quantity Take-off"
    Then nothing happens

Scenario: Perform quantity take-off
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And I look at the "Quantity Take-off" panel
    When I see "Quantifying 1 Selected Objects"
    And I click "Perform Quantity Take-off"
    When I look at the "Quantity Sets" panel
    Then I see "Qto_WallBaseQuantities"
    And I see "NetVolume"

Scenario: Perform quantity take-off - using Blender engine
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And I look at the "Quantity Take-off" panel
    When I set the "qto_rule" property to "IFC4 Base Quantities - Blender"
    And I see "Quantifying 1 Selected Objects"
    And I click "Perform Quantity Take-off"
    When I look at the "Quantity Sets" panel
    Then I see "Qto_WallBaseQuantities"
    And I see "NetVolume"

Scenario: Manual quantification
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And I look at the "Manual Quantification" panel
    When I set the "qto_name" property to "Foo"
    And I set the "prop_name" property to "Bar"
    And I click "Calculate Single Quantity"
    When I look at the "Quantity Sets" panel
    Then I see "Foo"
    And I see "Bar"

Scenario: Manual quantification - set an engine and function
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And I look at the "Manual Quantification" panel
    And I set the "Calculator" property to "IfcOpenShell"
    And I set the "Function" property to "Volume: Net Volume"
    When I set the "qto_name" property to "Foo"
    And I set the "prop_name" property to "Bar"
    And I click "Calculate Single Quantity"
    When I look at the "Quantity Sets" panel
    Then I see "Foo"
    And I see "Bar"
