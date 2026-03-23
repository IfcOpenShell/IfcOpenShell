# This file was generated with the assistance of an AI coding tool.
from __future__ import annotations

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.owner.settings
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.sequence
import ifcopenshell.api.unit
import pytest

from ifcquery.schedule import schedule


@pytest.fixture
def schedule_model():
    """Create an IFC4 model with a work schedule and nested tasks."""
    f = ifcopenshell.api.project.create_file()
    ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
    ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]

    project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="TestProject")
    ifcopenshell.api.unit.assign_unit(f)

    ws = ifcopenshell.api.sequence.add_work_schedule(f, name="Construction Schedule")

    task1 = ifcopenshell.api.sequence.add_task(f, work_schedule=ws, name="Phase 1", identification="P1")
    tt1 = ifcopenshell.api.sequence.add_task_time(f, task=task1)
    ifcopenshell.api.sequence.edit_task_time(
        f, task_time=tt1, attributes={"ScheduleStart": "2024-01-01", "ScheduleFinish": "2024-06-30"}
    )

    task2 = ifcopenshell.api.sequence.add_task(f, work_schedule=ws, name="Phase 2", identification="P2")
    subtask = ifcopenshell.api.sequence.add_task(f, parent_task=task1, name="Sub Task", identification="S1")

    return f


class TestSchedule:
    def test_returns_list(self, schedule_model):
        result = schedule(schedule_model)
        assert isinstance(result, list)

    def test_finds_work_schedule(self, schedule_model):
        result = schedule(schedule_model)
        assert len(result) == 1

    def test_work_schedule_has_name(self, schedule_model):
        result = schedule(schedule_model)
        assert result[0]["name"] == "Construction Schedule"

    def test_work_schedule_has_id(self, schedule_model):
        result = schedule(schedule_model)
        assert isinstance(result[0]["id"], int)
        assert result[0]["id"] > 0

    def test_work_schedule_has_tasks(self, schedule_model):
        result = schedule(schedule_model)
        tasks = result[0]["tasks"]
        assert isinstance(tasks, list)
        assert len(tasks) >= 1

    def test_task_has_required_fields(self, schedule_model):
        result = schedule(schedule_model)
        task = result[0]["tasks"][0]
        assert "id" in task
        assert "name" in task
        assert "start" in task
        assert "finish" in task
        assert "is_milestone" in task
        assert "outputs" in task
        assert "subtasks" in task

    def test_task_name(self, schedule_model):
        result = schedule(schedule_model)
        task_names = [t["name"] for t in result[0]["tasks"]]
        assert "Phase 1" in task_names

    def test_task_start_finish(self, schedule_model):
        result = schedule(schedule_model)
        phase1 = next(t for t in result[0]["tasks"] if t["name"] == "Phase 1")
        assert phase1["start"] is not None
        assert phase1["finish"] is not None

    def test_subtasks(self, schedule_model):
        result = schedule(schedule_model)
        phase1 = next(t for t in result[0]["tasks"] if t["name"] == "Phase 1")
        assert len(phase1["subtasks"]) == 1
        assert phase1["subtasks"][0]["name"] == "Sub Task"

    def test_empty_model_returns_empty_list(self, model):
        result = schedule(model)
        assert result == []

    def test_max_depth_none_returns_full_tree(self, schedule_model):
        result = schedule(schedule_model, max_depth=None)
        phase1 = next(t for t in result[0]["tasks"] if t["name"] == "Phase 1")
        assert isinstance(phase1["subtasks"], list)
        assert len(phase1["subtasks"]) == 1

    def test_max_depth_1_truncates_subtasks(self, schedule_model):
        result = schedule(schedule_model, max_depth=1)
        phase1 = next(t for t in result[0]["tasks"] if t["name"] == "Phase 1")
        assert isinstance(phase1["subtasks"], dict)
        assert phase1["subtasks"]["truncated"] is True
        assert phase1["subtasks"]["count"] == 1

    def test_max_depth_truncation_shows_count(self, schedule_model):
        result = schedule(schedule_model, max_depth=1)
        # Phase 2 has no subtasks — should return empty list, not truncation dict
        phase2 = next(t for t in result[0]["tasks"] if t["name"] == "Phase 2")
        assert phase2["subtasks"] == []

    def test_max_depth_2_expands_to_depth_2(self, schedule_model):
        result = schedule(schedule_model, max_depth=2)
        phase1 = next(t for t in result[0]["tasks"] if t["name"] == "Phase 1")
        # subtask at depth 2 should be fully expanded (it has no children)
        assert isinstance(phase1["subtasks"], list)
        assert phase1["subtasks"][0]["name"] == "Sub Task"
        assert phase1["subtasks"][0]["subtasks"] == []
