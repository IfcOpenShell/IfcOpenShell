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

Scenario: Set IFC grid north
    Given an empty IFC project
    And I press "bim.add_georeferencing"
    And I press "bim.enable_editing_georeferencing"
    When I press "bim.set_ifc_grid_north"
    Then nothing happens

Scenario: Set Blender grid north
    Given an empty IFC project
    And I press "bim.add_georeferencing"
    And I press "bim.enable_editing_georeferencing"
    And I press "bim.set_ifc_grid_north"
    When I press "bim.set_blender_grid_north"
    Then nothing happens

Scenario: Get cursor location
    Given an empty IFC project
    When I press "bim.get_cursor_location"
    Then nothing happens

Scenario: Set cursor location
    Given an empty IFC project
    When I set "scene.BIMGeoreferenceProperties.coordinate_output" to "0,0,0"
    And I press "bim.set_cursor_location"
    Then nothing happens

Scenario: Set IFC true north
    Given an empty IFC project
    When I press "bim.set_ifc_true_north"
    Then nothing happens

Scenario: Set Blender true north
    Given an empty IFC project
    And I press "bim.set_ifc_true_north"
    When I press "bim.set_blender_true_north"
    Then nothing happens

Scenario: Convert local to global
    Given an empty IFC project
    When I set "scene.BIMGeoreferenceProperties.coordinate_input" to "0,0,0"
    And I press "bim.convert_local_to_global"
    Then "scene.BIMGeoreferenceProperties.coordinate_output" is "0.0,0.0,0.0"

Scenario: Convert global to local
    Given an empty IFC project
    When I set "scene.BIMGeoreferenceProperties.coordinate_input" to "0,0,0"
    And I press "bim.convert_global_to_local"
    Then "scene.BIMGeoreferenceProperties.coordinate_output" is "0.0,0.0,0.0"
