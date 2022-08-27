@spatial
Feature: Spatial
    Covers spatial containment management.

Scenario: Enable editing container
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.enable_editing_container"
    Then nothing happens

Scenario: Disable editing container
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I press "bim.enable_editing_container"
    When I press "bim.disable_editing_container"
    Then nothing happens

Scenario: Assign container
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.enable_editing_container"
    And the variable "site" is "tool.Ifc.get().by_type('IfcSite')[0].id()"
    When I press "bim.assign_container(structure={site})"
    Then the object "IfcWall/Cube" is in the collection "IfcSite/My Site"

Scenario: Copy to container
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.enable_editing_container"
    When I set "scene.BIMSpatialProperties.containers[0].is_selected" to "True"
    And I press "bim.copy_to_container"
    Then the object "IfcWall/Cube.001" is in the collection "IfcSite/My Site"

Scenario: Reference structure
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.enable_editing_container"
    When I set "scene.BIMSpatialProperties.containers[0].is_selected" to "True"
    And I press "bim.reference_structure"
    Then nothing happens

Scenario: Dereference structure
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.enable_editing_container"
    When I set "scene.BIMSpatialProperties.containers[0].is_selected" to "True"
    And I press "bim.reference_structure"
    And I press "bim.dereference_structure"
    Then nothing happens

Scenario: Select container
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.enable_editing_container"
    And the variable "site" is "tool.Ifc.get().by_type('IfcSite')[0].id()"
    And I press "bim.assign_container(structure={site})"
    When I press "bim.select_container"
    Then nothing happens

Scenario: Select similar container
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.enable_editing_container"
    And the variable "site" is "tool.Ifc.get().by_type('IfcSite')[0].id()"
    And I press "bim.assign_container(structure={site})"
    When I press "bim.select_similar_container"
    Then nothing happens
