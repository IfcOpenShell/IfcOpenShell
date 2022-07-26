@search
Feature: Search

Scenario: Select all walls
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a new item to "scene.IfcSelectorProperties.groups"
    And I add a new item to "scene.IfcSelectorProperties.groups[0].queries"
    And I set "scene.IfcSelectorProperties.groups[0].queries[0].selector" to "IFC Class"
    And I set "scene.IfcSelectorProperties.groups[0].queries[0].active_option" to "124: IfcWall"
    When I press "bim.filter_model_elements(option='select')"
    Then the object "IfcWall/Cube" is selected

Scenario: Add selection to IfcGroup
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I set "scene.IfcSelectorProperties.selector_query_syntax" to ".IfcWall"
    And I set "scene.IfcSelectorProperties.manual_override" to "True"
    When I press "bim.add_to_ifc_group(group_name='Walls')"
    And I press "bim.load_groups"
    Then "scene.BIMGroupProperties.groups[-1].name" is "Walls"
