# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.


import bpy
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.root
import pytest

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.sequence import Sequence as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Sequence)


class TestGetElementStatus(NewFile):
    def test_common_pset(self):
        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, element, "Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(ifc, pset, properties={"Status": ["EXISTING", "TEMPORARY"]})
        assert subject.get_element_status(element) == {"EXISTING", "TEMPORARY"}

    def test_epset(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        element = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, element, "EPset_Status")
        ifcopenshell.api.pset.edit_pset(ifc, pset, properties={"Status": ["EXISTING", "TEMPORARY"]})
        assert subject.get_element_status(element) == {"EXISTING", "TEMPORARY"}


class TestEnableStatusFiltersOperator(NewFile):
    @pytest.mark.parametrize("schema", ["IFC2X3", "IFC4", "IFC4X3_ADD2"])
    def test_enumerated_status_property(self, schema):
        tool.Project.get_project_props().export_schema = schema
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        element = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, element, "Pset_WallCommon")
        values = [ifc.create_entity("IfcLabel", v) for v in ("EXISTING", "TEMPORARY")]
        pset.HasProperties = [ifc.create_entity("IfcPropertyEnumeratedValue", Name="Status", EnumerationValues=values)]

        assert bpy.ops.bim.enable_status_filters() == {"FINISHED"}

        props = tool.Sequence.get_status_props()
        assert props.is_enabled
        assert {s.name for s in props.statuses} >= {"No Status", "EXISTING", "TEMPORARY"}


class TestAssignStatus(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()

        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        obj = bpy.data.objects["Cube"]
        bpy.ops.bim.assign_class(ifc_class="IfcActuator", predefined_type="ELECTRICACTUATOR", userdefined_type="")
        element = tool.Ifc.get_entity(obj)
        assert element

        bpy.ops.bim.assign_status(status="NEW")
        assert subject.get_element_status(element) == {"NEW"}

        bpy.ops.bim.assign_status(status="EXISTING")
        assert subject.get_element_status(element) == {"EXISTING"}

        bpy.ops.bim.assign_status(status="EXISTING", should_unassign_status=True)
        assert subject.get_element_status(element) == set()


class TestParseDatetime:
    def test_reading_a_value_without_a_time_as_a_date(self):
        import datetime

        import bonsai.bim.module.sequence.helper as helper

        assert helper.parse_datetime("2026-01-19") == datetime.date(2026, 1, 19)
        assert helper.parse_datetime("19/01/26") == datetime.date(2026, 1, 19)

    def test_keeping_a_given_time(self):
        import datetime

        import bonsai.bim.module.sequence.helper as helper

        assert helper.parse_datetime("2026-01-19T13:00:00") == datetime.datetime(2026, 1, 19, 13)
        assert helper.parse_datetime("19/01/26 13:30") == datetime.datetime(2026, 1, 19, 13, 30)


class TestCanonicaliseDatetime:
    def test_showing_the_time_of_a_task_date(self):
        import datetime

        import bonsai.bim.module.sequence.helper as helper

        assert helper.canonicalise_datetime(datetime.datetime(2026, 1, 19, 13, 30)) == "19/01/26 13:30"
        assert helper.canonicalise_datetime(None) == "-"
        assert helper.parse_datetime(helper.canonicalise_datetime(datetime.datetime(2026, 1, 19, 13))) == (
            datetime.datetime(2026, 1, 19, 13)
        )


class TestLoadTaskProperties(NewFile):
    def test_showing_the_times_and_work_hours_of_tasks(self):
        import ifcopenshell.api.sequence
        import ifcopenshell.util.date

        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        work_schedule = ifcopenshell.api.sequence.add_work_schedule(ifc)
        summary = ifcopenshell.api.sequence.add_task(ifc, work_schedule=work_schedule, identification="1")
        for identification, start in (("1.1", "2026-01-19T09:00:00"), ("1.2", "2026-01-20T13:00:00")):
            task = ifcopenshell.api.sequence.add_task(ifc, parent_task=summary, identification=identification)
            task_time = ifcopenshell.api.sequence.add_task_time(ifc, task=task)
            attributes = {"ScheduleStart": start, "ScheduleDuration": "PT2H", "DurationType": "WORKTIME"}
            ifcopenshell.api.sequence.edit_task_time(ifc, task_time=task_time, attributes=attributes)
        subject.load_task_tree(work_schedule)
        subject.load_task_properties()
        items = {item.identification: item for item in subject.get_task_tree_props().tasks}
        assert items["1"].derived_start == "19/01/26 09:00"
        assert items["1"].derived_finish == "20/01/26 15:00"
        assert items["1"].derived_duration == str(ifcopenshell.util.date.readable_ifc_duration("P1DT6H"))
