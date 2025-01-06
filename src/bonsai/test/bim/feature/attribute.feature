@attribute
Feature: Attribute

Scenario: Enable editing attributes
    Given an empty IFC project
    And the object "IfcSite/My Site" is selected
    When I press "bim.enable_editing_attributes(obj='IfcSite/My Site')"
    Then nothing happens

Scenario: Disable editing attributes
    Given an empty IFC project
    And the object "IfcSite/My Site" is selected
    And I press "bim.enable_editing_attributes(obj='IfcSite/My Site')"
    When I press "bim.disable_editing_attributes(obj='IfcSite/My Site')"
    Then nothing happens

Scenario: Edit attributes
    Given an empty IFC project
    And the object "IfcSite/My Site" is selected
    And I press "bim.enable_editing_attributes(obj='IfcSite/My Site')"
    And I set "active_object.BIMAttributeProperties.attributes[1].string_value" to "Name"
    When I press "bim.edit_attributes(obj='IfcSite/My Site')"
    Then the object "IfcSite/Name" is an "IfcSite"
    And the object "IfcSite/My Site" does not exist

Scenario: Edit attributes - longitude / latitude
    Given an empty IFC project
    And the object "IfcSite/My Site" is selected
    And I press "bim.enable_editing_attributes(obj='IfcSite/My Site')"
    Then "active_object.BIMAttributeProperties.attributes[6].name" is "RefLatitude"
    When I set "active_object.BIMAttributeProperties.attributes[6].string_value" to "[1,2]"
    And I press "bim.edit_attributes(obj='IfcSite/My Site')"
    And I press "bim.enable_editing_attributes(obj='IfcSite/My Site')"
    And I press "bim.edit_attributes(obj='IfcSite/My Site')"
    Then nothing happens

Scenario: Copy attribute to selected
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcWall/Cube.001" is selected
    And I press "bim.enable_editing_attributes(obj='IfcWall/Cube.001')"
    And I set "active_object.BIMAttributeProperties.attributes[2].string_value" to "Foo"
    When I press "bim.copy_attribute_to_selection(name='Description')"
    Then nothing happens
