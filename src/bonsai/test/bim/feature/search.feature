@search
Feature: Search

Scenario: Select all walls
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    When I look at the "Search" panel
    And I click "Add Search Group"
    And I click "Add Filter"
    And I set the "FILE_3D" property to "IfcWall"
    And I click "Search"
    Then the object "IfcWall/Cube" is selected

Scenario: Edit filter query
    Given an empty IFC project
    When I look at the "Search" panel
    And I click "FILTER"
    Then nothing happens

Scenario: Colour by property - default class query
    Given an empty IFC project
    When I look at the "Colour By Property" panel
    And I click "Colour by Property"
    Then the "BIM_UL_colourscheme" list has 4 items

Scenario: Colour by property - no query
    Given an empty IFC project
    When I look at the "Colour By Property" panel
    And I set the "Query" property to " "
    And I click "Colour by Property" and expect error "Error: No Query Provided"
    Then I don't see the "BIM_UL_colourscheme" list

Scenario: Reset colours
    Given an empty IFC project
    And I look at the "Colour By Property" panel
    And I click "Colour by Property"
    When I click "Reset Colours"
    Then I don't see the "BIM_UL_colourscheme" list

Scenario: Flat colours
    Given an empty IFC project
    And I look at the "Colour By Property" panel
    And I click "Colour by Property"
    When I click "SHADING_RENDERED"
    Then nothing happens

Scenario: Select by property
    Given an empty IFC project
    And I look at the "Colour By Property" panel
    And I click "Colour by Property"
    When I click "RESTRICT_SELECT_OFF"
    Then nothing happens
