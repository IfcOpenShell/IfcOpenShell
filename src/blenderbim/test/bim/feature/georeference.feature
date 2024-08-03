@georeference
Feature: Georeference

Scenario: Add georeferencing
    Given an empty IFC project
    When I press "bim.add_georeferencing"
    Then nothing happens

Scenario: Enable editing georeferencing
    Given an empty IFC project
    And I press "bim.add_georeferencing"
    When I press "bim.enable_editing_georeferencing"
    Then nothing happens

Scenario: Remove georeferencing
    Given an empty IFC project
    And I press "bim.add_georeferencing"
    When I press "bim.remove_georeferencing"
    Then nothing happens

Scenario: Edit georeferencing
    Given an empty IFC project
    And I press "bim.add_georeferencing"
    And I press "bim.enable_editing_georeferencing"
    When I press "bim.edit_georeferencing"
    Then nothing happens

Scenario: Disable editing georeferencing
    Given an empty IFC project
    And I press "bim.add_georeferencing"
    And I press "bim.enable_editing_georeferencing"
    When I press "bim.disable_editing_georeferencing"
    Then nothing happens

Scenario: Get cursor location
    Given an empty IFC project
    When I press "bim.get_cursor_location"
    Then nothing happens

Scenario: Convert local to map
    Given an empty IFC project
    When I set "scene.BIMGeoreferenceProperties.local_coordinates" to "0,0,0"
    Then "scene.BIMGeoreferenceProperties.map_coordinates" is "0.0,0.0,0.0"

Scenario: Convert map to local
    Given an empty IFC project
    When I set "scene.BIMGeoreferenceProperties.map_coordinates" to "0,0,0"
    Then "scene.BIMGeoreferenceProperties.local_coordinates" is "0.0,0.0,0.0"
