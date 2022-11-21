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
    And I press "bim.enable_editing_aggregate"
    And the variable "relating_object" is "tool.Ifc.get().by_type('IfcSite')[0].id()"
    And the variable "related_object" is "tool.Ifc.get().by_type('IfcBuildingStorey')[0].id()"
    When I press "bim.assign_object(relating_object={relating_object}, related_object={related_object})"
    Then the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuildingStorey/My Storey" is in the collection "IfcBuildingStorey/My Storey"
    And the collection "IfcBuildingStorey/My Storey" is in the collection "IfcSite/My Site"

Scenario: Unassign object
    Given an empty IFC project
    And the object "IfcBuildingStorey/My Storey" is selected
    And I press "bim.enable_editing_aggregate"
    And the variable "relating_object" is "tool.Ifc.get().by_type('IfcSite')[0].id()"
    And the variable "related_object" is "tool.Ifc.get().by_type('IfcBuildingStorey')[0].id()"
    And I press "bim.assign_object(relating_object={relating_object}, related_object={related_object})"
    And the object "IfcBuildingStorey/My Storey" is selected
    When I press "bim.unassign_object(relating_object={relating_object}, related_object={related_object})"
    Then the object "IfcSite/My Site" is in the collection "IfcSite/My Site"
    And the object "IfcBuildingStorey/My Storey" is in the collection "IfcBuildingStorey/My Storey"
    And the collection "IfcBuildingStorey/My Storey" is in the collection "IfcProject/My Project"

Scenario: Add aggregate
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    When I press "bim.add_aggregate"
    Then the object "IfcWall/Cube" is in the collection "IfcElementAssembly/Assembly"
    And the object "IfcElementAssembly/Assembly" is in the collection "IfcElementAssembly/Assembly"
    And the collection "IfcElementAssembly/Assembly" is in the collection "IfcBuildingStorey/My Storey"

Scenario: Add aggregate - with the aggregate inheriting the existing spatial collection
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is placed in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcWall/Cube" is selected
    When I press "bim.add_aggregate"
    Then the object "IfcWall/Cube" is in the collection "IfcElementAssembly/Assembly"
    And the object "IfcElementAssembly/Assembly" is in the collection "IfcElementAssembly/Assembly"
    And the collection "IfcElementAssembly/Assembly" is in the collection "IfcBuildingStorey/My Storey"

Scenario: Add aggregate - add a nested aggregate
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is placed in the collection "IfcBuildingStorey/My Storey"
    And the object "IfcWall/Cube" is selected
    When I press "bim.add_aggregate"
    And the object "IfcWall/Cube" is selected
    And I press "bim.add_aggregate"
    Then the object "IfcWall/Cube" is in the collection "IfcElementAssembly/Assembly.001"
    And the object "IfcElementAssembly/Assembly.001" is in the collection "IfcElementAssembly/Assembly.001"
    And the collection "IfcElementAssembly/Assembly.001" is in the collection "IfcElementAssembly/Assembly"
    And the collection "IfcElementAssembly/Assembly" is in the collection "IfcBuildingStorey/My Storey"
