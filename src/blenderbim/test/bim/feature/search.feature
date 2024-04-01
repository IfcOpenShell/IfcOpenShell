@search
Feature: Search

Scenario: Select all walls
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_filter_group(module='search')"
    And I set "scene.BIMSearchProperties.facet" to "entity"
    And I press "bim.add_filter(index=0, type='entity', module='search')"
    And I set "scene.BIMSearchProperties.filter_groups[0].filters[0].value" to "IfcWall"
    When I press "bim.search"
    Then the object "IfcWall/Cube" is selected
