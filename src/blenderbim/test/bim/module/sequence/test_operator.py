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
