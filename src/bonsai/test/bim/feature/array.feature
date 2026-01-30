@array
Feature: Array

Scenario: Add array
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    When the object "IfcColumn/Column" is selected
    And I look at the "Array" panel
    And I see "No Array Found"
    And I click "ADD"
    Then the object "IfcColumn/Column" exists
    And I see "Column"
    And I see "1 Items"
    And I don't see "No Array Found"
    And the object "IfcColumn/Column" is at "0,0,0"

Scenario: Enable editing array
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    And the object "IfcColumn/Column" is selected
    And I look at the "Array" panel
    And I click "ADD"
    When I click "GREASEPENCIL"
    Then I see "Count"
    And I see "Method"
    And I don't see "1 Items"

Scenario: Disable editing array
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    And the object "IfcColumn/Column" is selected
    And I look at the "Array" panel
    And I click "ADD"
    And I click "GREASEPENCIL"
    When I click "CANCEL"
    Then I see "1 Items"
    And I don't see "Count"

Scenario: Edit array
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    And the object "IfcColumn/Column" is selected
    And I look at the "Array" panel
    And I click "ADD"
    And I click "GREASEPENCIL"
    When I set the "Count" property to "2"
    And I click "CHECKMARK"
    Then the object "IfcColumn/Column.001" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcColumn/Column" is at "0,0,0"
    And the object "IfcColumn/Column.001" is at "0,0,0"
    And the object "IfcColumn/Column" dimensions are "0.5,0.6,3"

Scenario: Edit array - offset method
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    And the object "IfcColumn/Column" is selected
    And I look at the "Array" panel
    And I click "ADD"
    And I click "GREASEPENCIL"
    When I set the "Count" property to "3"
    And I set the "Method" property to "Offset"
    And I set the "X" property to "1"
    And I click "CHECKMARK"
    Then the object "IfcColumn/Column.001" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcColumn/Column.002" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcColumn/Column" is at "0,0,0"
    And the object "IfcColumn/Column.001" is at "1,0,0"
    And the object "IfcColumn/Column.002" is at "2,0,0"
    And the object "IfcColumn/Column" dimensions are "0.5,0.6,3"
    And the object "IfcColumn/Column.001" dimensions are "0.5,0.6,3"
    And the object "IfcColumn/Column.002" dimensions are "0.5,0.6,3"

Scenario: Edit array - distribute method
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    And the object "IfcColumn/Column" is selected
    And I look at the "Array" panel
    And I click "ADD"
    And I click "GREASEPENCIL"
    When I set the "Count" property to "3"
    And I set the "Method" property to "Distribute"
    And I set the "X" property to "2"
    And I click "CHECKMARK"
    Then the object "IfcColumn/Column.001" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcColumn/Column.002" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcColumn/Column" is at "0,0,0"
    And the object "IfcColumn/Column.001" is at "1,0,0"
    And the object "IfcColumn/Column.002" is at "2,0,0"
    And the object "IfcColumn/Column" dimensions are "0.5,0.6,3"
    And the object "IfcColumn/Column.001" dimensions are "0.5,0.6,3"
    And the object "IfcColumn/Column.002" dimensions are "0.5,0.6,3"

Scenario: Edit array - local space
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    And the object "IfcColumn/Column" is rotated by "0,0,90" deg
    And the object "IfcColumn/Column" is selected
    And I look at the "Array" panel
    And I click "ADD"
    And I click "GREASEPENCIL"
    When I set the "Count" property to "2"
    And I set the "Method" property to "Offset"
    And I set the "Use Local Space" property to "TRUE"
    And I set the "X" property to "1"
    And I click "CHECKMARK"
    Then the object "IfcColumn/Column" is at "0,0,0"
    And the object "IfcColumn/Column.001" is at "0,1,0"

Scenario: Edit array - world space
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    And the object "IfcColumn/Column" is rotated by "0,0,90" deg
    And the object "IfcColumn/Column" is selected
    And I look at the "Array" panel
    And I click "ADD"
    And I click "GREASEPENCIL"
    When I set the "Count" property to "2"
    And I set the "Method" property to "Offset"
    And I set the "Use Local Space" property to "FALSE"
    And I set the "X" property to "1"
    And I click "CHECKMARK"
    Then the object "IfcColumn/Column" is at "0,0,0"
    And the object "IfcColumn/Column.001" is at "1,0,0"

Scenario: Edit array - decrease count
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    And the object "IfcColumn/Column" is selected
    And I look at the "Array" panel
    And I click "ADD"
    And I click "GREASEPENCIL"
    When I set the "Count" property to "3"
    And I click "CHECKMARK"
    And I click "GREASEPENCIL"
    When I set the "Count" property to "2"
    And I click "CHECKMARK"
    Then the object "IfcColumn/Column.001" exists
    And the object "IfcColumn/Column.002" does not exist

Scenario: Edit array - multiple arrays
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    And the object "IfcColumn/Column" is selected
    And I look at the "Array" panel
    And I click "ADD"
    And I click "GREASEPENCIL"
    When I set the "Count" property to "3"
    And I set the "Method" property to "Offset"
    And I set the "X" property to "1"
    And I click "CHECKMARK"
    And I see "3 Items"
    And I click "ADD"
    And I click the "GREASEPENCIL" after the text "1 Items (Offset)"
    And I set the "Count" property to "2"
    And I set the "Method" property to "Offset"
    And I set the "Y" property to "1"
    And I click the "CHECKMARK" after the text "Count"
    Then I see "3 Items"
    And I see "2 Items"
    Then the object "IfcColumn/Column.001" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcColumn/Column.002" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcColumn/Column.003" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcColumn/Column.004" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcColumn/Column.005" is in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcColumn/Column" is at "0,0,0"
    And the object "IfcColumn/Column.001" is at "1,0,0"
    And the object "IfcColumn/Column.002" is at "2,0,0"
    And the object "IfcColumn/Column.003" is at "0,1,0"
    And the object "IfcColumn/Column.004" is at "1,1,0"
    And the object "IfcColumn/Column.005" is at "2,1,0"
    And the object "IfcColumn/Column" dimensions are "0.5,0.6,3"
    And the object "IfcColumn/Column.001" dimensions are "0.5,0.6,3"
    And the object "IfcColumn/Column.002" dimensions are "0.5,0.6,3"
    And the object "IfcColumn/Column.003" dimensions are "0.5,0.6,3"
    And the object "IfcColumn/Column.004" dimensions are "0.5,0.6,3"
    And the object "IfcColumn/Column.005" dimensions are "0.5,0.6,3"

Scenario: Remove array
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    And the object "IfcColumn/Column" is selected
    And I look at the "Array" panel
    And I click "ADD"
    And I click "GREASEPENCIL"
    And I set the "Count" property to "2"
    And I set the "Method" property to "Offset"
    And I set the "X" property to "1"
    And I click "CHECKMARK"
    When I click "X"
    Then the object "IfcColumn/Column" exists
    And the object "IfcColumn/Column.001" does not exist

Scenario: Regenerate array
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    And the object "IfcColumn/Column" is selected
    And I look at the "Array" panel
    And I click "ADD"
    And I click "GREASEPENCIL"
    And I set the "Count" property to "2"
    And I click "CHECKMARK"
    When I click "FILE_REFRESH"
    Then the object "IfcColumn/Column" exists
    And the object "IfcColumn/Column.001" exists

Scenario: Apply array
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    And the object "IfcColumn/Column" is selected
    And I look at the "Array" panel
    And I click "ADD"
    And I click "GREASEPENCIL"
    And I set the "Count" property to "2"
    And I click "CHECKMARK"
    When I click "CHECKMARK"
    Then the object "IfcColumn/Column" exists
    And the object "IfcColumn/Column.001" exists
    And I see "No Array Found"

Scenario: Select array parent
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    And the object "IfcColumn/Column" is selected
    And I look at the "Array" panel
    And I click "ADD"
    And I click "GREASEPENCIL"
    And I set the "Count" property to "2"
    And I click "CHECKMARK"
    When the object "IfcColumn/Column.001" is selected
    And I click "OBJECT_DATA"
    Then the object "IfcColumn/Column" is selected
    And the object "IfcColumn/Column.001" is not selected

Scenario: Select all array objects
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    And the object "IfcColumn/Column" is selected
    And I look at the "Array" panel
    And I click "ADD"
    And I click "GREASEPENCIL"
    And I set the "Count" property to "2"
    And I click "CHECKMARK"
    When the object "IfcColumn/Column.001" is selected
    And I click "RESTRICT_SELECT_OFF"
    Then the object "IfcColumn/Column" is selected
    And the object "IfcColumn/Column.001" is selected
