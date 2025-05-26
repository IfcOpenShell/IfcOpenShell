@spatial
Feature: Spatial
    Covers spatial containment management and spatial tool.

Scenario: Set default container
    Given an empty IFC project
    When I look at the "Spatial Decomposition" panel
    Then I see "My Site" in the "1st" list
    And I see "Default: My Storey"
    When I select the row where I see "My Building" in the "1st" list
    And I click "Set Default"
    Then I don't see "Default: My Storey"
    And I see "Default: My Building"

Scenario: Select container
    Given an empty IFC project
    And I look at the "Spatial Decomposition" panel
    When I select the row where I see "My Building" in the "1st" list
    And I click "OBJECT_DATA"
    Then the object "IfcBuilding/My Building" is selected

Scenario: View elements - view elements recursively in the project
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    When I look at the "Spatial Decomposition" panel
    And I select the row where I see "My Project" in the "1st" list
    Then I see "IfcColumn" in the "2nd" list

Scenario: View elements - view elements non-recursively in their container
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcColumnType"
    And I add the construction type
    When I look at the "Spatial Decomposition" panel
    And I select the row where I see "My Project" in the "1st" list
    And I click "OUTLINER"
    Then there are "1" lists
    And I see "No Elements"
    And I select the row where I see "My Storey" in the "1st" list
    Then I see "IfcColumn" in the "2nd" list

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
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And the object "IfcWall/Cube" is selected
    And I look at the "Spatial Decomposition" panel
    And I select the "My Site" item in the "BIM_UL_containers_manager" list
    And I click "Set Default"
    And I look at the "Spatial Container" panel
    And I click "GREASEPENCIL"
    When I click "CHECKMARK"
    Then the object "IfcWall/Cube" is in the collection "IfcSite/My Site"

Scenario: Copy to container
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And the object "IfcSite/My Site" is selected
    And additionally the object "IfcWall/Cube" is selected
    And I press "bim.enable_editing_container"
    When I press "bim.copy_to_container"
    Then the object "IfcWall/Cube.001" is in the collection "IfcSite/My Site"

Scenario: Reference structure
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And the object "IfcBuilding/My Building" is selected
    And additionally the object "IfcWall/Cube" is selected
    And I press "bim.enable_editing_container"
    When I press "bim.reference_structure"
    Then nothing happens

Scenario: Dereference structure
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And the object "IfcBuilding/My Building" is selected
    And additionally the object "IfcWall/Cube" is selected
    And I press "bim.enable_editing_container"
    When I press "bim.reference_structure"
    And I press "bim.dereference_structure"
    Then nothing happens

Scenario: Assign container
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And the object "IfcWall/Cube" is selected
    And I look at the "Spatial Decomposition" panel
    And I select the "My Site" item in the "BIM_UL_containers_manager" list
    And I click "Set Default"
    # Assign container.
    And I look at the "Spatial Container" panel
    And I click "GREASEPENCIL"
    And I click "CHECKMARK"
    When I click "OBJECT_DATA"
    Then nothing happens

Scenario: Select similar container
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I look at the "Class" panel
    And I set the "Products" property to "IfcElement"
    And I set the "Class" property to "IfcWall"
    And I click "Assign IFC Class"
    And the object "IfcWall/Cube" is selected
    And I look at the "Spatial Decomposition" panel
    And I select the "My Site" item in the "BIM_UL_containers_manager" list
    And I click "Set Default"
    # Assign container.
    And I look at the "Spatial Container" panel
    And I click "GREASEPENCIL"
    And I click "CHECKMARK"
    When I click "RESTRICT_SELECT_OFF"
    Then nothing happens

Scenario: Execute generate space from cursor position
    Given an empty IFC project
    Then I press "bim.generate_space" and expect error "Error: Couldn't find any polygons to form the space shape. Perhaps, RL value need to be adjusted."

Scenario: Execute generate spaces from walls
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
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

Scenario: Set element visibility - Isolate spatial container
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Definition" property to "IfcElement"
    And I set the "Class" property to "IfcFurniture"
    And I set the "Representation" property to "No Geometry"
    And I click "OK"
    And I look at the "Spatial Decomposition" panel
    When I select the "My Site" item in the "BIM_UL_containers_manager" list
    And I click "FULLSCREEN_EXIT"
    Then nothing happens

Scenario: Set element visibility - Show spatial container
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Definition" property to "IfcElement"
    And I set the "Class" property to "IfcFurniture"
    And I set the "Representation" property to "No Geometry"
    And I click "OK"
    And I look at the "Spatial Decomposition" panel
    When I select the "My Site" item in the "BIM_UL_containers_manager" list
    And I click "HIDE_OFF"
    Then nothing happens

Scenario: Set element visibility - Hide spatial container
    Given an empty IFC project
    And I trigger "Add Element"
    And I set the "Definition" property to "IfcElement"
    And I set the "Class" property to "IfcFurniture"
    And I set the "Representation" property to "No Geometry"
    And I click "OK"
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
