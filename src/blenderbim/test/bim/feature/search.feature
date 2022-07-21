@root
Feature: Search

Scenario: Select all walls
    Given an empty IFC project
    And I add a cube
    When the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a new group to IfcSelector
    And I add a new query to IfcSelector
    And I set "scene.IfcSelectorProperties.groups[0].queries[0].active_option" to "IFC Class"
    And I set "scene.IfcSelectorProperties.groups[0].queries[0].active_option" to "124: IfcWall"
    And I press 'bim.filter_model_elements'
    Then bpy.context.selected_objects should contain "Cube"

