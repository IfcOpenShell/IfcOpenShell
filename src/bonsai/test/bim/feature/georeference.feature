@georeference
Feature: Georeference

Scenario: Add georeferencing
    Given an empty IFC project
    And I look at the "Georeferencing" panel
    And I see "Not Georeferenced"
    And I don't see "Projected CRS"
    When I click "ADD"
    Then I see "Projected CRS"
    And I see "EPSG:3857"

Scenario: Enable editing georeferencing
    Given an empty IFC project
    And I look at the "Georeferencing" panel
    And I click "ADD"
    When I click "GREASEPENCIL"
    Then I see the "Name" property

Scenario: Remove georeferencing
    Given an empty IFC project
    And I look at the "Georeferencing" panel
    And I click "ADD"
    When I click "X"
    Then I see "Not Georeferenced"

Scenario: Edit georeferencing
    Given an empty IFC project
    And I look at the "Georeferencing" panel
    And I click "ADD"
    And I click "GREASEPENCIL"
    When I click "CHECKMARK"
    Then I don't see the "Name" property
    And I see "EPSG:3857"

Scenario: Disable editing georeferencing
    Given an empty IFC project
    And I look at the "Georeferencing" panel
    And I click "ADD"
    And I click "GREASEPENCIL"
    When I click "CANCEL"
    Then I don't see the "Name" property
    And I see "EPSG:3857"

Scenario: Get cursor location
    Given an empty IFC project
    And I look at the "Georeferencing Calculator" panel
    And I see the "Local (mm)" property is "0,0,0"
    And I see the "Map (n/a)" property is "0,0,0"
    When I click "TRACKER"
    Then I see the "Local (mm)" property is "0.0,0.0,0.0"
    And I see the "Map (n/a)" property is "0.0,0.0,0.0"

Scenario: Convert local to map
    Given an empty IFC project
    And I look at the "Georeferencing Calculator" panel
    And I see the "Map (n/a)" property is "0,0,0"
    When I set the "Local (mm)" property to "0,0,0"
    And I look at the "Georeferencing Calculator" panel
    Then I see the "Map (n/a)" property is "0.0,0.0,0.0"

Scenario: Convert map to local
    Given an empty IFC project
    And I look at the "Georeferencing Calculator" panel
    And I see the "Local (mm)" property is "0,0,0"
    When I set the "Map (n/a)" property to "0,0,0"
    And I look at the "Georeferencing Calculator" panel
    Then I see the "Local (mm)" property is "0.0,0.0,0.0"
