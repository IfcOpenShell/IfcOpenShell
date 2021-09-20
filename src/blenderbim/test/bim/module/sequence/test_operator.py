# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import test.bim.bootstrap


class TestVisualiseWorkScheduleDateRange(test.bim.bootstrap.NewFile):
    @test.bim.bootstrap.scenario
    def test_seeing_the_current_frame_date_as_text(self):
        return """
        Given an empty IFC project
        And I press "bim.add_work_schedule"
        And I press "bim.enable_editing_tasks(work_schedule=72)"
        And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
        And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
        And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
        And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
        And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "P1W"
        And I press "bim.visualise_work_schedule_date_range(work_schedule=72)"
        When I am on frame "1"
        Then the object "Timeline" has a body of "2021-01-01"
        When I am on frame "2"
        Then the object "Timeline" has a body of "2021-01-02"
        """

    @test.bim.bootstrap.scenario
    def test_animating_the_construction_of_a_wall(self):
        return """
        Given an empty IFC project
        And I press "bim.add_work_schedule"
        And I press "bim.enable_editing_tasks(work_schedule=72)"
        And I press "bim.add_summary_task(work_schedule=72)"
        And I press "bim.enable_editing_task(task=76)"
        And I set "scene.BIMWorkScheduleProperties.task_attributes.get("PredefinedType").enum_value" to "CONSTRUCTION"
        And I press "bim.edit_task"
        And I press "bim.enable_editing_task_time(task=76)"
        And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get("ScheduleStart").string_value" to "2021-01-02"
        And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get("ScheduleFinish").string_value" to "2021-01-06"
        And I press "bim.edit_task_time"
        And the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        And the object "IfcWall/Cube" is selected
        And I press "bim.assign_product(task=76, relating_product='')"
        And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
        And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
        And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
        And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
        And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "P1W"
        And I press "bim.visualise_work_schedule_date_range(work_schedule=72)"
        When I am on frame "1"
        Then "scene.objects.get('IfcWall/Cube').hide_viewport" is "True"
        And "scene.objects.get('IfcWall/Cube').hide_render" is "True"
        When I am on frame "2"
        Then "scene.objects.get('IfcWall/Cube').hide_viewport" is "False"
        And "scene.objects.get('IfcWall/Cube').hide_render" is "False"
        And "scene.objects.get('IfcWall/Cube').color" is "[0.0, 1.0, 0.0, 1]"
        When I am on frame "6"
        Then "scene.objects.get('IfcWall/Cube').color" is "[1.0, 1.0, 1.0, 1]"
        """

    @test.bim.bootstrap.scenario
    def test_animating_the_demolition_of_a_wall(self):
        return """
        Given an empty IFC project
        And I press "bim.add_work_schedule"
        And I press "bim.enable_editing_tasks(work_schedule=72)"
        And I press "bim.add_summary_task(work_schedule=72)"
        And I press "bim.enable_editing_task(task=76)"
        And I set "scene.BIMWorkScheduleProperties.task_attributes.get("PredefinedType").enum_value" to "DEMOLITION"
        And I press "bim.edit_task"
        And I press "bim.enable_editing_task_time(task=76)"
        And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get("ScheduleStart").string_value" to "2021-01-02"
        And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get("ScheduleFinish").string_value" to "2021-01-06"
        And I press "bim.edit_task_time"
        And the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        And the object "IfcWall/Cube" is selected
        And I press "bim.assign_product(task=76, relating_product='')"
        And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
        And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
        And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
        And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
        And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "P1W"
        And I press "bim.visualise_work_schedule_date_range(work_schedule=72)"
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
        """

    @test.bim.bootstrap.scenario
    def test_animating_the_operation_of_a_wall(self):
        return """
        Given an empty IFC project
        And I press "bim.add_work_schedule"
        And I press "bim.enable_editing_tasks(work_schedule=72)"
        And I press "bim.add_summary_task(work_schedule=72)"
        And I press "bim.enable_editing_task(task=76)"
        And I set "scene.BIMWorkScheduleProperties.task_attributes.get("PredefinedType").enum_value" to "OPERATION"
        And I press "bim.edit_task"
        And I press "bim.enable_editing_task_time(task=76)"
        And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get("ScheduleStart").string_value" to "2021-01-02"
        And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get("ScheduleFinish").string_value" to "2021-01-06"
        And I press "bim.edit_task_time"
        And the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        And the object "IfcWall/Cube" is selected
        And I press "bim.assign_product(task=76, relating_product='')"
        And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
        And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
        And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
        And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
        And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "P1W"
        And I press "bim.visualise_work_schedule_date_range(work_schedule=72)"
        When I am on frame "1"
        Then "scene.objects.get('IfcWall/Cube').color" is "[1.0, 1.0, 1.0, 1]"
        When I am on frame "2"
        Then "scene.objects.get('IfcWall/Cube').color" is "[0.0, 0.0, 1.0, 1]"
        When I am on frame "6"
        Then "scene.objects.get('IfcWall/Cube').color" is "[1.0, 1.0, 1.0, 1]"
        """

    @test.bim.bootstrap.scenario
    def test_animating_the_movement_of_a_wall(self):
        return """
        Given an empty IFC project
        And I press "bim.add_work_schedule"
        And I press "bim.enable_editing_tasks(work_schedule=72)"
        And I press "bim.add_summary_task(work_schedule=72)"
        And I press "bim.enable_editing_task(task=76)"
        And I set "scene.BIMWorkScheduleProperties.task_attributes.get("PredefinedType").enum_value" to "MOVE"
        And I press "bim.edit_task"
        And I press "bim.enable_editing_task_time(task=76)"
        And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get("ScheduleStart").string_value" to "2021-01-02"
        And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get("ScheduleFinish").string_value" to "2021-01-06"
        And I press "bim.edit_task_time"
        And I rename the object "Cube" to "ToObject"
        And the object "ToObject" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        And the object "IfcWall/ToObject" is selected
        And I press "bim.assign_product(task=76, relating_product='')"
        When I add a cube
        And I rename the object "Cube" to "FromObject"
        And the object "FromObject" is selected
        And I press "bim.assign_class"
        And the object "IfcWall/FromObject" is selected
        And I press "bim.assign_process(task=76, related_object_type="PRODUCT", related_object='')"
        And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
        And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
        And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
        And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
        And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "P1W"
        And I press "bim.visualise_work_schedule_date_range(work_schedule=72)"
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
        """

    @test.bim.bootstrap.scenario
    def test_animating_the_consumption_of_a_wall(self):
        return """
        Given an empty IFC project
        And I press "bim.add_work_schedule"
        And I press "bim.enable_editing_tasks(work_schedule=72)"
        And I press "bim.add_summary_task(work_schedule=72)"
        And I press "bim.enable_editing_task_time(task=76)"
        And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get("ScheduleStart").string_value" to "2021-01-02"
        And I set "scene.BIMWorkScheduleProperties.task_time_attributes.get("ScheduleFinish").string_value" to "2021-01-06"
        And I press "bim.edit_task_time"
        And the object "Cube" is selected
        And I set "scene.BIMRootProperties.ifc_class" to "IfcWall"
        And I press "bim.assign_class"
        And the object "IfcWall/Cube" is selected
        And I press "bim.assign_process(task=76, related_object_type="PRODUCT", related_object='')"
        And I set "scene.BIMWorkScheduleProperties.visualisation_start" to "01/01/21"
        And I set "scene.BIMWorkScheduleProperties.visualisation_finish" to "01/02/21"
        And I set "scene.BIMWorkScheduleProperties.speed_types" to "FRAME_SPEED"
        And I set "scene.BIMWorkScheduleProperties.speed_animation_frames" to "7"
        And I set "scene.BIMWorkScheduleProperties.speed_real_duration" to "P1W"
        And I press "bim.visualise_work_schedule_date_range(work_schedule=72)"
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
        """
