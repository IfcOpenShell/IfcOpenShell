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
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And the object "IfcWall/Cube" is selected
    When I press "bim.add_aggregate"
    Then the object "IfcElementAssembly/Default_Name" exists
    And the object "IfcWall/Cube" is aggregated by object "IfcElementAssembly/Default_Name"
    And the object "IfcElementAssembly/Default_Name" is contained in object "IfcBuildingStorey/My Storey"

Scenario: Add aggregate - add a nested aggregate
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And the object "IfcWall/Cube" is selected
    When I press "bim.add_aggregate"
    # Tab into the aggregate to restructure its contents. Outside aggregate mode,
    # selecting a part collects the whole aggregate instead of extracting the part.
    And the object "IfcElementAssembly/Default_Name" is selected
    And I press "bim.override_mode_set_edit"
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

Scenario: Add aggregate - keep linked aggregates intact when their parts are selected
    Given I load the IFC test file "/test/files/linked-aggregates.ifc"
    And the object "IfcWall/Wall_01" is selected
    When I duplicate linked aggregate the selected objects
    Then the object "Assembly_01" exists
    When I deselect all objects
    And the object "IfcElementAssembly/Assembly" is selected
    And additionally the object "IfcWall/Wall_01" is selected
    And additionally the object "IfcWall/Wall_02" is selected
    And additionally the object "Assembly_01" is selected
    And additionally the object "IfcWall/Wall_01.001" is selected
    And additionally the object "IfcWall/Wall_02.001" is selected
    And I press "bim.add_aggregate(aggregate_name='Wrapper')"
    Then the object "IfcElementAssembly/Assembly" is aggregated by object "IfcElementAssembly/Wrapper"
    And the object "Assembly_01" is aggregated by object "IfcElementAssembly/Wrapper"
    And the object "IfcWall/Wall_01" is aggregated by object "IfcElementAssembly/Assembly"
    And the object "IfcWall/Wall_02" is aggregated by object "IfcElementAssembly/Assembly"
    And the object "IfcWall/Wall_01.001" is aggregated by object "Assembly_01"
    And the object "IfcWall/Wall_02.001" is aggregated by object "Assembly_01"

Scenario: Add aggregate - promote a selected part to its whole linked aggregate
    Given I load the IFC test file "/test/files/linked-aggregates.ifc"
    And the object "IfcWall/Wall_01" is selected
    When I duplicate linked aggregate the selected objects
    Then the object "Assembly_01" exists
    When I deselect all objects
    And the object "IfcWall/Wall_01" is selected
    And additionally the object "IfcWall/Wall_01.001" is selected
    And I press "bim.add_aggregate(aggregate_name='Wrapper')"
    Then the object "IfcElementAssembly/Assembly" is aggregated by object "IfcElementAssembly/Wrapper"
    And the object "Assembly_01" is aggregated by object "IfcElementAssembly/Wrapper"
    And the object "IfcWall/Wall_01" is aggregated by object "IfcElementAssembly/Assembly"
    And the object "IfcWall/Wall_02" is aggregated by object "IfcElementAssembly/Assembly"
    And the object "IfcWall/Wall_01.001" is aggregated by object "Assembly_01"
    And the object "IfcWall/Wall_02.001" is aggregated by object "Assembly_01"

Scenario: Add aggregate - promote a selected part to its whole aggregate
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And the object "IfcWall/Cube" is selected
    When I press "bim.add_aggregate"
    # Not in aggregate mode, so selecting the part collects the whole aggregate.
    And the object "IfcWall/Cube" is selected
    And I press "bim.add_aggregate(aggregate_name='Wrapper')"
    Then the object "IfcElementAssembly/Default_Name" is aggregated by object "IfcElementAssembly/Wrapper"
    And the object "IfcWall/Cube" is aggregated by object "IfcElementAssembly/Default_Name"
    And the object "IfcElementAssembly/Wrapper" is contained in object "IfcBuildingStorey/My Storey"

Scenario: Add aggregate - a sub-assembly inside a linked aggregate stays plain
    Given I load the IFC test file "/test/files/linked-aggregates.ifc"
    And the object "IfcWall/Wall_01" is selected
    When I duplicate linked aggregate the selected objects
    Then the object "Assembly_01" exists
    # Tab into the linked aggregate, then group one of its parts into a sub-assembly.
    When I deselect all objects
    And the object "IfcElementAssembly/Assembly" is selected
    And I press "bim.override_mode_set_edit"
    And the object "IfcWall/Wall_01" is selected
    And I press "bim.add_aggregate(aggregate_name='Sub')"
    Then the object "IfcWall/Wall_01" is aggregated by object "IfcElementAssembly/Sub"
    And the object "IfcElementAssembly/Sub" is aggregated by object "IfcElementAssembly/Assembly"
    And the object "IfcWall/Wall_02" is aggregated by object "IfcElementAssembly/Assembly"
    # It is structure, not an instance: linked-ness is inherited from the aggregate
    # above it rather than duplicated onto every level of nesting.
    And the object "IfcElementAssembly/Sub" is not part of a Linked Aggregate
