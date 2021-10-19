@root
Feature: Root

Scenario: Unlink object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I add a material
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_material"
    When I press "bim.unlink_object(obj='IfcWall/Cube')"
    Then the object "Cube" is not an IFC element
    And the material "Material" is not an IFC material
    And the material "Material" is not an IFC style


Scenario: Copy class
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    When I press "bim.copy_class(obj='IfcWall/Cube')"
    Then the object "IfcWall/Cube" is an "IfcWall"
