@sequence
Feature: Sequence

Scenario: Add work plan
    Given an empty IFC project
    When I press "bim.add_work_plan"
    Then nothing happens

Scenario: Enable editing task
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    When I press "bim.enable_editing_task(task={task})"
    Then nothing happens

Scenario: Copy task attribute
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_attributes[2].string_value" to "Foo"
    When I set "scene.BIMTaskTreeProperties.tasks[1].is_selected" to "True"
    And I press "bim.copy_task_attribute(name='Description')"
    Then nothing happens

Scenario: See the current frame date as text
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_tasks(work_schedule={work_schedule})"
    And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
    And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
    And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
    And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
    And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "P1W"
    And I press "bim.visualise_work_schedule_date_range(work_schedule={work_schedule})"
    When I am on frame "1"
    Then the object "Timeline" has a body of "2021-01-01"
    When I am on frame "2"
    Then the object "Timeline" has a body of "2021-01-02"

Scenario: Animate the construction of a wall
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_attributes.get('PredefinedType').enum_value" to "CONSTRUCTION"
    And I press "bim.edit_task"
    And I press "bim.enable_editing_task_time(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    And I press "bim.edit_task_time"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_product(task={task}, relating_product='')"
    And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
    And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
    And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
    And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
    And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "P1W"
    And I press "bim.visualise_work_schedule_date_range(work_schedule={work_schedule})"
    When I am on frame "1"
    Then "scene.objects.get('IfcWall/Cube').hide_viewport" is "True"
    And "scene.objects.get('IfcWall/Cube').hide_render" is "True"
    When I am on frame "2"
    Then "scene.objects.get('IfcWall/Cube').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/Cube').hide_render" is "False"
    And "scene.objects.get('IfcWall/Cube').color" is "[0.0, 1.0, 0.0, 1]"
    When I am on frame "6"
    Then "scene.objects.get('IfcWall/Cube').color" is "[1.0, 1.0, 1.0, 1]"

Scenario: Animate the demolition of a wall
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_attributes.get('PredefinedType').enum_value" to "DEMOLITION"
    And I press "bim.edit_task"
    And I press "bim.enable_editing_task_time(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    And I press "bim.edit_task_time"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_product(task={task}, relating_product='')"
    And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
    And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
    And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
    And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
    And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "P1W"
    And I press "bim.visualise_work_schedule_date_range(work_schedule={work_schedule})"
    When I am on frame "1"
    Then "scene.objects.get('IfcWall/Cube').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/Cube').hide_render" is "False"
    And "scene.objects.get('IfcWall/Cube').color" is "[1.0, 1.0, 1.0, 1]"
    When I am on frame "2"
    Then "scene.objects.get('IfcWall/Cube').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/Cube').hide_render" is "False"
    And "scene.objects.get('IfcWall/Cube').color" is "[1.0, 0.0, 0.0, 1]"
    When I am on frame "6"
    Then "scene.objects.get('IfcWall/Cube').hide_viewport" is "True"
    And "scene.objects.get('IfcWall/Cube').hide_render" is "True"
    And "scene.objects.get('IfcWall/Cube').color" is "[0.0, 0.0, 0.0, 1]"

Scenario: Animate the operation of a wall
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_attributes.get('PredefinedType').enum_value" to "OPERATION"
    And I press "bim.edit_task"
    And I press "bim.enable_editing_task_time(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    And I press "bim.edit_task_time"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_product(task={task}, relating_product='')"
    And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
    And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
    And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
    And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
    And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "P1W"
    And I press "bim.visualise_work_schedule_date_range(work_schedule={work_schedule})"
    When I am on frame "1"
    Then "scene.objects.get('IfcWall/Cube').color" is "[1.0, 1.0, 1.0, 1]"
    When I am on frame "2"
    Then "scene.objects.get('IfcWall/Cube').color" is "[0.0, 0.0, 1.0, 1]"
    When I am on frame "6"
    Then "scene.objects.get('IfcWall/Cube').color" is "[1.0, 1.0, 1.0, 1]"

Scenario: Animate the movement of a wall
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_attributes.get('PredefinedType').enum_value" to "MOVE"
    And I press "bim.edit_task"
    And I press "bim.enable_editing_task_time(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    And I press "bim.edit_task_time"
    And I add a cube
    And I rename the object "Cube" to "ToObject"
    And the object "ToObject" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/ToObject" is selected
    And I press "bim.assign_product(task={task}, relating_product='')"
    When I add a cube
    And I rename the object "Cube" to "FromObject"
    And the object "FromObject" is selected
    And I press "bim.assign_class"
    And the object "IfcWall/FromObject" is selected
    And I press "bim.assign_process(task={task}, related_object_type='PRODUCT', related_object='')"
    And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
    And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
    And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
    And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
    And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "P1W"
    And I press "bim.visualise_work_schedule_date_range(work_schedule={work_schedule})"
    When I am on frame "1"
    Then "scene.objects.get('IfcWall/FromObject').color" is "[1.0, 1.0, 1.0, 1]"
    And "scene.objects.get('IfcWall/FromObject').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/FromObject').hide_render" is "False"
    And "scene.objects.get('IfcWall/ToObject').hide_viewport" is "True"
    And "scene.objects.get('IfcWall/ToObject').hide_render" is "True"
    When I am on frame "2"
    Then "scene.objects.get('IfcWall/FromObject').color" is "[1.0, 0.5, 0.0, 1]"
    And "scene.objects.get('IfcWall/FromObject').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/FromObject').hide_render" is "False"
    And "scene.objects.get('IfcWall/ToObject').color" is "[1.0, 1.0, 0.0, 1]"
    And "scene.objects.get('IfcWall/ToObject').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/ToObject').hide_render" is "False"
    When I am on frame "6"
    Then "scene.objects.get('IfcWall/FromObject').color" is "[0.0, 0.0, 0.0, 1]"
    Then "scene.objects.get('IfcWall/FromObject').hide_viewport" is "True"
    Then "scene.objects.get('IfcWall/FromObject').hide_render" is "True"
    And "scene.objects.get('IfcWall/ToObject').color" is "[1.0, 1.0, 1.0, 1]"
    And "scene.objects.get('IfcWall/ToObject').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/ToObject').hide_render" is "False"

Scenario: Animate the consumption of a wall
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task_time(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    And I press "bim.edit_task_time"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_process(task={task}, related_object_type='PRODUCT', related_object='')"
    And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
    And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
    And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
    And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
    And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "P1W"
    And I press "bim.visualise_work_schedule_date_range(work_schedule={work_schedule})"
    When I am on frame "1"
    Then "scene.objects.get('IfcWall/Cube').color" is "[1.0, 1.0, 1.0, 1]"
    And "scene.objects.get('IfcWall/Cube').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/Cube').hide_render" is "False"
    When I am on frame "2"
    Then "scene.objects.get('IfcWall/Cube').color" is "[0.0, 1.0, 1.0, 1]"
    And "scene.objects.get('IfcWall/Cube').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/Cube').hide_render" is "False"
    When I am on frame "6"
    Then "scene.objects.get('IfcWall/Cube').color" is "[0.0, 0.0, 0.0, 1]"
    Then "scene.objects.get('IfcWall/Cube').hide_viewport" is "True"
    Then "scene.objects.get('IfcWall/Cube').hide_render" is "True"
