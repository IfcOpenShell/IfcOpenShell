@pset
Feature: Pset

Scenario: Add pset - object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I set "active_object.PsetProperties.pset_name" to "Pset_WallCommon"
    When I press "bim.add_pset(obj='IfcWall/Cube', obj_type='Object')"
    Then nothing happens

Scenario: Add pset - multiple objects
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcWall/Cube.001" is selected
    And I set "active_object.PsetProperties.pset_name" to "Pset_WallCommon"
    When I press "bim.add_pset(obj='IfcWall/Cube', obj_type='Object')"
    Then nothing happens

Scenario: Enable pset editing - object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I set "active_object.PsetProperties.pset_name" to "Pset_WallCommon"
    And I press "bim.add_pset(obj='IfcWall/Cube', obj_type='Object')"
    And I set "active_object.PsetProperties.properties[0].metadata.string_value" to "Foobar"
    And I press "bim.edit_pset(obj='IfcWall/Cube', obj_type='Object')"
    And the variable "pset" is "{ifc}.by_type('IfcPropertySet')[-1].id()"
    When I press "bim.enable_pset_editing(pset_id={pset}, obj='IfcWall/Cube', obj_type='Object')"
    Then nothing happens

Scenario: Enable pset editing - material
    Given an empty IFC project
    And I press "bim.add_material()"
    And I press "bim.load_materials"
    And I press "bim.expand_material_category(category='Uncategorised')"
    And I set "scene.BIMMaterialProperties.active_material_index" to "1"
    And I set "scene.MaterialPsetProperties.pset_name" to "Pset_MaterialCommon"
    And I press "bim.add_pset(obj='', obj_type='Material')"
    And I set "scene.MaterialPsetProperties.properties[0].metadata.float_value" to "0.42"
    And I press "bim.edit_pset(obj='', obj_type='Material')"
    And the variable "pset" is "{ifc}.by_type('IfcMaterialProperties')[-1].id()"
    When I press "bim.enable_pset_editing(pset_id={pset}, obj='', obj_type='Material')"
    Then nothing happens

Scenario: Enable pset editing - profile
    Given an empty IFC project
    And I press "bim.load_profiles"
    And I press "bim.add_profile_def"
    And I set "scene.ProfilePsetProperties.pset_name" to "Pset_ProfileMechanical"
    And I press "bim.add_pset(obj_type='Profile')"
    And I set "scene.ProfilePsetProperties.properties[0].metadata.float_value" to "0.42"
    And I press "bim.edit_pset(obj='', obj_type='Profile')"
    And the variable "pset" is "{ifc}.by_type('IfcProfileProperties')[-1].id()"
    When I press "bim.enable_pset_editing(pset_id={pset}, obj='', obj_type='Profile')"
    Then nothing happens

Scenario: Enable pset editing - work schedule
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "{ifc}.by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I set "scene.WorkSchedulePsetProperties.pset_name" to "Pset_WorkControlCommon"
    And I press "bim.add_pset(obj_type='WorkSchedule')"
    And I set "scene.WorkSchedulePsetProperties.properties[0].metadata.string_value" to "Foobar"
    And I press "bim.edit_pset(obj='', obj_type='WorkSchedule')"
    And the variable "pset" is "{ifc}.by_type('IfcPropertySet')[-1].id()"
    When I press "bim.enable_pset_editing(pset_id={pset}, obj='', obj_type='WorkSchedule')"
    Then nothing happens

Scenario: Enable pset editing - resource with time series properties
    Given an empty IFC project
    And I press "bim.load_resources"
    And I press "bim.add_resource(ifc_class='IfcSubContractResource', parent_resource=0)"
    And I set "scene.ResourcePsetProperties.pset_name" to "Pset_ConstructionResource"
    When I press "bim.add_pset(obj_type='Resource')"
    Then nothing happens

Scenario: Enable pset editing - resource with regular single properties
    Given an empty IFC project
    And I press "bim.load_resources"
    And I press "bim.add_resource(ifc_class='IfcCrewResource', parent_resource=0)"
    And the variable "resource" is "{ifc}.by_type('IfcCrewResource')[-1].id()"
    And I press "bim.add_resource(ifc_class='IfcLaborResource', parent_resource={resource})"
    And I set "scene.BIMResourceProperties.active_resource_index" to "1"
    And I set "scene.ResourcePsetProperties.pset_name" to "EPset_Productivity"
    And I press "bim.add_pset(obj_type='Resource')"
    And I set "scene.ResourcePsetProperties.properties[0].metadata.string_value" to "Foobar"
    And I press "bim.edit_pset(obj='', obj_type='Resource')"
    And the variable "pset" is "{ifc}.by_type('IfcPropertySet')[-1].id()"
    When I press "bim.enable_pset_editing(pset_id={pset}, obj='', obj_type='Resource')"
    Then nothing happens

Scenario: Enable pset editing - task
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And I set "scene.TaskPsetProperties.qto_name" to "Qto_TaskBaseQuantities"
    And I press "bim.add_qto(obj_type='Task')"
    And I set "scene.TaskPsetProperties.properties[0].metadata.float_value" to "0.42"
    And I press "bim.edit_pset(obj='', obj_type='Task')"
    And the variable "pset" is "{ifc}.by_type('IfcElementQuantity')[-1].id()"
    When I press "bim.enable_pset_editing(pset_id={pset}, obj='', obj_type='Task')"
    Then nothing happens

Scenario: Disable pset editing - object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I set "active_object.PsetProperties.pset_name" to "Pset_WallCommon"
    And I press "bim.add_pset(obj='IfcWall/Cube', obj_type='Object')"
    When I press "bim.disable_pset_editing(obj='IfcWall/Cube', obj_type='Object')"
    Then nothing happens

Scenario: Disable pset editing - material
    Given an empty IFC project
    And I press "bim.add_material()"
    And I press "bim.load_materials"
    And I press "bim.expand_material_category(category='Uncategorised')"
    And I set "scene.BIMMaterialProperties.active_material_index" to "1"
    And I press "bim.add_pset(obj='Default', obj_type='Material')"
    When I press "bim.disable_pset_editing(obj='Default', obj_type='Material')"
    Then nothing happens

Scenario: Disable pset editing - profile
    Given an empty IFC project
    And I press "bim.load_profiles"
    And I press "bim.add_profile_def"
    And I set "scene.ProfilePsetProperties.pset_name" to "Pset_ProfileMechanical"
    And I press "bim.add_pset(obj_type='Profile')"
    When I press "bim.disable_pset_editing(obj='', obj_type='Profile')"
    Then nothing happens

Scenario: Disable pset editing - work schedule
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "{ifc}.by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I set "scene.WorkSchedulePsetProperties.pset_name" to "Pset_WorkControlCommon"
    And I press "bim.add_pset(obj_type='WorkSchedule')"
    When I press "bim.disable_pset_editing(obj='', obj_type='WorkSchedule')"
    Then nothing happens

Scenario: Disable pset editing - resource with time series properties
    Given an empty IFC project
    And I press "bim.load_resources"
    And I press "bim.add_resource(ifc_class='IfcSubContractResource', parent_resource=0)"
    And I set "scene.ResourcePsetProperties.pset_name" to "Pset_ConstructionResource"
    And I press "bim.add_pset(obj_type='Resource')"
    When I press "bim.disable_pset_editing(obj='', obj_type='Resource')"
    Then nothing happens

Scenario: Disable pset editing - resource with regular single properties
    Given an empty IFC project
    And I press "bim.load_resources"
    And I press "bim.add_resource(ifc_class='IfcCrewResource', parent_resource=0)"
    And the variable "resource" is "{ifc}.by_type('IfcCrewResource')[-1].id()"
    And I press "bim.add_resource(ifc_class='IfcLaborResource', parent_resource={resource})"
    And I set "scene.BIMResourceProperties.active_resource_index" to "1"
    And I set "scene.ResourcePsetProperties.pset_name" to "EPset_Productivity"
    And I press "bim.add_pset(obj_type='Resource')"
    When I press "bim.disable_pset_editing(obj='', obj_type='Resource')"
    Then nothing happens

Scenario: Disable pset editing - task
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And I set "scene.TaskPsetProperties.qto_name" to "Qto_TaskBaseQuantities"
    And I press "bim.add_qto(obj_type='Task')"
    When I press "bim.disable_pset_editing(obj='', obj_type='Task')"
    Then nothing happens

Scenario: Edit pset - object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I set "active_object.PsetProperties.pset_name" to "Pset_WallCommon"
    And I press "bim.add_pset(obj='IfcWall/Cube', obj_type='Object')"
    When I press "bim.edit_pset(obj='IfcWall/Cube', obj_type='Object')"
    Then nothing happens

Scenario: Edit qto - object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I set "active_object.PsetProperties.qto_name" to "Qto_WallBaseQuantities"
    When I press "bim.add_qto(obj='IfcWall/Cube', obj_type='Object')"
    And I set "active_object.PsetProperties.properties[0].metadata.float_value" to "0.42"
    And I press "bim.edit_pset(obj='IfcWall/Cube', obj_type='Object')"
    Then nothing happens

Scenario: Edit pset - material
    Given an empty IFC project
    And I press "bim.add_material()"
    And I press "bim.load_materials"
    And I press "bim.expand_material_category(category='Uncategorised')"
    And I set "scene.BIMMaterialProperties.active_material_index" to "1"
    And I press "bim.add_pset(obj='', obj_type='Material')"
    When I press "bim.edit_pset(obj='', obj_type='Material')"
    Then nothing happens

Scenario: Edit pset - profile
    Given an empty IFC project
    And I press "bim.load_profiles"
    And I press "bim.add_profile_def"
    And I set "scene.ProfilePsetProperties.pset_name" to "Pset_ProfileMechanical"
    And I press "bim.add_pset(obj_type='Profile')"
    When I press "bim.edit_pset(obj='', obj_type='Profile')"
    Then nothing happens

Scenario: Edit pset - work schedule
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "{ifc}.by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I set "scene.WorkSchedulePsetProperties.pset_name" to "Pset_WorkControlCommon"
    And I press "bim.add_pset(obj_type='WorkSchedule')"
    When I press "bim.edit_pset(obj='', obj_type='WorkSchedule')"
    Then nothing happens

Scenario: Edit pset - resource with time series properties
    Given an empty IFC project
    And I press "bim.load_resources"
    And I press "bim.add_resource(ifc_class='IfcSubContractResource', parent_resource=0)"
    And I set "scene.ResourcePsetProperties.pset_name" to "Pset_ConstructionResource"
    And I press "bim.add_pset(obj_type='Resource')"
    When I press "bim.edit_pset(obj='', obj_type='Resource')"
    Then nothing happens

Scenario: Edit pset - resource with regular single properties
    Given an empty IFC project
    And I press "bim.load_resources"
    And I press "bim.add_resource(ifc_class='IfcCrewResource', parent_resource=0)"
    And the variable "resource" is "{ifc}.by_type('IfcCrewResource')[-1].id()"
    And I press "bim.add_resource(ifc_class='IfcLaborResource', parent_resource={resource})"
    And I set "scene.BIMResourceProperties.active_resource_index" to "1"
    And I set "scene.ResourcePsetProperties.pset_name" to "EPset_Productivity"
    And I press "bim.add_pset(obj_type='Resource')"
    When I press "bim.edit_pset(obj='', obj_type='Resource')"
    Then nothing happens

Scenario: Edit pset - task
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And I set "scene.TaskPsetProperties.qto_name" to "Qto_TaskBaseQuantities"
    And I press "bim.add_qto(obj_type='Task')"
    When I press "bim.edit_pset(obj='', obj_type='Task')"
    Then nothing happens

Scenario: Copy property to selected - copy property
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcWall/Cube.001" is selected
    And I set "active_object.PsetProperties.pset_name" to "Pset_WallCommon"
    And I press "bim.add_pset(obj='IfcWall/Cube.001', obj_type='Object')"
    And I set "active_object.PsetProperties.properties[2].metadata.string_value" to "Foo"
    When I press "bim.copy_property_to_selection(name='FireRating')"
    Then nothing happens

Scenario: Remove pset - object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I set "active_object.PsetProperties.pset_name" to "Pset_WallCommon"
    And I press "bim.add_pset(obj='IfcWall/Cube', obj_type='Object')"
    And I set "active_object.PsetProperties.properties[0].metadata.string_value" to "Foobar"
    And I press "bim.edit_pset(obj='IfcWall/Cube', obj_type='Object')"
    And the variable "pset" is "{ifc}.by_type('IfcPropertySet')[-1].id()"
    When I press "bim.remove_pset(pset_id={pset}, obj='IfcWall/Cube', obj_type='Object')"
    Then nothing happens

Scenario: Remove pset - multiple objects
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcWall/Cube.001" is selected
    And I set "active_object.PsetProperties.pset_name" to "Pset_WallCommon"
    And I press "bim.add_pset(obj='IfcWall/Cube.001', obj_type='Object')"
    And I set "active_object.PsetProperties.properties[0].metadata.string_value" to "Foobar"
    And I press "bim.edit_pset(obj='IfcWall/Cube.001', obj_type='Object')"
    And the variable "pset" is "{ifc}.by_type('IfcPropertySet')[-1].id()"
    When I press "bim.remove_pset(pset_id={pset}, obj='IfcWall/Cube', obj_type='Object')"
    Then nothing happens

Scenario: Edit pset length property
    Given an empty IFC project
    And I press "mesh.add_stair"
    And the variable "pset" is "tool.Pset.get_element_pset(tool.Ifc.get_entity(bpy.context.active_object), 'Pset_StairFlightCommon').id()"
    And the variable "si_conversion" is "ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())"
    And I press "bim.enable_pset_editing(pset_id={pset}, obj='IfcStairFlight/StairFlight', obj_type='Object')"

    # Testing IfcPositiveLengthMeasure type of prop
    Then "active_object.PsetProperties.properties['TreadLength'].metadata.special_type" is "LENGTH"
    And "active_object.PsetProperties.properties['TreadLength'].metadata.float_value" is "250"
    And "active_object.PsetProperties.properties['TreadLength'].metadata.length_value" is roughly "0.25"

    When I set "active_object.PsetProperties.properties['TreadLength'].metadata.float_value" to "350"
    Then "active_object.PsetProperties.properties['TreadLength'].metadata.float_value" is roughly "350"

    When I set "active_object.PsetProperties.properties['TreadLength'].metadata.length_value" to "0.45"
    Then "active_object.PsetProperties.properties['TreadLength'].metadata.float_value" is roughly "450"

    # Testing IfcLengthMeasure type of prop
    Then "active_object.PsetProperties.properties['NosingLength'].metadata.special_type" is "LENGTH"
    And "active_object.PsetProperties.properties['NosingLength'].metadata.float_value" is "0.0"
    And "active_object.PsetProperties.properties['NosingLength'].metadata.length_value" is roughly "0.0"

    When I set "active_object.PsetProperties.properties['NosingLength'].metadata.float_value" to "350"
    Then "active_object.PsetProperties.properties['NosingLength'].metadata.float_value" is roughly "350"

    When I set "active_object.PsetProperties.properties['NosingLength'].metadata.length_value" to "0.45"
    Then "active_object.PsetProperties.properties['NosingLength'].metadata.float_value" is roughly "450"

    When I press "bim.edit_pset(obj='IfcStairFlight/StairFlight', obj_type='Object')"
    Then nothing happens

Scenario: Edit qset length property
    Given an empty IFC project
    And I press "mesh.add_stair"
    And I press "bim.perform_quantity_take_off"
    And the variable "pset" is "tool.Pset.get_element_pset(tool.Ifc.get_entity(bpy.context.active_object), 'Qto_StairFlightBaseQuantities').id()"
    And the variable "si_conversion" is "ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())"
    And I press "bim.enable_pset_editing(pset_id={pset}, obj='IfcStairFlight/StairFlight', obj_type='Object')"

    # Testing Q_LENGTH type of prop
    Then "active_object.PsetProperties.properties['Length'].metadata.special_type" is "LENGTH"
    And "active_object.PsetProperties.properties['Length'].metadata.float_value" is roughly "2156.485"
    And "active_object.PsetProperties.properties['Length'].metadata.length_value" is roughly "2.156"

    When I set "active_object.PsetProperties.properties['Length'].metadata.float_value" to "350"
    Then "active_object.PsetProperties.properties['Length'].metadata.length_value" is roughly "0.35"

    When I set "active_object.PsetProperties.properties['Length'].metadata.length_value" to "0.45"
    Then "active_object.PsetProperties.properties['Length'].metadata.float_value" is roughly "450"

    When I press "bim.edit_pset(obj='IfcStairFlight/StairFlight', obj_type='Object')"
    Then nothing happens
