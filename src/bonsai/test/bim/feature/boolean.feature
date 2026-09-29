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
    And the variable "extrusion" is "{ifc}.by_type('IfcExtrudedAreaSolid')[0].id()"
    And the object "Item/IfcExtrudedAreaSolid/{extrusion}" exists
    And I open the "Add Item" menu
    When I click "Half Space Solid"
    And the variable "half_space" is "{ifc}.by_type('IfcHalfSpaceSolid')[0].id()"
    And the variable "boolean" is "{ifc}.by_type('IfcBooleanResult')[0].id()"
    And the object "Item/IfcHalfSpaceSolid/{half_space}" exists
    And I deselect all objects
    And I toggle edit mode
    And I select the object "IfcFurniture/Unnamed"
    And I look at the "Property Sets" panel
    Then I see "BBIM_Boolean"
    And I see "[{boolean}]"

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
    And the variable "extrusion" is "{ifc}.by_type('IfcExtrudedAreaSolid')[0].id()"
    And the object "Item/IfcExtrudedAreaSolid/{extrusion}" exists
    And I open the "Add Item" menu
    And I click "Half Space Solid"
    And the variable "half_space" is "{ifc}.by_type('IfcHalfSpaceSolid')[0].id()"
    And the variable "boolean" is "{ifc}.by_type('IfcBooleanResult')[0].id()"
    And I deselect all objects
    And I toggle edit mode
    And I select the object "IfcFurniture/Unnamed"
    And I toggle edit mode
    And I select the object "Item/IfcHalfSpaceSolid/{half_space}"
    When I delete the selected objects
    And I toggle edit mode
    And I select the object "IfcFurniture/Unnamed"
    And I look at the "Property Sets" panel
    Then I don't see "BBIM_Boolean"
    And I don't see "[{boolean}]"
