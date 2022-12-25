@pset
Feature: Pset

Scenario: Add pset - object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
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
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I add a cube
    And the object "Cube" is selected
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
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I set "active_object.PsetProperties.pset_name" to "Pset_WallCommon"
    And I press "bim.add_pset(obj='IfcWall/Cube', obj_type='Object')"
    And the variable "pset" is "{ifc}.by_type('IfcPropertySet')[-1].id()"
    When I press "bim.enable_pset_editing(pset_id={pset}, obj='IfcWall/Cube', obj_type='Object')"
    Then nothing happens

Scenario: Enable pset editing - material
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_material(obj='')"
    And I set "active_object.BIMObjectMaterialProperties.material_type" to "IfcMaterial"
    And I press "bim.assign_material"
    And the object "IfcWall/Cube" is selected
    And I press "bim.add_pset(obj='Default', obj_type='Material')"
    And the variable "pset" is "{ifc}.by_type('IfcMaterialProperties')[-1].id()"
    When I press "bim.enable_pset_editing(pset_id={pset}, obj='Default', obj_type='Material')"
    Then nothing happens

Scenario: Enable pset editing - profile
    Given an empty IFC project
    And I press "bim.load_profiles"
    And I press "bim.add_profile_def"
    And I set "scene.ProfilePsetProperties.pset_name" to "Pset_ProfileMechanical"
    And I press "bim.add_pset(obj_type='Profile')"
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
    And the variable "pset" is "{ifc}.by_type('IfcPropertySet')[-1].id()"
    When I press "bim.enable_pset_editing(pset_id={pset}, obj='', obj_type='WorkSchedule')"

Scenario: Enable pset editing - resource with time series properties
    Given an empty IFC project
    And I press "bim.load_resources"
    And I press "bim.add_resource(ifc_class='IfcSubContractResource', parent_resource=0)"
    And I set "scene.ResourcePsetProperties.pset_name" to "Pset_ConstructionResource"
    And I press "bim.add_pset(obj_type='Resource')"
    And the variable "pset" is "{ifc}.by_type('IfcPropertySet')[-1].id()"
    When I press "bim.enable_pset_editing(pset_id={pset}, obj='', obj_type='Resource')"
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
    And the variable "pset" is "{ifc}.by_type('IfcElementQuantity')[-1].id()"
    When I press "bim.enable_pset_editing(pset_id={pset}, obj='', obj_type='Task')"
    Then nothing happens

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
    And I set "active_object.PsetProperties.pset_name" to "Pset_WallCommon"
    And I press "bim.add_pset(obj='IfcWall/Cube.001', obj_type='Object')"
    And the variable "pset" is "{ifc}.by_type('IfcPropertySet')[-1].id()"
    And I press "bim.enable_pset_editing(obj='IfcWall/Cube.001', obj_type='Object', pset_id={pset})"
    And I set "active_object.PsetProperties.properties[2].metadata.string_value" to "Foo"
    When I press "bim.copy_property_to_selection(name='FireRating')"
    Then nothing happens

Scenario: Remove pset - object
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I set "active_object.PsetProperties.pset_name" to "Pset_WallCommon"
    And I press "bim.add_pset(obj='IfcWall/Cube', obj_type='Object')"
    And the variable "pset" is "{ifc}.by_type('IfcPropertySet')[-1].id()"
    When I press "bim.remove_pset(pset_id={pset}, obj='IfcWall/Cube', obj_type='Object')"
    Then nothing happens

Scenario: Remove pset - multiple objects
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And additionally the object "IfcWall/Cube.001" is selected
    And I set "active_object.PsetProperties.pset_name" to "Pset_WallCommon"
    And I press "bim.add_pset(obj='IfcWall/Cube', obj_type='Object')"
    And the variable "pset" is "{ifc}.by_type('IfcPropertySet')[-1].id()"
    When I press "bim.remove_pset(pset_id={pset}, obj='IfcWall/Cube', obj_type='Object')"
    Then nothing happens
