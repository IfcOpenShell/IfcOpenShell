@covering
Feature: Covering
    Covers covering tool.

Scenario: Execute generate flooring coverings from walls
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_constr_type_instance"
    And the object "IfcWall/Wall" is selected
    When I press "bim.add_instance_flooring_coverings_from_walls"
    Then nothing happens

