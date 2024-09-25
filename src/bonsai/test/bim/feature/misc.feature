@misc
Feature: Misc

Scenario: Set override colour
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.set_override_colour"
    Then nothing happens

Scenario: Snap spaces together
    Given an empty Blender session
    And I add a cube
    And I add a cube
    And the object "Cube" is selected
    And additionally the object "Cube.001" is selected
    When I press "bim.snap_spaces_together"
    Then nothing happens

Scenario: Resize to storey
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And the variable "storey" is "tool.Ifc.get().by_type('IfcBuildingStorey')[0].id()"
    And I press "bim.set_default_container(container={storey})"
    And I press "bim.assign_container(container={storey})"
    When I press "bim.resize_to_storey(total_storeys=1)"
    Then nothing happens

Scenario: Split along edge
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a plane of size "4" at "0,0,0"
    And the object "IfcWall/Cube" is selected
    And additionally the object "Plane" is selected
    When I press "bim.split_along_edge"
    Then the object "IfcWall/Cube" is an "IfcWall"
    And the object "IfcWall/Cube.001" is an "IfcWall"

Scenario: Enabling and disabling IFC Sverchok
    Given an empty IFC project
    And I press "preferences.addon_enable(module="sverchok")"
    And I press "preferences.addon_enable(module="ifcsverchok")"
    And I press "preferences.addon_disable(module="sverchok")"
    And I press "preferences.addon_disable(module="ifcsverchok")"
