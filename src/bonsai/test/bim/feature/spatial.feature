@spatial
Feature: Spatial
    Covers spatial containment management and spatial tool.

Scenario: Enable editing container
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.enable_editing_container"
    Then nothing happens

Scenario: Disable editing container
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I press "bim.enable_editing_container"
    When I press "bim.disable_editing_container"
    Then nothing happens

Scenario: Assign container
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And the variable "site" is "tool.Ifc.get().by_type('IfcSite')[0].id()"
    And I press "bim.set_default_container(container={site})"
    And I press "bim.enable_editing_container"
    When I press "bim.assign_container()"
    Then the object "IfcWall/Cube" is in the collection "IfcSite/My Site"

Scenario: Copy to container
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcSite/My Site" is selected
    And additionally the object "IfcWall/Cube" is selected
    And I press "bim.enable_editing_container"
    When I press "bim.copy_to_container"
    Then the object "IfcWall/Cube.001" is in the collection "IfcSite/My Site"

Scenario: Reference structure
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcBuilding/My Building" is selected
    And additionally the object "IfcWall/Cube" is selected
    And I press "bim.enable_editing_container"
    When I press "bim.reference_structure"
    Then nothing happens

Scenario: Dereference structure
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcBuilding/My Building" is selected
    And additionally the object "IfcWall/Cube" is selected
    And I press "bim.enable_editing_container"
    When I press "bim.reference_structure"
    And I press "bim.dereference_structure"
    Then nothing happens

Scenario: Select container
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.enable_editing_container"
    And the variable "site" is "tool.Ifc.get().by_type('IfcSite')[0].id()"
    And I press "bim.set_default_container(container={site})"
    And I press "bim.assign_container()"
    When I press "bim.select_container"
    Then nothing happens

Scenario: Select similar container
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.enable_editing_container"
    And the variable "site" is "tool.Ifc.get().by_type('IfcSite')[0].id()"
    And I press "bim.set_default_container(container={site})"
    And I press "bim.assign_container()"
    When I press "bim.select_similar_container"
    Then nothing happens

Scenario: Execute generate space from cursor position
    Given an empty IFC project
    When I press "bim.generate_space"
    Then nothing happens

Scenario: Execute generate spaces from walls
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_constr_type_instance"
    And the object "IfcWall/Wall" is selected
    When I press "bim.generate_spaces_from_walls"
    Then nothing happens

Scenario: Execute toggle space visibility
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I press "bim.assign_class(ifc_class='IfcSpace', predefined_type='SPACE')"
    When I press "bim.toggle_space_visibility"
    Then nothing happens

Scenario: Spatial decomposition - see panel
    Given an empty IFC project
    When I look at the "Spatial Decomposition" panel
    Then the "BIM_UL_containers_manager" list has 4 items
    And I don't see the "BIM_UL_elements" list

Scenario: Isolate spatial container
    Given an empty IFC project
    And I look at the "Spatial Decomposition" panel
    When I select the "My Site" item in the "BIM_UL_containers_manager" list
    And I click "Isolate"
    Then nothing happens

Scenario: Show spatial container
    Given an empty IFC project
    And I look at the "Spatial Decomposition" panel
    When I select the "My Site" item in the "BIM_UL_containers_manager" list
    And I click "HIDE_OFF"
    Then nothing happens

Scenario: Hide spatial container
    Given an empty IFC project
    And I look at the "Spatial Decomposition" panel
    When I select the "My Site" item in the "BIM_UL_containers_manager" list
    And I click "HIDE_ON"
    Then nothing happens

Scenario: Select spatial container
    Given an empty IFC project
    And I look at the "Spatial Decomposition" panel
    When I select the "My Site" item in the "BIM_UL_containers_manager" list
    And I click "OBJECT_DATA"
    Then the object "IfcSite/My Site" is selected

Scenario: Delete spatial container
    Given an empty IFC project
    And I look at the "Spatial Decomposition" panel
    When I select the "My Building" item in the "BIM_UL_containers_manager" list
    And I click "X"
    Then the "BIM_UL_containers_manager" list has 2 items

Scenario: Add spatial container
    Given an empty IFC project
    And I look at the "Spatial Decomposition" panel
    And I set the "subelement_class" property to "IfcExternalSpatialElement"
    When I click "ADD"
    Then the "BIM_UL_containers_manager" list has 5 items
