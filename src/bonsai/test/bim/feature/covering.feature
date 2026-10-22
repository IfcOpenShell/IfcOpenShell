@covering
Feature: Covering
    Covers covering tool.

Scenario: Add flooring from walls
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    # 1st wall
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And I press "bim.change_layer_length(length=3.6)"
    # 2nd wall
    And the cursor is at "3.6,0.1,3"
    And I set "scene.BIMModelProperties.length" to "2.0"
    And I press "bim.add_occurrence"
    # 3rd wall
    And the cursor is at "3.5,2.1,3"
    And I set "scene.BIMModelProperties.length" to "3.5"
    And I press "bim.add_occurrence"
    # 4th wall
    And the cursor is at "0,2.0,0"
    And I set "scene.BIMModelProperties.length" to "1.9"
    And I press "bim.add_occurrence"
    # Set COV30 predefined type to FLOORING.
    And the object "IfcCoveringType/COV30" is selected
    And I look at the "Object Attributes" panel
    And I click "Edit"
    And I set the "PredefinedType" property to "FLOORING"
    And I click "Save Attributes"
    # Run the operator.
    When the object "IfcWall/Wall" is selected
    And additionally the object "IfcWall/Wall.001" is selected
    And additionally the object "IfcWall/Wall.002" is selected
    And additionally the object "IfcWall/Wall.003" is selected
    And I set "scene.BIMModelProperties.ifc_class" to "IfcCoveringType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcCoveringType') if e.Name == 'COV30'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_instance_flooring_coverings_from_walls"
    Then the object "IfcCovering/Covering0" exists
    And the object "IfcCovering/Covering0" is at "1.8,1.05,0.0"
    And the object "IfcCovering/Covering0" dimensions are "3.4,1.9,0.03"

Scenario: Add ceiling from walls
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And I press "bim.change_layer_length(length=3.6)"
    And the cursor is at "3.6,0.1,3"
    And I set "scene.BIMModelProperties.length" to "2.0"
    And I press "bim.add_occurrence"
    And the cursor is at "3.5,2.1,3"
    And I set "scene.BIMModelProperties.length" to "3.5"
    And I press "bim.add_occurrence"
    And the cursor is at "0,2.0,0"
    And I set "scene.BIMModelProperties.length" to "1.9"
    And I press "bim.add_occurrence"
    # Set COV30 predefined type to CEILING.
    And the object "IfcCoveringType/COV30" is selected
    And I look at the "Object Attributes" panel
    And I click "Edit"
    And I set the "PredefinedType" property to "CEILING"
    And I click "Save Attributes"
    # Run the operator with ceiling height = 2.7 (default).
    When the object "IfcWall/Wall" is selected
    And additionally the object "IfcWall/Wall.001" is selected
    And additionally the object "IfcWall/Wall.002" is selected
    And additionally the object "IfcWall/Wall.003" is selected
    And I set "scene.BIMModelProperties.ifc_class" to "IfcCoveringType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcCoveringType') if e.Name == 'COV30'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_instance_ceiling_coverings_from_walls"
    Then the object "IfcCovering/Covering0" exists
    And the object "IfcCovering/Covering0" is at "1.8,1.05,2.7"
    And the object "IfcCovering/Covering0" dimensions are "3.4,1.9,0.03"

Scenario: Add flooring from cursor
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the cursor is at "1.1,0,0"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall.001" is selected
    And I press "bim.hotkey(hotkey='S_R')"
    And the cursor is at "0,.9,0"
    And I press "bim.add_occurrence"
    And the cursor is at "-1,0,0"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall.003" is selected
    And I press "bim.hotkey(hotkey='S_R')"
    And the object "IfcWall/Wall.003" is moved to "0,0,0"
    # Set COV30 predefined type to FLOORING.
    And the object "IfcCoveringType/COV30" is selected
    And I look at the "Object Attributes" panel
    And I click "Edit"
    And I set the "PredefinedType" property to "FLOORING"
    And I click "Save Attributes"
    # Generate covering from cursor inside the room.
    When the cursor is at "0.5,0.5,0"
    And I deselect all objects
    And I set "scene.BIMModelProperties.ifc_class" to "IfcCoveringType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcCoveringType') if e.Name == 'COV30'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_instance_flooring_covering_from_cursor"
    Then the object "IfcCovering/Covering" exists
    And the object "IfcCovering/Covering" dimensions are "1,0.8,0.03"

Scenario: Add ceiling from cursor
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the cursor is at "1.1,0,0"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall.001" is selected
    And I press "bim.hotkey(hotkey='S_R')"
    And the cursor is at "0,.9,0"
    And I press "bim.add_occurrence"
    And the cursor is at "-1,0,0"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall.003" is selected
    And I press "bim.hotkey(hotkey='S_R')"
    And the object "IfcWall/Wall.003" is moved to "0,0,0"
    # Set COV30 predefined type to CEILING.
    And the object "IfcCoveringType/COV30" is selected
    And I look at the "Object Attributes" panel
    And I click "Edit"
    And I set the "PredefinedType" property to "CEILING"
    And I click "Save Attributes"
    # Generate covering from cursor inside the room.
    When the cursor is at "0.5,0.5,0"
    And I deselect all objects
    And I set "scene.BIMModelProperties.ifc_class" to "IfcCoveringType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcCoveringType') if e.Name == 'COV30'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_instance_ceiling_covering_from_cursor"
    Then the object "IfcCovering/Covering" exists
    And the object "IfcCovering/Covering" dimensions are "1,0.8,0.03"

Scenario: Add wall covering from a single wall on the side facing the cursor
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And I press "bim.change_layer_length(length=2.4)"
    # Set COV30 predefined type to CLADDING.
    And the object "IfcCoveringType/COV30" is selected
    And I look at the "Object Attributes" panel
    And I click "Edit"
    And I set the "PredefinedType" property to "CLADDING"
    And I click "Save Attributes"
    # Cursor on the wall's +Y side.
    When the cursor is at "1.2,0.5,1.0"
    And the object "IfcWall/Wall" is selected
    And I set "scene.BIMModelProperties.ifc_class" to "IfcCoveringType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcCoveringType') if e.Name == 'COV30'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_instance_wall_coverings_from_walls"
    Then the object "IfcCovering/Covering" exists
    And the object "IfcCovering/Covering" is at "1.2,0.1,1.5"
    And the object "IfcCovering/Covering" dimensions are "2.4,3.0,0.03"
    And the object "IfcCovering/Covering" is an "IfcCovering"
    And the object "IfcCovering/Covering" is contained in "My Storey"
    And the variable "covering_type_name" is "ifcopenshell.util.element.get_type({ifc}.by_id(tool.Blender.get_ifc_definition_id(bpy.data.objects['IfcCovering/Covering']))).Name"
    Then the variable "covering_type_name" equals "'COV30'"

Scenario: Add wall covering from a single wall on the side away from the cursor
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And I press "bim.change_layer_length(length=2.4)"
    # Set COV30 predefined type to CLADDING.
    And the object "IfcCoveringType/COV30" is selected
    And I look at the "Object Attributes" panel
    And I click "Edit"
    And I set the "PredefinedType" property to "CLADDING"
    And I click "Save Attributes"
    # Cursor is still on the +Y side, but "Facing Cursor" is unchecked, so the
    # covering must land on the opposite (-Y, i.e. y=0) face instead.
    When the cursor is at "1.2,0.5,1.0"
    And the object "IfcWall/Wall" is selected
    And I set "scene.BIMModelProperties.ifc_class" to "IfcCoveringType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcCoveringType') if e.Name == 'COV30'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_instance_wall_coverings_from_walls(facing_cursor=False)"
    Then the object "IfcCovering/Covering" exists
    And the object "IfcCovering/Covering" is at "1.2,0.0,1.5"
    And the object "IfcCovering/Covering" dimensions are "2.4,3.0,0.03"

Scenario: Add wall coverings from multiple selected walls
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcWallType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcWallType') if e.Name == 'WAL100'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    # 1st wall
    And I press "bim.add_occurrence"
    And the object "IfcWall/Wall" is selected
    And I press "bim.change_layer_length(length=3.6)"
    # 2nd wall
    And the cursor is at "3.6,0.1,3"
    And I set "scene.BIMModelProperties.length" to "2.0"
    And I press "bim.add_occurrence"
    # 3rd wall
    And the cursor is at "3.5,2.1,3"
    And I set "scene.BIMModelProperties.length" to "3.5"
    And I press "bim.add_occurrence"
    # 4th wall
    And the cursor is at "0,2.0,0"
    And I set "scene.BIMModelProperties.length" to "1.9"
    And I press "bim.add_occurrence"
    # Set COV30 predefined type to CLADDING.
    And the object "IfcCoveringType/COV30" is selected
    And I look at the "Object Attributes" panel
    And I click "Edit"
    And I set the "PredefinedType" property to "CLADDING"
    And I click "Save Attributes"
    # Run the operator on all 4 walls at once.
    When the object "IfcWall/Wall" is selected
    And additionally the object "IfcWall/Wall.001" is selected
    And additionally the object "IfcWall/Wall.002" is selected
    And additionally the object "IfcWall/Wall.003" is selected
    And I set "scene.BIMModelProperties.ifc_class" to "IfcCoveringType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcCoveringType') if e.Name == 'COV30'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_instance_wall_coverings_from_walls"
    Then the object "IfcCovering/Covering" exists
    And the object "IfcCovering/Covering.001" exists
    And the object "IfcCovering/Covering.002" exists
    And the object "IfcCovering/Covering.003" exists
    And the object "IfcCovering/Covering" is contained in "My Storey"
    And the object "IfcCovering/Covering.001" is contained in "My Storey"
    And the object "IfcCovering/Covering.002" is contained in "My Storey"
    And the object "IfcCovering/Covering.003" is contained in "My Storey"
    And the variable "covering_count" is "len([o for o in bpy.data.objects if o.name.startswith('IfcCovering/')])"
    Then the variable "covering_count" equals "4"

Scenario: Add wall covering does nothing when the selection has no wall
    Given an empty IFC project
    And I load the demo construction library
    And I set "scene.BIMModelProperties.ifc_class" to "IfcSlabType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcSlabType')][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    And I press "bim.add_occurrence"
    # Set COV30 predefined type to CLADDING.
    And the object "IfcCoveringType/COV30" is selected
    And I look at the "Object Attributes" panel
    And I click "Edit"
    And I set the "PredefinedType" property to "CLADDING"
    And I click "Save Attributes"
    When the object "IfcSlab/Slab" is selected
    And I set "scene.BIMModelProperties.ifc_class" to "IfcCoveringType"
    And the variable "element_type" is "[e for e in {ifc}.by_type('IfcCoveringType') if e.Name == 'COV30'][0].id()"
    And I set "scene.BIMModelProperties.relating_type_id" to "{element_type}"
    Then I press "bim.add_instance_wall_coverings_from_walls" and expect error "Operator bpy.ops.bim.add_instance_wall_coverings_from_walls.poll() LAYER2 based IfcWall must be selected."
    And the object "IfcCovering/Covering" does not exist
