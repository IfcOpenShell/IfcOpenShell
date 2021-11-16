@pset
Feature: Pset

Scenario: Copy property to selected - copy property
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcWall/Cube.001" is selected
    And I set "active_object.PsetProperties.pset_name" to "Pset_BuildingElementCommon"
    And I press "bim.add_pset(obj='IfcWall/Cube.001', obj_type='Object')"
    And the variable "pset" is "{ifc}.by_type('IfcPropertySet')[-1].id()"
    And I press "bim.enable_pset_editing(obj='IfcWall/Cube.001', obj_type='Object', pset_id={pset})"
    And I set "active_object.PsetProperties.properties[2].string_value" to "Foo"
    When I press "bim.copy_property_to_selection(name='FireRating')"
    Then nothing happens

Scenario: Copy property to selected - copy quantity
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcWall/Cube.001" is selected
    And I set "active_object.PsetProperties.pset_name" to "Pset_BuildingElementCommon"
    And I press "bim.add_qto(obj='IfcWall/Cube.001', obj_type='Object')"
    And the variable "qto" is "{ifc}.by_type('IfcQuantitySet')[-1].id()"
    And I press "bim.enable_pset_editing(obj='IfcWall/Cube.001', obj_type='Object', pset_id={qto})"
    And I set "active_object.PsetProperties.properties[0].float_value" to "1"
    When I press "bim.copy_property_to_selection(name='Length')"
    Then nothing happens
