@brick
Feature: Brick

Scenario: Create Brick project
    Given an empty Blender session
    And the Brickschema is stubbed
    When I press "bim.new_brick_file"
    Then nothing happens

Scenario: Load Brick project
    Given an empty Blender session
    And the Brickschema is stubbed
    When I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    Then nothing happens

Scenario: View Brick class
    Given an empty Blender session
    And the Brickschema is stubbed
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    When I press "bim.view_brick_class(brick_class='Building')"
    Then nothing happens

Scenario: View Brick item
    Given an empty Blender session
    And the Brickschema is stubbed
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    When I press "bim.view_brick_item(item='https://example.org/digitaltwin#lighting_zone_1')"
    Then nothing happens

Scenario: Rewind Brick class
    Given an empty Blender session
    And the Brickschema is stubbed
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And I press "bim.view_brick_class(brick_class='Building')"
    When I press "bim.rewind_brick_class"
    Then nothing happens

Scenario: Close Brick project
    Given an empty Blender session
    And the Brickschema is stubbed
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    When I press "bim.close_brick_project"
    Then nothing happens

Scenario: Close Brick project then create Brick project
    Given an empty Blender session
    And the Brickschema is stubbed
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And I press "bim.close_brick_project"
    And the Brickschema is stubbed
    When I press "bim.new_brick_file"
    Then nothing happens

Scenario: Add Brick - vanilla Brick with no IFC
    Given an empty Blender session
    And the Brickschema is stubbed
    And I press "bim.new_brick_file"
    And I set "scene.BIMBrickProperties.namespace" to "https://example.org/digitaltwin#"
    And I set "scene.BIMBrickProperties.new_brick_label" to "abc123"
    When I press "bim.add_brick"
    Then nothing happens

Scenario: Add Brick - from geometry without a Brick IFC library
    Given an empty IFC project
    And the Brickschema is stubbed
    And I press "bim.new_brick_file"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcChiller"
    And I press "bim.assign_class"
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And the object "IfcChiller/Cube" is selected
    And I set "scene.BIMBrickProperties.namespace" to "https://example.org/digitaltwin#"
    When I press "bim.add_brick"
    Then nothing happens

Scenario: Add Brick - from geometry with a Brick IFC library
    Given an empty IFC project
    And the Brickschema is stubbed
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcChiller"
    And I press "bim.assign_class"
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And I press "bim.convert_brick_project"
    And the object "IfcChiller/Cube" is selected
    And I set "scene.BIMBrickProperties.namespace" to "https://example.org/digitaltwin#"
    When I press "bim.add_brick"
    Then nothing happens

Scenario: Refresh Brick viewer
    Given an empty Blender session
    And the Brickschema is stubbed
    And I press "bim.new_brick_file"
    When I press "bim.refresh_brick_viewer"
    Then nothing happens

Scenario: Add Brick relation - vanilla Brick with no IFC
    Given an empty Blender session
    And the Brickschema is stubbed
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And I set "scene.BIMBrickProperties.namespace" to "https://example.org/digitaltwin#"
    And I press "bim.view_brick_class(brick_class='Lighting_Zone')"
    And I set "scene.BIMBrickProperties.active_brick_index" to "0"
    And I set "scene.BIMBrickProperties.brick_create_relations_toggled" to "True"
    And I set "scene.BIMBrickProperties.new_brick_relation_object" to "xyz789"
    When I press "bim.add_brick_relation"
    Then nothing happens

Scenario: Add Brick relation - vanilla Brick with no IFC and with split screen
    Given an empty Blender session
    And the Brickschema is stubbed
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And I set "scene.BIMBrickProperties.namespace" to "https://example.org/digitaltwin#"
    And I set "scene.BIMBrickProperties.brick_entity_create_type" to "Location"
    And I set "scene.BIMBrickProperties.new_brick_label" to "abc123"
    And I set "scene.BIMBrickProperties.brick_entity_class" to "https://brickschema.org/schema/Brick#Building"
    And I press "bim.add_brick"
    And I press "bim.view_brick_class(brick_class='Lighting_Zone')"
    And I set "scene.BIMBrickProperties.active_brick_index" to "0"
    And I set "scene.BIMBrickProperties.split_screen_toggled" to "True"
    And I press "bim.view_brick_class(brick_class='Building', split_screen=True)"
    And I set "scene.BIMBrickProperties.split_screen_active_brick_index" to "0"
    And I set "scene.BIMBrickProperties.brick_create_relations_toggled" to "True"
    When I press "bim.add_brick_relation"
    Then nothing happens

Scenario: Remove Brick - vanilla Brick
    Given an empty Blender session
    And the Brickschema is stubbed
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And I press "bim.view_brick_class(brick_class='Lighting_Zone')"
    And I set "scene.BIMBrickProperties.active_brick_index" to "0"
    When I press "bim.remove_brick"
    Then nothing happens

Scenario: Remove Brick - with a Brick IFC library reference
    Given an empty IFC project
    And the Brickschema is stubbed
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcChiller"
    And I press "bim.assign_class"
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And the object "IfcChiller/Cube" is selected
    And I set "scene.BIMBrickProperties.namespace" to "https://example.org/digitaltwin#"
    And I press "bim.add_brick"
    And I press "bim.view_brick_class(brick_class='Equipment')"
    And I set "scene.BIMBrickProperties.active_brick_index" to "0"
    When I press "bim.remove_brick"
    Then nothing happens

Scenario: Change viewer list root
    Given an empty Blender session
    And the Brickschema is stubbed
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And I set "scene.BIMBrickProperties.set_list_root_toggled" to "True"
    When I set "scene.BIMBrickProperties.brick_list_root" to "Location"
    Then nothing happens

Scenario: Change viewer list root - split screen
    Given an empty Blender session
    And the Brickschema is stubbed
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And I set "scene.BIMBrickProperties.set_list_root_toggled" to "True"
    And I set "scene.BIMBrickProperties.split_screen_toggled" to "True"
    When I set "scene.BIMBrickProperties.split_screen_brick_list_root" to "Location"
    Then nothing happens

Scenario: Toggle split screen
    Given an empty Blender session
    And the Brickschema is stubbed
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    When I set "scene.BIMBrickProperties.split_screen_toggled" to "True"
    Then nothing happens

Scenario: Set active namespace
    Given an empty Blender session
    And the Brickschema is stubbed
    When I set "scene.BIMBrickProperties.namespace" to "https://example.org/digitaltwin#"
    Then nothing happens

Scenario: Bind new namespace
    Given an empty Blender session
    And the Brickschema is stubbed
    And I set "scene.BIMBrickProperties.new_brick_namespace_alias" to "digitaltwin2"
    And I set "scene.BIMBrickProperties.new_brick_namespace_uri" to "https://example.org/digitaltwin2#"
    When I press "bim.add_brick_namespace"
    Then nothing happens

Scenario: Convert brick project
    Given an empty IFC project
    And the Brickschema is stubbed
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    When I press "bim.convert_brick_project"
    Then nothing happens

Scenario: Convert IFC to brick
    Given an empty IFC project
    And the Brickschema is stubbed
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And I press "bim.convert_brick_project"
    And I set "scene.BIMBrickProperties.namespace" to "https://example.org/digitaltwin#"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcUnitaryEquipment"
    And I set "scene.BIMRootProperties.ifc_predefined_type" to "AIRHANDLER"
    And I press "bim.assign_class"
    When I press "bim.convert_ifc_to_brick"
    Then nothing happens

Scenario: Assign brick reference
    Given an empty IFC project
    And the Brickschema is stubbed
    And I press "bim.load_brick_project(filepath='{cwd}/test/files/spaces.ttl')"
    And I set "scene.BIMBrickProperties.namespace" to "https://example.org/digitaltwin#"
    And I set "scene.BIMBrickProperties.brick_entity_class" to "https://brickschema.org/schema/Brick#Chiller"
    And I press "bim.add_brick"
    And I press "bim.view_brick_class(brick_class='Chiller')"
    And I set "scene.BIMBrickProperties.active_brick_index" to "0"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcChiller"
    And I press "bim.assign_class"
    And the object "IfcChiller/Cube" is selected
    And I press "bim.convert_brick_project"
    When I press "bim.assign_brick_reference"
    Then nothing happens
