@boolean
Feature: Boolean
    Manage boolean hierarchies and boolean results

Scenario: Ensure added booleans are marked as manual
    Given an empty IFC project
    And I open the "Add" menu
    And I trigger "Add Element"
    And I set the "Definition" property to "IfcElement"
    And I set the "Class" property to "IfcFurniture"
    And I set the "Representation" property to "Custom Extruded Solid"
    And I click "OK"
    And the object "IfcFurniture/Unnamed" exists
    And I toggle edit mode
    And the object "Item/IfcExtrudedAreaSolid/77" exists
    And I open the "Add Item" menu
    When I click "Half Space Solid"
    And the object "Item/IfcHalfSpaceSolid/90" exists
    And I deselect all objects
    And I toggle edit mode
    And I select the object "IfcFurniture/Unnamed"
    And I look at the "Property Sets" panel
    Then I see "BBIM_Boolean"
    And I see "[91]"

Scenario: Ensure removed booleans are unmarked as manual
    Given an empty IFC project
    And I open the "Add" menu
    And I trigger "Add Element"
    And I set the "Definition" property to "IfcElement"
    And I set the "Class" property to "IfcFurniture"
    And I set the "Representation" property to "Custom Extruded Solid"
    And I click "OK"
    And the object "IfcFurniture/Unnamed" exists
    And I toggle edit mode
    And the object "Item/IfcExtrudedAreaSolid/77" exists
    And I open the "Add Item" menu
    And I click "Half Space Solid"
    And I deselect all objects
    And I toggle edit mode
    And I select the object "IfcFurniture/Unnamed"
    And I toggle edit mode
    And I select the object "Item/IfcHalfSpaceSolid/90"
    When I delete the selected objects
    And I toggle edit mode
    And I select the object "IfcFurniture/Unnamed"
    And I look at the "Property Sets" panel
    Then I don't see "BBIM_Boolean"
    And I don't see "[91]"
