@system
Feature: System

Scenario: Load systems
    Given an empty IFC project
    When I press "bim.load_systems"
    Then nothing happens

Scenario: Disable system editing UI
    Given an empty IFC project
    When I press "bim.load_systems"
    And I press "bim.disable_system_editing_ui"
    Then nothing happens

Scenario: Add system
    Given an empty IFC project
    And I press "bim.load_systems"
    When I press "bim.add_system"
    Then nothing happens

Scenario: Edit system
    Given an empty IFC project
    And I press "bim.load_systems"
    And I press "bim.add_system"
    And the variable "system" is "{ifc}.by_type('IfcSystem')[0].id()"
    And I press "bim.enable_editing_system(system={system})"
    When I press "bim.edit_system"
    Then nothing happens

Scenario: Edit system
    Given an empty IFC project
    And I press "bim.load_systems"
    And I press "bim.add_system"
    And the variable "system" is "{ifc}.by_type('IfcSystem')[0].id()"
    When I press "bim.remove_system(system={system})"
    Then nothing happens

Scenario: Enable editing system
    Given an empty IFC project
    And I press "bim.load_systems"
    And I press "bim.add_system"
    And the variable "system" is "{ifc}.by_type('IfcSystem')[0].id()"
    When I press "bim.enable_editing_system(system={system})"
    Then nothing happens

Scenario: Disable editing system
    Given an empty IFC project
    And I press "bim.load_systems"
    And I press "bim.add_system"
    And the variable "system" is "{ifc}.by_type('IfcSystem')[0].id()"
    And I press "bim.enable_editing_system(system={system})"
    When I press "bim.disable_editing_system"
    Then nothing happens

Scenario: Assign system
    Given an empty IFC project
    And I press "bim.load_systems"
    And I set "scene.BIMSystemProperties.system_class" to "IfcDistributionSystem"
    And I press "bim.add_system"
    And the variable "system" is "{ifc}.by_type('IfcSystem')[0].id()"
    And I press "bim.enable_editing_system(system={system})"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcPump"
    And I press "bim.assign_class"
    And the object "IfcPump/Cube" is selected
    When I press "bim.assign_system(system={system})"
    Then nothing happens

Scenario: Unassign system
    Given an empty IFC project
    And I press "bim.load_systems"
    And I set "scene.BIMSystemProperties.system_class" to "IfcDistributionSystem"
    And I press "bim.add_system"
    And the variable "system" is "{ifc}.by_type('IfcSystem')[0].id()"
    And I press "bim.enable_editing_system(system={system})"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcPump"
    And I press "bim.assign_class"
    And the object "IfcPump/Cube" is selected
    And I press "bim.assign_system(system={system})"
    When I press "bim.unassign_system(system={system})"
    Then nothing happens

Scenario: Select system products
    Given an empty IFC project
    And I press "bim.load_systems"
    And I set "scene.BIMSystemProperties.system_class" to "IfcDistributionSystem"
    And I press "bim.add_system"
    And the variable "system" is "{ifc}.by_type('IfcSystem')[0].id()"
    And I press "bim.enable_editing_system(system={system})"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcPump"
    And I press "bim.assign_class"
    And the object "IfcPump/Cube" is selected
    And I press "bim.assign_system(system={system})"
    When I press "bim.select_system_products(system={system})"
    Then nothing happens

Scenario: Assign flow controls to flow element_type
    Given an empty IFC project
    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcActuator"
    And I press "bim.assign_class"

    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcActuator"
    And I press "bim.assign_class"

    And I add an empty
    And the object "Empty" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcFlowSegment"
    And I press "bim.assign_class"

    And the object "IfcActuator/Empty" is selected
    And additionally the object "IfcActuator/Empty.001" is selected
    And additionally the object "IfcFlowSegment/Empty" is selected
    When I press "bim.assign_unassign_flow_control(assign=True)"
    And the variable "assigned_controls" is "set(tool.System.get_flow_element_controls({ifc}.by_type('IfcFlowSegment')[0]))"
    Then the variable "assigned_controls" is "set({ifc}.by_type('IfcActuator'))"

Scenario: Connect MEP elements
    Given an empty IFC project
    And I create default MEP types
    And the variable "segment_types" is "[str(e.id()) for e in {ifc}.by_type('IfcDuctSegmentType')]"
    And the variable "actuator_type_id" is "{ifc}.by_type('IfcActuatorType')[0].id()"

    # segment 1
    And I set "scene.BIMModelProperties.ifc_class" to "IfcDuctSegmentType"
    And I set "scene.BIMModelProperties.relating_type_id" to "{segment_types}[0]"
    And I set "scene.BIMModelProperties.extrusion_depth" to "5.0"
    And I press "bim.add_constr_type_instance"
    And I rename the object "IfcDuctSegment/DuctSegment" to "IfcDuctSegment/Seg1"

    # actuator
    And I set "scene.BIMModelProperties.ifc_class" to "IfcActuatorType"
    And I set "scene.BIMModelProperties.relating_type_id" to "{actuator_type_id}"
    And I press "bim.add_constr_type_instance"
    And the object "IfcActuator/Actuator" is moved to "10,0,0"

    # connect actuator
    And the object "IfcActuator/Actuator" is selected
    And additionally the object "IfcDuctSegment/Seg1" is selected
    And I press "bim.mep_connect_elements"

    # final check
    Then the object "IfcDuctSegment/Seg1" is at "0,0,1"
    And the object "IfcDuctSegment/Seg1" dimensions are "0.4,0.2,5.0"
    And the object "IfcActuator/Actuator" is at "5.5,0.0,1.0"
    And the variable "connected_elements" is "set(tool.System.get_connected_elements({ifc}.by_type('IfcActuator')[0]))"

Scenario: Connect MEP elements and regenerate
    Given an empty IFC project
    And I create default MEP types
    And the variable "segment_types" is "[str(e.id()) for e in {ifc}.by_type('IfcDuctSegmentType')]"
    And the variable "actuator_type_id" is "{ifc}.by_type('IfcActuatorType')[0].id()"

    # segment1
    And I set "scene.BIMModelProperties.ifc_class" to "IfcDuctSegmentType"
    And I set "scene.BIMModelProperties.relating_type_id" to "{segment_types}[0]"
    And I set "scene.BIMModelProperties.extrusion_depth" to "5.0"
    And I press "bim.add_constr_type_instance"
    And I rename the object "IfcDuctSegment/DuctSegment" to "IfcDuctSegment/Seg1"

    # segment2
    And I set "scene.BIMModelProperties.relating_type_id" to "{segment_types}[0]"
    And I press "bim.add_constr_type_instance"
    And I rename the object "IfcDuctSegment/DuctSegment" to "IfcDuctSegment/Seg2"
    And the object "IfcDuctSegment/Seg2" is rotated by "0,0,90" deg

    # bend between segments 1 and 2
    And the object "IfcDuctSegment/Seg1" is selected
    And additionally the object "IfcDuctSegment/Seg2" is selected
    And I press "bim.mep_add_bend"

    # actuator
    And I set "scene.BIMModelProperties.ifc_class" to "IfcActuatorType"
    And I set "scene.BIMModelProperties.relating_type_id" to "{actuator_type_id}"
    And I press "bim.add_constr_type_instance"
    And the object "IfcActuator/Actuator" is moved to "10,0,0"

    # connect actuator
    And the object "IfcActuator/Actuator" is selected
    And additionally the object "IfcDuctSegment/Seg1" is selected
    And I press "bim.mep_connect_elements"

    # move and regenerate
    And the object "IfcActuator/Actuator" is moved to "0.0,5.0,10"
    And the object "IfcActuator/Actuator" is selected
    And I press "bim.regenerate_distribution_element"

    # final check
    Then the object "IfcActuator/Actuator" is at "0.0,5.0,10"
    And the object "IfcDuctSegment/Seg1" is at "-6.0,5.0,10.0"
    And the object "IfcDuctSegment/Seg1" dimensions are "0.4,0.2,5.5"
    And the object "IfcDuctFitting/DuctFitting" is at "-6.5,5.5,10.0"
    And the object "IfcDuctSegment/Seg2" is at "-6.5,5.5,10.0"
    And the object "IfcDuctSegment/Seg2" dimensions are "0.4,0.2,5.0"
