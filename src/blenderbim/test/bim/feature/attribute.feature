@attribute
Feature: Attribute

Scenario: Copy attribute to selected
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcWall/Cube.001" is selected
    And I press "bim.enable_editing_attributes(obj='IfcWall/Cube.001', obj_type='Object')"
    And I set "active_object.BIMAttributeProperties.attributes[2].string_value" to "Foo"
    When I press "bim.copy_attribute_to_selection(name='Description')"
    Then nothing happens
