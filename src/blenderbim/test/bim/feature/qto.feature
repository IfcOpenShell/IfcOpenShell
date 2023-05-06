@qto
Feature: Qto

Scenario: Calculate circle radius
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.calculate_circle_radius"
    Then "scene.BIMQtoProperties.qto_result" is "1.732"

Scenario: Calculate edge lengths
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.calculate_edge_lengths"
    Then "scene.BIMQtoProperties.qto_result" is "24.0"

Scenario: Calculate face areas
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.calculate_face_areas"
    Then "scene.BIMQtoProperties.qto_result" is "24.0"

Scenario: Calculate object volumes
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I press "bim.calculate_object_volumes"
    Then "scene.BIMQtoProperties.qto_result" is "8.0"

Scenario: Execute qto method - formwork areas
    Given an empty Blender session
    And I add a cube
    And I add a cube of size "1" at "1,0,0"
    And the object "Cube" is selected
    And additionally the object "Cube.001" is selected
    When I set "scene.BIMQtoProperties.qto_methods" to "FORMWORK"
    And I press "bim.execute_qto_method"
    Then "scene.BIMQtoProperties.qto_result" is "21.5"

Scenario: Execute qto method - side formwork areas
    Given an empty Blender session
    And I add a cube
    And the object "Cube" is selected
    When I set "scene.BIMQtoProperties.qto_methods" to "SIDE_FORMWORK"
    And I press "bim.execute_qto_method"
    Then "scene.BIMQtoProperties.qto_result" is "16.0"

 Scenario: Assign objects base qto
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I press "bim.assign_class(ifc_class='IfcWall', predefined_type='SOLIDWALL')"
    When I press "bim.assign_objects_base_qto"
    Then "active_object.PsetProperties.qto_name" is "Qto_WallBaseQuantities"

Scenario: Calculate all quantities
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I press "bim.assign_class(ifc_class='IfcWall', predefined_type='SOLIDWALL')"
    When I press "bim.calculate_all_quantities"
    And the variable "qset_id" is "{ifc}.by_type('IfcElementQuantity')[0].id()"
    And I press "bim.enable_pset_editing(pset_id={qset_id}, obj='IfcWall/Cube', obj_type='Object')"
    And I press "bim.disable_pset_editing(obj='IfcWall/Cube', obj_type='Object')"
    Then "active_object.PsetProperties.qto_name" is "Qto_WallBaseQuantities"
    Then "active_object.PsetProperties.properties['Length'].metadata.float_value" is "2000.0"
