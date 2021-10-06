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
    Then the object "IfcBuildingStorey/My Storey" is in the collection "IfcBuildingStorey/My Storey"
    Then the collection "IfcBuildingStorey/My Storey" is in the collection "IfcSite/My Site"

