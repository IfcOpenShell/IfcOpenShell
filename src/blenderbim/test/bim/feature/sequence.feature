@sequence
Feature: Sequence

Scenario: Add work plan
    Given an empty IFC project
    When I press "bim.add_work_plan"
    And the variable "work_plan" is "IfcStore.get_file().by_type('IfcWorkPlan')[0].id()"
    Then nothing happens

Scenario: Add Work schedule
    Given an empty IFC project
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    Then nothing happens

Scenario: Remove work plan
    Given an empty IFC project
    When I press "bim.add_work_plan"
    And the variable "work_plan" is "IfcStore.get_file().by_type('IfcWorkPlan')[0].id()"
    When I press "bim.remove_work_plan(work_plan={work_plan})"
    Then nothing happens

Scenario: Remove work schedule
    Given an empty IFC project
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    When I press "bim.remove_work_schedule(work_schedule={work_schedule})"
    Then nothing happens

Scenario: Enable Editing Work Plan
    Given an empty IFC project
    When I press "bim.add_work_plan"
    And the variable "work_plan" is "IfcStore.get_file().by_type('IfcWorkPlan')[0].id()"
    When I press "bim.enable_editing_work_plan(work_plan={work_plan})"
    Then nothing happens

Scenario: Edit Work Plan
    Given an empty IFC project
    When I press "bim.add_work_plan"
    And the variable "work_plan" is "IfcStore.get_file().by_type('IfcWorkPlan')[0].id()"
    And I press "bim.enable_editing_work_plan(work_plan={work_plan})"
    And I set "scene.BIMWorkPlanProperties.work_plan_attributes.get('Name').string_value" to "FooPlan"
    When I press "bim.edit_work_plan()"
    Then nothing happens

Scenario: Edit Work Schedule
    Given an empty IFC project
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule(work_schedule={work_schedule})"
    And I set "scene.BIMWorkScheduleProperties.work_schedule_attributes.get('Name').string_value" to "FooSchedule"
    When I press "bim.edit_work_schedule()"
    Then nothing happens

Scenario: Disable Editing Work Plan
    Given an empty IFC project
    When I press "bim.add_work_plan"
    And the variable "work_plan" is "IfcStore.get_file().by_type('IfcWorkPlan')[0].id()"
    And I press "bim.enable_editing_work_plan_schedules(work_plan={work_plan})"
    When I press "bim.disable_editing_work_plan"
    Then nothing happens

Scenario: Assign work schedule
    Given an empty IFC project
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    When I press "bim.add_work_plan"
    And the variable "work_plan" is "IfcStore.get_file().by_type('IfcWorkPlan')[0].id()"
    And I press "bim.enable_editing_work_plan_schedules(work_plan={work_plan})"
    And I press "bim.assign_work_schedule(work_plan={work_plan}, work_schedule={work_schedule})"
    Then nothing happens

Scenario: Unassign work schedule
    Given an empty IFC project
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    When I press "bim.add_work_plan"
    And the variable "work_plan" is "IfcStore.get_file().by_type('IfcWorkPlan')[0].id()"
    And I press "bim.enable_editing_work_plan_schedules(work_plan={work_plan})"
    And I press "bim.assign_work_schedule(work_plan={work_plan}, work_schedule={work_schedule})"
    And I press "bim.unassign_work_schedule(work_plan={work_plan}, work_schedule={work_schedule})"
    Then nothing happens

Scenario: Delete assigned work schedule
    Given an empty IFC project
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    When I press "bim.add_work_plan"
    And the variable "work_plan" is "IfcStore.get_file().by_type('IfcWorkPlan')[0].id()"
    And I press "bim.enable_editing_work_plan_schedules(work_plan={work_plan})"
    And I press "bim.assign_work_schedule(work_plan={work_plan}, work_schedule={work_schedule})"
    When I press "bim.remove_work_schedule(work_schedule={work_schedule})"
    Then nothing happens

Scenario: Remove Assigned work schedule
    Given an empty IFC project
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    When I press "bim.add_work_plan"
    And the variable "work_plan" is "IfcStore.get_file().by_type('IfcWorkPlan')[0].id()"
    And I press "bim.enable_editing_work_plan_schedules(work_plan={work_plan})"
    When I press "bim.assign_work_schedule(work_plan={work_plan}, work_schedule={work_schedule})"
    Then nothing happens

Scenario: Add work calendar
    Given an empty IFC project
    When I press "bim.add_work_calendar"
    And the variable "work_calendar" is "IfcStore.get_file().by_type('IfcWorkCalendar')[0].id()"
    Then nothing happens

Scenario: Remove work calendar
    Given an empty IFC project
    When I press "bim.add_work_calendar"
    And the variable "work_calendar" is "IfcStore.get_file().by_type('IfcWorkCalendar')[0].id()"
    When I press "bim.remove_work_calendar(work_calendar={work_calendar})"
    Then nothing happens

Scenario: Edit work calendar attributes
    Given an empty IFC project
    When I press "bim.add_work_calendar"
    And the variable "work_calendar" is "IfcStore.get_file().by_type('IfcWorkCalendar')[0].id()"
    When I press "bim.enable_editing_work_calendar(work_calendar={work_calendar})"
    And I set "scene.BIMWorkCalendarProperties.work_calendar_attributes.get('Name').string_value" to "FooCalendar"
    When I press "bim.edit_work_calendar()"
    Then nothing happens

Scenario: Enable editing calendar times
    Given an empty IFC project
    When I press "bim.add_work_calendar"
    And the variable "work_calendar" is "IfcStore.get_file().by_type('IfcWorkCalendar')[0].id()"
    When I press "bim.enable_editing_work_calendar_times(work_calendar={work_calendar})"
    Then nothing happens

Scenario: Add calendar Working Time
    Given an empty IFC project
    When I press "bim.add_work_calendar"
    And the variable "work_calendar" is "IfcStore.get_file().by_type('IfcWorkCalendar')[0].id()"
    When I press "bim.enable_editing_work_calendar_times(work_calendar={work_calendar})"
    When I press "bim.add_work_time(work_calendar={work_calendar}, time_type="WorkingTimes")"
    Then nothing happens

Scenario: Add calendar Exception Time
    Given an empty IFC project
    When I press "bim.add_work_calendar"
    And the variable "work_calendar" is "IfcStore.get_file().by_type('IfcWorkCalendar')[0].id()"
    And I press "bim.enable_editing_work_calendar_times(work_calendar={work_calendar})"
    When I press "bim.add_work_time(work_calendar={work_calendar}, time_type="ExceptionTimes")"
    Then nothing happens

Scenario: Enable editing Working Time Attributes
    Given an empty IFC project
    When I press "bim.add_work_calendar"
    And the variable "work_calendar" is "IfcStore.get_file().by_type('IfcWorkCalendar')[0].id()"
    When I press "bim.enable_editing_work_calendar_times(work_calendar={work_calendar})"
    When I press "bim.add_work_time(work_calendar={work_calendar}, time_type="WorkingTimes")"
    And the variable "work_time" is "IfcStore.get_file().by_type('IfcWorkTime')[0].id()"
    When I press "bim.enable_editing_work_time(work_time={work_time})"

Scenario: Edit Working Time Start and End Period
    Given an empty IFC project
    When I press "bim.add_work_calendar"
    And the variable "work_calendar" is "IfcStore.get_file().by_type('IfcWorkCalendar')[0].id()"
    When I press "bim.enable_editing_work_calendar_times(work_calendar={work_calendar})"
    When I press "bim.add_work_time(work_calendar={work_calendar}, time_type='WorkingTimes')"
    And the variable "work_time" is "IfcStore.get_file().by_type('IfcWorkTime')[0].id()"
    When I press "bim.enable_editing_work_time(work_time={work_time})"
    And I set "scene.BIMWorkCalendarProperties.work_time_attributes.get('Start').string_value" to "2021-01-01"
    And I set "scene.BIMWorkCalendarProperties.work_time_attributes.get('Finish').string_value" to "2022-01-01"
    When I press "bim.edit_work_time()"
    Then nothing happens

Scenario: Add Working Time Period
    Given an empty IFC project
    When I press "bim.add_work_calendar"
    And the variable "work_calendar" is "IfcStore.get_file().by_type('IfcWorkCalendar')[0].id()"
    When I press "bim.enable_editing_work_calendar_times(work_calendar={work_calendar})"
    When I press "bim.add_work_time(work_calendar={work_calendar}, time_type='WorkingTimes')"
    And the variable "work_time" is "IfcStore.get_file().by_type('IfcWorkTime')[0].id()"
    When I press "bim.enable_editing_work_time(work_time={work_time})"
    When I press "bim.assign_recurrence_pattern(work_time={work_time}, recurrence_type='DAILY')"
    And the variable "recurrence_pattern" is "IfcStore.get_file().by_type('IfcRecurrencePattern')[0].id()"
    And I set "scene.BIMWorkCalendarProperties.start_time" to "9AM"
    And I set "scene.BIMWorkCalendarProperties.end_time" to "1PM"
    When I press "bim.add_time_period(recurrence_pattern={recurrence_pattern})"
    When I press "bim.edit_work_time()"
    Then nothing happens

Scenario: Edit Working Time start finish and time period
    Given an empty IFC project
    When I press "bim.add_work_calendar"
    And the variable "work_calendar" is "IfcStore.get_file().by_type('IfcWorkCalendar')[0].id()"
    When I press "bim.enable_editing_work_calendar_times(work_calendar={work_calendar})"
    When I press "bim.add_work_time(work_calendar={work_calendar}, time_type='WorkingTimes')"
    And the variable "work_time" is "IfcStore.get_file().by_type('IfcWorkTime')[0].id()"
    When I press "bim.enable_editing_work_time(work_time={work_time})"
    And I set "scene.BIMWorkCalendarProperties.work_time_attributes.get('Start').string_value" to "2021-01-01"
    And I set "scene.BIMWorkCalendarProperties.work_time_attributes.get('Finish').string_value" to "2022-01-01"
    When I press "bim.assign_recurrence_pattern(work_time={work_time}, recurrence_type='DAILY')"
    And the variable "recurrence_pattern" is "IfcStore.get_file().by_type('IfcRecurrencePattern')[0].id()"
    And I set "scene.BIMWorkCalendarProperties.start_time" to "9AM"
    And I set "scene.BIMWorkCalendarProperties.end_time" to "1PM"
    When I press "bim.add_time_period(recurrence_pattern={recurrence_pattern})"
    When I press "bim.edit_work_time()"
    Then nothing happens


Scenario: Unassign Calendar to task
    Given an empty IFC project
    When I press "bim.add_work_calendar"
    And the variable "work_calendar" is "IfcStore.get_file().by_type('IfcWorkCalendar')[0].id()"
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task_calendar(task={task})"
    And I press "bim.edit_task_calendar(work_calendar={work_calendar}, task={task})"
    When I press "bim.remove_task_calendar(work_calendar={work_calendar}, task={task})"
    Then nothing happens

Scenario: Enable editing task
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    When I press "bim.enable_editing_task_attributes(task={task})"
    Then nothing happens

Scenario: Copy task attribute
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task_attributes(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_attributes[2].string_value" to "Foo"
    When I set "scene.BIMTaskTreeProperties.tasks[1].is_selected" to "True"
    And I press "bim.copy_task_attribute(name='Description')"
    Then nothing happens

Scenario: Unassign task Successor
    Given an empty IFC project
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    When I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_one" is "IfcStore.get_file().by_type('IfcTask')[1].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_two" is "IfcStore.get_file().by_type('IfcTask')[2].id()"
    And I press "bim.enable_editing_task_attributes(task={nested_task_one})"
    And I press "bim.assign_successor(task={nested_task_two})"
    When I press "bim.unassign_successor(task={nested_task_two})"
    Then nothing happens

Scenario: Edit time Lag
    Given an empty IFC project
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    When I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_one" is "IfcStore.get_file().by_type('IfcTask')[1].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_two" is "IfcStore.get_file().by_type('IfcTask')[2].id()"
    And I press "bim.enable_editing_task_attributes(task={nested_task_one})"
    When I press "bim.assign_successor(task={nested_task_two})"
    And the variable "rel_sequence" is "IfcStore.get_file().by_type('IfcRelSequence')[0].id()"
    When I press "bim.assign_lag_time(sequence={rel_sequence})"
    And the variable "lag_time" is "IfcStore.get_file().by_type('IfcLagTime')[0].id()"
    And I press "bim.enable_editing_sequence_lag_time(sequence={rel_sequence}, lag_time={lag_time})"
    And I set "scene.BIMWorkScheduleProperties.lag_time_attributes.get('LagValue').string_value" to "P5D"
    When I press "bim.edit_sequence_lag_time(lag_time={lag_time})"
    Then nothing happens

Scenario: Unassign time Lag
    Given an empty IFC project
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    When I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_one" is "IfcStore.get_file().by_type('IfcTask')[1].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_two" is "IfcStore.get_file().by_type('IfcTask')[2].id()"
    And I press "bim.enable_editing_task_attributes(task={nested_task_one})"
    When I press "bim.assign_successor(task={nested_task_two})"
    And the variable "rel_sequence" is "IfcStore.get_file().by_type('IfcRelSequence')[0].id()"
    When I press "bim.assign_lag_time(sequence={rel_sequence})"
    And the variable "lag_time" is "IfcStore.get_file().by_type('IfcLagTime')[0].id()"
    When I press "bim.unassign_lag_time(sequence={rel_sequence})"
    Then nothing happens

Scenario: Edit Sequence Relationship
    Given an empty IFC project
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    When I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_one" is "IfcStore.get_file().by_type('IfcTask')[1].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_two" is "IfcStore.get_file().by_type('IfcTask')[2].id()"
    And I press "bim.enable_editing_task_attributes(task={nested_task_one})"
    When I press "bim.assign_successor(task={nested_task_two})"
    And the variable "rel_sequence" is "IfcStore.get_file().by_type('IfcRelSequence')[0].id()"
    And I press "bim.enable_editing_sequence_attributes(sequence={rel_sequence})"
    And I set "scene.BIMWorkScheduleProperties.sequence_attributes.get('SequenceType').enum_value" to "START_START"
    When I press "bim.edit_sequence_attributes()"
    Then nothing happens

Scenario: See the current frame date as text
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
    And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
    And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
    And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
    And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "1 w"
    And I press "bim.visualise_work_schedule_date_range(work_schedule={work_schedule})"
    When I am on frame "1"
    Then the object "Timeline" has a body of "2021-01-01"
    When I am on frame "2"
    Then the object "Timeline" has a body of "2021-01-02"

Scenario: Animate the construction of a wall
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task_attributes(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_attributes.get('PredefinedType').enum_value" to "CONSTRUCTION"
    And I press "bim.edit_task"
    And I press "bim.enable_editing_task_time(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    And I press "bim.edit_task_time"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_product(task={task})"
    And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
    And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
    And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
    And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
    And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "1 w"
    And I press "bim.visualise_work_schedule_date_range(work_schedule={work_schedule})"
    When I am on frame "1"
    Then "scene.objects.get('IfcWall/Cube').hide_viewport" is "True"
    And "scene.objects.get('IfcWall/Cube').hide_render" is "True"
    When I am on frame "2"
    Then "scene.objects.get('IfcWall/Cube').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/Cube').hide_render" is "False"
    And "scene.objects.get('IfcWall/Cube').color[:]" is "[0.0, 1.0, 0.0, 1]"
    When I am on frame "7"
    Then "scene.objects.get('IfcWall/Cube').color[:]" is "[1.0, 1.0, 1.0, 1]"

Scenario: Animate the demolition of a wall
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task_attributes(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_attributes.get('PredefinedType').enum_value" to "DEMOLITION"
    And I press "bim.edit_task"
    And I press "bim.enable_editing_task_time(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    And I press "bim.edit_task_time"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_process(task={task}, related_object=0, related_object_type='PRODUCT')"
    And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
    And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
    And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
    And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
    And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "1 w"
    And I press "bim.visualise_work_schedule_date_range(work_schedule={work_schedule})"
    When I am on frame "1"
    Then "scene.objects.get('IfcWall/Cube').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/Cube').hide_render" is "False"
    And "scene.objects.get('IfcWall/Cube').color[:]" is "[1.0, 1.0, 1.0, 1]"
    When I am on frame "2"
    Then "scene.objects.get('IfcWall/Cube').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/Cube').hide_render" is "False"
    And "scene.objects.get('IfcWall/Cube').color[:]" is "[1.0, 0.0, 0.0, 1]"
    When I am on frame "7"
    Then "scene.objects.get('IfcWall/Cube').hide_viewport" is "True"
    And "scene.objects.get('IfcWall/Cube').hide_render" is "True"
    And "scene.objects.get('IfcWall/Cube').color[:]" is "[0.0, 0.0, 0.0, 1]"

Scenario: Animate the operation of a wall
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task_attributes(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_attributes.get('PredefinedType').enum_value" to "OPERATION"
    And I press "bim.edit_task"
    And I press "bim.enable_editing_task_time(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    And I press "bim.edit_task_time"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_product(task={task}, relating_product=0)"
    And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
    And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
    And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
    And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
    And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "1 w"
    And I press "bim.visualise_work_schedule_date_range(work_schedule={work_schedule})"
    When I am on frame "1"
    Then "scene.objects.get('IfcWall/Cube').color[:]" is "[1.0, 1.0, 1.0, 1]"
    When I am on frame "2"
    Then "scene.objects.get('IfcWall/Cube').color[:]" is "[0.0, 0.0, 1.0, 1]"
    When I am on frame "7"
    Then "scene.objects.get('IfcWall/Cube').color[:]" is "[1.0, 1.0, 1.0, 1]"

Scenario: Animate the movement of a wall
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task_attributes(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_attributes.get('PredefinedType').enum_value" to "MOVE"
    And I press "bim.edit_task"
    And I press "bim.enable_editing_task_time(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    And I press "bim.edit_task_time"
    And I add a cube
    And I rename the object "Cube" to "ToObject"
    And the object "ToObject" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/ToObject" is selected
    And I press "bim.assign_product(task={task}, relating_product=0)"
    When I add a cube
    And I rename the object "Cube" to "FromObject"
    And the object "FromObject" is selected
    And I press "bim.assign_class"
    And the object "IfcWall/FromObject" is selected
    And I press "bim.assign_process(task={task}, related_object_type='PRODUCT', related_object=0)"
    And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
    And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
    And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
    And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
    And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "1 w"
    And I press "bim.visualise_work_schedule_date_range(work_schedule={work_schedule})"
    When I am on frame "1"
    Then "scene.objects.get('IfcWall/FromObject').color[:]" is "[1.0, 1.0, 1.0, 1]"
    And "scene.objects.get('IfcWall/FromObject').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/FromObject').hide_render" is "False"
    And "scene.objects.get('IfcWall/ToObject').hide_viewport" is "True"
    And "scene.objects.get('IfcWall/ToObject').hide_render" is "True"
    When I am on frame "2"
    Then "scene.objects.get('IfcWall/FromObject').color[:]" is "[1.0, 0.5, 0.0, 1]"
    And "scene.objects.get('IfcWall/FromObject').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/FromObject').hide_render" is "False"
    And "scene.objects.get('IfcWall/ToObject').color[:]" is "[1.0, 1.0, 0.0, 1]"
    And "scene.objects.get('IfcWall/ToObject').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/ToObject').hide_render" is "False"
    When I am on frame "7"
    Then "scene.objects.get('IfcWall/FromObject').color[:]" is "[0.0, 0.0, 0.0, 1]"
    Then "scene.objects.get('IfcWall/FromObject').hide_viewport" is "True"
    Then "scene.objects.get('IfcWall/FromObject').hide_render" is "True"
    And "scene.objects.get('IfcWall/ToObject').color[:]" is "[1.0, 1.0, 1.0, 1]"
    And "scene.objects.get('IfcWall/ToObject').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/ToObject').hide_render" is "False"

Scenario: Animate the consumption of a wall
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task_time(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    And I press "bim.edit_task_time"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_process(task={task}, related_object_type='PRODUCT', related_object=0)"
    And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
    And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
    And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
    And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
    And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "1 w"
    And I press "bim.visualise_work_schedule_date_range(work_schedule={work_schedule})"
    When I am on frame "1"
    Then "scene.objects.get('IfcWall/Cube').color[:]" is "[1.0, 1.0, 1.0, 1]"
    And "scene.objects.get('IfcWall/Cube').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/Cube').hide_render" is "False"
    When I am on frame "2"
    Then "scene.objects.get('IfcWall/Cube').color[:]" is "[0.2, 0.2, 0.2, 1]"
    And "scene.objects.get('IfcWall/Cube').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/Cube').hide_render" is "False"
    When I am on frame "7"
    Then "scene.objects.get('IfcWall/Cube').color[:]" is "[0.0, 0.0, 0.0, 1]"
    Then "scene.objects.get('IfcWall/Cube').hide_viewport" is "True"
    Then "scene.objects.get('IfcWall/Cube').hide_render" is "True"



Scenario: Clear Previous Animation
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task_attributes(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_attributes.get('PredefinedType').enum_value" to "CONSTRUCTION"
    And I press "bim.edit_task"
    And I press "bim.enable_editing_task_time(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    And I press "bim.edit_task_time"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_product(task={task})"
    And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
    And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
    And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
    And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
    And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "1 w"
    And I press "bim.visualise_work_schedule_date_range(work_schedule={work_schedule})"
    And I press "bim.clear_previous_animation"
    When I am on frame "3"
    Then "scene.objects.get('IfcWall/Cube').hide_viewport" is "False"
    And "scene.objects.get('IfcWall/Cube').hide_render" is "False"
    And "scene.objects.get('IfcWall/Cube').color[:]" is "[1.0, 1.0, 1.0, 1]"

Scenario: Generate Gantt Chart
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I press "bim.enable_editing_task_attributes(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_attributes.get('PredefinedType').enum_value" to "CONSTRUCTION"
    And I press "bim.edit_task"
    And I press "bim.enable_editing_task_time(task={task})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    And I press "bim.edit_task_time"
    And I press "bim.generate_gantt_chart(work_schedule={work_schedule})"
    Then nothing happens

Scenario: Edit task with calendar
    Given an empty IFC project
    When I press "bim.add_work_calendar"
    And the variable "work_calendar" is "IfcStore.get_file().by_type('IfcWorkCalendar')[0].id()"
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_one" is "IfcStore.get_file().by_type('IfcTask')[1].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_two" is "IfcStore.get_file().by_type('IfcTask')[2].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_three" is "IfcStore.get_file().by_type('IfcTask')[3].id()"
    When I press "bim.enable_editing_work_calendar_times(work_calendar={work_calendar})"
    When I press "bim.add_work_time(work_calendar={work_calendar}, time_type="WorkingTimes")"
    When I press "bim.add_work_time(work_calendar={work_calendar}, time_type="ExceptionTimes")"
    And I press "bim.disable_editing_work_calendar"
    And I set "scene.BIMWorkScheduleProperties.active_task_index" to "1"
    And I press "bim.enable_editing_task_sequence()"
    And I press "bim.assign_successor(task={nested_task_two})"
    And I set "scene.BIMWorkScheduleProperties.active_task_index" to "3"
    And I press "bim.assign_predecessor(task={nested_task_two})"
    And I press "bim.disable_editing_task"
    And I press "bim.enable_editing_task_time(task={nested_task_three})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    And I press "bim.edit_task_time"
    And I press "bim.enable_editing_task_calendar(task={task})"
    And I press "bim.edit_task_calendar(work_calendar={work_calendar}, task={task})"
    And I set "scene.BIMWorkScheduleProperties.active_task_index" to "1"
    And I press "bim.enable_editing_task_sequence()"
    And I press "bim.disable_editing_task()"
    Then nothing happens


Scenario: Assign task calendar with Working Time
    Given an empty IFC project
    When I press "bim.add_work_calendar"
    And the variable "work_calendar" is "IfcStore.get_file().by_type('IfcWorkCalendar')[0].id()"
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_one" is "IfcStore.get_file().by_type('IfcTask')[1].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_two" is "IfcStore.get_file().by_type('IfcTask')[2].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_three" is "IfcStore.get_file().by_type('IfcTask')[3].id()"
    When I press "bim.enable_editing_work_calendar_times(work_calendar={work_calendar})"
    When I press "bim.add_work_time(work_calendar={work_calendar}, time_type="WorkingTimes")"
    When I press "bim.add_work_time(work_calendar={work_calendar}, time_type="ExceptionTimes")"
    And I press "bim.disable_editing_work_calendar"
    And I press "bim.enable_editing_task_sequence()"
    And I set "scene.BIMWorkScheduleProperties.active_task_index" to "1"
    And I press "bim.assign_successor(task={nested_task_two})"
    And I set "scene.BIMWorkScheduleProperties.active_task_index" to "3"
    And I press "bim.assign_predecessor(task={nested_task_two})"
    And I press "bim.disable_editing_task"
    And I press "bim.enable_editing_task_calendar(task={task})"
    And I press "bim.edit_task_calendar(work_calendar={work_calendar}, task={nested_task_three})"
    And I press "bim.disable_editing_task()"
    And I press "bim.enable_editing_task_time(task={nested_task_three})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    # And I press "bim.edit_task_time"
    Then nothing happens

Scenario: Assign task calendar with no working time
    Given an empty IFC project
    When I press "bim.add_work_calendar"
    And the variable "work_calendar" is "IfcStore.get_file().by_type('IfcWorkCalendar')[0].id()"
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_one" is "IfcStore.get_file().by_type('IfcTask')[1].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_two" is "IfcStore.get_file().by_type('IfcTask')[2].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_three" is "IfcStore.get_file().by_type('IfcTask')[3].id()"
    And I press "bim.enable_editing_task_sequence()"
    And I set "scene.BIMWorkScheduleProperties.active_task_index" to "1"
    And I press "bim.assign_successor(task={nested_task_two})"
    And I set "scene.BIMWorkScheduleProperties.active_task_index" to "3"
    And I press "bim.assign_predecessor(task={nested_task_two})"
    And I press "bim.disable_editing_task"
    And I press "bim.enable_editing_task_calendar(task={task})"
    And I press "bim.edit_task_calendar(work_calendar={work_calendar}, task={nested_task_three})"
    And I press "bim.disable_editing_task()"
    When I press "bim.enable_editing_work_calendar_times(work_calendar={work_calendar})"
    When I press "bim.add_work_time(work_calendar={work_calendar}, time_type="WorkingTimes")"
    And the variable "work_time" is "IfcStore.get_file().by_type('IfcWorkTime')[0].id()"
    When I press "bim.enable_editing_work_time(work_time={work_time})"
    And I set "scene.BIMWorkCalendarProperties.work_time_attributes.get('Start').string_value" to "01-08-2021"
    And I set "scene.BIMWorkCalendarProperties.work_time_attributes.get('Finish').string_value" to "01-08-2022"
    When I press "bim.assign_recurrence_pattern(work_time={work_time}, recurrence_type='DAILY')"
    And the variable "recurrence_pattern" is "IfcStore.get_file().by_type('IfcRecurrencePattern')[0].id()"
    And I set "scene.BIMWorkCalendarProperties.start_time" to "9AM"
    And I set "scene.BIMWorkCalendarProperties.end_time" to "1PM"
    When I press "bim.add_time_period(recurrence_pattern={recurrence_pattern})"
    And I press "bim.edit_work_time"
    # When I press "bim.add_work_time(work_calendar={work_calendar}, time_type="ExceptionTimes")"
    And I press "bim.disable_editing_work_calendar"
    And I press "bim.enable_editing_task_time(task={nested_task_three})"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleStart').string_value" to "2021-01-02"
    And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get('ScheduleFinish').string_value" to "2021-01-06"
    And I press "bim.edit_task_time"
    Then nothing happens

Scenario: Contract Task
    Given an empty IFC project
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "summary_task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    When I press "bim.add_task(task={summary_task})"
    And I press "bim.contract_task(task={summary_task})"
    Then nothing happens

Scenario: Expand Task
    Given an empty IFC project
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "summary_task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    When I press "bim.add_task(task={summary_task})"
    And I press "bim.contract_task(task={summary_task})"
    And I press "bim.expand_task(task={summary_task})"
    Then nothing happens

Scenario: Contract All Tasks
    Given an empty IFC project
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "summary_task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    When I press "bim.add_task(task={summary_task})"
    And the variable "nested_task_one" is "IfcStore.get_file().by_type('IfcTask')[-1].id()"
    When I press "bim.add_task(task={summary_task})"
    And the variable "nested_task_two" is "IfcStore.get_file().by_type('IfcTask')[-1].id()"
    When I press "bim.contract_all_tasks()"
    Then nothing happens

Scenario: Expand All Tasks
    Given an empty IFC project
    When I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "summary_task" is "IfcStore.get_file().by_type('IfcTask')[-1].id()"
    When I press "bim.add_task(task={summary_task})"
    And the variable "nested_task_one" is "IfcStore.get_file().by_type('IfcTask')[-1].id()"
    When I press "bim.add_task(task={summary_task})"
    And the variable "nested_task_two" is "IfcStore.get_file().by_type('IfcTask')[-1].id()"
    And I press "bim.contract_all_tasks()"
    When I press "bim.expand_all_tasks()"
    Then nothing happens

Scenario: Assign Product Output
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class(ifc_class='IfcWall', predefined_type='SOLIDWALL')"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_product(task={task})"
    Then nothing happens

Scenario: Assign Product Input
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class(ifc_class='IfcWall', predefined_type='SOLIDWALL')"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_process(task={task},related_object=0, related_object_type='PRODUCT')"
    Then nothing happens

Scenario: Select Assigned Outputs
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class()"
    And I press "bim.assign_product(task={task})"
    When I press "bim.select_task_related_products(task={task})"
    Then nothing happens

Scenario: Select Assigned Inputs
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    And I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class()"
    And the object "IfcWall/Cube" is selected
    And I press "bim.assign_process(task={task}, related_object_type='PRODUCT')"
    When I press "bim.select_task_related_products(task={task})"
    Then nothing happens

Scenario: Duplicate Task
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    When I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_one" is "IfcStore.get_file().by_type('IfcTask')[1].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_two" is "IfcStore.get_file().by_type('IfcTask')[2].id()"
    And I press "bim.enable_editing_task_attributes(task={nested_task_one})"
    And I press "bim.assign_successor(task={nested_task_two})"
    When I press "bim.duplicate_task(task={task})"
    Then nothing happens

Scenario: Duplicate Task and edit sequence Relationship
    Given an empty IFC project
    And I press "bim.add_work_schedule"
    And the variable "work_schedule" is "IfcStore.get_file().by_type('IfcWorkSchedule')[0].id()"
    And I press "bim.enable_editing_work_schedule_tasks(work_schedule={work_schedule})"
    When I press "bim.add_summary_task(work_schedule={work_schedule})"
    And the variable "task" is "IfcStore.get_file().by_type('IfcTask')[0].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_one" is "IfcStore.get_file().by_type('IfcTask')[1].id()"
    When I press "bim.add_task(task={task})"
    And the variable "nested_task_two" is "IfcStore.get_file().by_type('IfcTask')[2].id()"
    And I press "bim.enable_editing_task_attributes(task={nested_task_one})"
    And I press "bim.assign_successor(task={nested_task_two})"
    And I press "bim.duplicate_task(task={task})"
    When I press "bim.enable_editing_task_sequence()"
    And I set "scene.BIMWorkScheduleProperties.active_task_index" to "1"
    Then nothing happens

Scenario: Add Animation Camera
    Given an empty IFC project
    And I add a cube
    And the object "Cube" is selected
    And I set "scene.BIMRootProperties.ifc_product" to "IfcElement"
    And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
    And I press "bim.assign_class"
    And I press "bim.add_animation_camera"
    Then "scene.objects.get('4D Camera').name" is "4D Camera"
