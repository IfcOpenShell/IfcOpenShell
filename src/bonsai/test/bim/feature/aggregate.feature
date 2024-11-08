@aggregate
Feature: Aggregate
    Covers element and spatial aggregation

Scenario: Enable editing aggregate
    Given an empty IFC project
    And the object "IfcSite/My Site" is selected
    When I press "bim.enable_editing_aggregate"
    Then nothing happens

Scenario: Disable editing aggregate
    Given an empty IFC project
    And the object "IfcSite/My Site" is selected
    And I press "bim.enable_editing_aggregate"
    When I press "bim.disable_editing_aggregate"
    Then nothing happens

Scenario: Assign object
    Given an empty IFC project
    And the object "IfcSite/My Site" is selected
    And the object "IfcBuildingStorey/My Storey" is selected
    And I press "bim.enable_editing_aggregate"
    And the variable "relating_object" is "tool.Ifc.get().by_type('IfcSite')[0].id()"
    When I press "bim.aggregate_assign_object(relating_object={relating_object})"
    Then the object "IfcBuildingStorey/My Storey" is aggregated by object "IfcSite/My Site"

Scenario: Unassign object
    Given an empty IFC project
    And the object "IfcBuildingStorey/My Storey" is selected
    And I press "bim.enable_editing_aggregate"
    And the variable "relating_object" is "tool.Ifc.get().by_type('IfcSite')[0].id()"
    And I press "bim.aggregate_assign_object(relating_object={relating_object})"
    And the object "IfcBuildingStorey/My Storey" is selected
    When I press "bim.aggregate_unassign_object"
    Then the object "IfcBuildingStorey/My Storey" has no aggregate

Scenario: Add aggregate
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When I press "bim.add_aggregate"
    Then the object "IfcElementAssembly/Default_Name" exists
    And the object "IfcWall/Cube" is aggregated by object "IfcElementAssembly/Default_Name"
    And the object "IfcElementAssembly/Default_Name" is contained in object "IfcBuildingStorey/My Storey"

Scenario: Add aggregate - add a nested aggregate
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When I press "bim.add_aggregate"
    And the object "IfcWall/Cube" is selected
    And I press "bim.add_aggregate(aggregate_name='Default_Name2')"
    Then the object "IfcElementAssembly/Default_Name" exists
    And the object "IfcElementAssembly/Default_Name" is contained in object "IfcBuildingStorey/My Storey"
    And the object "IfcElementAssembly/Default_Name2" exists
    And the object "IfcWall/Cube" is aggregated by object "IfcElementAssembly/Default_Name2"
    And the object "IfcElementAssembly/Default_Name2" is aggregated by object "IfcElementAssembly/Default_Name"

Scenario: Add aggregate - add multiple elements to a custom aggregate class
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcMember"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcCovering"
    And I press "bim.assign_class"
    And the object "IfcMember/Cube" is selected
    And additionally the object "IfcCovering/Cube" is selected
    When I press "bim.add_aggregate(ifc_class='IfcWall', aggregate_name='Assembly')"
    Then the object "IfcMember/Cube" is aggregated by object "IfcWall/Assembly"
    And the object "IfcCovering/Cube" is aggregated by object "IfcWall/Assembly"
    And the object "IfcWall/Assembly" is contained in object "IfcBuildingStorey/My Storey"
